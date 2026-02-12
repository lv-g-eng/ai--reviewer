#!/usr/bin/env python3
"""
数据库连接测试脚本
测试Docker容器内部网络通信
"""

import asyncio
import asyncpg
from neo4j import GraphDatabase
import redis
import httpx
import psycopg2
import os
from typing import Dict, Any, Optional


class ConnectionTester:
    """Docker网络连接测试器"""
    
    def __init__(self):
        self.results = []
        
    def log_result(self, service: str, status: bool, message: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """记录测试结果"""
        result = {
            "service": service,
            "status": "✅ PASS" if status else "❌ FAIL",
            "message": message,
            "details": details or {}
        }
        self.results.append(result)
        return status
    
    async def test_postgresql(self) -> bool:
        """测试PostgreSQL连接"""
        try:
            # 使用Docker服务名连接
            conn = await asyncpg.connect(
                host="postgres",
                port=5432,
                database=os.getenv("POSTGRES_DB", "ai_code_review"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "")
            )
            
            # 测试查询
            version = await conn.fetchval("SELECT version();")
            await conn.close()
            
            return self.log_result(
                "PostgreSQL", 
                True, 
                "连接成功", 
                {"version": version.split()[1] if version else "unknown"}
            )
            
        except Exception as e:
            return self.log_result(
                "PostgreSQL", 
                False, 
                f"连接失败: {str(e)}",
                {"error": str(e)}
            )
    
    async def test_neo4j(self) -> bool:
        """测试Neo4j连接"""
        try:
            # 使用Docker服务名连接
            uri = "bolt://neo4j:7687"
            username = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "")
            
            driver = GraphDatabase.driver(uri, auth=(username, password))
            
            # 测试查询
            with driver.session() as session:
                result = session.run("RETURN 1 AS test_value")
                record = result.single()
                test_value = record[0] if record else None
                
            driver.close()
            
            return self.log_result(
                "Neo4j", 
                True, 
                "连接成功", 
                {"test_value": test_value}
            )
            
        except Exception as e:
            return self.log_result(
                "Neo4j", 
                False, 
                f"连接失败: {str(e)}",
                {"error": str(e)}
            )
    
    def test_redis(self) -> bool:
        """测试Redis连接"""
        try:
            # 使用Docker服务名连接
            host = "redis"
            port = 6379
            password = os.getenv("REDIS_PASSWORD")
            
            if password:
                r = redis.Redis(host=host, port=port, password=password, decode_responses=True)
            else:
                r = redis.Redis(host=host, port=port, decode_responses=True)
            
            # 测试ping
            if r.ping():
                # 测试读写
                test_key = "connection_test"
                test_value = "test_data"
                r.set(test_key, test_value)
                retrieved_value = r.get(test_key)
                r.delete(test_key)
                
                return self.log_result(
                    "Redis", 
                    True, 
                    "连接成功", 
                    {"can_write": retrieved_value == test_value}
                )
            else:
                return self.log_result("Redis", False, "Ping失败")
                
        except Exception as e:
            return self.log_result(
                "Redis", 
                False, 
                f"连接失败: {str(e)}",
                {"error": str(e)}
            )
    
    async def test_backend_api(self) -> bool:
        """测试后端API连接"""
        try:
            async with httpx.AsyncClient() as client:
                # 使用Docker服务名连接
                response = await client.get("http://backend:8000/health")
                
                if response.status_code == 200:
                    data = response.json()
                    return self.log_result(
                        "Backend API", 
                        True, 
                        "健康检查通过", 
                        {"status": data.get("status"), "response_time": response.elapsed.total_seconds()}
                    )
                else:
                    return self.log_result(
                        "Backend API", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                
        except Exception as e:
            return self.log_result(
                "Backend API", 
                False, 
                f"连接失败: {str(e)}",
                {"error": str(e)}
            )
    
    async def test_docker_network(self) -> bool:
        """测试Docker内部DNS解析"""
        services = ["postgres", "redis", "neo4j", "backend"]
        all_passed = True
        
        for service in services:
            try:
                # 测试DNS解析
                import socket
                socket.gethostbyname(service)
                self.log_result(f"DNS - {service}", True, "DNS解析成功")
            except Exception as e:
                all_passed = False
                self.log_result(f"DNS - {service}", False, f"DNS解析失败: {str(e)}")
        
        return all_passed
    
    def test_local_database_migration(self) -> bool:
        """测试本地数据库迁移连接"""
        try:
            # 测试本地PostgreSQL（用于迁移）
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="ai_code_review",
                user="postgres",
                password=input("请输入本地PostgreSQL密码: ")
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version_result = cursor.fetchone()
            version = version_result[0] if version_result else None
            
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            return self.log_result(
                "Local PostgreSQL (for migration)", 
                True, 
                "本地数据库可访问", 
                {
                    "version": version.split()[1] if version else "unknown",
                    "table_count": len(tables),
                    "tables": tables[:5]  # 只显示前5个表
                }
            )
            
        except Exception as e:
            return self.log_result(
                "Local PostgreSQL (for migration)", 
                False, 
                f"本地数据库连接失败: {str(e)}",
                {"error": str(e)}
            )
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("=== Docker网络连接测试 ===\n")
        
        # Docker内部网络测试
        print("🐳 Docker内部网络测试:")
        await self.test_docker_network()
        
        # 数据库连接测试
        print("\n🗄️  数据库连接测试:")
        await self.test_postgresql()
        await self.test_neo4j()
        self.test_redis()
        
        # API测试
        print("\n🌐 API服务测试:")
        await self.test_backend_api()
        
        # 本地数据库测试（用于迁移）
        print("\n🔁 本地数据库迁移测试:")
        self.test_local_database_migration()
        
        # 显示结果汇总
        self.print_results()
        
        # 计算通过率
        passed = sum(1 for r in self.results if "✅" in r["status"])
        total = len(self.results)
        
        return passed == total
    
    def print_results(self):
        """打印测试结果"""
        print("\n=== 测试结果汇总 ===")
        
        for result in self.results:
            print(f"{result['status']} {result['service']}")
            print(f"   {result['message']}")
            
            if result['details']:
                for key, value in result['details'].items():
                    print(f"   {key}: {value}")
            print()
        
        passed = sum(1 for r in self.results if "✅" in r["status"])
        total = len(self.results)
        
        print(f"=== 总结 ===")
        print(f"通过: {passed}/{total}")
        print(f"成功率: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("✅ 所有测试通过！Docker网络配置正确。")
        else:
            print("⚠️  部分测试失败，请检查Docker网络和服务配置。")


async def main():
    """主函数"""
    tester = ConnectionTester()
    success = await tester.run_all_tests()
    
    print("\n🔧 建议操作:")
    if not success:
        print("1. 检查Docker容器是否正常运行: docker-compose ps")
        print("2. 查看失败的容器日志: docker logs <container_name>")
        print("3. 检查网络配置: docker network inspect ai_review_network")
        print("4. 重启服务: docker-compose restart")
    else:
        print("✅ Docker网络配置正常，可以进行数据迁移和部署。")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_status = asyncio.run(main())
    exit(exit_status)