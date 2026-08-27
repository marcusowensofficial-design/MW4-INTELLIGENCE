"""
MW4 Weapon Intelligence Lab - Streamlit State Management
Thread-safe session state caching and global selectors for Game Version and Ruleset.
"""

import streamlit as st
from typing import Tuple, List, Optional
from ..database.connection import db_manager, DatabaseManager
from ..database.repository import IntelligenceRepository
from ..database.models import GameVersion, Ruleset


def get_shared_repository() -> IntelligenceRepository:
    """Returns a singleton IntelligenceRepository backed by the primary DuckDB instance."""
    db_manager.init_database()
    return IntelligenceRepository(db_manager)


def init_session_state() -> IntelligenceRepository:
    """Initializes global session state variables (version, ruleset, filters)."""
    repo = get_shared_repository()

    # Load available versions & rulesets
    if "available_versions" not in st.session_state:
        versions = repo.get_game_versions()
        st.session_state["available_versions"] = [v.version_id for v in versions] or ["v1.1.0-launch"]

    if "selected_version" not in st.session_state:
        active = repo.get_active_game_version()
        st.session_state["selected_version"] = active.version_id if active else "v1.1.0-launch"

    if "available_rulesets" not in st.session_state:
        rulesets = repo.get_rulesets()
        st.session_state["available_rulesets"] = [r.ruleset_id for r in rulesets] or ["core", "hardcore"]

    if "selected_ruleset" not in st.session_state:
        st.session_state["selected_ruleset"] = "core"

    return repo


def render_sidebar_controls(repo: IntelligenceRepository) -> Tuple[str, str, Ruleset]:
    """
    Renders standard sidebar selectors for Game Version and Ruleset.
    Ensures version and ruleset state changes propagate globally.
    """
    st.sidebar.markdown("### 🎛️ Global Intelligence Scope")

    versions = repo.get_game_versions()
    version_ids = [v.version_id for v in versions] or ["v1.1.0-launch"]
    curr_ver_idx = version_ids.index(st.session_state["selected_version"]) if st.session_state["selected_version"] in version_ids else 0

    selected_ver = st.sidebar.selectbox(
        "Select Game Patch Version",
        options=version_ids,
        index=curr_ver_idx,
        help="All calculations and stats are versioned. Past stats are never overwritten."
    )
    st.session_state["selected_version"] = selected_ver

    rulesets = repo.get_rulesets()
    ruleset_ids = [r.ruleset_id for r in rulesets] or ["core", "hardcore"]
    curr_rs_idx = ruleset_ids.index(st.session_state["selected_ruleset"]) if st.session_state["selected_ruleset"] in ruleset_ids else 0

    selected_rs_id = st.sidebar.selectbox(
        "Combat Ruleset",
        options=ruleset_ids,
        index=curr_rs_idx,
        format_func=lambda x: f"🛡️ {x.upper()} ({30 if x == 'hardcore' else 100} HP)",
        help="Core (100 HP) and Hardcore (30 HP) are completely independent rulesets."
    )
    st.session_state["selected_ruleset"] = selected_rs_id

    active_ruleset = repo.get_ruleset(selected_rs_id) or Ruleset(ruleset_id="core", name="Core 100 HP", target_health=100.0)

    st.sidebar.markdown("---")
    st.sidebar.caption("⚡ **MW4 Intel Lab v2.0-Alpha**")
    st.sidebar.caption("🔒 Local-First DuckDB • No Memory Hooks")

    return selected_ver, selected_rs_id, active_ruleset
