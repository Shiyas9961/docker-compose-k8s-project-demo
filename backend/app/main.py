import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import (
    Base,
    engine,
    get_database_session,
    wait_for_database,
)
from app.models import Task
from app.schemas import (
    HealthResponse,
    MessageResponse,
    TaskCreate,
    TaskListResponse,
    TaskOperationResponse,
    TaskUpdate,
)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s"
    ),
)

logger = logging.getLogger("task-manager-api")


@asynccontextmanager
async def application_lifespan(app: FastAPI):
    logger.info(
        "Starting application instance: %s",
        settings.instance_name,
    )

    wait_for_database()

    Base.metadata.create_all(bind=engine)

    logger.info("Database tables are ready")

    yield

    logger.info(
        "Stopping application instance: %s",
        settings.instance_name,
    )

    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=application_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Task Manager API is running",
        "documentation": "/docs",
        "handled_by": settings.instance_name,
    }


@app.get(
    "/api/health",
    response_model=HealthResponse,
)
def health_check(
    database_session: Session = Depends(get_database_session),
) -> HealthResponse:
    try:
        database_session.execute(text("SELECT 1"))

        database_status = "connected"

    except SQLAlchemyError as error:
        logger.exception("Database health check failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from error

    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        environment=settings.app_environment,
        handled_by=settings.instance_name,
        database=database_status,
    )


@app.get(
    "/api/instance",
    response_model=MessageResponse,
)
def instance_information() -> MessageResponse:
    return MessageResponse(
        message="Request successfully handled",
        handled_by=settings.instance_name,
    )


@app.get(
    "/api/tasks",
    response_model=TaskListResponse,
)
def get_tasks(
    database_session: Session = Depends(get_database_session),
) -> TaskListResponse:
    query = select(Task).order_by(Task.created_at.desc())

    tasks = database_session.scalars(query).all()

    logger.info(
        "Returned %s tasks from instance %s",
        len(tasks),
        settings.instance_name,
    )

    return TaskListResponse(
        tasks=list(tasks),
        count=len(tasks),
        handled_by=settings.instance_name,
    )


@app.post(
    "/api/tasks",
    response_model=TaskOperationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    database_session: Session = Depends(get_database_session),
) -> TaskOperationResponse:
    cleaned_title = task_data.title.strip()

    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task title cannot be empty",
        )

    task = Task(
        title=cleaned_title,
        completed=False,
    )

    try:
        database_session.add(task)
        database_session.commit()
        database_session.refresh(task)

    except SQLAlchemyError as error:
        database_session.rollback()

        logger.exception("Failed to create task")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create task",
        ) from error

    logger.info(
        "Created task %s using instance %s",
        task.id,
        settings.instance_name,
    )

    return TaskOperationResponse(
        task=task,
        message="Task created successfully",
        handled_by=settings.instance_name,
    )


@app.patch(
    "/api/tasks/{task_id}",
    response_model=TaskOperationResponse,
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    database_session: Session = Depends(get_database_session),
) -> TaskOperationResponse:
    task = database_session.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    updated_fields = task_data.model_dump(exclude_unset=True)

    if "title" in updated_fields:
        cleaned_title = updated_fields["title"].strip()

        if not cleaned_title:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Task title cannot be empty",
            )

        task.title = cleaned_title

    if "completed" in updated_fields:
        task.completed = updated_fields["completed"]

    try:
        database_session.commit()
        database_session.refresh(task)

    except SQLAlchemyError as error:
        database_session.rollback()

        logger.exception("Failed to update task %s", task_id)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update task",
        ) from error

    return TaskOperationResponse(
        task=task,
        message="Task updated successfully",
        handled_by=settings.instance_name,
    )


@app.delete(
    "/api/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    database_session: Session = Depends(get_database_session),
) -> Response:
    task = database_session.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    try:
        database_session.delete(task)
        database_session.commit()

    except SQLAlchemyError as error:
        database_session.rollback()

        logger.exception("Failed to delete task %s", task_id)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete task",
        ) from error

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
