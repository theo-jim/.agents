# Issue tracker examples

## Bug report example

```markdown
**L'export CSV échoue depuis le tableau de bord**

📚 **CONTEXTE**
- Lorsque l'on essaie d'exporter le fichier CSV depuis le tableau de bord, il y a une erreur 500 qui se produit à chaque fois.

📝 **COMMENT REPRODUIRE**
1. Ouvrir le tableau de bord
2. Cliquer sur Exporter
3. Choisir le format CSV
4. Valider l'export

❌ **COMPORTEMENT ACTUEL**
- L'export échoue avec une erreur 500
- Aucun fichier n'est téléchargé
- [capture]

✅ **COMPORTEMENT ATTENDU**
- Un fichier CSV est téléchargé
- Aucune erreur serveur ne s'affiche
```

## User story example

```markdown
**Permettre aux utilisateurs de sauvegarder leurs préférences de notification**

📝 **USER STORY**

En tant qu'utilisateur connecté, je veux enregistrer mes préférences de notification, afin de recevoir uniquement les alertes utiles.

📚 **CONTEXTE**
- Les emails actuels sont trop fréquents et augmentent le risque de désabonnement.

📍 **Localisation** : Paramètres > Notifications
💥 **Impact** : Réduction du bruit et meilleure rétention.

🚀 **SOLUTION**
- Afficher des préférences par canal : email, push, in-app.
- Confirmer la sauvegarde après validation.

🚫 **HORS SCOPE**
- Les préférences par produit : traitées dans PROJ-457.

🔗 **TICKETS LIÉS**
- PROJ-457 : même lot, préférences par produit

🔍 **TRACKING**
- `notification_preferences_saved` - Link to the documentation

🎨 **WIREFRAMES**
- Page Notifications : https://www.figma.com/design/<fileKey>/<fileName>?node-id=66-2645
- Section Confirmation : https://www.figma.com/design/<fileKey>/<fileName>?node-id=2530-25039

❓ **QUESTIONS**
- Les préférences sont-elles globales ou par produit ? - owner: Product

🧾 **CRITÈRES D'ACCEPTATION**

**Scénario 1 : Enregistrement réussi**
- Etant donné que je suis sur la page des préférences de notification
- Et que je désactive l'email
- Quand j'enregistre
- Alors mes préférences sont sauvegardées et une confirmation s'affiche
```

## Task example

```markdown
**Refactorer le module d'authentification**

📚 **CONTEXTE**
- Le module actuel contient de la dette technique accumulée sur 3 ans.
- Certaines dépendances sont obsolètes et non mises à jour.

📍 **Localisation**
- Projet : `front/app`
- Zone : `front/app/src/auth/` (`login.tsx`, `session.ts`, `token.service.ts`)

💥 **Impact**
- Améliore la maintenabilité et réduit les risques de sécurité.
- Prépare le terrain pour l'authentification par SSO.

🚀 **SOLUTION**
- Remplacer le système de tokens custom par une library standard.
- Extrapoler les validations dans des utilitaires réutilisables.
- Ajouter des tests unitaires sur les flows existants.

🧾 **CRITÈRES D'ACCEPTATION**

**Scénario 1 : Login existant**
- Etant donné un utilisateur avec des identifiants valides
- Quand il se connecte
- Alors il accède à son tableau de bord sans erreur

**Scénario 2 : Session expirée**
- Etant donné un utilisateur avec une session expirée
- Quand il tente d'accéder à une page protégée
- Alors il est redirigé vers la page de login
```
