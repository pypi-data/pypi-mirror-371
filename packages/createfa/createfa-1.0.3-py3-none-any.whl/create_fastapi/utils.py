"""Utilitaires pour FastAPI Generator"""

import sys

from colorama import Fore, Style, init

# Initialiser colorama
init(autoreset=True)


def print_success(message: str) -> None:
    """Afficher un message de succès en vert"""
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    """Afficher un message d'erreur en rouge"""
    print(f"{Fore.RED}{message}{Style.RESET_ALL}", file=sys.stderr)


def print_info(message: str) -> None:
    """Afficher un message d'information en bleu"""
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")


def print_warning(message: str) -> None:
    """Afficher un message d'avertissement en jaune"""
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")
