"""Interface en ligne de commande"""

from pathlib import Path

import click

from .generator import FastAPIGenerator
from .utils import print_error, print_info, print_success


@click.group()
@click.version_option()
def cli():
    """FastAPI Generator - Générateur d'applications FastAPI"""
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--template",
    "-t",
    default="minimal",
    type=click.Choice(["minimal", "full", "api", "microservice"]),
    help="Template à utiliser",
)
@click.option(
    "--database",
    "-d",
    type=click.Choice(["none", "sqlite", "postgresql", "mysql"]),
    default="none",
    help="Base de données à configurer",
)
@click.option("--auth", is_flag=True, help="Inclure l'authentification JWT")
@click.option("--docker", is_flag=True, help="Inclure les fichiers Docker")
@click.option("--tests", is_flag=True, default=True, help="Inclure les tests")
@click.option(
    "--force", "-f", is_flag=True, help="Forcer la création même si le dossier existe"
)
def create(project_name, template, database, auth, docker, tests, force):
    """Créer une nouvelle application FastAPI"""

    try:
        generator = FastAPIGenerator(
            project_name=project_name,
            template=template,
            database=database,
            include_auth=auth,
            include_docker=docker,
            include_tests=tests,
            force_overwrite=force,
        )

        generator.generate()

        print_success(f"✅ Application '{project_name}' créée avec succès!")
        print_info(f"\n📁 Structure créée dans: {Path(project_name).absolute()}")
        print_info("\n🚀 Pour commencer:")
        print_info(f"   cd {project_name}")
        print_info("   python -m venv venv")
        print_info("   source venv/bin/activate  # Windows: venv\\Scripts\\activate")
        print_info("   pip install -r requirements.txt")
        print_info("   uvicorn main:app --reload")
        print_info("\n🌐 Puis visitez: http://localhost:8000/docs")

    except Exception as e:
        print_error(f"❌ Erreur: {e}")
        raise click.Abort()


@cli.command()
@click.argument("router_name")
@click.option("--model", "-m", help="Nom du modèle Pydantic")
@click.option("--crud", is_flag=True, help="Générer les opérations CRUD complètes")
def add_router(router_name, model, crud):
    """Ajouter un nouveau router à l'application existante"""

    try:
        generator = FastAPIGenerator.from_existing_project()
        generator.add_router(router_name, model_name=model, include_crud=crud)
        print_success(f"✅ Router '{router_name}' ajouté avec succès!")

    except Exception as e:
        print_error(f"❌ Erreur: {e}")
        raise click.Abort()


@cli.command()
@click.argument("model_name")
@click.option("--fields", "-f", help="Champs du modèle (format: nom:type,nom:type)")
def add_model(model_name, fields):
    """Ajouter un nouveau modèle Pydantic"""

    try:
        generator = FastAPIGenerator.from_existing_project()

        # Parser les champs
        field_dict = {}
        if fields:
            for field in fields.split(","):
                name, field_type = field.split(":")
                field_dict[name.strip()] = field_type.strip()

        generator.add_model(model_name, field_dict)
        print_success(f"✅ Modèle '{model_name}' ajouté avec succès!")

    except Exception as e:
        print_error(f"❌ Erreur: {e}")
        raise click.Abort()


@cli.command()
def info():
    """Afficher les informations sur l'application courante"""

    try:
        generator = FastAPIGenerator.from_existing_project()
        info = generator.get_project_info()

        print_info("📊 Informations sur le projet:")
        print_info(f"   Nom: {info['name']}")
        print_info(f"   Template: {info['template']}")
        print_info(f"   Routers: {len(info['routers'])}")
        print_info(f"   Modèles: {len(info['models'])}")

    except Exception as e:
        print_error(f"❌ Erreur: {e}")


def main():
    """Point d'entrée principal"""
    cli()


if __name__ == "__main__":
    main()
