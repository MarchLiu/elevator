from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from datetime import datetime

class BaseMessage(BaseModel):
    id: int
    scene_id: int
    tick: int
    category: Literal["call", "want", "into", "out", "grace exit", "passenger", "up", "down", "stop"]

class PassengerAction(BaseModel):
    id: int
    scene_id: int
    tick: int
    category: Literal["call", "want", "into", "out", "grace exit", "passenger", "up", "down", "stop"]

class UpAction(BaseMessage):
    elevator_id: int
    category: Literal["up"]

class DownAction(BaseMessage):
    elevator_id: int
    category: Literal["down"]
    
class StopAction(BaseMessage):
    elevator_id: int
    category: Literal["stop"]

class CallAction(BaseMessage):
    direction: Literal["up", "down"]
    level: int
    want: int
    category: Literal["call"]

class WantAction(BaseMessage):
    elevator_id: int
    want: int
    category: Literal["want"]
    
class CloseAction(BaseMessage):
    elevator_id: int
    category: Literal["close"]

class OpenAction(BaseMessage):
    elevator_id: int
    category: Literal["open"]

class GraceExit(BaseMessage):
    timeout_ticks: int
    category: Literal["grace exit"]
    
class DBMeta(BaseModel):
    category: Literal["call", "want", "into", "out", "grace exit", "passenger", "up", "down", "stop"]
    
class DBMessage(BaseMessage):
    meta: DBMeta
    content: dict[str, Any]

    def to_message(self) -> BaseMessage:
        if self.meta.category == "call":
            return CallAction(
                id=self.id,
                scene_id=self.scene_id,
                tick=self.tick,
                direction=self.content["direction"],
                level=self.content["level"],
                want=self.content["want"],
                category=self.meta.category
            )
        elif self.meta.category == "want":
            return WantAction(
                id=self.id,
                scene_id=self.scene_id,
                tick=self.tick,
                elevator_id=self.content["elevator_id"],
                want=self.content["want"],
                category=self.meta.category
            )
        elif self.meta.category == "grace exit":
            return GraceExit(
                id=self.id,
                scene_id=self.scene_id,
                timeout_ticks=self.content["timeout_ticks"],
                tick=self.tick,
                category=self.meta.category
            )
        elif self.meta.category == "passenger":
            return PassengerAction(
                id=self.id,
                scene_id=self.scene_id,
                tick=self.tick,
                category=self.content["category"],
                level=self.content["level"],
                want=self.content["want"]
            )
        elif self.meta.category == "up":
            return UpAction(
                id=self.id,
                scene_id=self.scene_id,
                tick=self.tick,
                category=self.content["category"],
                elevator_id=self.content["elevator_id"]
            )
        elif self.meta.category == "down":
            return DownAction(
                id=self.id,
                scene_id=self.scene_id,
                tick=self.tick,
                category=self.content["category"],
                elevator_id=self.content["elevator_id"]
            )
        elif self.meta.category == "stop":
            return StopAction(
                id=self.id,
                scene_id=self.scene_id,
                tick=self.tick,
                category=self.content["category"],
                elevator_id=self.content["elevator_id"]
            )
        elif self.meta.category == "close":
            return CloseAction(
                id=self.id,
                scene_id=self.scene_id,
                tick=self.tick,
                category=self.content["category"],
                elevator_id=self.content["elevator_id"]
            )
        elif self.meta.category == "open":
            return OpenAction(
                id=self.id,
                scene_id=self.scene_id,
                tick=self.tick,
                category=self.content["category"],
                elevator_id=self.content["elevator_id"]
            )
        else:
            raise ValueError(f"Unknown message category: {self.meta.category}")

