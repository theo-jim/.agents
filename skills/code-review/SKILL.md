---
name: code-review
description: "Passe en revue les modifications depuis un point fixe (commit, branche, tag ou merge-base) selon trois axes : Normes (normes de codage du dépôt), Spécifications (conformité au ticket d'origine) et Risques (exécution tracée, cas limites, dépendances à la production). Exécute les trois analyses en sous-agents parallèles. À utiliser lorsque l'utilisateur souhaite réviser une branche, une PR/MR, des modifications en cours ou demande une « revue depuis X »."
---

Revue à trois axes du diff entre `HEAD` et un point fixe fourni par l'utilisateur :

- **Normes** : le code respecte-t-il les normes de codage documentées dans ce dépôt ?
- **Spécifications** : le code implémente-t-il fidèlement le ticket ou la spécification d'origine ?
- **Risques** : le code fonctionne-t-il réellement, branche par branche, y compris en production ?

Les trois axes s'exécutent au sein de **sous-agents parallèles** afin de ne pas polluer leurs contextes respectifs. Cet outil (skill) agrège ensuite leurs conclusions.

Le suivi de tickets (issue tracker) devrait vous avoir été fourni. Si `docs/agents/issue-tracker.md` est absent, demandez à l'utilisateur d'exécuter `/setup-matt-pocock-skills`.

## Procédure

### 1. Définir le point fixe

Le point fixe correspond à ce qu'a indiqué l'utilisateur (un SHA de commit, un nom de branche, un tag, `main`, `HEAD~5`, etc.). S'il n'en a pas spécifié, demandez-lui.

Récupérez la commande de diff en une fois : `git diff <point-fixe>...HEAD` (à trois points, pour comparer par rapport à la base de fusion). Notez également la liste des commits via `git log <point-fixe>..HEAD --oneline`.

Avant d'aller plus loin, vérifiez que le point fixe existe (`git rev-parse <point-fixe>`) et que le diff n'est pas vide. Une référence invalide ou un diff vide doit échouer à cette étape, et non à l'intérieur des deux sous-agents parallèles.

### 2. Identifier la source de la spécification

Cherchez la spécification d'origine dans l'ordre suivant :

1. Les références de tickets dans les messages de commit (`#123`, `Closes #45`, GitLab `!67`, etc.), récupérées via la procédure décrite dans `docs/agents/issue-tracker.md`.
2. Un chemin passé en argument par l'utilisateur.
3. Un fichier de spécification sous `docs/`, `specs/` ou `.scratch/` correspondant au nom de la branche ou de la fonctionnalité.
4. Si rien n'est trouvé, demandez à l'utilisateur où se trouve la spécification. S'il répond qu'il n'y en a pas, le sous-agent **Spécifications** ignorera cette partie et indiquera « aucune spécification disponible ».

### 3. Identifier les sources des normes

Tout ce qui documente la façon de rédiger le code dans le dépôt, comme `CODING_STANDARDS.md` ou `CONTRIBUTING.md`.

En plus de ce qui est documenté dans le dépôt, l'axe Normes intègre toujours le **référentiel de mauvaises pratiques** (*smell baseline*) ci-dessous : un ensemble fixe de *code smells* de Fowler (*Refactoring*, ch. 3) qui s'applique même lorsqu'un dépôt ne documente rien. Deux règles s'appliquent :

- **Le dépôt prévaut.** Une norme documentée dans le dépôt l'emporte toujours ; lorsqu'elle approuve une pratique que le référentiel signalerait, ignorez l'alerte.
- **C'est toujours une question de jugement.** Chaque mauvaise pratique est une heuristique indicative (« possible envie de fonctionnalité / *Feature Envy* »), jamais une violation stricte. Comme pour toute norme ici, ignorez tout ce qui est déjà géré par les outils de linter/formatting.

Chaque mauvaise pratique est présentée selon la structure *ce que c'est* → *comment la corriger* ; comparez-la au diff :

- **Nom mystérieux** (*Mysterious Name*) : une fonction, variable ou type dont le nom ne révèle pas ce qu'il fait ou contient. → Renommer ; si aucun nom explicite ne vient, le design est confus.
- **Code dupliqué** (*Duplicated Code*) : la même logique apparaît dans plus d'un bloc ou fichier du diff. → Extraire la logique commune et l'appeler aux deux endroits.
- **Envie de fonctionnalité** (*Feature Envy*) : une méthode qui manipule les données d'un autre objet plus que les siennes. → Déplacer la méthode sur l'objet dont elle envie les données.
- **Groupes de données** (*Data Clumps*) : les mêmes champs ou paramètres voyagent systématiquement ensemble (un type cherche à émerger). → Les regrouper dans un type unique et passer ce dernier.
- **Obsession des types primitifs** (*Primitive Obsession*) : un type primitif ou une chaîne utilisé à la place d'un concept métier qui mérite son propre type. → Créer un petit type dédié au concept.
- **Structures conditionnelles répétées** (*Repeated Switches*) : la même cascade de `switch`/`if` sur un même type se répète à plusieurs endroits. → Remplacer par du polymorphisme ou par une table de correspondance partagée.
- **Changements dispersés** (*Shotgun Surgery*) : une seule modification logique exige de petites retouches éparpillées dans de nombreux fichiers. → Regrouper ce qui varie ensemble dans un seul module.
- **Modifications divergentes** (*Divergent Change*) : un fichier ou module est modifié pour plusieurs raisons non liées. → Scinder le module pour qu'il n'ait plus qu'une seule raison de changer.
- **Généralisation spéculative** (*Speculative Generality*) : des abstractions, paramètres ou crochets ajoutés pour des besoins absents de la spécification. → Les supprimer ; ré-intégrer le code en ligne jusqu'à l'apparition d'un besoin réel.
- **Chaînes de messages** (*Message Chains*) : de longues navigations `a.b().c().d()` dont l'appelant ne devrait pas dépendre. → Masquer ce parcours derrière une méthode sur le premier objet.
- **Intermédiaire inutile** (*Middle Man*) : une classe ou fonction qui ne fait presque que déléguer. → La supprimer et appeler directement la cible.
- **Héritage refusé** (*Refused Bequest*) : une sous-classe ou implémentation qui ignore ou écrase la majorité de ce qu'elle hérite. → Abandonner l'héritage et utiliser la composition.

### 4. Lancer les trois sous-agents en parallèle

Le **prompt du sous-agent Normes** doit inclure :

- La commande de diff complète et la liste des commits.
- La liste des fichiers de normes trouvés à l'étape 3, **ainsi que le référentiel de mauvaises pratiques de l'étape 3** copié intégralement (le sous-agent n'y a pas accès autrement).
- Les consignes : « Rapportez, par fichier/bloc si nécessaire : (a) chaque endroit où le diff viole une norme documentée (citez le fichier + la règle) ; et (b) chaque mauvaise pratique du référentiel détectée (nommez-la et citez le bloc). Distinguez les violations strictes des appréciations personnelles : les manquements aux normes documentées peuvent être stricts, mais les mauvaises pratiques du référentiel restent toujours soumises au jugement, et les normes du dépôt prévalent. Ignorez ce que la chaîne d'outillage vérifie déjà. Moins de 400 mots. »

Le **prompt du sous-agent Spécifications** doit inclure :

- La commande de diff et la liste des commits.
- Le chemin ou le contenu récupéré de la spécification.
- Les consignes : « Rapportez : (a) les exigences demandées par la spécification qui sont manquantes ou incomplètes ; (b) les comportements présents dans le diff non demandés (dérive du périmètre / *scope creep*) ; (c) les exigences qui semblent implémentées mais dont la réalisation semble incorrecte. Citez la ligne de la spécification pour chaque constatation. Moins de 400 mots. »

Si la spécification est absente, sautez le sous-agent Spécifications et notez-le dans le rapport final.

Le **prompt du sous-agent Risques** doit inclure :

- La commande de diff et la liste des commits.
- Les consignes : « Pour chaque point d'entrée modifié, tracez l'exécution en suivant le graphe d'appels réel (lisez les appelants et les appelés hors du diff), branche par branche, y compris les chemins d'erreur, les valeurs nulles ou vides, les volumes limites et les accès concurrents. Rapportez : (a) les bugs et cas limites non gérés, avec la trace d'appels qui y mène ; (b) les conditions de concurrence ; (c) les hypothèses dont dépend le code sans qu'il les vérifie (format de données, unicité, ordre, présence d'un enregistrement) ; (d) les comportements qui dépendent de données, de volumes ou de configurations propres à la production (variables d'environnement, feature flags, données historiques, services tiers) ; (e) les scénarios principaux et les cas limites de (a) que les tests ne couvrent pas ; si le dépôt documente une checklist de familles de tests (par exemple « Test families checklist » dans `tests-common.md`), les familles applicables au diff qui n'ont ni test ni justification d'absence. Les tests de caractérisation annoncés comme phase Protect (scaffolding jetable) ne sont pas jugés sur lisibilité, vitesse ou couplage : vérifiez seulement qu'ils couvrent la surface modifiée. Classez chaque constatation en risque fonctionnel (effet visible pour un utilisateur ou un client) ou risque technique (performance, données, déploiement, maintenance). Marquez chaque constatation *confirmée* (trace complète) ou *plausible* (trace partielle, à valider). Moins de 500 mots. »

### 5. Agrégation

Présentez les trois rapports sous les titres `## Normes`, `## Spécifications` et `## Risques`, de manière textuelle ou légèrement nettoyée. Ne **fusionnez pas** et ne re-classez pas les observations, car les axes sont délibérément distincts (voir *Pourquoi trois axes*).

Terminez par un résumé d'une ligne : nombre total de constatations par axe, et le problème le plus critique *au sein de chaque axe* (le cas échéant). Ne désignez pas un seul « gagnant » entre les axes : c'est précisément le reclassement que cette séparation cherche à éviter.

### 6. Confronter les conclusions de l'utilisateur

Si l'utilisateur a avancé un diagnostic, un choix de conception ou une conclusion (dans sa demande, le ticket ou la description de MR), confrontez-le aux constatations en reviewer senior : dites où il tient, où il ne tient pas, et quelle preuve le trancherait. Sans conclusion de l'utilisateur, passez cette étape.

## Pourquoi trois axes

Une modification peut valider un axe et échouer sur un autre :

- Un code qui respecte toutes les normes mais implémente la mauvaise fonctionnalité → **Normes : OK, Spécifications : Échec.**
- Un code qui fait exactement ce que demandait le ticket mais viole les conventions du projet → **Spécifications : OK, Normes : Échec.**
- Un code propre et conforme au ticket qui casse sur une donnée de production ou sous accès concurrent → **Normes : OK, Spécifications : OK, Risques : Échec.**

Les rapporter séparément empêche un axe de masquer les autres.