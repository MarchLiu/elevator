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
        calling = self.all_on_call(env)
        for elevator in envMap.elevators:
            on_level = envMap.passengers.get(elevator.on_level(), {})
            if elevator.arrive_level():
                if self.match_direction(elevator, "up") and len(on_level.get("up", [])) > 0 and not elevator.is_full():
                    if len(on_level.get("up", []))> 0:
                        await self.stop_and_open(elevator, env)
                        await self.up_action(elevator, env.tick)
                        moved = self.moved(elevator, len(on_level.get("up", [])))
                        rest = len(on_level.get("up", []))-moved
                        on_level["up"] = on_level.get("up", [])[:rest]
                elif self.match_direction(elevator, "down") and len(on_level.get("down", [])) > 0 and not elevator.is_full():
                    if len(on_level.get("down", []))> 0:
                        await self.stop_and_open(elevator, env)
                        await self.down_action(elevator, env.tick)
                        moved = self.moved(elevator, len(on_level.get("down", [])))
                        rest = len(on_level.get("down", []))-moved
                        on_level["down"] = on_level.get("down", [])[:rest]
                
                current = elevator.want.get(elevator.on_level(), 0)
                if current > 0:
                    # 在电梯打开后，环境程序会驱动乘客离开电梯
                    await self.stop_and_open(elevator, env)
                
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

    async def stop_and_open(self, elevator: Elevator, env: BaseEnv):
        await self.stop_action(elevator, env.tick)
        await self.open_action(elevator, env.tick)
    
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


class MemEnvTest(unittest.TestCase):
    """
测试纯内存环境的运行逻辑，验证程序逻辑的正确性
    """
    async def test_call0(self):
        """
这个测试在启动后，会立即有一个乘客呼叫电梯。
我们期待在消息发出后，执行两轮tick，电梯会打开，然后乘客进入电梯，并设定目的地。
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
        self.assertEqual(len(env.passengers[0]["up"]), 1)
        self.assertEqual(env.passengers[0]["up"][0].level, 0)
        self.assertEqual(env.passengers[0]["up"][0].want, 1)
        self.assertTrue(env.elevators[0].arrive_level())
        self.assertEqual(env.elevators[0].on_level(), 0)
        await env.run_tick()
        self.assertEqual(env.elevators[0].direction, "up")
        self.assertEqual(env.elevators[0].closed, False)
        self.assertEqual(env.elevators[0].want, {1: 1})
        self.assertEqual(env.elevators[0].running, False)
        self.assertIn(0, env.passengers)
        self.assertIn("up", env.passengers[0])
        
        self.assertEqual(len(env.passengers[0]["up"]), 0)

        for elevator in env.elevators[1:]:
            self.assertEqual(elevator.on_level(), 0)
            self.assertEqual(elevator.closed, True)
            self.assertEqual(elevator.want, {})
            self.assertEqual(elevator.running, False)
            

    async def test_call1(self):
        """
这个测试在启动后，会立即有一个乘客呼叫电梯。
我们期待在消息发出后的三秒后检查到：
- 电梯在0层向上的行进过程中，电梯门是关闭的
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
        while env.tick < 4000:
            await env.run_tick()
        self.assertTrue(env.elevators[0].level > 0)
        self.assertEqual(env.elevators[0].direction, "up")
        self.assertEqual(env.elevators[0].closed, True)
        self.assertEqual(env.elevators[0].want, {1: 1})
        self.assertEqual(env.elevators[0].running, True)
        
    async def test_level(self):
        """
根据 issue #4 的要求，测试单人乘坐电梯的完整流程：
1. 构造一个要从1楼前往2楼的乘客
2. 一部电梯在1楼打开
3. 乘客进入电梯
4. 三秒后电梯关闭并上行
5. 三秒后电梯到达2楼并停止
6. 电梯开门
7. 乘客离开
8. 3秒后电梯关门
9. 电梯应保持停止
        """
        env = MemEnv(scene_id=1, agent=TestAgent(scene_id=1))
        
        # 1. 构造一个要从1楼前往2楼的乘客
        await env.post_message(
            CallAction(**{
                "id": 1, 
                "scene_id": 1, 
                "tick": 0, 
                "direction": "up", 
                "level": 0,  # 从1楼开始
                "want": 1,   # 前往2楼
                "category": "call"
            })
        )
        
        # 2. 一部电梯在1楼打开 - 运行两轮tick让电梯到达1楼并开门
        await env.run_tick()
        await env.run_tick()
        
        # 验证电梯在1楼并开门
        self.assertEqual(env.elevators[0].level, 0)
        self.assertEqual(env.elevators[0].closed, False)
        self.assertEqual(env.elevators[0].want, {1: 1})
        
        # 3. 乘客进入电梯 - 乘客应该已经进入电梯
        self.assertEqual(len(env.passengers[0]["up"]), 0)  # 1楼没有等待的乘客
        
        # 4. 三秒后电梯关闭并上行 - 运行3000个tick (3秒)
        initial_tick = env.tick
        while env.tick < initial_tick + 3000:
            await env.run_tick()
        
        # 验证电梯关闭并上行
        self.assertEqual(env.elevators[0].closed, True)
        self.assertEqual(env.elevators[0].direction, "up")
        self.assertEqual(env.elevators[0].running, True)
        
        # 5. 三秒后电梯到达2楼并停止
        while env.tick < initial_tick + 5000:
            await env.run_tick()
        
        # 验证电梯到达2楼并停止
        self.assertEqual(env.elevators[0].on_level(), 1)
        self.assertEqual(env.elevators[0].running, False)
        
        # 6. 电梯开门
        # 电梯应该自动开门让乘客离开
        self.assertEqual(env.elevators[0].closed, False)
                        
        await env.run_tick()
        await env.run_tick()
        
        # 7. 乘客离开
        # 乘客应该已经离开电梯
        self.assertEqual(env.elevators[0].want, {})  # 没有乘客了
        
        # 8. 3秒后电梯关门 - 再运行3000个tick
        while env.tick < initial_tick + 9000:
            await env.run_tick()
        
        # 9. 电梯应保持停止
        self.assertEqual(env.elevators[0].closed, True)
        self.assertEqual(env.elevators[0].running, False)
        self.assertEqual(env.elevators[0].direction, None)  # 没有方向
        self.assertEqual(env.elevators[0].want, {})  # 没有乘客
        

if __name__ == "__main__":
    asyncio.run(MemEnvTest().test_call0())
    asyncio.run(MemEnvTest().test_call1())
    asyncio.run(MemEnvTest().test_level())
    