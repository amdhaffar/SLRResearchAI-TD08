# TD08 — QualityAgent et orchestration multi-agent

## Objectif

Le TD08 réutilise `artifacts/td06_evidence.json` et
`artifacts/td07_writing_artifact.json`. Le rapport contient volontairement
l'affirmation A5 mal soutenue. Vous allez construire huit blocs correspondant
aux notions du cours : contrôle structuré, couverture, ancrage des preuves,
juge LLM, réflexion, handoff et orchestration avec routage.

## Les huit TODO

Les modèles Pydantic, les retours de fonctions et les artefacts sont déjà
fournis. Il ne faut pas réécrire une application complète : chaque TODO
demande quelques expressions essentielles, puis un test ciblé.

| TODO | Fichier | Notion | Résultat attendu |
|---|---|---|---|
| 1 | `quality_agent.py` | données structurées | objets `Claim` validés |
| 2 | `quality_agent.py` | couverture | RQ présentes / RQ requises |
| 3 | `quality_agent.py` | grounding | preuves, métriques et verdict |
| 4 | `quality_agent.py` | LLM-as-a-judge | `QualityJudgeDecision` structuré |
| 5 | `quality_agent.py` | réflexion bornée | réviser puis accepter ou escalader |
| 6 | `orchestrator.py` | handoff et permissions | transitions, preuves et budget contrôlés |
| 7 | `orchestrator.py` | pipeline fixe | Search → Screening → RAG → Writing → Quality |
| 8 | `orchestrator.py` | superviseur | routage vers l'agent responsable |

Les fonctions `pipeline_run()` et `supervisor_run()` des anciennes versions
ne sont plus à compléter. Utilisez `full_pipeline_run()` et
`full_supervisor_run()`.

## TODO 1 — Contrat des affirmations

**Concept :** sortie LLM structurée et validation Pydantic.

Dans `quality_agent.py`, ouvrez `parse_claims()`. Pour chaque élément de
`report["claims"]`, construisez un `Claim` validé. Retournez une liste vide si
le champ est absent. Consultez le modèle `Claim` pour connaître ses champs.

Point de départ :

```python
return [Claim.model_validate(item)
        for item in report.get("claims", [])]
```

Vérifiez ensuite `pytest -v -k "todo_1"` : le résultat doit contenir autant
d'objets `Claim` que d'affirmations dans l'artefact.

## TODO 2 — Couverture des questions de recherche

**Concept :** métrique de couverture et contrôle d'exhaustivité.

Dans `evaluate_rules()`, comparez l'ensemble des `rq_id` présents dans les
sections avec `required_rqs`. Divisez le nombre de RQ couvertes par le nombre
de RQ requises, en évitant une division par zéro. Remplacez uniquement
`rq_coverage = None`.

La formule attendue suit ce modèle :

```python
rq_coverage = len(sections & required_rqs) / max(1, len(required_rqs))
```

Testez un rapport complet puis un rapport auquel il manque une section. La
couverture doit diminuer dans le second cas.

## TODO 3 — Contrôle des preuves et verdict

**Concept :** grounding, traçabilité des preuves et décision explicable.

Le squelette contient quatre valeurs `None`. Avant de les remplacer, lisez les
quelques lignes qui les suivent : elles utilisent directement vos résultats.
Pour chaque remplacement, identifiez d'abord le type de la valeur attendue,
puis expliquez en une phrase ce que votre expression produit. Le code ci-dessous
sert de référence ; il ne dispense pas de vérifier les variables et les tests.

**TODO 3a — `selected = None`**

Objectif : transformer les identifiants cités par l'affirmation en objets de
preuve. Un identifiant absent doit rester représenté par `None` afin que le
contrôle fourni puisse le détecter.

```python
selected = [evidence_by_id.get(identifier)
            for identifier in claim.evidence_ids]
```

**TODO 3b — `overlap = None`**

Objectif : obtenir l'ensemble des mots communs entre l'affirmation et le texte
des preuves. Vérifiez ensuite pourquoi le test utilise `len(overlap) >= 2`.

```python
overlap = _tokens(claim.text) & _tokens(source_text)
```

**TODO 3c — `verdict = None`**

Objectif : accepter uniquement un rapport suffisamment bien noté et sans
feedback. Si l'une des deux conditions échoue, le rapport doit être révisé.

```python
verdict = "ACCEPT" if score >= threshold and not feedback else "REVISE"
```

**TODO 3d — `repair_target = None`**

Objectif : router le problème vers l'agent qui peut réellement le corriger :
le RAG pour une preuve insuffisante, le Writer pour une formulation.

```python
repair_target = (
    "rag" if any(f.status != "supported" for f in findings)
    else "writing"
)
```

Le cas A5 doit produire une preuve non soutenue, `REVISE` et un retour vers
`rag`.

## TODO 4 — Juge LLM structuré

**Concept :** LLM-as-a-judge avec sortie structurée.

Dans `quality_agent.py`, la fusion avec le verdict déterministe est déjà
fournie. Complétez seulement les trois `None` de `build_llm_judge()`.

**TODO 4a — `prompt = None`**

Construisez une chaîne qui transmet au juge le rapport et
`rule_report.model_dump()`. Demandez une réponse conforme à
`QualityJudgeDecision`.

Exemple de forme attendue :

```python
prompt = f"Rapport : {report}\nContrôle : {rule_report.model_dump()}"
```

**TODO 4b — `result = None`**

Utilisez l'objet `structured` déjà créé et appelez-le une seule fois avec le
prompt :

```python
result = structured.invoke(prompt)
```

**TODO 4c — `decision = None`**

Validez la réponse avec le modèle Pydantic. Si le modèle renvoie déjà un objet
`QualityJudgeDecision`, conservez-le ; sinon, utilisez
`QualityJudgeDecision.model_validate(result)`.

Le juge LLM complète le contrôle déterministe : il ne doit jamais rendre
acceptable une preuve inconnue.

## TODO 5 — Réflexion bornée

**Concept :** réflexion contrôlée et budget d'itérations.

Dans `run_quality_loop()`, complétez trois décisions indépendantes :

**TODO 5a — condition d'acceptation**

Remplacez la valeur `None` de la comparaison par la chaîne `"ACCEPT"`.

**TODO 5b — fin du budget**

Lorsque `revision == max_revisions`, retournez un rapport dont le verdict est
`"ESCALATE"`. Le Writer ne doit pas être appelé dans ce cas.

**TODO 5c — révision**

Si le verdict est encore `REVISE`, appelez le Writer avec le rapport courant et
`quality.feedback`, puis recommencez la boucle. Conservez chaque résultat dans
`history`.

Structure indicative :

```python
for revision in range(max_revisions + 1):
    quality = evaluate_rules(...)
    # décider : ACCEPT, réviser ou ESCALATE
```

## TODO 6 — Contrat de handoff

**Concept :** handoff sécurisé, permissions et état partagé.

Le squelette fournit déjà les contrôles des preuves et du budget. Remplacez
uniquement `allowed_target = None` par le test de permission, puis lisez les
trois invariants :

1. la cible appartient aux transitions autorisées ;
2. toutes les preuves du handoff existent dans l'état partagé ;
3. le budget n'est pas négatif.

Une violation de permission lève `PermissionError`; une preuve absente ou un
budget négatif lève `ValueError`. Testez une transition autorisée puis les
trois cas d'erreur.

Les tests doivent vérifier trois cas : transition inconnue, preuve absente et
budget négatif. Le corps de la fonction ne doit pas appeler de LLM.

## TODO 7 — Pipeline fixe

**Concept :** orchestration séquentielle déterministe.

Le squelette contient déjà la boucle et l'appel des workers. Il exécute une
seule fois la chaîne :

```text
Search → Screening → RAG → Writing → Quality
```

**TODO 7a — `handoff = None`**

Remplacez `None` par :

```python
make_handoff(source, target, state,
             artifact=state.artifacts[source])
```

Le squelette valide ensuite le handoff et l'ajoute à `handoffs`. Après le
remplacement, vérifiez que `handoff.source`, `handoff.target` et son artefact
correspondent à l'itération courante.

Le statut final (`FINISH` ou `ESCALATE`) est fourni dans le squelette. Comparez
les transitions produites et lancez le test ciblé du pipeline.

## TODO 8 — Superviseur avec routage

**Concept :** supervision adaptative et routage conditionnel.

Le pipeline initial et la cible `state.quality.repair_target` sont déjà fournis.
Vous ne complétez que la transmission vers cette cible et la boucle de
réparation :

**TODO 8 — transmettre le handoff et relancer les agents**

Créez un handoff `quality → target`, vérifiez-le avec `validate_handoff()` et
décrémentez le budget avant d'appeler l'agent cible. Le squelette appelle
ensuite la cible, `WritingAgent` et `QualityAgent` ; vérifiez que cet ordre est
respecté et que le verdict est réévalué.

```python
handoff = make_handoff(
    "quality", target, state, "partial",
    artifact={"feedback": state.quality.feedback,
              "repair_target": target},
)
```

Pour une cible `rag`, l'ordre est `RAG → Writing → Quality`; pour une cible
`writing`, l'ordre est directement `Writing → Quality`.

Les deux branches sont :

```text
problème de preuve      : Quality → RAG → Writing → Quality
problème de formulation : Quality → Writing → Quality
```

Pour A5, le chemin attendu est :

```text
quality→rag→writing→quality→finish
```

Arrêtez sur `ACCEPT`, `ESCALATE` ou `BUDGET_EXHAUSTED`. Ne créez pas un routeur
supplémentaire : le champ `repair_target` est le routage demandé.

## Exécution

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
pytest -v
python3 -m streamlit run streamlit_app.py
```

Dans Streamlit, commencez par la Phase 1, puis lancez la Phase 2. Comparez
les traces, les artefacts et l'évolution de la note.
