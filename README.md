# Vote Projets Étudiants

Application de vote en temps réel pour présenter et noter des projets étudiants.
Accessible depuis n'importe où — aucun WiFi commun requis.

## Fonctionnalités

- Interface **organisateur** (desktop) : QR code, gestion des projets, stats en direct
- Interface **votant** (mobile) : note de 1 à 5 étoiles, un seul vote par projet
- Mise à jour automatique toutes les 3 secondes
- Déploiement cloud via Railway (URL fixe, HTTPS)

## Déploiement sur Railway (gratuit)

### Étapes

1. Créez un compte sur [railway.app](https://railway.app)
2. Cliquez sur **"New Project"** → **"Deploy from GitHub repo"**
3. Uploadez ce dossier sur un dépôt GitHub (public ou privé)
4. Railway détecte automatiquement le `Procfile` et `requirements.txt`
5. Cliquez sur **"Generate Domain"** dans les settings du service
6. Votre app est en ligne 🎉

### Alternative : déploiement direct depuis le terminal

```bash
npm install -g @railway/cli
railway login
railway init
railway up
railway domain
```

## Structure des fichiers

```
vote-projets/
├── main.py           # Serveur FastAPI + HTML embarqué
├── requirements.txt  # Dépendances Python
├── Procfile          # Commande de démarrage Railway
└── README.md
```

## Utilisation

- **Organisateur** : ouvrez l'URL depuis un ordinateur → interface admin
- **Votants** : scannez le QR code ou ouvrez `votre-url.railway.app?mode=vote`

## Notes techniques

- Les données sont stockées **en mémoire** — elles sont perdues au redémarrage du serveur
- Adapté pour des sessions de vote courtes (une journée de présentations)
- Pour de la persistance, remplacer le stockage mémoire par SQLite ou Redis
