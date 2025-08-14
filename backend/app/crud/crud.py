# file: app/crud/crud.py
# Contains all the reusable functions to interact with the data in the database.

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List

from app.models import Experiment
from app.schemas import ExperimentCreate, ExperimentData

async def create_experiment(db: AsyncSession, *, experiment_in: ExperimentCreate) -> Experiment:
    """
    Creates a new experiment record in the database.

    Args:
        db: The asynchronous database session.
        experiment_in: A Pydantic model containing the title and description for the new experiment.

    Returns:
        The newly created Experiment database object.
    """
    data_payload = ExperimentData(description=experiment_in.description)
    db_obj = Experiment(title=experiment_in.title, data=data_payload.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_experiment(db: AsyncSession, experiment_id: int) -> Experiment | None:
    """
    Retrieves a single experiment by its ID.

    Args:
        db: The asynchronous database session.
        experiment_id: The ID of the experiment to retrieve.

    Returns:
        The Experiment database object if found, otherwise None.
    """
    return await db.get(Experiment, experiment_id)

async def get_all_experiments(db: AsyncSession) -> List[Experiment]:
    """
    Retrieves a list of all experiments from the database.

    Args:
        db: The asynchronous database session.

    Returns:
        A list of all Experiment database objects.
    """
    result = await db.execute(select(Experiment))
    return result.scalars().all()

async def update_experiment_data(db: AsyncSession, *, db_obj: Experiment, data_in: ExperimentData) -> Experiment:
    """
    Updates the JSON data field of an existing experiment record.

    Args:
        db: The asynchronous database session.
        db_obj: The existing Experiment database object to update.
        data_in: A Pydantic model containing the full, updated simulation data.

    Returns:
        The updated Experiment database object.
    """
    db_obj.data = data_in.model_dump()
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj