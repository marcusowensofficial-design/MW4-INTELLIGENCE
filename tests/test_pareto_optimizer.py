"""
Unit tests for Multi-Objective Pareto-Frontier Build Optimizer.
"""

import pytest
from src.database.models import EvaluatedBuildStats
from src.engines.pareto_optimizer import is_dominated, compute_pareto_frontier


def create_mock_evaluated_build(
    label: str,
    pet: float,
    recoil: float,
    mobility: float,
    range_mult: float
) -> EvaluatedBuildStats:
    return EvaluatedBuildStats(
        weapon_id="test_weapon",
        weapon_name="Test Weapon",
        build_label=label,
        game_version_id="v1",
        ruleset_id="core",
        attachment_ids=[],
        attachments_applied=[],
        effective_rpm=750.0,
        effective_ads_ms=230.0,
        effective_sprint_to_fire_ms=200.0,
        effective_bullet_velocity_mps=700.0,
        effective_reload_empty_s=2.4,
        effective_reload_tactical_s=1.8,
        effective_recoil_horizontal=15.0,
        effective_recoil_vertical=20.0,
        effective_hipfire_spread_deg=3.0,
        effective_move_speed_mps=4.8,
        effective_ads_move_speed_mps=2.9,
        effective_mag_size=30,
        range_multiplier=range_mult,
        close_ttk_ms=240.0,
        mid_ttk_ms=320.0,
        long_ttk_ms=400.0,
        close_pet_ms=pet,
        mid_pet_ms=pet,
        balance_score=80.0,
        recoil_index=recoil,
        mobility_index=mobility
    )


def test_pareto_strict_domination():
    # Build A is strictly superior to Build B across all metrics
    build_a = create_mock_evaluated_build("Build A (Superior)", pet=600.0, recoil=15.0, mobility=90.0, range_mult=1.2)
    build_b = create_mock_evaluated_build("Build B (Inferior)", pet=700.0, recoil=25.0, mobility=80.0, range_mult=1.0)

    # Build A dominates Build B
    assert is_dominated(candidate=build_b, other=build_a) is True
    # Build B does NOT dominate Build A
    assert is_dominated(candidate=build_a, other=build_b) is False


def test_pareto_tradeoff_non_domination():
    # Build A has faster kill time (PET=580), but higher recoil (recoil=30)
    # Build C has slower kill time (PET=650), but laser recoil (recoil=12)
    build_a = create_mock_evaluated_build("Fast CQB", pet=580.0, recoil=30.0, mobility=90.0, range_mult=1.0)
    build_c = create_mock_evaluated_build("Laser Beam", pet=650.0, recoil=12.0, mobility=75.0, range_mult=1.2)

    # Neither should dominate the other
    assert is_dominated(candidate=build_a, other=build_c) is False
    assert is_dominated(candidate=build_c, other=build_a) is False


def test_pareto_frontier_extraction():
    build_a = create_mock_evaluated_build("Build A", pet=580.0, recoil=30.0, mobility=90.0, range_mult=1.0)
    build_b = create_mock_evaluated_build("Build B (Dominated by A)", pet=700.0, recoil=35.0, mobility=80.0, range_mult=0.9)
    build_c = create_mock_evaluated_build("Build C", pet=650.0, recoil=12.0, mobility=75.0, range_mult=1.2)

    candidates = [build_a, build_b, build_c]
    pareto_front, all_pts = compute_pareto_frontier(candidates)

    pareto_labels = [p.build_label for p in pareto_front]
    assert "Build A" in pareto_labels
    assert "Build C" in pareto_labels
    assert "Build B (Dominated by A)" not in pareto_labels
    assert len(pareto_front) == 2
