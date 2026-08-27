"""
MW4 Weapon Intelligence Lab - Plotly Chart Visualizations
High-performance interactive analytical charts for TTK, Practical Engagement Time,
Pareto frontier tradeoffs, balance radar, and damage hitbox profiles.
"""

from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from ..database.models import TTKCalculationResult, PracticalEngagementResult, ParetoBuildPoint, BalanceScoreBreakdown


DARK_LAYOUT = dict(
    paper_bgcolor="rgba(11, 14, 20, 0.9)",
    plot_bgcolor="rgba(15, 23, 42, 0.6)",
    font=dict(color="#cbd5e1", family="Inter, sans-serif"),
    xaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.1)",
        zerolinecolor="rgba(148, 163, 184, 0.2)"
    ),
    yaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.1)",
        zerolinecolor="rgba(148, 163, 184, 0.2)"
    ),
    legend=dict(
        bgcolor="rgba(15, 23, 42, 0.7)",
        bordercolor="rgba(56, 189, 248, 0.2)",
        borderwidth=1
    ),
    margin=dict(l=40, r=30, t=40, b=40)
)

TACTICAL_COLORS = [
    "#38bdf8",  # Sky Cyan
    "#4ade80",  # Neon Green
    "#fb923c",  # Amber Orange
    "#f43f5e",  # Rose Red
    "#a855f7",  # Purple
    "#facc15",  # Yellow
    "#e879f9",  # Pink
]


def create_multi_ttk_curve_chart(
    results: List[TTKCalculationResult],
    title: str = "Theoretical Time-To-Kill (TTK) vs Distance",
    use_impact_ttk: bool = False
) -> go.Figure:
    """
    Renders multi-weapon continuous TTK vs distance step curve comparison.
    Supports toggling between Theoretical Fire TTK and True Impact TTK (with bullet travel time).
    """
    fig = go.Figure()

    for idx, r in enumerate(results):
        color = TACTICAL_COLORS[idx % len(TACTICAL_COLORS)]
        x_vals = [p.distance_m for p in r.curve_points]
        y_vals = [p.impact_ttk_ms if use_impact_ttk else p.ttk_ms for p in r.curve_points]
        
        if use_impact_ttk:
            custom_text = [
                f"<b>{r.weapon_name}</b><br>Dist: {p.distance_m}m<br>Impact TTK: {p.impact_ttk_ms}ms (Fire: {p.ttk_ms}ms + Flight: {p.bullet_travel_time_ms}ms)<br>STK: {p.shots_to_kill}<br>Dmg: {p.damage_per_shot}"
                for p in r.curve_points
            ]
        else:
            custom_text = [
                f"<b>{r.weapon_name}</b><br>Dist: {p.distance_m}m<br>TTK: {p.ttk_ms}ms<br>STK: {p.shots_to_kill}<br>Dmg: {p.damage_per_shot}"
                for p in r.curve_points
            ]

        obd_label = f" | OBD: {int(r.open_bolt_delay_ms)}ms" if r.open_bolt_delay_ms > 0 else ""
        line_shape = "linear" if use_impact_ttk else "hv"

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                line=dict(shape=line_shape, width=3, color=color),
                name=f"{r.weapon_name} ({r.rpm} RPM{obd_label})",
                hovertext=custom_text,
                hoverinfo="text"
            )
        )

    y_axis_label = "Impact Time-To-Kill with Flight Time (ms)" if use_impact_ttk else "Theoretical Fire TTK (ms)"

    fig.update_layout(
        title=f"<b>{title}</b>",
        xaxis_title="Distance (Meters)",
        yaxis_title=y_axis_label,
        hovermode="x unified",
        **DARK_LAYOUT
    )
    return fig


def create_practical_engagement_stacked_chart(
    results: List[PracticalEngagementResult],
    title: str = "Practical Engagement Time Breakdown (Sprint Encounter at 15m)"
) -> go.Figure:
    """
    Renders stacked horizontal bar chart breaking down PET components:
    Reaction + ADS + Sprint to Fire + Theoretical TTK + Expected Miss Penalty.
    """
    fig = go.Figure()

    names = [r.weapon_name for r in results]
    reaction = [r.reaction_ms for r in results]
    stf = [r.sprint_to_fire_ms for r in results]
    ads = [r.ads_ms for r in results]
    ttk = [r.theoretical_ttk_ms for r in results]
    miss = [r.expected_miss_penalty_ms for r in results]

    fig.add_trace(go.Bar(name="Reaction Latency", y=names, x=reaction, orientation='h', marker_color="#64748b"))
    fig.add_trace(go.Bar(name="Sprint-To-Fire", y=names, x=stf, orientation='h', marker_color="#f97316"))
    fig.add_trace(go.Bar(name="ADS Transition", y=names, x=ads, orientation='h', marker_color="#38bdf8"))
    fig.add_trace(go.Bar(name="Theoretical TTK", y=names, x=ttk, orientation='h', marker_color="#ef4444"))
    fig.add_trace(go.Bar(name="Miss Penalty (Accuracy)", y=names, x=miss, orientation='h', marker_color="#eab308"))

    fig.update_layout(
        barmode="stack",
        title=f"<b>{title}</b>",
        xaxis_title="Total Practical Engagement Latency (Milliseconds - Lower is Better)",
        yaxis_title="Weapon / Build",
        **DARK_LAYOUT
    )
    return fig


def create_pareto_scatter_chart(
    points: List[ParetoBuildPoint],
    title: str = "Pareto Frontier: Practical Engagement Time vs Recoil Stability"
) -> go.Figure:
    """
    Renders 2D scatter chart highlighting the non-dominated Pareto frontier builds in neon green.
    """
    fig = go.Figure()

    # Non-optimal builds
    sub_optimal = [p for p in points if not p.is_pareto_optimal]
    if sub_optimal:
        fig.add_trace(
            go.Scatter(
                x=[p.recoil_index for p in sub_optimal],
                y=[p.practical_engagement_ms for p in sub_optimal],
                mode="markers",
                marker=dict(size=7, color="rgba(148, 163, 184, 0.4)", symbol="circle"),
                name="Dominated Builds",
                hovertext=[
                    f"<b>{p.build_label}</b><br>Recoil Index: {p.recoil_index}<br>PET: {p.practical_engagement_ms}ms<br>ADS: {p.effective_ads_ms}ms<br>Attachments: {', '.join(p.attachment_names)}"
                    for p in sub_optimal
                ],
                hoverinfo="text"
            )
        )

    # Pareto Optimal Builds
    optimal = [p for p in points if p.is_pareto_optimal]
    if optimal:
        fig.add_trace(
            go.Scatter(
                x=[p.recoil_index for p in optimal],
                y=[p.practical_engagement_ms for p in optimal],
                mode="markers+lines",
                marker=dict(size=11, color="#4ade80", symbol="star", line=dict(width=1, color="#ffffff")),
                line=dict(color="#22c55e", width=2, dash="dot"),
                name="🏆 Pareto Frontier (Non-Dominated)",
                hovertext=[
                    f"<b>⭐ {p.build_label}</b><br>Recoil Index: {p.recoil_index}<br>PET: {p.practical_engagement_ms}ms<br>ADS: {p.effective_ads_ms}ms<br>Attachments: {', '.join(p.attachment_names)}"
                    for p in optimal
                ],
                hoverinfo="text"
            )
        )

    fig.update_layout(
        title=f"<b>{title}</b>",
        xaxis_title="Recoil Index (Lower = Less Recoil)",
        yaxis_title="Practical Engagement Time ms (Lower = Faster Kill)",
        **DARK_LAYOUT
    )
    return fig


def create_balance_radar_chart(
    score_breakdown: BalanceScoreBreakdown,
    title: Optional[str] = None
) -> go.Figure:
    """
    Renders radar chart showing normalized 0-100 scores across 6 balance dimensions.
    """
    categories = [
        "CQB TTK",
        "Mid-Range TTK",
        "Long-Range TTK",
        "Handling (ADS/STF)",
        "Recoil Stability",
        "Sustainability (Mag/Reload)"
    ]
    values = [
        score_breakdown.cqb_ttk_score,
        score_breakdown.mid_ttk_score,
        score_breakdown.long_ttk_score,
        score_breakdown.handling_score,
        score_breakdown.recoil_score,
        score_breakdown.sustainability_score
    ]
    # Close the radar polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(56, 189, 248, 0.25)',
            line=dict(color='#38bdf8', width=2),
            name=score_breakdown.weapon_name
        )
    )

    chart_title = title or f"<b>Balance Profile: {score_breakdown.weapon_name} (Score: {score_breakdown.composite_balance_score}/100 - Tier {score_breakdown.tier_rating})</b>"

    fig.update_layout(
        title=chart_title,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(148, 163, 184, 0.2)",
                tickfont=dict(color="#94a3b8", size=10)
            ),
            angularaxis=dict(
                gridcolor="rgba(148, 163, 184, 0.2)",
                tickfont=dict(color="#f8fafc", size=12)
            ),
            bgcolor="rgba(15, 23, 42, 0.6)"
        ),
        paper_bgcolor="rgba(11, 14, 20, 0.9)",
        font=dict(color="#cbd5e1", family="Inter, sans-serif"),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def create_recoil_spray_comparison_chart(
    base_result: Any,
    build_result: Optional[Any] = None,
    distance_m: float = 10.0
) -> go.Figure:
    """
    Renders 2D target canvas comparing Base Weapon spray vs 5-Attachment Build spray.
    X-axis = Horizontal deviation (cm), Y-axis = Vertical climb (cm).
    """
    fig = go.Figure()

    # Target concentric rings for visual frame of reference
    for r_cm in [10, 25, 50, 75]:
        fig.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=-r_cm, y0=-r_cm, x1=r_cm, y1=r_cm,
            line=dict(color="rgba(148, 163, 184, 0.15)", width=1, dash="dot"),
            fillcolor="rgba(0,0,0,0)"
        )

    # Base weapon trajectory
    bx = [imp.x_offset_cm for imp in base_result.impacts]
    by = [imp.y_offset_cm for imp in base_result.impacts]
    b_hover = [
        f"<b>Base {base_result.weapon_name}</b><br>Shot #{imp.shot_number}<br>X: {imp.x_offset_cm}cm<br>Y: +{imp.y_offset_cm}cm<br>Time: {imp.time_ms}ms"
        for imp in base_result.impacts
    ]

    fig.add_trace(
        go.Scatter(
            x=bx, y=by,
            mode="lines+markers+text",
            line=dict(color="#f43f5e", width=2, dash="dot"),
            marker=dict(size=8, color="#f43f5e", symbol="circle"),
            name=f"Naked Baseline (Climb: {base_result.max_vertical_climb_cm}cm)",
            hovertext=b_hover,
            hoverinfo="text"
        )
    )

    if build_result:
        cx = [imp.x_offset_cm for imp in build_result.impacts]
        cy = [imp.y_offset_cm for imp in build_result.impacts]
        c_hover = [
            f"<b>5-Attachment Build</b><br>Shot #{imp.shot_number}<br>X: {imp.x_offset_cm}cm<br>Y: +{imp.y_offset_cm}cm<br>Time: {imp.time_ms}ms"
            for imp in build_result.impacts
        ]

        vert_red = round((1.0 - (build_result.max_vertical_climb_cm / max(0.1, base_result.max_vertical_climb_cm))) * 100.0, 1)

        fig.add_trace(
            go.Scatter(
                x=cx, y=cy,
                mode="lines+markers+text",
                line=dict(color="#38bdf8", width=3),
                marker=dict(size=9, color="#38bdf8", symbol="diamond"),
                name=f"Custom Build (Climb: {build_result.max_vertical_climb_cm}cm • {vert_red:+.1f}%)",
                hovertext=c_hover,
                hoverinfo="text"
            )
        )

    # Bullseye center crosshair
    fig.add_trace(
        go.Scatter(
            x=[0], y=[0],
            mode="markers",
            marker=dict(size=14, color="#4ade80", symbol="cross"),
            name="Point of Aim (Center)",
            hoverinfo="name"
        )
    )

    fig.update_layout(
        title=f"<b>2D Wall Recoil Spray Pattern Simulation at {distance_m:.0f}m (30-Round Mag)</b>",
        xaxis_title="Horizontal Deflection (cm)",
        yaxis_title="Vertical Climb (cm)",
        hovermode="closest",
        **DARK_LAYOUT
    )
    fig.update_xaxes(
        range=[-60, 60],
        gridcolor="rgba(148, 163, 184, 0.1)",
        zerolinecolor="rgba(148, 163, 184, 0.3)"
    )
    fig.update_yaxes(
        range=[-10, 90],
        gridcolor="rgba(148, 163, 184, 0.1)",
        zerolinecolor="rgba(148, 163, 184, 0.3)"
    )
    return fig


def create_duel_timeline_chart(duel_result: Any) -> go.Figure:
    """
    Renders step-by-step health depletion chart over time in a 1v1 shootout.
    """
    fig = go.Figure()

    # Track HP changes over time
    a_name = duel_result.combat_log[0].shooter_name if duel_result.combat_log else "Combatant A"
    b_name = duel_result.combat_log[0].target_name if duel_result.combat_log else "Combatant B"

    # Compile HP timelines
    t_vals_a = [0.0]
    hp_vals_a = [duel_result.target_health]
    t_vals_b = [0.0]
    hp_vals_b = [duel_result.target_health]

    for ev in duel_result.combat_log:
        if ev.target_name == a_name:
            t_vals_a.append(ev.timestamp_ms)
            hp_vals_a.append(ev.target_hp_remaining)
        else:
            t_vals_b.append(ev.timestamp_ms)
            hp_vals_b.append(ev.target_hp_remaining)

    fig.add_trace(
        go.Scatter(
            x=t_vals_a, y=hp_vals_a,
            mode="lines+markers",
            line=dict(shape="hv", width=3, color="#38bdf8"),
            name=f"{a_name} HP"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=t_vals_b, y=hp_vals_b,
            mode="lines+markers",
            line=dict(shape="hv", width=3, color="#fb923c"),
            name=f"{b_name} HP"
        )
    )

    fig.update_layout(
        title=f"<b>1v1 Shootout Health Depletion Timeline ({duel_result.distance_m:.0f}m)</b>",
        xaxis_title="Time Elapsed (Milliseconds)",
        yaxis_title="Remaining Health (HP)",
        hovermode="x unified",
        **DARK_LAYOUT
    )
    return fig
