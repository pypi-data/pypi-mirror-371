

import typer
from rich.console import Console
import questionary
import os
import json
from pathlib import Path
from .config_app import configure_app
from .files_content import *
from .utils import clear_console

console = Console(force_terminal=True)
app = typer.Typer()

@app.command()

@app.command()
def create_app(
    name: str = typer.Argument(..., help="App name"),
):
    """
    Create a minimal FastAPI app with main.py, config.db, and models.py only.
    """
    clear_console()
    from pathlib import Path
    from fastapi_start_project.files_content import contenido_main_base
    app_path = Path(name)
    app_path.mkdir(parents=True, exist_ok=True)
    # main.py con CRUD completo para User y evento de mapeo
    main_content = '''\
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from config_db import engine, Base, get_session
from models import User

app = FastAPI()

# Evento para mapear la base de datos al iniciar
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CRUD endpoints para User
@app.post("/users/", response_model=dict)
async def create_user(user: dict, session: AsyncSession = Depends(get_session)):
    db_user = User(**user)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email, "full_name": db_user.full_name}

@app.get("/users/", response_model=list)
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return [
        {"id": u.id, "username": u.username, "email": u.email, "full_name": u.full_name}
        for u in users
    ]

@app.get("/users/{user_id}", response_model=dict)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name}

@app.put("/users/{user_id}", response_model=dict)
async def update_user(user_id: int, user: dict, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.items():
        setattr(db_user, key, value)
    await session.commit()
    await session.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email, "full_name": db_user.full_name}

@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(db_user)
    await session.commit()
    return {"ok": True}
'''
    (app_path / "main.py").write_text(main_content, encoding="utf-8")
    # config_db.py (igual que antes)
    db_content = '''\
# config_db.py
# SQLAlchemy async database configuration for FastAPI (MySQL by default, using aiomysql)

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  # Core async engine/session
from sqlalchemy.orm import DeclarativeBase  # Declarative base for models

# Database URL (MySQL, change user/password/db as needed)
DATABASE_URL = "mysql+aiomysql://user:password@localhost/dbname"

# Create the async engine (echo=True shows SQL queries in console)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,    # Show SQL queries in console
)

# Create an async session factory
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

# Declarative base class for models
class Base(DeclarativeBase):
    pass

# Dependency to get a DB session in FastAPI endpoints
async def get_session():
    async with async_session() as session:
        yield session
'''
    (app_path / "config_db.py").write_text(db_content, encoding="utf-8")
    # models.py con modelo User de ejemplo
    user_model = '''\
from sqlalchemy import Column, Integer, String
from config_db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(128), nullable=False)
'''
    (app_path / "models.py").write_text(user_model, encoding="utf-8")
    # requirements.txt
    requirements = """fastapi\nuvicorn[standard]\nsqlalchemy\nmysql-connector-python\naiomysql\n"""
    (app_path / "requirements.txt").write_text(requirements, encoding="utf-8")
    # README.md
    readme = f'''# {name}\n\nMinimal FastAPI app with MySQL async support (using aiomysql).\n\n## Installation\n\n```bash\npython -m venv venv\nvenv\\Scripts\\activate  # En Windows\npip install -r requirements.txt\n```\n\n## Configuration\n\nEdit `config_db.py` and set your MySQL credentials in `DATABASE_URL`.\n\n## Run\n\n```bash\nuvicorn main:app --reload\n```\n'''
    (app_path / "README.md").write_text(readme, encoding="utf-8")
    console.print(f"[bold green]Minimal FastAPI app '{name}' created with main.py, config_db.py, models.py, requirements.txt, and README.md![/]")

@app.command()
def create_project():
    """
    Create a FastAPI project with advanced options.
    """
    clear_console()
    name = questionary.text("Project name:").ask()
    templates = questionary.confirm("Include Jinja2 templates?").ask()
    db = questionary.select(
        "Database:",
        choices=["None", "MySQL", "PostgreSQL", "SQLite"]
    ).ask()
    docker = questionary.confirm("Include Docker support?").ask()
    envs = questionary.text("Environments (comma separated, optional):").ask()
    config = {
        "templates": templates,
        "base_de_datos": db.lower() if db != "None" else "",
        "docker": docker,
        "entornos": envs,
        "extra_env_vars": None
    }
    configure_app(name, config)
    console.print(f"[bold green]Project {name} created successfully![/]")

@app.command()
def add_entity(
    app_path: str = typer.Argument(..., help="App folder name"),
    entity: str = typer.Argument(..., help="Entity name (singular, e.g. User)"),
):
    """
    Add an entity (model and schema) to the app.
    """
    models_path = Path(app_path) / "models.py"
    schemas_path = Path(app_path) / "schemas.py"
    model_code = f"""
class {entity}(Base):
    __tablename__ = '{entity.lower()}'
    id = Column(Integer, primary_key=True, index=True)
    # Add your fields here
"""
    schema_code = f"""
class {entity}Schema(BaseModel):
    id: int
    # Add your fields here
"""
    with open(models_path, "a", encoding="utf-8") as f:
        f.write(model_code)
    with open(schemas_path, "a", encoding="utf-8") as f:
        f.write(schema_code)
    console.print(f"[bold green]Entity {entity} added to {app_path}![/]")

if __name__ == "__main__":
    app()
