import asyncpg
import asyncio

async def test_connect():
    try:
        conn = await asyncpg.connect('postgresql://postgres:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6@localhost:5432/ai_code_review')
        print("✓ Connection successful!")
        await conn.close()
    except Exception as e:
        print(f"✗ Connection failed: {e}")

asyncio.run(test_connect())
