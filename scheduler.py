#!/usr/bin/env python3
"""
Planificateur pour le bot de vote Vanadia
Exécute le bot toutes les 1H30
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from vote_bot import VanadiaVoteBot
from colorama import init, Fore, Back, Style

init()

class VoteScheduler:
    def __init__(self):
        self.bot = VanadiaVoteBot()
        self.last_vote_time = None
        self.next_vote_time = None

        # Configuration logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def run_scheduled_vote(self):
        """Exécute un vote planifié"""
        try:
            print(f"\n{Back.BLUE}{Fore.WHITE} 🕒 VOTE PLANIFIÉ - {datetime.now().strftime('%H:%M:%S')} {Style.RESET_ALL}")

            success = await self.bot.main()

            if success:
                self.last_vote_time = datetime.now()
                self.next_vote_time = self.last_vote_time + timedelta(hours=1, minutes=30)

                print(f"{Fore.GREEN}✅ Vote planifié réussi!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Prochain vote: {self.next_vote_time.strftime('%H:%M:%S')}{Style.RESET_ALL}")

                self.bot.show_notification(
                    "Vanadia Vote Bot - Planifié",
                    f"Vote réussi! Prochain: {self.next_vote_time.strftime('%H:%M')}"
                )
            else:
                print(f"{Fore.RED}❌ Échec du vote planifié{Style.RESET_ALL}")
                self.bot.show_notification(
                    "Vanadia Vote Bot - Erreur",
                    "Échec du vote planifié. Vérifiez les logs."
                )

        except Exception as e:
            self.logger.error(f"Erreur vote planifié: {e}")

    def schedule_job_wrapper(self):
        """Wrapper pour permettre l'exécution asynchrone avec schedule"""
        asyncio.run(self.run_scheduled_vote())

    def start_scheduler(self):
        """Démarre le planificateur"""
        print(f"{Fore.CYAN}🕒 Planificateur Vanadia Vote Bot{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Intervalle: 1 heure 30 minutes{Style.RESET_ALL}")

        # Exécuter un vote immédiatement au démarrage
        print(f"{Fore.GREEN}🚀 Exécution du premier vote immédiatement...{Style.RESET_ALL}")
        self.schedule_job_wrapper()

        # Programmer l'exécution toutes les 1h30
        schedule.every(90).minutes.do(self.schedule_job_wrapper)

        print(f"{Fore.GREEN}✅ Planificateur démarré!{Style.RESET_ALL}")
        if self.next_vote_time:
            print(f"{Fore.CYAN}Prochain vote: {self.next_vote_time.strftime('%H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Appuyez sur Ctrl+C pour arrêter{Style.RESET_ALL}")

        # Notification de démarrage
        if self.next_vote_time:
            self.bot.show_notification(
                "Vanadia Vote Bot",
                f"Planificateur démarré! Prochain vote: {self.next_vote_time.strftime('%H:%M')}"
            )

        # Boucle principale
        try:
            while True:
                schedule.run_pending()

                # Afficher le statut toutes les 10 minutes
                now = datetime.now()
                if self.next_vote_time and now.minute % 10 == 0 and now.second < 10:
                    remaining = self.next_vote_time - now
                    if remaining.total_seconds() > 0:
                        hours, remainder = divmod(remaining.seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        print(f"{Fore.BLUE}⏰ Prochain vote dans: {hours}h {minutes}m{Style.RESET_ALL}")

                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Arrêt du planificateur demandé{Style.RESET_ALL}")
            self.bot.show_notification(
                "Vanadia Vote Bot",
                "Planificateur arrêté"
            )

    def run_immediate_vote(self):
        """Lance un vote immédiat"""
        print(f"{Fore.CYAN}🚀 Vote immédiat demandé{Style.RESET_ALL}")
        asyncio.run(self.bot.main())

def main():
    """Menu principal"""
    scheduler = VoteScheduler()

    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  🤖 VANADIA VOTE BOT - PLANIFICATEUR{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print()
    print(f"{Fore.WHITE}Options disponibles:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. Démarrer le planificateur (1h30 intervalle){Style.RESET_ALL}")
    print(f"{Fore.BLUE}2. Lancer un vote immédiat{Style.RESET_ALL}")
    print(f"{Fore.RED}3. Quitter{Style.RESET_ALL}")
    print()

    while True:
        try:
            choice = input(f"{Fore.YELLOW}Votre choix (1-3): {Style.RESET_ALL}")

            if choice == "1":
                scheduler.start_scheduler()
                break
            elif choice == "2":
                scheduler.run_immediate_vote()
                break
            elif choice == "3":
                print(f"{Fore.CYAN}Au revoir! 👋{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}Choix invalide. Veuillez sélectionner 1, 2 ou 3.{Style.RESET_ALL}")

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Au revoir! 👋{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    main()