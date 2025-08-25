"""Gestionnaire de templates pour FastAPI Generator"""

from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, Template


class TemplateManager:
    """Gestionnaire des templates Jinja2"""

    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template_files(self, template_type: str) -> List[Dict[str, str]]:
        """Obtenir la liste des fichiers à générer pour un template"""

        base_templates = [
            {"template": "main.py.j2", "output": "main.py"},
            {"template": "requirements.txt.j2", "output": "requirements.txt"},
            {"template": "README.md.j2", "output": "README.md"},
            {"template": "app/__init__.py.j2", "output": "app/__init__.py"},
            {"template": "router_example.py.j2", "output": "app/routers/items.py"},
            {"template": "__init__.py.j2", "output": "app/routers/__init__.py"},
            {"template": "__init__.py.j2", "output": "app/models/__init__.py"},
        ]

        templates = {
            "minimal": base_templates,
            "full": base_templates
            + [
                {"template": "config.py.j2", "output": "app/core/config.py"},
                {"template": "database.py.j2", "output": "app/core/database.py"},
                {"template": "__init__.py.j2", "output": "app/core/__init__.py"},
                {"template": "Dockerfile.j2", "output": "Dockerfile"},
                {"template": "docker-compose.yml.j2", "output": "docker-compose.yml"},
                {"template": "test_main.py.j2", "output": "tests/test_main.py"},
                {"template": ".gitignore.j2", "output": ".gitignore"},
                {"template": "__init__.py.j2", "output": "tests/__init__.py"},
            ],
            "api": base_templates
            + [
                {"template": "config.py.j2", "output": "app/core/config.py"},
                {"template": "__init__.py.j2", "output": "app/core/__init__.py"},
            ],
            "microservice": base_templates
            + [
                {"template": "config.py.j2", "output": "app/core/config.py"},
                {"template": "__init__.py.j2", "output": "app/core/__init__.py"},
                {"template": "test_main.py.j2", "output": "tests/test_main.py"},
                {"template": "__init__.py.j2", "output": "tests/__init__.py"},
            ],
        }

        return templates.get(template_type, templates["minimal"])

    def render_file(
        self, template_name: str, output_path: Path, context: Dict[str, Any]
    ) -> None:
        """Rendre un template et l'écrire dans un fichier"""

        template = self.env.get_template(template_name)
        content = template.render(**context)

        # Créer le répertoire parent si nécessaire
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def render_router(
        self,
        project_path: Path,
        router_name: str,
        model_name: str = None,
        include_crud: bool = False,
    ) -> None:
        """Rendre un template de router"""

        # Définir des champs par défaut si pas de model_name
        default_fields = {
            "name": "str",
            "description": "Optional[str]",
            "value": "float",
        }

        context = {
            "router_name": router_name,
            "model_name": model_name or router_name.title().rstrip("s"),
            "include_crud": include_crud,
            "fields": default_fields,  # Ajouter les champs par défaut
            "database": "none",  # Par défaut, pas de BDD pour les tests
        }

        template = self.env.get_template("router.py.j2")
        content = template.render(**context)

        router_path = project_path / "app" / "routers" / f"{router_name}.py"
        # S'assurer que le répertoire existe
        router_path.parent.mkdir(parents=True, exist_ok=True)

        with open(router_path, "w", encoding="utf-8") as f:
            f.write(content)

    def render_model(
        self, project_path: Path, model_name: str, fields: Dict[str, str]
    ) -> None:
        """Rendre un template de modèle"""

        context = {
            "model_name": model_name,
            "fields": fields,
            "database": "none",  # Par défaut pour les tests
        }

        template = self.env.get_template("model.py.j2")
        content = template.render(**context)

        model_path = project_path / "app" / "models" / f"{model_name.lower()}.py"
        # S'assurer que le répertoire existe
        model_path.parent.mkdir(parents=True, exist_ok=True)

        with open(model_path, "w", encoding="utf-8") as f:
            f.write(content)
