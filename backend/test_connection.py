import logging
logger = logging.getLogger(__name__)

import asyncpg
import asyncio

async def test_connect():
    try:
        conn = await asyncpg.connect('postgresql://postgres:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6@localhost:5432/ai_code_review')
        logger.info("✓ Connection successful!")
        await conn.close()
    except Exception as e:
        logger.info("✗ Connection failed: {e}")

asyncio.run(test_connect())
