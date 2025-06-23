from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class BaseMessage(BaseModel):
    id: int
    scene_id: int
    tick: int

class CallAction(BaseMessage):
    direction: Literal["up", "down"]
    level: int
    tick: int

class WantAction(BaseMessage):
    elevator_id: int
    want: int
    tick: int

class InToAction(BaseMessage):
    elevator_id: int
    level: int
    tick: int

class OutToAction(BaseMessage):
    elevator_id: int
    level: int
    tick: int


class GraceStop(BaseMessage):
    timeout_ticks: int
    