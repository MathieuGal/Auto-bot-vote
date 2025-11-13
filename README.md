# 🤖 Vanadia Vote Bot

Bot automatique pour voter sur le serveur Vanadia.fr avec gestion intelligente des captchas.

## 🚀 Fonctionnalités

- **Navigation automatique** jusqu'aux captchas
- **Notifications desktop** quand intervention manuelle requise
- **Planificateur intégré** (exécution toutes les 1h30)
- **Interface colorée** avec logs détaillés
- **Gestion d'erreurs robuste**

## 📋 Installation

### 1. Installation automatique (recommandée)
```bash
python setup.py
```

### 2. Installation manuelle avec uv
```bash
# Installer uv si nécessaire
pip install uv

# Synchroniser les dépendances
uv sync

# Installer les navigateurs Playwright
uv run playwright install chromium
```

### 3. Installation legacy avec pip
```bash
# Installer les dépendances
pip install -r requirements.txt

# Installer les navigateurs Playwright
playwright install chromium
```

## 🎮 Utilisation

### Vote immédiat
```bash
# Avec uv (recommandé)
uv run python vote_bot.py

# Ou traditionnel
python vote_bot.py
```

### Planificateur automatique (1h30 intervalle)
```bash
# Avec uv (recommandé)
uv run python scheduler.py

# Ou traditionnel
python scheduler.py
```

## ⚙️ Configuration

Les identifiants sont définis dans `vote_bot.py`:
```python
self.username = "Tenji"
self.password = "Titi2006_7813"
```

## 🔧 Fonctionnement

1. **Connexion automatique** sur https://vanadia.fr/auth/login
2. **Navigation** vers la page de vote
3. **Détection des captchas** (reCAPTCHA, hCaptcha, etc.)
4. **Notification utilisateur** si captcha détecté
5. **Attente intervention manuelle** pour compléter le captcha
6. **Finalisation automatique** du vote

## 📊 Logs et Monitoring

- Logs sauvegardés dans `logs/vote_bot_YYYYMMDD.log`
- Notifications desktop en temps réel
- Affichage console coloré avec statuts

## 🛡️ Sécurité

- **Respect des captchas** - pas de contournement
- **Identifiants en dur** (à modifier selon vos besoins)
- **Délais réalistes** pour éviter la détection

## 📁 Structure des fichiers

```
Auto vote bot/
├── vote_bot.py      # Bot principal
├── scheduler.py     # Planificateur
├── setup.py         # Installation
├── pyproject.toml   # Configuration uv
├── requirements.txt # Dépendances (legacy)
├── logs/           # Journaux
└── data/           # Données (future utilisation)
```

## 🎯 Technologies utilisées

- **uv** - Gestionnaire de paquets Python moderne
- **Playwright** - Automatisation navigateur
- **Schedule** - Planification des tâches
- **Plyer** - Notifications système
- **Colorama** - Interface colorée
- **AsyncIO** - Programmation asynchrone

## ⚠️ Important

- Le bot s'arrête automatiquement aux captchas
- Intervention manuelle requise pour les compléter
- Respecte les conditions d'utilisation du site

## 🐛 Dépannage

### Erreur d'installation uv
```bash
# Installation manuelle de uv
pip install uv
# ou
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Erreur d'installation Playwright
```bash
# Avec uv
uv run playwright install chromium

# Ou traditionnel
python -m playwright install chromium
```

### Problème de notifications
- Vérifiez les permissions de notifications système
- Les notifications s'afficheront aussi en console

### Échec de connexion
- Vérifiez vos identifiants dans `vote_bot.py`
- Consultez les logs pour plus de détails

### Problèmes de dépendances
```bash
# Nettoyer et réinstaller avec uv
rm -rf .venv
uv sync --force

# Ou avec pip (fallback)
pip install -r requirements.txt
```

## 📝 Support

Pour des questions ou problèmes:
1. Consultez les logs dans `logs/`
2. Vérifiez votre connexion internet
3. Assurez-vous que le site est accessible