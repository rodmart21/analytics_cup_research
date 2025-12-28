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
In football, "invisible work"—off-ball movement—is often praised but rarely quantified. Traditional event data fails to capture the value of runs that don't receive passes, dismissing them as irrelevant "decoys." This study uses tracking data to unmask the true impact of off-ball runs. Specifically, I investigate whether untargeted runs improve possession outcomes and propose a new metric, **Run Value Added (RVA)**, to identify the league's most effective off-ball movers and understand when runs create—or destroy—value.

#### Methods
I utilized **SkillCorner Open Data** across multiple matches from the dataset. The analysis pipeline consisted of four steps:

1. **Comparative Analysis:** Systematically compared possession outcomes (pass success rate, field progression, defensive separation, and shot creation rate) between possessions with runs versus without runs, and between targeted versus ignored dangerous runs, using independent t-tests to measure statistical significance.

2. **Metric Development:** Created **Run Value Added (RVA)**, an evidence-based composite metric calibrated to empirical findings. RVA comprises five components: Shot Creation Value (2.5x weight for targeted dangerous runs, 0.3x for ignored), Direct Threat Value (xThreat × completion probability when targeted), Progression Value (0.12x weight reflecting +0.225m advancement), Decoy Penalty (−0.25x for ignored dangerous runs that lose space), and Overload Value (0.08x for simultaneous runs). Weights were derived from observed effect sizes in the comparative analysis.

#### Results
The analysis reveals a paradoxical relationship between off-ball runs and possession outcomes. Possessions with runs showed a **+77% increase in shot creation** (7.8% vs 4.4%, p<0.001) and **+0.225m better field progression** (p<0.001), confirming runs drive offensive threat.

However, the "Decoy Hypothesis" was **disproven**. Contrary to conventional wisdom, untargeted dangerous runs had **negative value**: they caused 0.45m *more* separation loss than targeted runs (−2.45m vs −2.00m), suggesting hesitation costs and defensive intelligence. When dangerous runs were ignored, defenders didn't "bite" on the decoy—they stayed disciplined and closed down the actual pass target.

The RVA metric successfully identified elite movers: **G. May** (501 total RVA, 0.0095 avg) led the league with 40% dangerous run conversion and balanced shot creation (67%) and direct involvement (43%). Targeting efficiency proved critical—runs that received passes were **3.1x more valuable** (0.0068 vs 0.0022 avg RVA) than untargeted runs.

| **Run Type** | **Avg RVA** | **vs Baseline** | **Key Finding** |
|:-------------|:------------|:----------------|:----------------|
| **Targeted Dangerous** | 0.0068 | +3.1x | Elite value—shot creation + direct threat |
| **Untargeted Normal** | −0.0001 | Neutral | Minimal impact (neither help nor harm) |
| **Untargeted Dangerous** | **−0.0005** | **Negative** | **Waste opportunity—cause hesitation** |

#### Conclusion
This study confirms that dangerous runs are high-reward actions—but only when **targeted**. Ignored dangerous runs have negative value, losing more space (−2.45m vs −2.00m) and contributing to worse outcomes. The +77% shot creation benefit comes from *using* runs, not merely making them. The **RVA metric** successfully quantifies this nuance, rewarding efficient movers like G. May while penalizing volume-based runners whose movements aren't converted into goals. Off-ball movement matters, but execution and decision-making matter more.