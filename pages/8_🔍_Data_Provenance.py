"""
MW4 Weapon Intelligence Lab - Data Provenance & Evidence Explorer
Searchable audit trail tracking the exact source URL, test methodology, and confidence
rating behind every weapon stat and attachment modifier in Modern Warfare 4.
"""

import os
import yaml
import streamlit as st
import pandas as pd
from src.ui.theme import render_page_header
from src.ui.state import init_session_state, render_sidebar_controls
from src.database.models import SourceTier, VerificationStatus


st.set_page_config(page_title="Data Provenance - MW4 Intel", page_icon="🔍", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="🔍 Data Provenance & Evidence Explorer",
    subtitle="The Definitive Source Audit Trail & Provenance Ledger for Every Gun & Stat in MW4",
    active_version=selected_ver,
    active_ruleset=selected_rs_id
)

all_evidence = repo.get_evidence_ledger()
weapons = repo.get_weapons()

# Summary Metrics
t1_count = sum(1 for e in all_evidence if e.source_tier == SourceTier.TIER_1)
t2_count = sum(1 for e in all_evidence if e.source_tier == SourceTier.TIER_2)
avg_conf = (sum(e.confidence_score for e in all_evidence) / len(all_evidence) * 100.0) if all_evidence else 100.0

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Evidence Receipts", len(all_evidence))
with m2:
    st.metric("Tier 1 Official Citations", t1_count)
with m3:
    st.metric("Tier 2 Frame-Count Logs", t2_count)
with m4:
    st.metric("Average Confidence Score", f"{avg_conf:.1f}%")

st.markdown("---")

tab_ledger, tab_hierarchy = st.tabs([
    "📜 Searchable Evidence Receipts Ledger",
    "⚖️ Pro Truth Hierarchy & Registered Sources"
])

# ---------------------------------------------------------------------------
# TAB 1: Searchable Evidence Receipts Ledger
# ---------------------------------------------------------------------------
with tab_ledger:
    st.markdown("### 📜 Verified Evidence Receipts")
    st.caption("Every numerical stat in the database retains full provenance tracking, methodology, and confidence scoring.")

    c_tier_f, c_entity_f, c_search = st.columns([1, 1, 2])
    with c_tier_f:
        tier_opts = ["All Tiers"] + [t.value.upper() for t in SourceTier]
        chosen_tier = st.selectbox("Filter by Source Tier", options=tier_opts)
    with c_entity_f:
        entity_opts = ["All Entities"] + sorted(list({e.target_entity_type for e in all_evidence}))
        chosen_entity = st.selectbox("Filter by Entity Type", options=entity_opts)
    with c_search:
        search_query = st.text_input("🔍 Search by Weapon ID, Stat Field, or Source Name", value="")

    filtered_ev = all_evidence
    if chosen_tier != "All Tiers":
        filtered_ev = [e for e in filtered_ev if e.source_tier.value.upper() == chosen_tier]
    if chosen_entity != "All Entities":
        filtered_ev = [e for e in filtered_ev if e.target_entity_type == chosen_entity]
    if search_query.strip():
        q = search_query.lower().strip()
        filtered_ev = [
            e for e in filtered_ev
            if q in e.target_entity_id.lower() or q in e.field_name.lower() or q in e.source_name.lower() or q in (e.notes or "").lower()
        ]

    if filtered_ev:
        ev_table_rows = [
            {
                "Evidence ID": e.evidence_id,
                "Target Entity": f"{e.target_entity_type} ({e.target_entity_id})",
                "Field": e.field_name,
                "Observed Value": e.observed_value,
                "Tier": e.source_tier.value.upper(),
                "Source Name": e.source_name,
                "Methodology": e.test_method,
                "Status": e.verification_status.value.upper(),
                "Confidence": f"{int(e.confidence_score*100)}%",
                "Captured Date": e.captured_timestamp[:10],
                "Source URL": e.source_url
            }
            for e in filtered_ev
        ]
        df_ev = pd.DataFrame(ev_table_rows)
        st.dataframe(df_ev, use_container_width=True, hide_index=True)

        csv_ev = df_ev.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Evidence Audit Ledger CSV",
            data=csv_ev,
            file_name="mw4_evidence_ledger_audit.csv",
            mime="text/csv"
        )
    else:
        st.info("No evidence entries matching the selected filters.")


# ---------------------------------------------------------------------------
# TAB 2: Source Truth Hierarchy & Registered Sources
# ---------------------------------------------------------------------------
with tab_hierarchy:
    st.markdown("### ⚖️ Source Truth Hierarchy & Confidence Standards")

    st.markdown(
        """
        | Source Tier | Verification Standard | Base Confidence | Ingestion Policy |
        | :--- | :--- | :--- | :--- |
        | **Tier 1: Official Patch Notes** | Direct Activision / Infinity Ward first-party release notes & developer blogs. | **98% - 100%** | Auto-verified via guardrails into DuckDB. |
        | **Tier 2: Controlled Measured Tests** | 240fps/120fps frame-by-frame video capture testing in private matches with fixed distance markers. | **92% - 95%** | Auto-verified with empirical test methodology audit. |
        | **Tier 3: Reproducible Public Testing** | Community repositories (Sym.gg / TrueGameData / JGOD / CODMunity) with corroborating datasets. | **78% - 88%** | Accepted with cross-validation. |
        | **Tier 4: Community Leads & AI Drafts** | Unverified community rumors, automated screenshot OCR drafts, or AI extractions. | **40% - 65%** | Tagged as `[UNVERIFIED DATA]` with 0% delta until confirmed. |
        """
    )

    st.markdown("---")
    st.markdown("#### 🌐 Registered Pro Sources & Testing Repositories")

    reg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs", "source_registry.yaml")
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            src_cfg = yaml.safe_load(f)
            reg_sources = src_cfg.get("registered_sources", [])
            if reg_sources:
                src_df = pd.DataFrame([
                    {
                        "Source Name": s.get("name"),
                        "Tier": s.get("tier", "").upper(),
                        "Test Methodology": s.get("test_method"),
                        "Source URL": s.get("url")
                    }
                    for s in reg_sources
                ])
                st.dataframe(src_df, use_container_width=True, hide_index=True)
