from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Task(BaseModel):
    id: int
    name: str
    description: str
    status: str
    
class CallTask(BaseModel):
    id: int
    task_id: int
    level: int
    want: int


@router.post("/tasks/list")
async def create_task(task: Task):
    return task

@router.post("/tasks/create")
async def create_task(task: Task):
    return task


@router.post("/tasks/call")
async def call_task(task: Task):
    return task




