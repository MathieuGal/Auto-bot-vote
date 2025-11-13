#!/usr/bin/env python3
"""
Script d'installation et configuration pour Vanadia Vote Bot
"""

import subprocess
import sys
import os
from pathlib import Path
from colorama import init, Fore, Back, Style

init()

def run_command(command, description=""):
    """Exécute une commande et affiche le résultat"""
    try:
        print(f"{Fore.BLUE}🔧 {description}...{Style.RESET_ALL}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ {description} réussi{Style.RESET_ALL}")
            if result.stdout.strip():
                print(f"{Fore.WHITE}{result.stdout}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Erreur {description}:{Style.RESET_ALL}")
            print(f"{Fore.RED}{result.stderr}{Style.RESET_ALL}")
            return False

    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors de l'exécution: {e}{Style.RESET_ALL}")
        return False

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    print(f"{Fore.CYAN}🐍 Version Python: {version.major}.{version.minor}.{version.micro}{Style.RESET_ALL}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{Fore.RED}❌ Python 3.8+ requis. Version actuelle: {version.major}.{version.minor}{Style.RESET_ALL}")
        return False

    print(f"{Fore.GREEN}✅ Version Python compatible{Style.RESET_ALL}")
    return True

def check_uv_installed():
    """Vérifie si uv est installé"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ uv trouvé: {result.stdout.strip()}{Style.RESET_ALL}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_uv():
    """Installe uv si nécessaire"""
    if check_uv_installed():
        return True

    print(f"{Fore.YELLOW}📦 Installation de uv...{Style.RESET_ALL}")

    # Installation de uv
    install_commands = [
        "pip install uv",
        f"{sys.executable} -m pip install uv"
    ]

    for cmd in install_commands:
        if run_command(cmd, "Installation uv"):
            if check_uv_installed():
                return True

    print(f"{Fore.RED}❌ Impossible d'installer uv automatiquement{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}💡 Installez uv manuellement: pip install uv{Style.RESET_ALL}")
    return False

def sync_dependencies():
    """Synchronise les dépendances avec uv"""
    print(f"{Fore.YELLOW}📦 Synchronisation des dépendances avec uv...{Style.RESET_ALL}")

    # Vérifier si pyproject.toml existe
    if not Path("pyproject.toml").exists():
        print(f"{Fore.RED}❌ Fichier pyproject.toml non trouvé{Style.RESET_ALL}")
        return False

    # Synchroniser les dépendances
    success = run_command("uv sync", "Synchronisation des dépendances")
    if not success:
        # Essayer avec pip comme fallback
        print(f"{Fore.YELLOW}⚠️ Fallback vers pip...{Style.RESET_ALL}")
        if Path("requirements.txt").exists():
            success = run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installation avec pip")

    return success

def install_playwright_browsers():
    """Installe les navigateurs Playwright"""
    print(f"{Fore.YELLOW}🌐 Installation des navigateurs Playwright...{Style.RESET_ALL}")

    # Essayer avec uv d'abord
    commands = [
        "uv run playwright install chromium",
        "playwright install chromium",
        f"{sys.executable} -m playwright install chromium"
    ]

    for cmd in commands:
        print(f"{Fore.BLUE}Tentative: {cmd}{Style.RESET_ALL}")
        if run_command(cmd, f"Installation navigateur avec {cmd.split()[0]}"):
            return True

    print(f"{Fore.RED}❌ Échec installation navigateurs Playwright{Style.RESET_ALL}")
    return False

def create_directories():
    """Crée les répertoires nécessaires"""
    directories = ["logs", "data"]

    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"{Fore.GREEN}✅ Répertoire '{directory}' créé{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur création '{directory}': {e}{Style.RESET_ALL}")
            return False

    return True

def test_installation():
    """Test rapide de l'installation"""
    print(f"{Fore.CYAN}🧪 Test de l'installation...{Style.RESET_ALL}")

    try:
        import playwright
        print(f"{Fore.GREEN}✅ Playwright importé{Style.RESET_ALL}")
    except ImportError as e:
        print(f"{Fore.RED}❌ Erreur import Playwright: {e}{Style.RESET_ALL}")
        return False

    try:
        import schedule
        print(f"{Fore.GREEN}✅ Schedule importé{Style.RESET_ALL}")
    except ImportError as e:
        print(f"{Fore.RED}❌ Erreur import Schedule: {e}{Style.RESET_ALL}")
        return False

    try:
        import plyer
        print(f"{Fore.GREEN}✅ Plyer importé{Style.RESET_ALL}")
    except ImportError as e:
        print(f"{Fore.RED}❌ Erreur import Plyer: {e}{Style.RESET_ALL}")
        return False

    try:
        import colorama
        print(f"{Fore.GREEN}✅ Colorama importé{Style.RESET_ALL}")
    except ImportError as e:
        print(f"{Fore.RED}❌ Erreur import Colorama: {e}{Style.RESET_ALL}")
        return False

    print(f"{Fore.GREEN}✅ Tous les modules sont correctement installés!{Style.RESET_ALL}")
    return True

def show_usage_instructions():
    """Affiche les instructions d'utilisation"""
    print(f"\n{Back.GREEN}{Fore.BLACK} 🎉 INSTALLATION TERMINÉE! 🎉 {Style.RESET_ALL}\n")

    print(f"{Fore.CYAN}📋 Instructions d'utilisation:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}1. Vote immédiat:{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}uv run python vote_bot.py{Style.RESET_ALL}")
    print(f"   {Fore.GRAY}   ou: python vote_bot.py{Style.RESET_ALL}")
    print()
    print(f"{Fore.WHITE}2. Planificateur (toutes les 1h30):{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}uv run python scheduler.py{Style.RESET_ALL}")
    print(f"   {Fore.GRAY}   ou: python scheduler.py{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}📁 Fichiers créés:{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}• vote_bot.py{Style.RESET_ALL}      - Bot principal")
    print(f"   {Fore.WHITE}• scheduler.py{Style.RESET_ALL}     - Planificateur")
    print(f"   {Fore.WHITE}• pyproject.toml{Style.RESET_ALL}   - Configuration uv")
    print(f"   {Fore.WHITE}• requirements.txt{Style.RESET_ALL} - Dépendances (legacy)")
    print(f"   {Fore.WHITE}• logs/           {Style.RESET_ALL} - Journaux")
    print(f"   {Fore.WHITE}• data/           {Style.RESET_ALL} - Données")
    print()
    print(f"{Fore.MAGENTA}💡 Conseils:{Style.RESET_ALL}")
    print(f"   • Le bot s'arrête aux captchas pour intervention manuelle")
    print(f"   • Les notifications apparaîtront sur votre bureau")
    print(f"   • Les logs sont sauvegardés dans le dossier 'logs/'")
    print(f"   • Utilisez Ctrl+C pour arrêter le planificateur")

def main():
    """Installation principale"""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  🤖 VANADIA VOTE BOT - INSTALLATION{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

    steps = [
        ("Vérification Python", check_python_version),
        ("Installation uv", install_uv),
        ("Création des répertoires", create_directories),
        ("Synchronisation des dépendances", sync_dependencies),
        ("Installation navigateurs Playwright", install_playwright_browsers),
        ("Test de l'installation", test_installation)
    ]

    for step_name, step_function in steps:
        print(f"\n{Back.BLUE}{Fore.WHITE} ÉTAPE: {step_name.upper()} {Style.RESET_ALL}")

        success = step_function()

        if not success:
            print(f"\n{Back.RED}{Fore.WHITE} ❌ ÉCHEC DE L'INSTALLATION {Style.RESET_ALL}")
            print(f"{Fore.RED}Erreur à l'étape: {step_name}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}✅ {step_name} terminé avec succès{Style.RESET_ALL}")

    show_usage_instructions()

if __name__ == "__main__":
    main()