# SLRResearchAI — TD08 étudiant

Le TD08 ajoute au projet du TD07, dans cet ordre pédagogique :

1. un QualityAgent qui contrôle la fidélité des affirmations ;
2. ensuite, une orchestration par pipeline et par superviseur.

Artefacts utilisés :

- `artifacts/td06_evidence.json` ;
- `artifacts/td07_writing_artifact.json`.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
pytest -v
```

Consultez [ENONCE_TD08.md](ENONCE_TD08.md), puis complétez les TODO dans
`slrresearch/quality_agent.py` et `slrresearch/orchestrator.py`.

Après réalisation :

```bash
python3 main.py
python3 -m streamlit run streamlit_app.py
```
