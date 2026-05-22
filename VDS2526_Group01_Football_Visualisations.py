# VDS2526 — Group 1 | Football Dataset

# Mansoor Khurram (2505888)
# Murtaza Javed (2501823)
# Muhammad Shoaib (2501708)
# Yogesh Tarachand More (2469856)


# %% CELL 1: Install & Imports

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"
print("Libraries imported successfully.")


# %% CELL 2: Load Datasets

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "data")

match       = pd.read_csv(os.path.join(data_path, "Match.csv"))
league      = pd.read_csv(os.path.join(data_path, "League.csv"))
team_attr   = pd.read_csv(os.path.join(data_path, "Team_Attributes.csv"))
player_attr = pd.read_csv(os.path.join(data_path, "Player_Attributes.csv"))
pos_ref     = pd.read_csv(os.path.join(data_path, "PositionReference.csv"))
team        = pd.read_csv(os.path.join(data_path, "Team.csv"))

print(f"Match:             {match.shape}")
print(f"League:            {league.shape}")
print(f"Team_Attributes:   {team_attr.shape}")
print(f"Player_Attributes: {player_attr.shape}")
print(f"PositionReference: {pos_ref.shape}")
print(f"Team:              {team.shape}")


# ════════════════════════════════════════════════════════════
# Stacked Bar Chart: Match Outcomes Across Leagues
# Created by: Mansoor Khurram - 2505888
# Research Question: Q1 / Task T1.1
# ════════════════════════════════════════════════════════════


# %% CELL 3: Data Preparation For Plot 1: Match Outcomes per League

# Combine match and league data
df_viz1 = match.merge(league[["id", "name"]], left_on="league_id", right_on="id")

home_goals = df_viz1["home_team_goal"].values
away_goals = df_viz1["away_team_goal"].values

outcomes = []
for h, a in zip(home_goals, away_goals):
    if h > a:
        outcomes.append("Home Win")
    elif h < a:
        outcomes.append("Away Win")
    else:
        outcomes.append("Draw")

df_viz1["outcome"] = outcomes

outcome_counts = df_viz1.groupby(["name", "outcome"]).size().reset_index(name="match_count")

# Calculate the % for bars
total_matches = outcome_counts.groupby("name")["match_count"].transform("sum")
outcome_counts["percentage"] = (outcome_counts["match_count"] / total_matches) * 100

# Sort the leagues by most Home Wins
home_wins_only = outcome_counts[outcome_counts["outcome"] == "Home Win"]
sorted_home_wins = home_wins_only.sort_values("percentage", ascending=False)
hw_order = sorted_home_wins["name"].tolist()


# %% CELL 4: Plot 1

color_map = {
    "Home Win": "#2980b9",
    "Draw":     "#95a5a6",
    "Away Win": "#e74c3c",
}

fig1 = px.bar(
    outcome_counts,
    x="name",
    y="percentage",
    color="outcome",
    color_discrete_map=color_map,
    category_orders={
        "name": hw_order,
        "outcome": ["Home Win", "Draw", "Away Win"],
    },
    title="Q1 - Match Outcomes Across 11 European Leagues (2008–2016)",
    labels={
        "name": "League",
        "percentage": "Match Outcome (%)",
        "outcome": "Result",
        "match_count": "Number of Matches",
    },
    hover_data={"match_count": True, "percentage": ":.1f"},
    barmode="stack",
    template="plotly_white",
)

fig1.update_layout(
    xaxis_tickangle=-35,
    xaxis_title="League",
    yaxis_title="Percentage of Matches (%)",
    legend_title="Match Result",
    height=520,
)

top_league = hw_order[0]
top_hw_pct = outcome_counts[
    (outcome_counts["name"] == top_league) & (outcome_counts["outcome"] == "Home Win")
]["percentage"].values[0]

fig1.add_annotation(
    x=top_league,
    y=top_hw_pct / 2,
    text=f"Highest home wins<br>{top_hw_pct:.1f}%",
    showarrow=True,
    arrowhead=2,
    font=dict(size=10, color="white"),
    bgcolor="#2980b9",
    bordercolor="white",
)

fig1.show()
fig1.write_html("viz1_match_outcomes.html")


# ════════════════════════════════════════════════════════════
# Scatter Plot: Tactical Attributes vs Goal Difference
# Created by: Yogesh More
# Research Questions: Q1 / Tasks T1.2, T1.3
#
# PEER FEEDBACK FIX:
#   - Y-axis = season goal difference (from Match.csv)
#     NOT chanceCreationShooting (original code was tactics vs tactics)
#   - Aggregated to team-season level (~1,458 pts, not 25,979)
#   - Colour = performance tier (Top 4 / Mid / Bottom 4)
#   - OLS trendline added
# ════════════════════════════════════════════════════════════


# %%── CELL 5: Data Preparation ─────────────────────────────────

# Step 1: Season goal difference per team (home + away combined)
home_gd = match.groupby(["home_team_api_id", "season"]).agg(
    scored=("home_team_goal", "sum"),
    conceded=("away_team_goal", "sum")
).reset_index().rename(columns={
    "home_team_api_id": "team_api_id",
    "scored": "h_scored",
    "conceded": "h_conceded"
})

away_gd = match.groupby(["away_team_api_id", "season"]).agg(
    scored=("away_team_goal", "sum"),
    conceded=("home_team_goal", "sum")
).reset_index().rename(columns={
    "away_team_api_id": "team_api_id",
    "scored": "a_scored",
    "conceded": "a_conceded"
})

team_season = home_gd.merge(away_gd, on=["team_api_id", "season"])
team_season["goal_diff"] = (
    (team_season["h_scored"] + team_season["a_scored"]) -
    (team_season["h_conceded"] + team_season["a_conceded"])
)

# Step 2: Add league info
match_lg = match[["home_team_api_id", "league_id", "season"]].drop_duplicates()
match_lg.columns = ["team_api_id", "league_id", "season"]
team_season = team_season.merge(match_lg, on=["team_api_id", "season"])

# Step 3: Derive Top 4 / Bottom 4 tier per league per season (T1.3)
team_season["rank"] = team_season.groupby(["league_id", "season"])["goal_diff"].rank(
    ascending=False, method="min"
)
n_teams = team_season.groupby(["league_id", "season"])["team_api_id"].transform("count")
team_season["tier"] = np.where(
    team_season["rank"] <= 4, "Top 4",
    np.where(team_season["rank"] > n_teams - 4, "Bottom 4", "Mid")
)

# Step 4: Join tactical attributes (average per team per year)
team_attr["year"] = pd.to_datetime(team_attr["date"], errors="coerce").dt.year
team_season["year"] = team_season["season"].str[:4].astype(int)

tactic_cols = ["buildUpPlaySpeed", "chanceCreationShooting",
               "defencePressure", "defenceAggression"]
ta_agg = team_attr.groupby(["team_api_id", "year"])[tactic_cols].mean().reset_index()

df_viz2 = team_season.merge(ta_agg, on=["team_api_id", "year"], how="inner")
df_viz2 = df_viz2.merge(league[["id", "name"]], left_on="league_id", right_on="id", how="left")
df_viz2 = df_viz2.merge(team[["team_api_id", "team_long_name"]], on="team_api_id", how="left")

# print(f"Viz 2 data ready — {len(df_viz2)} team-season records.")
# print(f"Tier distribution:\n{df_viz2['tier'].value_counts()}")


# %% CELL 6: Plot 2

tier_colors = {
    "Top 4":    "#27ae60",  # Green  — successful teams
    "Mid":      "#bdc3c7",  # Grey   — mid-table
    "Bottom 4": "#e74c3c",  # Red    — struggling teams
}

fig2 = px.scatter(
    df_viz2,
    x="buildUpPlaySpeed",
    y="goal_diff",
    color="tier",
    color_discrete_map=tier_colors,
    category_orders={"tier": ["Top 4", "Mid", "Bottom 4"]},
    opacity=0.55,
    trendline="ols",
    hover_data={
        "team_long_name": True,
        "name": True,
        "season": True,
        "goal_diff": True,
        "buildUpPlaySpeed": True,
    },
    labels={
        "buildUpPlaySpeed": "Build-Up Play Speed",
        "goal_diff": "Season Goal Difference",
        "tier": "Performance Tier",
        "team_long_name": "Team",
        "name": "League",
        "season": "Season",
    },
    title="Q1 — Build-Up Play Speed vs Season Goal Difference (Team-Season Level)",
    template="plotly_white",
)

fig2.update_layout(
    xaxis_title="Build-Up Play Speed (Tactical Attribute)",
    yaxis_title="Season Goal Difference",
    legend_title="Performance Tier",
    height=540,
    title_font_size=15,
    hovermode="closest",
)

# Horizontal reference at Goal Diff = 0
fig2.add_hline(
    y=0, line_dash="dash", line_color="black", line_width=1,
    annotation_text="Break-even line (Goal Diff = 0)",
    annotation_position="bottom right",
)

fig2.show()
fig2.write_html("viz2_tactics_vs_success.html")

# NOTE: To explore other tactical attributes, re-run with:
#   x="chanceCreationShooting"
#   x="defencePressure"
#   x="defenceAggression"


# ════════════════════════════════════════════════════════════
# Multi-Line Chart: Player Skill Evolution 2008–2016
# Created by: Murtaza
# Research Question: Q2 / Tasks T2.1 + T2.2
#
# PEER FEEDBACK FIX:
#   - Reduced to exactly 6 representative skills (one per category)
#     as specified in the design report operationalisation
#   - GK skills completely removed (they skew averages)
#   - Year range filtered strictly to 2008–2016
#   - Annotation on peak / largest change
# ════════════════════════════════════════════════════════════


# %% CELL 7: Data Preparation

player_attr["date"] = pd.to_datetime(player_attr["date"], errors="coerce")
player_attr["year"] = player_attr["date"].dt.year

# 6 skills — one per category (operationalisation note in design report)
skill_cols = [
    "sprint_speed",     # Speed / Pace category
    "short_passing",    # Passing category
    "finishing",        # Shooting / Attacking category
    "standing_tackle",  # Defending category
    "stamina",          # Physical category
    "dribbling",        # Technical / Dribbling category
]

skill_labels = {
    "sprint_speed":    "Sprint Speed (Speed)",
    "short_passing":   "Short Passing (Passing)",
    "finishing":       "Finishing (Shooting)",
    "standing_tackle": "Standing Tackle (Defending)",
    "stamina":         "Stamina (Physical)",
    "dribbling":       "Dribbling (Technical)",
}

pa_clean = player_attr.dropna(subset=skill_cols + ["overall_rating"])

# Mean per year — all leagues combined (T2.1)
df_trends = (
    pa_clean.groupby("year")[skill_cols]
    .mean()
    .reset_index()
    .query("year >= 2008 and year <= 2016")   # 2008-2016
)

df_long = df_trends.melt(
    id_vars="year",
    value_vars=skill_cols,
    var_name="skill",
    value_name="mean_value",
)
df_long["skill_label"] = df_long["skill"].map(skill_labels)

# print("Viz 3 data ready — trend data shape:", df_trends.shape)
# print("Year range:", df_trends["year"].min(), "—", df_trends["year"].max())


# %% CELL 8: Plot 3

skill_colors = {
    "Sprint Speed (Speed)":          "#e74c3c",
    "Short Passing (Passing)":       "#2980b9",
    "Finishing (Shooting)":          "#e67e22",
    "Standing Tackle (Defending)":   "#27ae60",
    "Stamina (Physical)":            "#8e44ad",
    "Dribbling (Technical)":         "#f39c12",
}

league_options = ["All Leagues"] + sorted(league["name"].dropna().unique().tolist())

fig3 = go.Figure()

for league_name in league_options:
    if league_name == "All Leagues":
        subset = pa_clean
    else:
        league_id = league[league["name"] == league_name]["id"].values[0]
        players_in_league = []
        for col in [f"home_player_{i}" for i in range(1, 12)] + [f"away_player_{i}" for i in range(1, 12)]:
            if col in match.columns:
                players_in_league.extend(match[match["league_id"] == league_id][col].dropna().tolist())
        players_in_league = list(set(players_in_league))
        subset = pa_clean[pa_clean["player_api_id"].isin(players_in_league)]

    df_sub = (
        subset.groupby("year")[skill_cols]
        .mean()
        .reset_index()
        .query("year >= 2008 and year <= 2016")
    )

    for skill in skill_cols:
        fig3.add_trace(go.Scatter(
            x=df_sub["year"],
            y=df_sub[skill],
            mode="lines+markers",
            name=skill_labels[skill],
            line=dict(color=skill_colors[skill_labels[skill]]),
            visible=(league_name == "All Leagues"),
            legendgroup=skill_labels[skill],
            showlegend=(league_name == "All Leagues"),
            hovertemplate=f"<b>{skill_labels[skill]}</b><br>Year: %{{x}}<br>Value: %{{y:.1f}}<extra>{league_name}</extra>",
        ))

# dropdown buttons
n_skills = len(skill_cols)
n_leagues = len(league_options)

buttons = []
for i, league_name in enumerate(league_options):
    visibility = [False] * (n_skills * n_leagues)
    for j in range(n_skills):
        visibility[i * n_skills + j] = True
    buttons.append(dict(
        label=league_name,
        method="update",
        args=[{"visible": visibility}],
    ))

# Annotation for peak skill
max_change_raw  = (df_trends[skill_cols].iloc[-1] - df_trends[skill_cols].iloc[0]).abs().idxmax()
top_skill_label = skill_labels[max_change_raw]
peak_year       = df_trends.loc[df_trends[max_change_raw].idxmax(), "year"]
peak_val        = df_trends.loc[df_trends["year"] == peak_year, max_change_raw].values[0]

fig3.add_annotation(
    x=peak_year,
    y=peak_val,
    text=f"<b>{top_skill_label.split(' ')[0]}</b><br>peak: {peak_val:.1f}",
    showarrow=True,
    arrowhead=2,
    font=dict(size=10),
    bgcolor="white",
    bordercolor="#aaa",
)

fig3.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        x=1.15,
        y=1.1,
        showactive=True,
    )],
    xaxis=dict(tickmode="linear", dtick=1, title="Season Year"),
    yaxis_title="Mean Attribute Value (0–100)",
    legend_title="Skill Category",
    height=520,
    hovermode="x unified",
    title="Q2 — Player Skill Profile Evolution Across European Football (2008–2016)",
    title_font_size=15,
    template="plotly_white",
)

fig3.show()
fig3.write_html("viz3_skill_evolution.html")


# ════════════════════════════════════════════════════════════
# Diverging Lollipop Chart: Elite vs Average by Role
# Created by: Shoaib
# Research Question: Q3 / Tasks T3.1 + T3.2
#
# PEER FEEDBACK FIX:
#   - TRUE diverging chart: X-axis = Elite minus Average (diff from 0)
#     NOT absolute rating values side-by-side
#   - Role derivation via PositionReference.csv (not manual thresholds)
#   - Sorted by absolute difference (most distinguishing skill at top)
#   - Top 2 skills annotated per role view
# ════════════════════════════════════════════════════════════


# %% CELL 9: Derive Player Roles via PositionReference

player_cols = [f"home_player_{i}" for i in range(1, 12)] + \
              [f"away_player_{i}" for i in range(1, 12)]
x_cols      = [f"home_player_X{i}" for i in range(1, 12)] + \
              [f"away_player_X{i}" for i in range(1, 12)]
y_cols      = [f"home_player_Y{i}" for i in range(1, 12)] + \
              [f"away_player_Y{i}" for i in range(1, 12)]

dfs = []
for p, x, y in zip(player_cols, x_cols, y_cols):
    tmp = match[["id", p, x, y]].dropna()
    tmp.columns = ["match_id", "player_api_id", "pos_x", "pos_y"]
    dfs.append(tmp)

lineup = (
    pd.concat(dfs)
    .drop_duplicates(subset="player_api_id")
    .copy()
)
lineup["pos_x"] = lineup["pos_x"].astype(int)
lineup["pos_y"] = lineup["pos_y"].astype(int)

# Join PositionReference: (pos_x, pos_y) → role_y (GK / DF / MF / FW)
lineup_roles = lineup.merge(
    pos_ref[["player_pos_x", "player_pos_y", "role_y"]],
    left_on=["pos_x", "pos_y"],
    right_on=["player_pos_x", "player_pos_y"],
    how="left",
)

# Merge roles into player attributes
pa_role = pa_clean.merge(
    lineup_roles[["player_api_id", "role_y"]].drop_duplicates(subset="player_api_id"),
    on="player_api_id",
    how="left",
)
pa_role["tier"] = np.where(pa_role["overall_rating"] >= 85, "Elite", "Average")

# print("Role distribution (PositionReference):")
# print(pa_role["role_y"].value_counts())
# print(f"\nElite players:   {(pa_role['tier']=='Elite').sum():,} records")
# print(f"Average players: {(pa_role['tier']=='Average').sum():,} records")


# %% CELL 10: Data Preparation

# 10 representative non-GK skills for Q3
skills_q3 = [
    "crossing", "finishing", "short_passing", "dribbling",
    "sprint_speed", "stamina", "vision", "standing_tackle",
    "ball_control", "long_passing",
]

def compute_diff(subset_df):
    """Compute Elite − Average mean difference per skill, sorted by diff."""
    elite_means = subset_df[subset_df["tier"] == "Elite"][skills_q3].mean()
    avg_means   = subset_df[subset_df["tier"] == "Average"][skills_q3].mean()
    diff        = (elite_means - avg_means).reset_index()
    diff.columns = ["skill", "diff"]
    return diff.sort_values("diff", ascending=True).reset_index(drop=True)

roles_to_plot = {
    "All Players":      pa_role,
    "Defenders (DF)":   pa_role[pa_role["role_y"] == "BK"],
    "Midfielders (MF)": pa_role[pa_role["role_y"] == "MF"],
    "Forwards (FW)":    pa_role[pa_role["role_y"] == "FW"],
}

diff_data = {label: compute_diff(df) for label, df in roles_to_plot.items()}
# print("\nDiff data computed for:", list(diff_data.keys()))


# %% CELL 11: Plot 4

def plot_lollipop(title_suffix, diff_df):
    colors = ["#e67e22" if d > 0 else "#7f8c8d" for d in diff_df["diff"]]

    fig = go.Figure()

    for idx, row in diff_df.iterrows():
        fig.add_shape(
            type="line",
            x0=0, x1=row["diff"],
            y0=row["skill"], y1=row["skill"],
            line=dict(color="#555555", width=2),
        )

    fig.add_trace(go.Scatter(
        x=diff_df["diff"],
        y=diff_df["skill"],
        mode="markers+text",
        marker=dict(
            color=colors,
            size=14,
            line=dict(color="white", width=1.5),
        ),
        text=[f" {v:+.1f}" for v in diff_df["diff"]],
        textposition="middle right",
        hovertemplate="<b>%{y}</b><br>Difference: %{x:.2f}<extra></extra>",
        showlegend=False,
    ))

    # Dashed Line
    fig.add_vline(x=0, line_dash="dash", line_color="black", line_width=1.5)

    # Annotate top 2 key differences
    top2_skills = diff_df.nlargest(2, "diff")
    for idx, row in top2_skills.iterrows():
        fig.add_annotation(
            x=row["diff"] + 0.3,
            y=row["skill"],
            text="← key differentiator",
            showarrow=False,
            font=dict(size=9, color="#e67e22"),
            xanchor="left",
        )

    fig.update_layout(
        title=f"Q3 — Elite vs Average Player Skills: {title_suffix}",
        xaxis_title="Mean Difference (Elite − Average)",
        yaxis_title="Skill Attribute",
        template="plotly_white",
        height=500,
        margin=dict(l=140, r=180),
    )
    
    return fig

for role_label, d_df in diff_data.items():
    fig = plot_lollipop(role_label, d_df)
    safe_name = role_label.lower().replace(" ", "_").replace("(", "").replace(")", "")
    fig.write_html(f"viz4_lollipop_{safe_name}.html")
    fig.show()

# %%
