# User story template

## Copy-paste template

```markdown
📝 **USER STORY**

En tant que [acteur], je veux [capacité], afin de [résultat].

📚 **CONTEXTE**
- [Contexte produit, problème utilisateur, données, feedback, contrainte]

📍 **Localisation** : [Surface, page, parcours, rôle, pays, plateforme]
💥 **Impact** : [Impact utilisateur, business, support, opérationnel, risque]

🚀 **SOLUTION**

**[Tâche 1]**
- [Comportement attendu]
- [Contraintes ou limites de scope]

**[Tâche 2]**
- [Comportement attendu]
- [Contraintes ou limites de scope]

🚫 **HORS SCOPE**
- [Ce que ce ticket ne couvre pas, et le ticket qui le couvre si connu]

🔗 **TICKETS LIÉS**
- [CLÉ-123] : [relation : bloque, dépend de, même lot]

🔍 **TRACKING**
- [Événement analytics, propriété, dashboard, ou "Aucun tracking identifié"]

🎨 **WIREFRAMES**
- [Nom de l'écran ou de la section] : [lien Figma copié depuis la page ou la section, avec `node-id`]
- [Nom de l'écran ou de la section] : [lien Figma copié depuis la page ou la section, avec `node-id`]

❓ **QUESTIONS**
- [Question ouverte] - owner: [nom/équipe]

🧾 **CRITÈRES D'ACCEPTATION**

**Scénario 1 : [titre]**
- Etant donné que [contexte]
- Quand [action]
- Alors [résultat observable]
```

## Field guidance

- `📝 USER STORY`: one sentence. Avoid multiple capabilities in one story.
- `📚 CONTEXTE`: explain why the work exists.
- `📍 Localisation`: say where the behavior appears.
- `💥 Impact`: state the expected user or business effect.
- `🚀 SOLUTION`: describe product behavior, not low-level implementation.
- `🚫 HORS SCOPE`: name what is handled elsewhere, one line per item, with the covering ticket when known.
- `🔗 TICKETS LIÉS`: one line per related issue with the relation (blocks, depends on, same batch). Skip the section when there is none.
- `🔍 TRACKING`: include event names when known; otherwise state the gap.
- `🎨 WIREFRAMES`: one link per screen or section, never the link of the whole Figma file. In Figma, right-click the page or the section, then "Copy link": the URL carries a `node-id`. A page link is the most useful one, it gives every section of the page at once. The name at the start of the line should match the page or section name in Figma.
- `🧾 CRITÈRES D'ACCEPTATION`: write one scenario per important path or edge case.
