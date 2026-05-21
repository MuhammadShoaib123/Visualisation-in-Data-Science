# VDS2526 — Group 1 | Football Dataset Visualisations

**Course:** Visualisation in Data Science (VDS2526) — 2025/2026  
**Instructor:** Prof. dr. Inigo BERMEJO DELGADO  
**Group:** Group 1  
**Members:**
- Mansoor Khurram (2505888)
- Murtaza Javed (2501823)
- Muhammad Shoaib (2501708)
- Yogesh Tarachand More (2469856)

---

## Project Context

This project was completed as part of the VDS2526 course assignment.  
We were assigned the **European Football dataset** and tasked with designing and implementing
interactive visualisations to answer data-driven questions about European football (2008–2016).

---

## Research Questions

| # | Question |
|---|---|
| Q1 | What makes a winning team? How do team tactical attributes (build-up play speed, chance creation, defensive pressure) relate to match outcomes across leagues? |
| Q2 | How have player skill profiles evolved from 2008 to 2016, and do different leagues show different trajectories? |
| Q3 | Which individual skills most strongly differentiate elite players (overall rating ≥ 85) from average players, and does this vary by role (attacker vs. defender)? |

---

## Visualisations

| File | Chart Type | Question |
|---|---|---|
| `viz1_match_outcomes.html` | Stacked Bar Chart | Q1 — Match outcome % per league |
| `viz2_tactics_vs_success.html` | Scatter Plot + OLS trendline | Q1 — Tactical attributes vs season goal difference |
| `viz3_skill_evolution.html` | Multi-Line Chart | Q2 — Player skill trends 2008–2016 |
| `viz4_lollipop_all_players.html` | Diverging Lollipop | Q3 — Elite vs average (all players) |
| `viz4_lollipop_defenders_df.html` | Diverging Lollipop | Q3 — Elite vs average (defenders) |
| `viz4_lollipop_midfielders_mf.html` | Diverging Lollipop | Q3 — Elite vs average (midfielders) |
| `viz4_lollipop_forwards_fw.html` | Diverging Lollipop | Q3 — Elite vs average (forwards) |

---

## How to Reproduce

### 1. Get the dataset
Download the **European Soccer Database** from Kaggle:  
https://www.kaggle.com/datasets/hugomathien/soccer  
Extract all CSV files into a local folder.  
Add the dataset to the \data folder in the working directory to ensure this works properly.

### 2. Install dependencies

Install the required Python libraries before running the project:

```bash
pip install plotly pandas numpy scipy statsmodels
```

### 3. Run the script
```bash
python VDS2526_Group01_Football_Visualisations.py
```

All 7 interactive HTML files will be saved in the `output/` folder.  
Open any `.html` file in a web browser — no server required.

---

## Dataset

- **Source:** European Soccer Database — Hugo Mathien (Kaggle)  
  https://www.kaggle.com/datasets/hugomathien/soccer
- **Coverage:** 11 European leagues, seasons 2008/09 – 2015/16
- **Key tables used:**

| Table | Rows | Used For |
|---|---|---|
| Match | 25,979 | Goal difference, outcomes, lineups |
| Player_Attributes | 183,978 | Skill evolution, elite vs average |
| Team_Attributes | 1,458 | Tactical attributes |
| Team | 299 | Team names |
| League | 11 | League names |
| PositionReference | 99 | Deriving player roles (GK/DF/MF/FW) |
 
> Download from Kaggle using the link above or use the zip data file (VDS2526 Football.zip) from blackboard.

---

## Screencast Video

YouTube link: *(paste full URL here after recording)*

---

## Report

The full project report (Parts 1–4) is submitted separately via Blackboard.
