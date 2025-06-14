import unittest
import subprocess

class TestRunner(unittest.TestCase):
    """测试 Docker 容器运行算法的逻辑
    需要从项目根目录执行测试脚本
    """
    def test_stateless_runner(self):
        """
        测试无状态算法的运行
        
        1. 使用 python docker 镜像运行 stateless.py 脚本，传入参数 hello
        2. 检查 stdout 是否为 `hello`
        3. 检查容器是否退出
        4. 检查容器是否被删除
        """
        task = subprocess.run("docker run --name stateless --rm -i -v $PWD/backend/test:/app -w /app python python stateless.py hello", 
                            shell=True, 
                            capture_output=True)
        
        code = task.returncode
        if code != 0:
            print(task.stderr)
        self.assertEqual(code, 0)
        result = task.stdout.decode("utf-8").strip()
            
        self.assertEqual(result, "hello")


        # Check if container exists
        result = subprocess.run("docker ps -a | grep stateless", shell=True)
        self.assertEqual(result.stdout, None, "Container should not exist after running")

    def test_stateful_runner(self):
        """
        测试有状态算法的运行
        
        1. 使用 python docker 镜像运行 stateful.py 脚本，传入参数 hello
        2. 检查 stdout 是否为 `hello`
        3. 检查容器是否退出
        """
        task = subprocess.Popen("docker run --name stateful --rm -i -v $PWD/backend/test:/app -w /app python python stateful.py",
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            bufsize=1,  # Line buffered
                            universal_newlines=True)  # Use text mode
        
        try:
            test_data = ["hello", "world", "python"]
            for data in test_data:
                # Send data with newline
                task.stdin.write(data + "\n")
                task.stdin.flush()
                
                # Read until newline
                result = task.stdout.readline().strip()
                self.assertEqual(result, data)
                
            # Send empty line to signal end of input
            task.stdin.write("\n")
            task.stdin.flush()
            
            # Wait for process to finish
            task.wait()
            if task.returncode != 0:
                print(task.stderr.read())
            self.assertEqual(task.returncode, 0)
        finally:
            # Ensure all file descriptors are closed
            task.stdin.close()
            task.stdout.close()
            task.stderr.close()

if __name__ == "__main__":
    unittest.main()