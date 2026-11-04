# Task template

Use this for technical tasks, chores, or backlog items that are not direct user stories.

## Copy-paste template

```markdown
📚 **CONTEXTE**
- [Contexte technique, dette, maintenance, ou raison de la tâche]

📍 **Localisation**
- Projet : [dossier de premier niveau du dépôt, ex. front/web, services/api]
- Zone : [chemin du dossier ou du fichier principal concerné, ex. front/web/src/modules/checkout]

💥 **Impact**
- [Pourquoi cette tâche est nécessaire, ce qu'elle améliore ou prévient]

🚀 **SOLUTION**
- [Action ou ensemble d'actions à réaliser]
- [Contraintes ou limites de scope]

🚫 **HORS SCOPE**
- [Ce que cette tâche ne couvre pas, et le ticket qui le couvre si connu]

🔗 **TICKETS LIÉS**
- [CLÉ-123] : [relation : bloque, dépend de, même lot]

🧾 **CRITÈRES D'ACCEPTATION**

**Scénario 1 : [titre]**
- Etant donné que [précondition ou contexte]
- Quand [action]
- Alors [résultat attendu]
```

## Field guidance

- `📍 Localisation`: the project is the top-level folder of the repository, the zone is a real path, not a description. A path lets tools route the matching technical documentation and derive the commit scope.
- `🚫 HORS SCOPE`: name what is handled elsewhere, one line per item, with the covering ticket when known.
- `🔗 TICKETS LIÉS`: one line per related issue with the relation. Skip the section when there is none.
- `🧾 CRITÈRES D'ACCEPTATION`: verify that existing behavior still holds after the change.
