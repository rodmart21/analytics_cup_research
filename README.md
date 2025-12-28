# SkillCorner X PySport Analytics Cup
This repository contains the submission template for the SkillCorner X PySport Analytics Cup **Research Track**. 
Your submission for the **Research Track** should be on the `main` branch of your own fork of this repository.

Find the Analytics Cup [**dataset**](https://github.com/SkillCorner/opendata/tree/master/data) and [**tutorials**](https://github.com/SkillCorner/opendata/tree/master/resources) on the [**SkillCorner Open Data Repository**](https://github.com/SkillCorner/opendata).

## Submitting
Make sure your `main` branch contains:
1. A single Jupyter Notebook in the root of this repository called `submission.ipynb`
    - This Juypter Notebook can not contain more than 2000 words.
    - All other code should also be contained in this repository, but should be imported into the notebook from the `src` folder.
2. An abstract of maximum 500 words that follows the **Research Track Abstract Template**.
    - The abstract can contain a maximum of 2 figures, 2 tables or 1 figure and 1 table.
3. Submit your GitHub repository on the [Analytics Cup Pretalx page](https://pretalx.pysport.org)

Finally:
- Make sure your GitHub repository does **not** contain big data files. The tracking data should be loaded directly from the [Analytics Cup Data GitHub Repository](https://github.com/SkillCorner/opendata).For more information on how to load the data directly from GitHub please see this [Jupyter Notebook](https://github.com/SkillCorner/opendata/blob/master/resources/getting-started-skc-tracking-kloppy.ipynb).
- Make sure the `submission.ipynb` notebook runs on a clean environment.

_⚠️ Not adhering to these submission rules and the [**Analytics Cup Rules**](https://pysport.org/analytics-cup/rules) may result in a point deduction or disqualification._

---

## Research Track Abstract Template (max. 500 words)

#### Introduction
In football, "invisible work"—off-ball movement—is often praised but rarely quantified. Traditional event data fails to capture the value of a run that does not receive a pass (a decoy). The objective of this study is to use tracking data to unmask this value. Specifically, I investigate whether untargeted runs improve possession outcomes and propose a new metric, **Run Value Added (RVA)**, to identify the league's most effective off-ball movers.

#### Methods
I utilized the **SkillCorner Open Data** (specifically Match 1886347 and aggregate datasets). The analysis pipeline consisted of three steps:
1.  **Synchronization:** Merging tracking and event data to link specific run trajectories to distinct possession chains.
2.  **Classification:** Runs were categorized by **Danger** (potential xThreat) and **Targeting** (received pass vs. decoy).
3.  **Metric Development:** I created **Run Value Added (RVA)**, a composite metric that rewards players for Shot Creation (empirically weighted), Field Progression, and Decoy Value (disrupting defensive shape), while penalizing movement that reduces spacing without tactical purpose.

#### Results
The analysis provides empirical evidence that off-ball movement drives offense, regardless of whether the runner receives the ball. Possessions with active runs showed a significant **77% increase in shot creation** compared to static possessions ($p < 0.001$).

Crucially, the study validated the "Decoy Effect." **Untargeted dangerous runs** (approx. 10% of all runs) acted as force multipliers. Additionally, the "Separation Paradox" finding revealed that effective runners often *reduce* their own separation to attract defenders, thereby creating space for teammates.

| Metric | Impact of Off-Ball Runs | Significance |
| :--- | :--- | :--- |
| **Shot Creation Rate** | **+77% Lift** (4.4% $\to$ 7.8%) | $p < 0.001$ |
| **Field Progression** | **+0.225 units** per possession | $p < 0.001$ |
| **Decoy Efficiency** | **38.1%** Shot Rate on ignored dangerous runs | High Tactical Value |
| **Separation Gain** | **-2.45m** (Runners attract pressure) | Defensive Disruption |

#### Conclusion
This study confirms that dangerous runs are high-reward actions that should be encouraged, even if the runner is not the target. By attracting defensive attention, runners significantly increase the team's probability of generating a shot. The **RVA** metric successfully identified top performers like **G. May** (0.016 Avg RVA), proving that we can quantify the contribution of players who facilitate play without touching the ball.
