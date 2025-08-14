# file: debug_mappers.py
import os
import sys
import logging
from pathlib import Path

# Fix module imports by adding project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Now import SQLAlchemy components
from sqlalchemy import inspect, create_engine
from sqlmodel import SQLModel

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def debug_models():
    # Temporary SQLite in-memory engine for debugging
    engine = create_engine("sqlite:///:memory:")
    
    # Import models AFTER engine creation
    from app.models.scenario import Scenario
    from app.models.perspective import Perspective
    from app.models.debateturn import DebateTurn
    from app.models.synthesis import Synthesis
    
    # Create tables
    SQLModel.metadata.create_all(engine)
    
    print("\n=== Model Debug ===")
    for model in [Scenario, Perspective, DebateTurn, Synthesis]:
        mapper = inspect(model)
        print(f"\nModel: {model.__name__}")
        print(f"Table: {mapper.tables[0].name}")
        
        for rel in mapper.relationships:
            print(f"\nRelationship: {rel.key}")
            print(f"  - Argument: {getattr(rel, 'argument', None)}")
            print(f"  - Backref: {rel.back_populates}")
            print(f"  - Mapper: {rel.mapper.class_.__name__ if rel.mapper else None}")
            print(f"  - Type: {model.__annotations__.get(rel.key, 'UNKNOWN')}")

if __name__ == "__main__":
    debug_models()