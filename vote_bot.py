#!/usr/bin/env python3
"""
Bot de vote automatique pour Vanadia.fr
Automatise la navigation jusqu'au captcha, puis notifie l'utilisateur
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import time
import os

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from plyer import notification
from colorama import init, Fore, Back, Style

init()

class VanadiaVoteBot:
    def __init__(self):
        self.username = "Tenji"
        self.password = "Titi2006_7813"
        self.base_url = "https://vanadia.fr"
        self.login_url = f"{self.base_url}/auth/login"
        self.vote_url = f"{self.base_url}/vote"

        # Configuration des logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"vote_bot_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def show_notification(self, title, message, timeout=10):
        """Affiche une notification système"""
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=timeout,
                app_name="Vanadia Vote Bot"
            )
            self.logger.info(f"Notification envoyée: {title} - {message}")
        except Exception as e:
            self.logger.error(f"Erreur notification: {e}")
            # Fallback: affichage console avec couleurs
            print(f"\n{Back.YELLOW}{Fore.BLACK} 🔔 NOTIFICATION {Style.RESET_ALL}")
            print(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{message}{Style.RESET_ALL}")
            print(f"{Back.YELLOW}{Fore.BLACK} =============== {Style.RESET_ALL}\n")

    async def wait_for_user_input(self, message="Appuyez sur Entrée pour continuer..."):
        """Attend une entrée utilisateur de manière asynchrone"""
        return await asyncio.get_event_loop().run_in_executor(None, input, f"{Fore.GREEN}{message}{Style.RESET_ALL}")

    async def login(self, page):
        """Se connecte au site Vanadia"""
        try:
            self.logger.info("Navigation vers la page de connexion...")
            await page.goto(self.login_url, wait_until="networkidle")

            # Attendre que la page soit chargée
            await page.wait_for_load_state("domcontentloaded")

            # Rechercher les champs de connexion
            username_selectors = [
                'input[name="name"]',
                'input[name="pseudonyme"]',
                'input[name="pseudo"]',
                'input[name="username"]',
                'input[name="email"]',
                'input[type="email"]',
                '#pseudonyme',
                '#pseudo',
                '#username',
                '#email'
            ]

            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '#password'
            ]

            # Trouver le champ utilisateur
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = await page.wait_for_selector(selector, timeout=2000)
                    if username_field:
                        break
                except:
                    continue

            if not username_field:
                raise Exception("Champ nom d'utilisateur non trouvé")

            # Trouver le champ mot de passe
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = await page.wait_for_selector(selector, timeout=2000)
                    if password_field:
                        break
                except:
                    continue

            if not password_field:
                raise Exception("Champ mot de passe non trouvé")

            # Saisir les identifiants
            self.logger.info("Saisie des identifiants...")
            await username_field.fill(self.username)
            await password_field.fill(self.password)

            # Chercher le bouton de soumission
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Connexion")',
                'button:has-text("Se connecter")',
                'button:has-text("Login")',
                '.btn-primary',
                '.submit-btn'
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = await page.wait_for_selector(selector, timeout=2000)
                    if submit_button:
                        break
                except:
                    continue

            if submit_button:
                await submit_button.click()
                self.logger.info("Formulaire de connexion soumis")
            else:
                # Essayer d'appuyer sur Entrée
                await password_field.press("Enter")
                self.logger.info("Connexion tentée avec Entrée")

            # Attendre le reCAPTCHA invisible
            self.logger.info("Attente de la résolution du reCAPTCHA invisible...")
            await asyncio.sleep(5)  # Délai pour le reCAPTCHA invisible

            # Attendre la redirection ou le chargement
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeoutError:
                self.logger.warning("Timeout lors de l'attente du chargement, on continue...")

            await asyncio.sleep(3)  # Délai supplémentaire pour s'assurer du chargement complet

            # Vérifier si la connexion a réussi
            current_url = page.url
            self.logger.info(f"URL actuelle après connexion: {current_url}")

            if "login" not in current_url.lower():
                self.logger.info("✅ Connexion réussie!")
                return True
            else:
                # Vérifier s'il y a des messages d'erreur visibles
                error_selectors = [
                    '.alert-danger',
                    '.error',
                    '.invalid-feedback',
                    '[class*="error"]'
                ]

                error_found = False
                for selector in error_selectors:
                    try:
                        error_element = await page.query_selector(selector)
                        if error_element:
                            # Vérifier si l'élément est visible et contient du texte
                            is_visible = await error_element.is_visible()
                            if is_visible:
                                error_text = await error_element.inner_text()
                                if error_text.strip():  # Seulement si le message n'est pas vide
                                    self.logger.error(f"Erreur de connexion: {error_text}")
                                    error_found = True
                                    break
                    except:
                        continue

                if error_found:
                    return False
                else:
                    # Pas d'erreur visible, mais toujours sur login - peut-être captcha en cours
                    self.logger.warning("Toujours sur la page de login mais pas d'erreur visible")
                    self.logger.info("Le reCAPTCHA invisible pourrait nécessiter une validation manuelle")
                    return False

        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion: {e}")
            return False

    async def navigate_to_vote(self, page):
        """Navigation vers la page de vote"""
        try:
            self.logger.info("Navigation vers la page de vote...")
            await page.goto(self.vote_url, wait_until="networkidle")
            await page.wait_for_load_state("domcontentloaded")
            return True
        except Exception as e:
            self.logger.error(f"Erreur navigation vers vote: {e}")
            return False

    async def detect_captcha_and_notify(self, page):
        """Détecte la présence d'un captcha et notifie l'utilisateur"""
        try:
            # Sélecteurs possibles pour les captchas
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                'iframe[src*="hcaptcha"]',
                '.g-recaptcha',
                '.h-captcha',
                '[class*="captcha"]',
                '[id*="captcha"]',
                'img[src*="captcha"]'
            ]

            self.logger.info("Recherche de captcha...")

            for selector in captcha_selectors:
                try:
                    captcha_element = await page.wait_for_selector(selector, timeout=5000)
                    if captcha_element:
                        self.logger.info(f"🤖 Captcha détecté: {selector}")

                        # Notification
                        self.show_notification(
                            "Vanadia Vote Bot",
                            "Captcha détecté! Veuillez le compléter manuellement.",
                            timeout=0  # Notification persistante
                        )

                        # Affichage console
                        print(f"\n{Back.RED}{Fore.WHITE} 🚨 CAPTCHA DÉTECTÉ 🚨 {Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Un captcha doit être complété manuellement.{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Le navigateur va s'ouvrir en mode visible.{Style.RESET_ALL}")

                        return True
                except PlaywrightTimeoutError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Erreur lors de la recherche de captcha {selector}: {e}")
                    continue

            # Vérifier aussi les boutons de vote
            vote_selectors = [
                'button:has-text("Voter")',
                'button:has-text("Vote")',
                '.vote-btn',
                '.btn-vote',
                '[class*="vote"]',
                'a[href*="vote"]'
            ]

            for selector in vote_selectors:
                try:
                    vote_element = await page.wait_for_selector(selector, timeout=3000)
                    if vote_element:
                        self.logger.info(f"Bouton de vote trouvé: {selector}")

                        # Essayer de cliquer
                        await vote_element.click()
                        await asyncio.sleep(3)  # Attendre que le captcha apparaisse

                        # Revérifier les captchas après le clic
                        for captcha_selector in captcha_selectors:
                            try:
                                captcha_after_click = await page.wait_for_selector(captcha_selector, timeout=5000)
                                if captcha_after_click:
                                    self.logger.info("🤖 Captcha apparu après clic sur vote")

                                    self.show_notification(
                                        "Vanadia Vote Bot",
                                        "Captcha apparu! Veuillez le compléter manuellement.",
                                        timeout=0
                                    )

                                    return True
                            except:
                                continue

                        break
                except:
                    continue

            self.logger.info("Aucun captcha détecté pour l'instant")
            return False

        except Exception as e:
            self.logger.error(f"Erreur lors de la détection de captcha: {e}")
            return False

    async def run_vote_process(self, headless=True):
        """Exécute le processus de vote complet"""
        try:
            async with async_playwright() as p:
                # Créer un dossier pour le profil utilisateur
                user_data_dir = Path("data/browser_profile")
                user_data_dir.mkdir(parents=True, exist_ok=True)

                # Lancement du navigateur avec profil persistant et configuration anti-détection
                context = await p.chromium.launch_persistent_context(
                    str(user_data_dir),
                    headless=headless,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-setuid-sandbox'
                    ],
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    locale='fr-FR',
                    timezone_id='Europe/Paris',
                    permissions=['geolocation', 'notifications']
                )

                page = context.pages[0]  # Utiliser la page déjà ouverte
                captcha_detected = False  # Initialisation de la variable

                # Injecter des scripts pour masquer l'automatisation
                await page.add_init_script("""
                    // Masquer webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });

                    // Masquer les propriétés de détection de bot
                    window.navigator.chrome = {
                        runtime: {}
                    };

                    // Override des permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """)

                try:
                    # Étape 1: Connexion
                    login_success = await self.login(page)
                    if not login_success:
                        self.show_notification(
                            "Vanadia Vote Bot - Erreur",
                            "Échec de la connexion. Vérifiez vos identifiants."
                        )
                        return False

                    # Étape 2: Navigation vers vote
                    nav_success = await self.navigate_to_vote(page)
                    if not nav_success:
                        self.show_notification(
                            "Vanadia Vote Bot - Erreur",
                            "Impossible d'accéder à la page de vote."
                        )
                        return False

                    # Attendre que la page de vote soit complètement chargée
                    await asyncio.sleep(3)
                    self.logger.info("Attente pour que la page de vote se charge complètement...")

                    # Sauvegarder la page Vanadia originale
                    vanadia_page = page
                    serverprive_page = None

                    # Chercher le lien serveur-prive.net
                    serverprive_selectors = [
                        'a[href*="serveur-prive.net"]',
                        'a[href*="serveur-prive"]',
                        'a:has-text("Serveur privé")',
                        'a:has-text("serveur-prive")',
                    ]

                    link_clicked = False
                    for selector in serverprive_selectors:
                        try:
                            serverprive_link = await page.wait_for_selector(selector, timeout=3000)
                            if serverprive_link:
                                link_text = await serverprive_link.inner_text()
                                self.logger.info(f"Lien serveur-prive.net trouvé: {link_text.strip()}")

                                # Vérifier si le lien ouvre un nouvel onglet
                                target = await serverprive_link.get_attribute("target")

                                # Attendre un éventuel nouvel onglet
                                async with context.expect_page() as new_page_info:
                                    await serverprive_link.click()
                                    self.logger.info("Clic effectué sur le lien serveur-prive.net")

                                    try:
                                        # Attendre max 5 secondes pour un nouvel onglet
                                        new_page = await asyncio.wait_for(new_page_info.value, timeout=5.0)
                                        self.logger.info("Nouvel onglet détecté, basculement vers celui-ci")
                                        serverprive_page = new_page
                                        page = new_page
                                        await page.wait_for_load_state("domcontentloaded")
                                    except asyncio.TimeoutError:
                                        # Pas de nouvel onglet, rester sur la page actuelle
                                        self.logger.info("Pas de nouvel onglet, navigation dans la même page")
                                        await page.wait_for_load_state("domcontentloaded")

                                link_clicked = True
                                await asyncio.sleep(3)  # Attendre le chargement complet
                                break
                        except Exception as e:
                            self.logger.debug(f"Erreur avec sélecteur {selector}: {e}")
                            continue

                    if not link_clicked:
                        self.logger.warning("Lien serveur-prive.net non trouvé")

                    # Étape 3: Détection captcha
                    captcha_detected = await self.detect_captcha_and_notify(page)

                    if captcha_detected:
                        # Captcha détecté sur serveur-prive.net
                        print(f"\n{Back.BLUE}{Fore.WHITE} 🔄 CAPTCHA DÉTECTÉ - Retour sur Vanadia {Style.RESET_ALL}")
                        self.logger.info("Captcha détecté sur serveur-prive.net, retour vers Vanadia")

                        # Retourner sur la page Vanadia
                        await vanadia_page.bring_to_front()
                        self.logger.info("Retour sur la page Vanadia")

                        # Attendre 5 secondes
                        print(f"{Fore.CYAN}⏳ Attente de 5 secondes avant validation...{Style.RESET_ALL}")
                        await asyncio.sleep(5)

                        # Chercher et cliquer sur le bouton "Valider le vote"
                        validate_selectors = [
                            'button:has-text("Valider")',
                            'button:has-text("Valider le vote")',
                            'button:has-text("Confirmer")',
                            'button:has-text("Confirmer le vote")',
                            'input[type="submit"][value*="Valider"]',
                            'input[type="submit"][value*="Confirmer"]',
                            '.btn-validate',
                            '.validate-btn',
                            '#validate-vote',
                            'button[type="submit"]'
                        ]

                        validate_clicked = False
                        for selector in validate_selectors:
                            try:
                                validate_button = await vanadia_page.wait_for_selector(selector, timeout=3000)
                                if validate_button:
                                    button_text = await validate_button.inner_text()
                                    self.logger.info(f"Bouton de validation trouvé: {button_text.strip()}")
                                    await validate_button.click()
                                    self.logger.info("✅ Clic effectué sur le bouton de validation")
                                    print(f"{Fore.GREEN}✅ Vote validé sur Vanadia!{Style.RESET_ALL}")
                                    validate_clicked = True
                                    await asyncio.sleep(2)
                                    break
                            except:
                                continue

                        if not validate_clicked:
                            self.logger.warning("⚠️ Bouton de validation non trouvé sur Vanadia")
                            print(f"{Fore.YELLOW}⚠️ Bouton de validation non trouvé automatiquement{Style.RESET_ALL}")

                        # Vérifier le succès
                        await asyncio.sleep(2)
                        page_content = await vanadia_page.content()

                        if any(keyword in page_content.lower() for keyword in
                               ['merci', 'vote réussi', 'vote enregistré', 'success', 'validé']):
                            self.logger.info("✅ Vote réussi!")
                            self.show_notification(
                                "Vanadia Vote Bot",
                                "Vote complété avec succès! ✅"
                            )
                            return True
                        else:
                            self.logger.info("Vote validé (vérification incertaine)")
                            return True

                    else:
                        # Pas de captcha détecté, essayer de voter automatiquement
                        self.logger.info("Aucun captcha - tentative de vote automatique")

                        # Chercher et cliquer sur les boutons de vote
                        vote_selectors = [
                            'button:has-text("Voter")',
                            '.vote-btn',
                            '.btn-vote'
                        ]

                        for selector in vote_selectors:
                            try:
                                vote_btn = await page.wait_for_selector(selector, timeout=3000)
                                if vote_btn:
                                    await vote_btn.click()
                                    await asyncio.sleep(3)
                                    break
                            except:
                                continue

                        # Vérifier le succès
                        page_content = await page.content()
                        if any(keyword in page_content.lower() for keyword in
                               ['merci', 'vote réussi', 'vote enregistré', 'success']):
                            self.logger.info("✅ Vote automatique réussi!")
                            self.show_notification(
                                "Vanadia Vote Bot",
                                "Vote automatique complété! ✅"
                            )
                            return True

                        self.logger.info("Vote automatique incertain")
                        return False

                except Exception as e:
                    self.logger.error(f"Erreur durant le processus: {e}")
                    return False

                finally:
                    if captcha_detected and not headless:
                        # Si captcha détecté en mode visible, on laisse le navigateur ouvert plus longtemps
                        self.logger.info("Fenêtre laissée ouverte pour compléter le captcha...")
                    else:
                        await asyncio.sleep(3)  # Court délai avant de fermer

                    # Toujours fermer à la fin
                    await context.close()

        except Exception as e:
            self.logger.error(f"Erreur critique: {e}")
            return False

    async def main(self, headless=False):
        """Fonction principale"""
        print(f"{Fore.CYAN}🤖 Vanadia Vote Bot - Démarrage{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Lancement du processus de vote en mode {'invisible' if headless else 'visible'}...{Style.RESET_ALL}")

        success = await self.run_vote_process(headless=headless)

        if success:
            print(f"{Fore.GREEN}✅ Processus terminé avec succès!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Erreur durant le processus{Style.RESET_ALL}")

        return success

if __name__ == "__main__":
    bot = VanadiaVoteBot()
    asyncio.run(bot.main())