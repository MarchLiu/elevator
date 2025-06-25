import unittest
import asyncio
from app.models.env import *
from app.models.messages import *

class TestAgent(BaseAgent):
    def __init__(self):
        self.messages = []
        
    def match_direction(self, elevator: Elevator, direction: str):
        if elevator.direction is None:
            return True
        return elevator.direction == direction
    
    async def post_env(self, env: BaseEnv):
        envMap = env.dump()
        print(envMap.model_dump_json())
        for elevator in envMap.elevators:
            if elevator.level == floor(elevator.level):
                if self.match_direction(elevator, "up"):
                    if envMap.passengers.get(elevator.level, {}).get("up", []):
                        heapq.heappush(self.messages, (env.tick, StopAction(**{
                            "id": 1,
                            "scene_id": 1,
                            "tick": env.tick,
                            "category": "stop",
                            "elevator_id": elevator.id
                        })))
                        heapq.heappush(self.messages, (env.tick, OpenAction(**{
                            "id": 1,
                            "scene_id": 1,
                            "tick": env.tick,
                            "category": "open",
                            "elevator_id": elevator.id
                        })))
    
    async def read(self):
        while len(self.messages) > 0:
            yield heapq.heappop(self.messages)[1]


class MemEnvTest(unittest.TestCase):
    """
测试纯内存环境的运行逻辑，验证程序逻辑的正确性
    """
    async def test_env(self):
        # Create a simple agent for testing
        
        env = MemEnv(scene_id=1, agent=TestAgent())
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
        # Check that the passenger was added to the correct level and direction
        self.assertIn(0, env.passengers)
        self.assertIn("up", env.passengers[0])
        self.assertEqual(len(env.passengers[0]["up"]), 1)
        self.assertEqual(env.passengers[0]["up"][0].level, 0)
        self.assertEqual(env.passengers[0]["up"][0].want, 1)
        

if __name__ == "__main__":
    asyncio.run(MemEnvTest().test_env())
    