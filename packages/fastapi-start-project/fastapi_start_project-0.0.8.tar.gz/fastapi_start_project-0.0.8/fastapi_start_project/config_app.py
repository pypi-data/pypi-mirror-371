import logging
from typing import Dict, Any, Optional

# Constants for database types
DB_MYSQL = "mysql"
DB_POSTGRESQL = "postgresql"
DB_SQLITE = "sqlite"

logger = logging.getLogger("fastapi_start_project.config_app")
logging.basicConfig(level=logging.INFO)
from rich.console import Console
from pathlib import Path
import json

from fastapi_start_project.utils import create_structure
from fastapi_start_project.files_content import (
    contenido_main_base, contenido_main_jinja2,
    contenido_docker, contenido_docker_compose,
    contenido_env, contenido_readme,
    base_html, index_html, estilos_index_jinja2,
    contenido_requisitos_base, contenido_jinja2,
    contenido_mysql, contenido_postgresql,
    contenido_routes_init, contenido_test_app, database_config
)

console = Console()


# Generate database_config.py
def generate_database_config(app_name: str, db_url: Optional[str]) -> None:
    if not db_url:
        return

    try:
        file_content = database_config(db_url)
        path = Path(app_name) / "database" / "database_config.py"
        path.write_text(file_content.rstrip() + "\n", encoding="utf-8")
        logger.info(f"Generated database_config.py at {path}")
    except Exception as e:
        logger.error(f"Failed to generate database_config.py: {e}")


# Generate environments
def generate_environments(app_name: str, environments: Optional[str]) -> None:
    if not environments:
        return

    try:
        env_list = [e.strip() for e in environments.split(",") if e.strip()]
        for env in env_list:
            env_name = f".env.{env.lower()}"
            env_path = Path(app_name) / env_name
            env_file_content = contenido_env(extra_vars={"ENV_NAME": env.upper()})
            env_path.write_text(env_file_content.rstrip() + "\n", encoding="utf-8")

            dc_name = f"docker-compose.{env.lower()}.yml"
            dc_path = Path(app_name) / dc_name
            dc_file_content = contenido_docker_compose(app_name, env)
            dc_path.write_text(dc_file_content.rstrip() + "\n", encoding="utf-8")

            logger.info(f"Files for environment '{env}' generated.")
        logger.info(f"All environments [{', '.join(env_list)}] have been configured.")
    except Exception as e:
        logger.error(f"Failed to generate environments: {e}")



def _create_template_and_static_files(app_path: Path) -> None:
    """Helper to create template and static files."""
    try:
        for folder in [
            app_path / "templates",
            app_path / "static" / "js",
            app_path / "static" / "styles",
            app_path / "static" / "images",
            app_path / "static" / "audio",
        ]:
            folder.mkdir(parents=True, exist_ok=True)
        (app_path / "templates" / "base.html").write_text(base_html.strip() + "\n", encoding="utf-8")
        (app_path / "templates" / "index.html").write_text(index_html.strip() + "\n", encoding="utf-8")
        (app_path / "static" / "styles" / "style.css").write_text(estilos_index_jinja2.strip() + "\n", encoding="utf-8")
        (app_path / "static" / "js" / "index.js").write_text("// Initial JavaScript\n", encoding="utf-8")
        logger.info("Template and static files created.")
    except Exception as e:
        logger.error(f"Failed to create template/static files: {e}")

def configure_app(app_name: str = "FastAPI-APP", config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Configure the FastAPI application project structure.
    Returns a status dict with success and error info.
    """
    status = {"success": True, "errors": []}
    if config is None:
        raise ValueError("Configuration cannot be None")

    app_path = Path(app_name)

    templates_enabled = bool(config.get("templates", False))
    database = str(config.get("base_de_datos", "")).lower()
    use_docker = bool(config.get("docker", False))

    structure = {
        "models": ["__init__.py"],
        "routes": ["__init__.py"],
        "schemas": ["__init__.py"],
        "services": ["__init__.py"],
        "database": ["__init__.py"]
    }

    if templates_enabled:
        structure["templates"] = ["base.html", "index.html"]
        structure["static/js"] = ["index.js"]
        structure["static/styles"] = ["style.css"]
        structure["static/images"] = []
        structure["static/audio"] = []

    try:
        create_structure(app_name, structure)
        # routes/__init__.py
        (app_path / "routes" / "__init__.py").write_text(contenido_routes_init.rstrip() + "\n", encoding="utf-8")
        # main.py
        main_content = contenido_main_jinja2 if templates_enabled else contenido_main_base
        (app_path / "main.py").write_text(main_content.strip() + "\n", encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to create base structure: {e}")
        status["success"] = False
        status["errors"].append(str(e))

    # Docker
    if use_docker:
        try:
            (app_path / "Dockerfile").write_text(contenido_docker.strip() + "\n", encoding="utf-8")
            environments = config.get("entornos", None)
            (app_path / "docker-compose.yml").write_text(
                contenido_docker_compose(app_name, environments).strip() + "\n", encoding="utf-8"
            )
            generate_environments(app_name, environments)
        except Exception as e:
            logger.error(f"Failed to create Docker files: {e}")
            status["success"] = False
            status["errors"].append(str(e))

    # .env and database_config.py
    if database == DB_MYSQL:
        db_url = "mysql+asyncmy://user:password@localhost/dbname"
    elif database == DB_POSTGRESQL:
        db_url = "postgresql+asyncpg://user:password@localhost/dbname"
    elif database == DB_SQLITE:
        db_url = "sqlite+aiosqlite:///./app.db"
    else:
        db_url = ""
        logger.warning("Unrecognized database. Connection configuration was skipped.")

    try:
        extra_env_vars = config.get("extra_env_vars", None)
        (app_path / ".env").write_text(
            contenido_env(db_url, extra_env_vars).strip() + "\n", encoding="utf-8"
        )
        generate_database_config(app_name, db_url)
    except Exception as e:
        logger.error(f"Failed to create .env or database config: {e}")
        status["success"] = False
        status["errors"].append(str(e))

    # README.md
    try:
        (app_path / "README.md").write_text(
            contenido_readme(app_name).strip() + "\n", encoding="utf-8"
        )
    except Exception as e:
        logger.error(f"Failed to create README.md: {e}")
        status["success"] = False
        status["errors"].append(str(e))

    # requirements.txt
    try:
        requirements = contenido_requisitos_base[:]
        if templates_enabled:
            requirements.append(contenido_jinja2.strip())
        if database == DB_MYSQL:
            requirements.append(contenido_mysql.strip())
        elif database == DB_POSTGRESQL:
            requirements.append(contenido_postgresql.strip())
        requirements.append("pytest")
        (app_path / "requirements.txt").write_text("\n".join(requirements) + "\n", encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to create requirements.txt: {e}")
        status["success"] = False
        status["errors"].append(str(e))

    # Template and static files
    if templates_enabled:
        _create_template_and_static_files(app_path)

    # test_app.py
    try:
        tests_path = app_path / "tests"
        tests_path.mkdir(parents=True, exist_ok=True)
        (tests_path / "test_app.py").write_text(contenido_test_app.rstrip() + "\n", encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to create test_app.py: {e}")
        status["success"] = False
        status["errors"].append(str(e))

    # config.json
    try:
        with open(app_path / "config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to create config.json: {e}")
        status["success"] = False
        status["errors"].append(str(e))

    logger.info(f"Configuration completed! Application {app_name} generated successfully.")
    return status
