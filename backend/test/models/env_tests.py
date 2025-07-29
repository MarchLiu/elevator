import unittest
from app.models.env import *
from app.models.messages import *
from test.models.universe import TestAgent

class MemEnvTest(unittest.IsolatedAsyncioTestCase):
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
    unittest.main()