import asyncio
import asyncpg

async def test_postgres():
    try:
        conn = await asyncpg.connect(
            host='localhost', 
            port=5432, 
            user='postgres'
        )
        print('AsyncPG connection successful')
        await conn.close()
    except Exception as e:
        print(f'AsyncPG connection failed: {e}')

if __name__ == "__main__":
    asyncio.run(test_postgres())