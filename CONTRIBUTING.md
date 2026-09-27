# Contribuer à ContexteTech

Merci de votre intérêt ! Les contributions (corrections, traductions, nouvelles fonctions) sont bienvenues.

## Démarrer en local

```bash
cp .env.example .env
docker compose --profile local-db up -d --build
```

Le site est alors sur http://localhost:8088 (compte admin : celui de `.env`).

## Proposer une modification

1. Ouvrez d'abord une *issue* pour tout changement important, afin d'en discuter.
2. Créez une branche à partir de `main`, une modification par *pull request*.
3. Vérifiez avant d'envoyer :
   - `npx astro build` et `npx svelte-check` dans `web/` passent ;
   - dans `api/` : `ruff check .` et `pytest` passent (l'intégration continue les relance à chaque push) ;
   - **toute nouvelle fonctionnalité importante est accompagnée de tests** dans `api/tests/` ;
   - les textes d'interface existent dans les **5 langues** (`web/src/lib/i18n.js` : fr, en, es, de, it).
4. Décrivez ce que fait la modification et comment la tester.

## Règles

- **Aucun secret** dans le code : clés, mots de passe et adresses vont dans `.env` (jamais versionné).
- Suivez le style du code existant ; pas de styles ni de scripts écrits dans les pages (CSS dans `web/src/styles/`, JS dans `web/src/scripts/`).
- Messages de commit courts, à l'impératif, en français ou en anglais.

## Sécurité

Ne signalez pas une faille dans une *issue* publique : écrivez à **coucou@contextetech.com**.

## Licence

En contribuant, vous acceptez que votre code soit publié sous licence **AGPL-3.0**, comme le reste du projet.
Les fiches publiées sur contextetech.com gardent la licence choisie par leur auteur.
