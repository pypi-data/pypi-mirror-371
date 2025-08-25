"""Tests pour le générateur FastAPI"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from create_fastapi.generator import FastAPIGenerator


class TestFastAPIGenerator:
    """Tests pour la classe FastAPIGenerator"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Nettoyage après chaque test"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)

    def test_create_minimal_app(self):
        """Test création d'une app minimale"""
        generator = FastAPIGenerator(project_name="test_app", template="minimal")

        generator.generate()

        # Vérifier que les fichiers sont créés
        assert Path("test_app").exists()
        assert Path("test_app/main.py").exists()
        assert Path("test_app/requirements.txt").exists()
        assert Path("test_app/app/routers/items.py").exists()

    def test_create_full_app(self):
        """Test création d'une app complète"""
        generator = FastAPIGenerator(
            project_name="full_app",
            template="full",
            database="sqlite",
            include_auth=True,
            include_docker=True,
            include_tests=True,
        )

        generator.generate()

        # Vérifier la structure complète
        assert Path("full_app/main.py").exists()
        assert Path("full_app/Dockerfile").exists()
        assert Path("full_app/docker-compose.yml").exists()
        assert Path("full_app/tests/test_main.py").exists()
        assert Path("full_app/app/core/config.py").exists()
        assert Path("full_app/app/core/database.py").exists()

    def test_add_router(self):
        """Test ajout d'un router"""
        # Créer d'abord une app
        generator = FastAPIGenerator(project_name="router_test", template="minimal")
        generator.generate()

        # Aller dans le répertoire du projet
        original_dir = Path.cwd()
        os.chdir("router_test")

        try:
            # Ajouter un router depuis le répertoire du projet
            generator = FastAPIGenerator.from_existing_project(".")
            generator.add_router("users", "User", include_crud=True)

            # Vérifier que le router est créé (depuis le répertoire du projet)
            assert Path("app/routers/users.py").exists()

            # Vérifier que main.py est mis à jour
            with open("main.py", "r") as f:
                content = f.read()
                assert "from app.routers import users" in content
                assert "app.include_router(users.router)" in content

        finally:
            # Revenir au répertoire original
            os.chdir(original_dir)

    def test_add_model(self):
        """Test ajout d'un modèle"""
        # Créer d'abord une app
        generator = FastAPIGenerator(project_name="model_test", template="minimal")
        generator.generate()

        # Aller dans le répertoire du projet
        original_dir = Path.cwd()
        os.chdir("model_test")

        try:
            # Ajouter un modèle depuis le répertoire du projet
            generator = FastAPIGenerator.from_existing_project(".")
            generator.add_model("User", {"name": "str", "email": "str", "age": "int"})

            # Vérifier que le modèle est créé
            assert Path("app/models/user.py").exists()

            # Vérifier le contenu
            with open("app/models/user.py", "r") as f:
                content = f.read()
                assert "class User" in content
                assert "name: str" in content
                assert "email: str" in content
                assert "age: int" in content

        finally:
            # Revenir au répertoire original
            os.chdir(original_dir)

    def test_project_info(self):
        """Test récupération des infos projet"""
        generator = FastAPIGenerator(
            project_name="info_test", template="full", database="postgresql"
        )
        generator.generate()

        os.chdir("info_test")
        generator = FastAPIGenerator.from_existing_project()
        info = generator.get_project_info()

        assert info["name"] == "info_test"
        assert info["template"] == "full"
        assert info["database"] == "postgresql"
        assert isinstance(info["routers"], list)
        assert isinstance(info["models"], list)
