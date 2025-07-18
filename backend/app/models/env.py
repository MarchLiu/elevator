from math import floor
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from app.models.messages import *
import heapq
from typing import Optional, Literal
import asyncio
from dataclasses import field
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

@dataclass
class Elevator:
    id: int
    scene_id: int
    maximum: int
    running: bool
    closed: bool
    level: float
    direction: Optional[Literal["up", "down"]]
    want: dict[int, int] = field(default_factory=dict)
    
    def is_full(self):
        return sum(self.want.values()) >= self.maximum

@dataclass
class Passenger:
    id: int
    scene_id: int
    level: int
    want: int

class BaseEnv:
    pass

class BaseAgent:
    async def post_env(self, env: BaseEnv):
        pass
    async def read(self) -> BaseMessage:
        pass
        
class BaseEnv:
    def __init__(self, scene_id: int, agent: BaseAgent, level: int=25, maximum: int=10, elevator_count: int=4):
        self.scene_id = scene_id
        self.elevators = [
            Elevator(
                    id=i, 
                    scene_id=scene_id, 
                    maximum=maximum, 
                    running=False, 
                    level=0, 
                    direction=None, 
                    want={}, 
                    current={}, 
                    closed=True
                ) 
                for i in range(elevator_count)
            ]
        self.passengers = {}
        self.tick = 0
        self.agent = agent
        self.level = level
        self.rate = 1000 # 这个参数表示电梯运行过程中多少个 tick 对应正常倍速下的 1 秒时间，用于需要模拟实时运行的场景
        self.step = 100 # 这个参数表示每次运行多少个 tick
        self.one_level = 3000 # 这个参数表示电梯运行过程中多少个 tick 上升或下降一个 level
        
    async def post_message(self, *messages: BaseMessage):
        raise NotImplementedError
    
    async def pop_message(self):
        raise NotImplementedError
                
    def on_message(self, message: BaseMessage):
        if isinstance(message, GraceExit):
            self.grace_stop(message.timeout_ticks)
        elif isinstance(message, CallAction):
            self.call_action(message)
        elif isinstance(message, WantAction):
            self.want_action(message.elevator_id, message.want)
        elif isinstance(message, UpAction):
            self.up_action(message)
        elif isinstance(message, DownAction):
            self.down_action(message)
        elif isinstance(message, StopAction):
            self.stop_action(message)
        elif isinstance(message, CloseAction):
            self.close_action(message)
        elif isinstance(message, OpenAction):
            self.open_action(message)
        else:
            raise ValueError(f"Unknown message type: {type(message)}")

    def grace_stop(self, timeout_ticks: int):
        raise NotImplementedError
                
    def call_action(self, message: CallAction):
        group = self.passengers.get(message.level, {})
        # 顶层只能向下，底层只能向上
        direction = message.direction
        if self.level - 1 == message.level:
            direction = "down"
        elif message.level == 0:
            direction = "up"            
        
        bucket = group.get(direction, [])
        bucket.append(Passenger(
            id=message.id,
            scene_id=message.scene_id,
            level=message.level,
            want=message.want
        ))
        group[message.direction] = bucket
        self.passengers[message.level] = group
        
    def want_action(self, message: WantAction):
        c = self.elevators[message.elevator_id].want.get(message.want, 0)
        self.elevators[message.elevator_id].want[message.want] = c + 1

    def up_action(self, message: UpAction):
        elevator = self.elevators[message.elevator_id]
        if elevator.level < self.level - 1:
            elevator.direction = "up"
            if elevator.closed:
                elevator.running = True
        else:
            elevator.running = False
        
    def down_action(self, message: DownAction):
        elevator = self.elevators[message.elevator_id]
        
        if elevator.level > 0:
            elevator.direction = "down"
            if elevator.closed:
                elevator.running = True
        else:
            elevator.running = False
            
            
    def stop_action(self, message: StopAction):
        elevator = self.elevators[message.elevator_id]
        elevator.running = False
        
    def dump(self):
        return EnvMap(
            level=self.level,
            tick=self.tick,
            elevators=self.elevators,
            passengers=self.passengers
        )
        
    def close_action(self, message: CloseAction):
        elevator = self.elevators[message.elevator_id]
        elevator.closed = True
        if elevator.direction is not None:
            elevator.running = True
        
    def open_action(self, message: OpenAction):
        self.elevators[message.elevator_id].closed = False

    @classmethod
    def from_json(cls, data: dict[str, Any]):
        return cls(
            scene_id=data["scene_id"],
            elevators=[Elevator.from_json(elevator) for elevator in data["elevators"]],
            passengers=[Passenger.from_json(passenger) for passenger in data["passengers"]],
            tick=data["tick"])
        
    async def run_tick(self, step=None):
        s = step or self.step
        await self.agent.post_env(self)
        async for message in self.agent.read():
            await self.post_message(message)

        while True:
            message = await self.pop_message()
            if message is None:
                break
            elif isinstance(message, GraceExit):
                return
            else:
                self.on_message(message)
            await asyncio.sleep(0)
        
        for elevator in self.elevators:
            if elevator.running and elevator.closed:
                elevator.level += s / self.one_level
            elif not (elevator.running or elevator.closed):
                passengers_count = 0
                if elevator.level == floor(elevator.level):
                    self.check_out(elevator)
                    passengers_count += self.check_in(elevator)
                waiting = 3000+(passengers_count-1)*2000 # 等待时间
                await self.post_message(CloseAction(
                    id=elevator.id,
                    scene_id=elevator.scene_id,
                    tick=self.tick+waiting,
                    category="close",
                    elevator_id=elevator.id
                ))
            elif elevator.direction is not None and elevator.closed:
                elevator.running = True
                
        self.tick += s
        
    def check_out(self, elevator):
        if elevator.level == floor(elevator.level):
            if not elevator.closed:
                passengers = elevator.want.get(elevator.level, 0)
                if passengers > 0:
                    del elevator.want[elevator.level]
                return passengers
        return 0
        
    def check_in(self, elevator):
        if not elevator.closed:
            passengers = self.passengers.get(elevator.level, {}).get(elevator.direction, [])
            if passengers:
                current = sum(elevator.want.values())
                moving = min(elevator.maximum-current, len(passengers))
                group = passengers[:moving]
                for passenger in group:
                    elevator.want[passenger.want] = elevator.want.get(passenger.want, 0) + 1
                self.passengers[elevator.level][elevator.direction] = passengers[moving:]
                return moving
        return 0
        
        
    async def run_loop(self, step=None):
        while True:            
            await self.run_tick(step)
            await asyncio.sleep(0)
            
                
class MemEnv(BaseEnv):
    def __init__(self, scene_id: int, agent: BaseAgent, level: int=25, maximum: int=10, elevator_count: int=4):
        super().__init__(scene_id, agent, level, maximum, elevator_count)
        self.messages = []
        self.serial = 0
        
    async def post_message(self, *messages: BaseModel):
        for message in messages:
            heapq.heappush(self.messages, 
                        (
                            message.tick, 
                            self.serial, 
                            message.model_copy(
                                update={"id": self.serial}
                            )
                        ))
            self.serial += 1
        
    async def pop_message(self):
        if len(self.messages) == 0:
            return None
        tick, serial, message = self.messages[0]
        if tick > self.tick:
            return None
        heapq.heappop(self.messages)

        return message
    
class DBMessage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    scene_id: int
    tick: int
    meta: dict = Field(sa_column=Column(JSON))
    content: dict = Field(sa_column=Column(JSON))
    
    def to_message(self) -> BaseMessage:
        return DBMessage.model_validate(self).to_message()
    
class DBEnv(BaseEnv):
    def __init__(self, db, scene_id: int, level: int=25, maximum: int=10, elevator_count: int=4):
        super().__init__(scene_id, level, maximum, elevator_count)
        self.db = db
        
    async def post_message(self, *messages: BaseModel):
        for message in messages:
            meta = DBMeta(
                category=message.category
            )
            db_message = DBMessage(
                scene_id=message.scene_id,
                tick=message.tick,
                meta=meta,
                content=message.to_dict()
            )
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)

    async def pop_message(self):
        message = self.db.query(BaseMessage)\
            .filter(BaseMessage.scene_id == self.scene_id)\
            .filter(BaseMessage.tick <= self.tick)\
            .order_by(BaseMessage.tick)\
            .with_for_update(skip_locked=True)\
            .delete(synchronize_session=False)\
            .returning(BaseMessage)\
            .first()
        if message is None:
            return None
        
        return message.to_message()

class EnvMap(BaseModel):
    level:int
    tick:int
    elevators: list[Elevator]
    passengers: dict[int, dict[Literal["up", "down"], list[Passenger]]]
