from pathlib import Path

import streamlit as st

from slrresearch.td08_runtime import load_td08_artifacts

st.set_page_config(page_title="TD08 — QualityAgent et orchestration", page_icon=":material/fact_check:", layout="wide")
ROOT = Path(__file__).parent
evidence, required_rqs, draft, repaired = load_td08_artifacts(ROOT)

st.title("TD08 — QualityAgent et orchestration")
st.warning("Complétez les TODO avant de lancer les expériences.")
st.write("Partie I : QualityAgent. Partie II : pipeline fixe et Supervisor–Workers.")
with st.container(border=True):
    st.metric("Preuves TD06", len(evidence))
    st.metric("Questions de recherche", len(required_rqs))
    st.caption("L'artefact de rédaction vient du TD07. Une affirmation volontairement insuffisante doit être détectée.")

st.header("Phase 1 — QualityAgent")
st.markdown("""
Commencez par compléter les TODO 1 à 6. Cette phase doit afficher :

- le QualityAgent décompose la note en affirmations ;
- il vérifie les citations et l'ancrage dans les preuves ;
- il retourne ACCEPT, REVISE ou ESCALATE ;
- un verdict ACCEPT, REVISE ou ESCALATE.
""")

with st.form("demo", border=True):
    budget = st.slider("Budget de handoffs", 5, 10, 8)
    run = st.form_submit_button("Lancer après avoir complété les TODO", type="primary")
if run:
    st.info("Après les TODO 1 à 5, cette phase affichera les affirmations, les preuves, le score et le feedback.")
    st.warning("Si l'exécution échoue, relisez les fonctions indiquées dans ENONCE_TD08.md.")

st.header("Phase 2 — Orchestration multi-agent")
st.info("Cette phase doit être lancée seulement après la phase 1. Elle comparera le pipeline fixe au superviseur avec routage.")
st.markdown("""
Après les TODO 6 à 8, vous devrez afficher :

- la chaîne Search → Screening → RAG → Writing → Quality ;
- les handoffs autorisés ou refusés ;
- l'état partagé ;
- un journal d'exécution indiquant quel agent a produit quel artefact ;
- les transitions writing→quality, quality→rag et rag→writing ;
- le budget et la condition d'arrêt.
""")
