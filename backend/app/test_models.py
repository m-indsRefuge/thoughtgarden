# test_models.py
import asyncio
from app.core.database import create_db_and_tables
from app.models import Scenario

async def test():
    await create_db_and_tables()
    scenario = Scenario(title="Test", description="Test")
    print("Model created successfully!")

asyncio.run(test())