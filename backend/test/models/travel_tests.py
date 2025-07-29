import unittest
from app.models.env import *
from test.models.universe import TestAgent
import loguru


class TravelTests(unittest.IsolatedAsyncioTestCase):
    """# TravelTests
测试乘客从任意楼层前往任意楼层的过程
    """
    def setUp(self):
        self.env = MemEnv(scene_id=1, agent=TestAgent(scene_id=1))
        
    def closet_elevator(self, from_floor: int):
        """
        找到距离给定楼层最近的电梯，并给出两者之间的距离
        """
        elevator = self.env.elevators[0]
        distance = abs(elevator.on_level() - from_floor)
        for e in self.env.elevators:
            d = abs(e.on_level() - from_floor)
            if d < distance:
                elevator = e
                distance = d
        return elevator, distance
    
    
    async def floor_to_floor(self, from_floor: int, to_floor: int):
        """
        测试单个用户从某个楼层到另一个楼层的完整过程
        """
        env = self.env
        
        # 1. 构造一个乘客，呼叫电梯
        await env.post_message(
            CallAction(**{
                "id": 1, 
                "scene_id": 1, 
                "tick": 0, 
                "direction": "up", 
                "level": from_floor,  # 从1楼开始
                "want": to_floor,   # 前往2楼
                "category": "call"
            })
        )
        
        # 2. 一部电梯在用户所在楼层打开，然后再运行一轮确保电梯开门
        # 这里我们使用一个最简单的智能体，我们预期在单用户场景下，总是离用户最近的电梯响应呼叫
        elevator, distance = self.closet_elevator(from_floor)
        tick = env.tick + distance * 3000
        loguru.logger.info(f"tick {env.tick} elevator {elevator.id} on_level {elevator.on_level()} level {elevator.level} will from {from_floor} to {to_floor} in {distance*3000} ticks")
        while env.tick < tick:
            await env.run_tick()
        
        await env.run_tick()
        await env.run_tick()
        
        # 验证电梯在from_floor楼并开门
        self.assertEqual(elevator.on_level(), from_floor)
        while not elevator.arrive_level():
            await env.run_tick()
        loguru.logger.info(f"tick {env.tick} elevator {elevator.id} on_level {elevator.on_level()} level {elevator.level} will from {from_floor} to {to_floor} in {distance*3000} ticks")
        loguru.logger.info(f"tick {env.tick} elevator {elevator.id} running {elevator.running} closed {elevator.closed} want {elevator.want}")
        self.assertEqual(elevator.closed, False)
        self.assertEqual(elevator.want, {to_floor: 1})
        
        # 3. 乘客进入电梯 - 乘客应该已经进入电梯
        self.assertEqual(len(env.passengers[0]["up"]), 0)  # 1楼没有等待的乘客
        
        # 4. 三秒后电梯关闭并上行 - 运行3000个tick (3秒)
        stop_tick = env.tick + 3000
        while env.tick < stop_tick:
            await env.run_tick()
        
        # 验证电梯关闭并上行
        self.assertEqual(elevator.closed, True)
        self.assertEqual(elevator.direction, "up")
        self.assertEqual(elevator.running, True)
        self.assertEqual(elevator.want, {to_floor: 1})
        
        # 5. 三秒后电梯到达 to_floor 楼并停止
        stop_tick = env.tick + abs(to_floor - from_floor) * 3000
        while env.tick < stop_tick:
            await env.run_tick()
        
        await env.run_tick()
        await env.run_tick()
        
        # 验证电梯到达2楼并停止
        self.assertEqual(elevator.on_level(), to_floor)
        self.assertEqual(elevator.running, False)
        
        # 6. 电梯开门
        # 电梯应该自动开门让乘客离开
        loguru.logger.info(f"tick {env.tick} passenger from {from_floor} to {to_floor}")
        loguru.logger.info(f"tick {env.tick} elevator {elevator.id} on_level {elevator.on_level()} level {elevator.level}")
        loguru.logger.info(f"tick {env.tick} elevator {elevator.id} closed {elevator.closed} want {elevator.want}")
        self.assertEqual(elevator.closed, False)
        
        await env.run_tick()
        await env.run_tick()
        
        # 7. 乘客离开
        # 乘客应该已经离开电梯
        self.assertEqual(elevator.want, {})  # 没有乘客了

        # 8. 3秒后电梯关门 
        stop_tick = env.tick + 3000
        while env.tick < stop_tick:
            await env.run_tick()
        await env.run_tick()
        await env.run_tick()
        
        loguru.logger.info(f"tick {env.tick} elevator {elevator.id} on_level {elevator.on_level()} level {elevator.level}")
        loguru.logger.info(f"tick {env.tick} elevator {elevator.id} closed {elevator.closed} want {elevator.want}")
    
        
        # 9. 电梯应保持停止
        self.assertEqual(elevator.closed, True)
        self.assertEqual(elevator.running, False)
        self.assertEqual(elevator.direction, None)  # 没有方向
        self.assertEqual(elevator.want, {})  # 没有乘客

    
    async def test_travel_up(self):
        """
        测试乘客上楼
        """
        await self.floor_to_floor(0, 1)
        await self.floor_to_floor(1, 2)
        await self.floor_to_floor(2, 3)
        await self.floor_to_floor(3, 4)
        await self.floor_to_floor(4, 5)
        await self.floor_to_floor(5, 6)
        await self.floor_to_floor(6, 7)
        await self.floor_to_floor(7, 8)
        
        
    async def test_travel_down(self):
        """
        测试乘客下楼
        """
        await self.floor_to_floor(8, 7)
        await self.floor_to_floor(7, 6)
        await self.floor_to_floor(6, 5)
        await self.floor_to_floor(5, 4)
        await self.floor_to_floor(4, 3)
        await self.floor_to_floor(3, 2)
        await self.floor_to_floor(2, 1)
        await self.floor_to_floor(1, 0)
        
    
if __name__ == "__main__":
    # unittest.main()
    test = TravelTests()
    test.setUp()
    # asyncio.run(test.test_travel_down())
    asyncio.run(test.test_travel_up())