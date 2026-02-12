#!/usr/bin/env python3
"""
简化版数据库连接测试脚本
测试Docker容器内部网络连接
"""

import subprocess
import json
import os
import time

class DockerConnectionTester:
    def __init__(self):
        self.results = []
    
    def run_command(self, command):
        """运行命令并返回结果"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def test_container_health(self):
        """测试容器健康状态"""
        containers = [
            ("PostgreSQL", "ai_review_postgres"),
            ("Neo4j", "ai_review_neo4j"),
            ("Redis", "ai_review_redis"),
            ("Backend", "ai_review_backend"),
            ("pgAdmin", "ai_review_pgadmin"),
        ]
        
        for name, container in containers:
            success, output, error = self.run_command(f"docker inspect {container} --format='{{{{.State.Status}}}}'")
            if success and output == "running":
                # 检查健康状态
                health_cmd = f"docker inspect {container} --format='{{{{.State.Health.Status}}}}'"
                health_success, health_output, _ = self.run_command(health_cmd)
                
                status = "running"
                if health_success and health_output:
                    status = f"running ({health_output})"
                
                self.results.append(f"✅ {name} ({container}): {status}")
            else:
                self.results.append(f"❌ {name} ({container}): not running")
    
    def test_docker_network(self):
        """测试Docker网络连接"""
        print("\n🔍 测试Docker内部DNS解析:")
        services = ["postgres", "redis", "neo4j", "backend"]
        
        for service in services:
            # 测试DNS解析
            cmd = f"docker exec ai_review_backend nslookup {service}"
            success, output, error = self.run_command(cmd)
            
            if success:
                self.results.append(f"✅ DNS解析 {service}: 成功")
            else:
                self.results.append(f"❌ DNS解析 {service}: 失败 - {error}")
    
    def test_postgresql_ping(self):
        """测试PostgreSQL连接"""
        print("\n🐘 测试PostgreSQL连接:")
        cmd = "docker exec ai_review_postgres pg_isready -U postgres"
        success, output, error = self.run_command(cmd)
        
        if success and "accepting connections" in output:
            self.results.append("✅ PostgreSQL连接: 正常")
        else:
            self.results.append(f"❌ PostgreSQL连接: 失败 - {error}")
    
    def test_redis_ping(self):
        """测试Redis连接"""
        print("\n🔴 测试Redis连接:")
        password = os.getenv("REDIS_PASSWORD", "")
        auth_part = f"-a {password}" if password else ""
        cmd = f"docker exec ai_review_redis redis-cli {auth_part} ping"
        success, output, error = self.run_command(cmd)
        
        if success and "PONG" in output:
            self.results.append("✅ Redis连接: 正常")
        else:
            self.results.append(f"❌ Redis连接: 失败 - {error}")
    
    def test_neo4j_connection(self):
        """测试Neo4j连接"""
        print("\n🔗 测试Neo4j连接:")
        password = os.getenv("NEO4J_PASSWORD", "")
        cmd = f'docker exec ai_review_neo4j cypher-shell -u neo4j -p "{password}" "RETURN 1;"'
        success, output, error = self.run_command(cmd)
        
        if success and "1" in output:
            self.results.append("✅ Neo4j连接: 正常")
        else:
            self.results.append(f"❌ Neo4j连接: 失败 - {error}")
    
    def test_backend_health(self):
        """测试后端健康检查"""
        print("\n🌐 测试后端健康检查:")
        cmd = "curl -f http://localhost:8000/health"
        success, output, error = self.run_command(cmd)
        
        if success:
            try:
                data = json.loads(output)
                status = data.get("status", "unknown")
                self.results.append(f"✅ 后端健康检查: {status}")
            except:
                self.results.append("✅ 后端健康检查: 响应正常")
        else:
            self.results.append(f"❌ 后端健康检查: 失败 - {error}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=== Docker网络连接测试 ===\n")
        
        # 检查环境文件
        if os.path.exists(".env"):
            print("✅ 发现.env文件")
        else:
            print("⚠️  未发现.env文件，请创建.env文件")
        
        self.test_container_health()
        self.test_docker_network()
        self.test_postgresql_ping()
        self.test_redis_ping()
        self.test_neo4j_connection()
        self.test_backend_health()
        
        # 显示结果
        print("\n=== 测试结果汇总 ===")
        for result in self.results:
            print(result)
        
        passed = sum(1 for r in self.results if r.startswith("✅"))
        total = len(self.results)
        
        print(f"\n=== 总结 ===")
        print(f"通过: {passed}/{total}")
        print(f"成功率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("🎉 所有测试通过！Docker环境配置正确。")
        else:
            print("⚠️  部分测试失败，请检查Docker配置。")
    
    def generate_setup_commands(self):
        """生成设置命令"""
        print("\n🔧 设置命令:")
        print("1. 复制环境模板: cp .env.template .env")
        print("2. 编辑环境变量: nano .env")
        print("3. 启动Docker服务: docker-compose up -d")
        print("4. 等待服务启动: sleep 30")
        print("5. 运行健康检查: ./setup-check.sh")
        print("6. 运行连接测试: python scripts/test_db_connections.py")

def main():
    tester = DockerConnectionTester()
    tester.run_all_tests()
    tester.generate_setup_commands()

if __name__ == "__main__":
    main()