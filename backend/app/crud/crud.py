# file: app/crud/crud.py (Corrected)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List, Optional
from app.schemas.schemas import ExperimentCreate, ExperimentData, ReasoningGraph
from app.models import Experiment
import uuid
from datetime import datetime

# Recursive helper to convert datetime objects to ISO strings
def datetime_to_str(obj):
    """
    Recursively converts datetime objects in a dict/list to ISO strings.
    """
    if isinstance(obj, dict):
        return {k: datetime_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [datetime_to_str(v) for v in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

async def create_experiment(
    db: AsyncSession,
    *,
    experiment_in: ExperimentCreate,
) -> Experiment:
    """
    Creates a new experiment record in the database with an empty ReasoningGraph.
    """
    # Create an empty graph for a new experiment
    initial_graph = ReasoningGraph(
        nodes=[],  # Start with an empty list of nodes
        edges=[]
    )

    initial_data = ExperimentData(
        description=experiment_in.description,
        graph=initial_graph
    )

    # Convert the entire data dict recursively before inserting
    db_obj = Experiment(
        title=experiment_in.title,
        data=datetime_to_str(initial_data.model_dump(by_alias=True, exclude_none=True))
    )

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_experiment(db: AsyncSession, experiment_id: int) -> Optional[Experiment]:
    """Retrieve a single experiment by its ID."""
    return await db.get(Experiment, experiment_id)


async def get_all_experiments(db: AsyncSession) -> List[Experiment]:
    """Retrieve all experiments from the database."""
    result = await db.execute(select(Experiment))
    return result.scalars().all()


async def update_experiment_data(
    db: AsyncSession, *, db_obj: Experiment, data_in: ExperimentData
) -> Experiment:
    """Update the JSON data field of an existing experiment record."""
    db_obj.data = datetime_to_str(data_in.model_dump(by_alias=True, exclude_none=True))
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj