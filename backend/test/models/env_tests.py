import unittest
import asyncio
import heapq
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
        on_call = {"up": True, "down": True}
        for elevator in envMap.elevators:
            if elevator.level == floor(elevator.level):
                if self.match_direction(elevator, "up"):
                    up = len(envMap.passengers.get(elevator.level, {}).get("up", []))> 0
                    if up and not elevator.is_full() and on_call["up"]:
                        await self.stop_action(elevator, env.tick)
                        await self.open_action(elevator, env.tick)
                        on_call["up"] = False
                elif self.match_direction(elevator, "down"):
                    down = len(envMap.passengers.get(elevator.level, {}).get("down", []))> 0
                    if down and not elevator.is_full() and on_call["down"]:
                        await self.stop_action(elevator, env.tick)
                        await self.open_action(elevator, env.tick)
                        on_call["down"] = False
    
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
    
    async def read(self):
        while len(self.messages) > 0:
            yield heapq.heappop(self.messages)[2]


class MemEnvTest(unittest.TestCase):
    """
测试纯内存环境的运行逻辑，验证程序逻辑的正确性
    """
    async def test_call0(self):
        """
这个测试在启动后，会立即有一个乘客呼叫电梯。
我们期待在消息发出后，执行两轮
        """
        env = MemEnv(scene_id=1, agent=TestAgent(scene_id=1))
        await env.post_message(
            CallAction(**{
                "id": 1, 
                "scene_id": 1, 
                "tick": 0, 
                "direction": "up", 
                "level": 0, 
                "want": 1,
                "category": "call"
            })
        )
        await env.run_tick()
        await env.run_tick()
        # Check that the passenger was added to the correct level and direction
        self.assertIn(0, env.passengers)
        self.assertIn("up", env.passengers[0])
        self.assertFalse(env.elevators[0].closed)
        self.assertEqual(len(env.passengers[0]["up"]), 1)
        self.assertEqual(env.passengers[0]["up"][0].level, 0)
        self.assertEqual(env.passengers[0]["up"][0].want, 1)
        for elevator in env.elevators[1:]:
            self.assertEqual(elevator.level, 0)
            self.assertEqual(elevator.closed, True)
            self.assertEqual(elevator.want, {})
            self.assertEqual(elevator.running, False)
            
        self.assertEqual(env.elevators[0].running, False)
        self.assertEqual(env.elevators[0].closed, False)
        
    async def test_call1(self):
        """
这个测试在启动后，会立即有一个乘客呼叫电梯。
我们期待在消息发出后的三秒后检查到：
- 电梯在0层，方向向上，电梯门是关闭的
- 电梯里有一个乘客，乘客在0层，想要去1层
        """
        env = MemEnv(scene_id=1, agent=TestAgent(scene_id=1))
        await env.post_message(
            CallAction(**{
                "id": 1, 
                "scene_id": 1, 
                "tick": 0, 
                "direction": "up", 
                "level": 0,
                "want": 1,
                "category": "call"
            })
        )
        while env.tick < 3000:
            await env.run_tick()
        self.assertEqual(env.elevators[0].level, 0)
        self.assertEqual(env.elevators[0].direction, "up")
        self.assertEqual(env.elevators[0].closed, True)
        self.assertEqual(env.elevators[0].want, {1: 1})
        self.assertEqual(env.elevators[0].running, True)
        

if __name__ == "__main__":
    asyncio.run(MemEnvTest().test_call0())
    # asyncio.run(MemEnvTest().test_call1())
    