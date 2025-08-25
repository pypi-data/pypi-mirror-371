import json
from pathlib import Path
from typing import Any, Dict, Optional

from .templates import TemplateManager
from .utils import print_info, print_success


class FastAPIGenerator:
    """Générateur d'applications FastAPI"""

    def __init__(
        self,
        project_name: str,
        template: str = "minimal",
        database: str = "none",
        include_auth: bool = False,
        include_docker: bool = False,
        include_tests: bool = True,
        force_overwrite: bool = False,
    ):
        self.project_name = project_name
        self.template = template
        self.database = database
        self.include_auth = include_auth
        self.include_docker = include_docker
        self.include_tests = include_tests
        self.force_overwrite = force_overwrite

        self.project_path = Path(project_name)
        self.template_manager = TemplateManager()

        # Configuration du projet
        self.config = {
            "name": project_name,
            "template": template,
            "database": database,
            "auth": include_auth,
            "docker": include_docker,
            "tests": include_tests,
            "routers": [],
            "models": [],
        }

    @classmethod
    def from_existing_project(cls, project_path: str = ".") -> "FastAPIGenerator":
        """Créer un générateur à partir d'un projet existant"""
        project_path_obj = Path(project_path).resolve()
        config_path = project_path_obj / ".fastapi-gen.json"

        if not config_path.exists():
            raise ValueError("Projet FastAPI Generator non trouvé dans ce répertoire")

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        generator = cls(
            project_name=config["name"],
            template=config["template"],
            database=config["database"],
            include_auth=config["auth"],
            include_docker=config["docker"],
            include_tests=config["tests"],
        )

        # CORRECTION IMPORTANTE : Utiliser le répertoire courant comme project_path
        # car on est déjà dans le projet
        generator.project_path = Path(".")
        generator.config = config
        return generator

    def generate(self) -> None:
        """Générer l'application complète"""

        # Vérifier si le projet existe
        if (
            self.project_path.exists()
            and not self.force_overwrite
            and self.project_path != Path(".")
        ):
            raise ValueError(
                f"Le répertoire '{self.project_name}' existe déjà. Utilisez --force pour le remplacer."
            )

        print_info(f"🚀 Génération de l'application FastAPI: {self.project_name}")

        # Créer la structure de base
        self._create_directory_structure()

        # Générer les fichiers selon le template
        self._generate_from_template()

        # Sauvegarder la configuration
        self._save_config()

        print_success("✨ Génération terminée!")

    def add_router(
        self,
        router_name: str,
        model_name: Optional[str] = None,
        include_crud: bool = False,
    ) -> None:
        """Ajouter un nouveau router"""

        router_info = {"name": router_name, "model": model_name, "crud": include_crud}

        # Générer le fichier router
        self.template_manager.render_router(
            self.project_path, router_name, model_name, include_crud
        )

        # Mettre à jour la configuration
        if "routers" not in self.config:
            self.config["routers"] = []
        self.config["routers"].append(router_info)
        self._save_config()

        # Mettre à jour main.py
        self._update_main_with_router(router_name)

    def add_model(self, model_name: str, fields: Dict[str, str]) -> None:
        """Ajouter un nouveau modèle Pydantic"""

        model_info = {"name": model_name, "fields": fields}

        # Générer le fichier modèle
        self.template_manager.render_model(self.project_path, model_name, fields)

        # Mettre à jour la configuration
        if "models" not in self.config:
            self.config["models"] = []
        self.config["models"].append(model_info)
        self._save_config()

    def get_project_info(self) -> Dict[str, Any]:
        """Obtenir les informations sur le projet"""
        return self.config.copy()

    def _create_directory_structure(self) -> None:
        """Créer la structure de répertoires"""

        directories = [
            self.project_path,
            self.project_path / "app",
            self.project_path / "app" / "routers",
            self.project_path / "app" / "models",
            self.project_path / "app" / "core",
        ]

        if self.include_auth:
            directories.append(self.project_path / "app" / "auth")

        if self.include_tests:
            directories.append(self.project_path / "tests")

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print_info(f"📁 Répertoire: {directory}")

    def _generate_from_template(self) -> None:
        """Générer les fichiers à partir du template"""

        context = {
            "project_name": self.project_name,
            "database": self.database,
            "include_auth": self.include_auth,
            "include_docker": self.include_docker,
            "include_tests": self.include_tests,
        }

        files_to_generate = self.template_manager.get_template_files(self.template)

        for file_info in files_to_generate:
            self.template_manager.render_file(
                template_name=file_info["template"],
                output_path=self.project_path / file_info["output"],
                context=context,
            )
            print_info(f"📄 Fichier: {file_info['output']}")

    def _save_config(self) -> None:
        """Sauvegarder la configuration du projet"""

        config_path = self.project_path / ".fastapi-gen.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def _update_main_with_router(self, router_name: str) -> None:
        """Mettre à jour main.py avec le nouveau router"""

        main_path = self.project_path / "main.py"
        if not main_path.exists():
            return

        # Lire le contenu actuel
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Ajouter l'import s'il n'existe pas
        import_line = f"from app.routers import {router_name}"
        if import_line not in content:
            # Trouver la ligne après les autres imports de routers
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if line.startswith("from app.routers"):
                    insert_index = i + 1
                elif line.startswith("from app") and "routers" not in line:
                    insert_index = i + 1

            lines.insert(insert_index, import_line)
            content = "\n".join(lines)

        # Ajouter l'inclusion du router s'il n'existe pas
        include_line = f"app.include_router({router_name}.router)"
        if include_line not in content:
            # Trouver où insérer (après les autres include_router)
            lines = content.split("\n")

            # Chercher la dernière ligne include_router
            insert_index = len(lines) - 1
            for i, line in enumerate(lines):
                if "app.include_router" in line:
                    insert_index = i + 1

            lines.insert(insert_index, include_line)
            content = "\n".join(lines)

        # Écrire le contenu modifié
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content)
