"""Configuration des tests pytest"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_project_dir():
    """Fixture pour un répertoire temporaire de projet"""
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    os.chdir(temp_dir)

    yield Path(temp_dir)

    os.chdir(original_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_app_structure(temp_project_dir):
    """Fixture pour une structure d'app exemple"""
    from create_fastapi.generator import FastAPIGenerator

    generator = FastAPIGenerator(project_name="sample_app", template="minimal")
    generator.generate()

    os.chdir("sample_app")
    return temp_project_dir / "sample_app"
