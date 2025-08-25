"""Tests pour l'interface CLI"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from create_fastapi.cli import cli


class TestCLI:
    """Tests pour l'interface CLI"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        self.runner = CliRunner()

    def teardown_method(self):
        """Nettoyage après chaque test"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)

    def test_create_command_minimal(self):
        """Test commande create minimale"""
        result = self.runner.invoke(cli, ["create", "test_cli_app"])

        assert result.exit_code == 0
        assert "créée avec succès" in result.output
        assert Path("test_cli_app").exists()
        assert Path("test_cli_app/main.py").exists()

    def test_create_command_with_options(self):
        """Test commande create avec options"""
        result = self.runner.invoke(
            cli,
            [
                "create",
                "full_cli_app",
                "--template",
                "full",
                "--database",
                "sqlite",
                "--auth",
                "--docker",
                "--tests",
            ],
        )

        assert result.exit_code == 0
        assert Path("full_cli_app/Dockerfile").exists()
        assert Path("full_cli_app/tests").exists()

    def test_add_router_command(self):
        """Test commande add-router"""
        # Créer d'abord une app
        self.runner.invoke(cli, ["create", "router_cli_test"])
        os.chdir("router_cli_test")

        # Ajouter un router
        result = self.runner.invoke(
            cli, ["add-router", "products", "--model", "Product", "--crud"]
        )

        assert result.exit_code == 0
        assert "ajouté avec succès" in result.output
        assert Path("app/routers/products.py").exists()

    def test_add_model_command(self):
        """Test commande add-model"""
        # Créer d'abord une app
        self.runner.invoke(cli, ["create", "model_cli_test"])
        os.chdir("model_cli_test")

        # Ajouter un modèle
        result = self.runner.invoke(
            cli, ["add-model", "Customer", "--fields", "name:str,email:str,age:int"]
        )

        assert result.exit_code == 0
        assert "ajouté avec succès" in result.output
        assert Path("app/models/customer.py").exists()

    def test_info_command(self):
        """Test commande info"""
        # Créer d'abord une app
        self.runner.invoke(cli, ["create", "info_cli_test"])
        os.chdir("info_cli_test")

        # Obtenir les infos
        result = self.runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        assert "Informations sur le projet" in result.output
        assert "info_cli_test" in result.output

    def test_force_overwrite(self):
        """Test option --force"""
        # Créer une app
        self.runner.invoke(cli, ["create", "force_test"])

        # Essayer de recréer sans --force (doit échouer)
        result = self.runner.invoke(cli, ["create", "force_test"])
        assert result.exit_code != 0

        # Recréer avec --force (doit réussir)
        result = self.runner.invoke(cli, ["create", "force_test", "--force"])
        assert result.exit_code == 0
