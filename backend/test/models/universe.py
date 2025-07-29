"""
设定测试过程中的通用逻辑
"""
from app.models.env import *
from app.models.messages import *


class TestAgent(BaseAgent):
    def __init__(self, scene_id: int):
        self.messages = []
        self.serial = 0
        self.scene_id = scene_id
        
    def match_direction(self, elevator: Elevator, direction: str):
        if elevator.direction is None:
            return True
        return elevator.direction == direction
    
    async def post_env(self, env: BaseEnv):
        envMap = env.dump()
        calling = self.all_on_call(env)
        for elevator in envMap.elevators:
            on_level = envMap.passengers.get(elevator.on_level(), {})
            if elevator.arrive_level():
                if self.match_direction(elevator, "up") and len(on_level.get("up", [])) > 0 and not elevator.is_full():
                    if len(on_level.get("up", []))> 0:
                        await self.stop_and_open(elevator, env.tick)
                        await self.up_action(elevator, env.tick)
                        moved = self.moved(elevator, len(on_level.get("up", [])))
                        rest = len(on_level.get("up", []))-moved
                        on_level["up"] = on_level.get("up", [])[:rest]
                elif self.match_direction(elevator, "down") and len(on_level.get("down", [])) > 0 and not elevator.is_full():
                    if len(on_level.get("down", []))> 0:
                        await self.stop_and_open(elevator, env.tick)
                        await self.down_action(elevator, env.tick)
                        moved = self.moved(elevator, len(on_level.get("down", [])))
                        rest = len(on_level.get("down", []))-moved
                        on_level["down"] = on_level.get("down", [])[:rest]
                
                current = elevator.want.get(elevator.on_level(), 0)
                if current > 0:
                    # 在电梯打开后，环境程序会驱动乘客离开电梯
                    await self.stop_and_open(elevator, env.tick)
                
                direction = elevator.direction
                
                if self.follow_call(calling, elevator) > 0:
                    await self.to_action(elevator, direction, env)
                    calling = self.clean_on_call(calling, elevator)
                elif sum(calling) > 0 and direction is None:
                    direction = self.closest_call(calling, elevator)
                    if direction is not None:
                        await self.to_action(elevator, direction, env)
                        elevator.direction = direction
                        calling = self.clean_on_call(calling, elevator)
                else: #此时没有等待的呼叫
                    if len(elevator.want) == 0:
                        if elevator.running or elevator.direction is not None:
                            await self.stop_action(elevator, env.tick)
                            await self.clean_direction_action(elevator, env.tick+100)
                    else:
                        await self.to_action(elevator, elevator.direction, env)
            envMap.passengers[elevator.on_level()] = on_level


    def moved(self, elevator: Elevator, passengers: int):
        max_moved = elevator.maximum - sum(elevator.want.values())
        return min(passengers, max_moved)
    
    def clean_on_call(self, calling, elevator: Elevator):
        up = calling[elevator.on_level()+1:]
        down = calling[:elevator.on_level()]
        if elevator.direction == "up":
            up = [0] * (len(up) - 1)
        elif elevator.direction == "down":
            down = [0] * (len(down) - 1)
        return up + down
                        
    def closest_call(self, calling, elevator: Elevator):
        """
        查找离电梯最近的呼叫在哪个方向，如果没有呼叫，返回None
        """
        up = calling[elevator.on_level()+1:]
        down = calling[:elevator.on_level()]
        
        if sum(up) == 0 and sum(down) == 0:
            return None
        elif sum(up) == 0:
            return "down"
        elif sum(down) == 0:
            return "up"
        else: # 此时 上下两端都有呼叫，需要判断哪个方向更近
            up_distance = 0
            for value in up:
                if value > 0:
                    break
                else:
                    up_distance += 1
            down_distance = 0
            for value in down:
                if value > 0:
                    break
                else:
                    down_distance += 1
            return "up" if up_distance < down_distance else "down"

    async def to_action(self, elevator: Elevator, direction: str, env: BaseEnv):
        if direction == "up":
            return await self.up_action(elevator, env.tick)
        elif direction == "down":
            return await self.down_action(elevator, env.tick)
        else:
            return None

    def follow_call(self, calling, elevator: Elevator):
        """
        检查电梯的前行方向是否有等待的呼叫
        """
        if elevator.direction == "up":
            return sum(calling[elevator.on_level():]) > 0
        elif elevator.direction == "down":
            return sum(calling[:elevator.on_level()]) > 0
        else:
            return 0
                    
    def all_on_call(self, env: BaseEnv):
        """
        生成各楼层中未得到响应的列表
        """
        calling = [0] * env.level
        for level in env.passengers:
            calling[level] = len(env.passengers.get(level, {}).get("up", [])) + len(env.passengers.get(level, {}).get("down", []))
        return calling

    async def stop_and_open(self, elevator: Elevator, tick: int):
        await self.stop_action(elevator, tick)
        await self.open_action(elevator, tick)
    
    async def up_action(self, elevator: Elevator, tick: int):
        await self.push_message(UpAction(**{
            "scene_id": self.scene_id,
            "tick": tick,
            "elevator_id": elevator.id,
            "category": "up"
        }))
    
    async def down_action(self, elevator: Elevator, tick: int):
        await self.push_message(DownAction(**{
            "scene_id": self.scene_id,
            "tick": tick,
            "elevator_id": elevator.id,
            "category": "down"
        }))
        
    async def stop_action(self, elevator: Elevator, tick: int):
        await self.push_message(StopAction(**{
            "scene_id": self.scene_id,
            "tick": tick,
            "elevator_id": elevator.id,
            "category": "stop"
        }))
        
    async def open_action(self, elevator: Elevator, tick: int):
        await self.push_message(OpenAction(**{
            "scene_id": self.scene_id,
            "tick": tick,
            "elevator_id": elevator.id,
            "category": "open"
        }))
    
    async def push_message(self, message: BaseMessage):
        heapq.heappush(self.messages, 
            (
                message.tick, self.serial, 
                message.model_copy(
                    update={"id": self.serial})
            ))
        self.serial += 1
        
    async def clean_direction_action(self, elevator: Elevator, tick: int):
        await self.push_message(CleanDirectionAction(**{
            "scene_id": self.scene_id,
            "tick": tick,
            "elevator_id": elevator.id,
            "category": "clean direction"
        }))
        
    async def read(self):
        while len(self.messages) > 0:
            yield heapq.heappop(self.messages)[2]

