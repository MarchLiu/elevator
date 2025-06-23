from pydantic import BaseModel
from messages import *
import heapq

class Elevator(BaseModel):
    def __init__(self, id: int, scene_id: int, maximum: int=10):
        self.id = id
        self.scene_id = scene_id
        self.maximum = maximum
        self.running = False
        self.level = 0
        self.direction = None
        self.want_level = None
        self.current = {}

class BaseEnv(BaseModel):
    def __init__(self, scene_id: int, level: int=25, maximum: int=10, elevator_count: int=4):
        self.scene_id = scene_id
        self.elevators = [Elevator(i, scene_id, maximum) for i in range(elevator_count)]
        self.characters = []
        self.tick = 0
        
    def post_message(self, *messages: BaseModel):
        raise NotImplementedError
    
    def pop_message(self):
        raise NotImplementedError

    def next_tick(self, next_tick: int=1000):
        self.tick += next_tick
        while len(self.messages) > 0 and self.messages[0].tick <= self.tick:
            message = self.pop_message()
            if isinstance(message, GraceStop):
                self.elevators[message.elevator_id].running = False
            elif isinstance(message, CallAction):
                self.elevators[message.elevator_id].want_level = message.level
                
class MemEnv(BaseEnv):
    def __init__(self, scene_id: int, level: int=25, maximum: int=10, elevator_count: int=4):
        super().__init__(scene_id, level, maximum, elevator_count)
        self.messages = []
        
    def post_message(self, *messages: BaseModel):
        for message in messages:
            heapq.heappush(self.messages, (message.tick, message))
        
    def pop_message(self):
        if len(self.messages) == 0:
            return None
        return heapq.heappop(self.messages)
    
class DBEnv(BaseEnv):
    def __init__(self, db, scene_id: int, level: int=25, maximum: int=10, elevator_count: int=4):
        super().__init__(scene_id, level, maximum, elevator_count)
        self.db = db
        
    def post_message(self, *messages: BaseModel):
        for message in messages:
            db_message = models.Message(
                scene_id=self.scene_id,
                tick=message.tick,
                message_type=message.__class__.__name__,
                elevator_id=message.elevator_id if hasattr(message, 'elevator_id') else None,
                level=message.level if hasattr(message, 'level') else None
            )
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)

    def pop_message(self):
        
        message = self.db.query(BaseMessage)\
            .filter(BaseMessage.scene_id == self.scene_id)\
            .order_by(BaseMessage.tick)\
            .with_for_update(skip_locked=True)\
            .delete(synchronize_session=False)\
            .returning(BaseMessage)\
            .first()
        if message is None:
            return None
        
        if message.message_type == "GraceStop":
            return GraceStop(message.tick, message.elevator_id)
        elif message.message_type == "CallAction":
            return CallAction(message.tick, message.elevator_id, message.level)
        
        if message.message_type == "GraceStop":
            return GraceStop(message.tick, message.elevator_id)
        elif message.message_type == "CallAction":
            return CallAction(message.tick, message.elevator_id, message.level)
    
class Character(BaseModel):
    def __init__(self, id: int, scene_id: int, level: int, want: int):
        self.id = id
        self.scene_id = scene_id
        self.level = level
        self.want = want
        
