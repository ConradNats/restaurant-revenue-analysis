"""Notebook cells, part 1: setup, overview, cleaning, distributions, composition."""

CELLS = []


def md(text):
    CELLS.append(("md", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n")))


md(r"""
# Restaurant Performance Analysis
### Module 03 - Data Visualization Milestone

**Dataset:** `restaurant_data.csv` - 8,368 restaurants, 17 columns
**Tools:** Python, Pandas, NumPy, Matplotlib, Seaborn, SciPy
**Prepared by:** *<your name here>*

---

## What this notebook does

This is a complete, end-to-end exploratory data analysis and data-mining story:

1. **Look at the data first** - shape, types, missing values, duplicates, ranges.
2. **Clean it** - impute missing values (none were found), remove duplicates (none), inspect and decide what to do with outliers.
3. **Describe it** - what every variable means, descriptive statistics, distributions.
4. **Visualise it** - histograms, bar charts, line charts, pie charts and scatter plots.
5. **Mine it** - ask business questions, look for hidden patterns, test them, and explain *why* they happen.
6. **Summarise it** - plain-English insights, inputs/outputs, recommendations, limitations.

| Assignment requirement | Where it is covered |
|---|---|
| Data overview, types, missing values | Section 1 |
| Outlier check and handling | Section 2 |
| Descriptive statistics and distributions | Sections 1 and 3 |
| Bar, line, pie, histogram and scatter charts | Sections 3-5 (see the chart checklist in Section 7) |
| Patterns, trends and key insights | Section 6 (Q1-Q8) and Section 8 |
| Inputs and outputs of every analysis | Section 9 |
""")

code(r"""
# ---- Core libraries -------------------------------------------------
import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from scipy import stats
from scipy.cluster import vq
from IPython.display import display

warnings.filterwarnings("ignore")

pd.set_option("display.max_columns", 60)
pd.set_option("display.width", 170)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

# ---- Design system used by every chart ------------------------------
NAVY  = "#102A43"
TEAL  = "#0E9594"
CORAL = "#EF6F6C"
AMBER = "#F2A541"
PLUM  = "#7B5EA7"
SKY   = "#4C9FBE"
INK   = "#102A43"
MUTED = "#627D98"
GRID  = "#E4EBF2"
BG    = "#FBFCFE"

LOC_COLORS = {"Downtown": CORAL, "Suburban": TEAL, "Rural": AMBER}
CUI_COLORS = {
    "Japanese": NAVY, "French": PLUM, "Italian": TEAL,
    "American": SKY, "Indian": AMBER, "Mexican": CORAL,
}

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": BG,
    "axes.edgecolor": "#D9E2EC",
    "axes.labelcolor": "#334E68",
    "axes.titlecolor": INK,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlepad": 10,
    "axes.labelsize": 10,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "grid.alpha": 1.0,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.frameon": False,
    "legend.fontsize": 9.5,
    "font.family": "DejaVu Sans",
    "figure.dpi": 110,
    "savefig.facecolor": "white",
})

os.makedirs("figures", exist_ok=True)


# ---- Small helpers ---------------------------------------------------
def money(x, pos=None):
    # Axis formatter: 656071 -> $656K, 1531868 -> $1.5M.
    if abs(x) >= 1_000_000:
        return f"${x / 1_000_000:.1f}M"
    if abs(x) >= 1_000:
        return f"${x / 1_000:.0f}K"
    return f"${x:.0f}"


def style_ax(ax, title="", xlabel="", ylabel=""):
    if title:
        ax.set_title(title, loc="left")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=MUTED)


def save(fig, name):
    filename = name if name.endswith(".png") else f"{name}.png"
    fig.savefig(f"figures/{filename}", dpi=170, bbox_inches="tight", facecolor="white")


def usd(value):
    return f"${value:,.0f}"
""")

md(r"""
## 0. How to run this notebook in Google Colab

1. Open [Google Colab](https://colab.research.google.com) and upload this `.ipynb` file.
2. Run the first two cells (`Runtime > Run all` also works).
3. When the loading cell asks for a file, upload `restaurant_data.csv`.
4. All charts are displayed inline and also saved to a `figures/` folder.

No extra installation is needed - Colab already ships with Pandas, NumPy, Matplotlib, Seaborn and SciPy.
""")

code(r"""
# ---- Load the data (works locally and in Colab) ----------------------
DATA_FILE = "restaurant_data.csv"

try:
    import google.colab  # noqa: F401
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if not os.path.exists(DATA_FILE):
    if IN_COLAB:
        from google.colab import files
        print("Please upload restaurant_data.csv")
        uploaded = files.upload()
        DATA_FILE = list(uploaded.keys())[0]
    else:
        raise FileNotFoundError(
            "restaurant_data.csv was not found. Place it in the same folder as this notebook."
        )

df_raw = pd.read_csv(DATA_FILE)
df = df_raw.copy()

print(f"Loaded {DATA_FILE}: {df.shape[0]:,} rows x {df.shape[1]} columns")
display(df.head())
""")

md(r"""
---
## 1. First look at the data

Before plotting anything, we need to know what we are working with: how big the data is, what type each column has, whether anything is missing, and whether the values make sense.
""")

code(r"""
print(f"Rows: {df.shape[0]:,}    Columns: {df.shape[1]}")
print(f"Numeric columns: {df.select_dtypes(include=np.number).shape[1]}")
print(f"Text columns:    {df.select_dtypes(exclude=np.number).shape[1]}")

overview = pd.DataFrame({
    "dtype": df.dtypes.astype(str),
    "non_null": df.notna().sum(),
    "missing": df.isna().sum(),
    "missing_%": (df.isna().mean() * 100).round(2),
    "unique": df.nunique(),
})
overview["example"] = [df[c].dropna().iloc[0] for c in overview.index]
overview.index.name = "column"

print("\nColumn-by-column overview")
display(overview)
""")

md(r"""
### 1.1 Data dictionary - what each column means

| Column | Meaning | Type | Range in this data | What information it carries |
|---|---|---|---|---|
| `Name` | Restaurant identifier | Text | 8,368 unique values | ID only; no analytical value |
| `Location` | Trade area | Categorical | Downtown, Suburban, Rural | Market type; in this data it is strongly tied to venue size |
| `Cuisine` | Main menu type | Categorical | 6 cuisines | Menu positioning; strongly tied to price |
| `Rating` | Average customer rating | Numeric | 3.0 - 5.0 (0.1 steps) | Perceived quality |
| `Seating Capacity` | Number of seats | Numeric | 30 - 90 | Size of the venue / maximum simultaneous covers |
| `Average Meal Price` | Average spend per diner | Numeric ($) | 25 - 76 | Price positioning / average check |
| `Marketing Budget` | Marketing spend | Numeric ($) | 604 - 9,978 | Marketing investment |
| `Social Media Followers` | Audience size | Numeric | 5,277 - 103,777 | Digital reach |
| `Chef Experience Years` | Experience of the head chef | Numeric | 1 - 19 | Kitchen skill proxy |
| `Number of Reviews` | Total reviews received | Numeric | 50 - 999 | Review volume |
| `Avg Review Length` | Average length of a review | Numeric | 50 - 300 | Review detail (unit not stated) |
| `Ambience Score` | Interior / atmosphere score | Numeric | 1 - 10 | Customer experience |
| `Service Quality Score` | Service score | Numeric | 1 - 10 | Customer experience |
| `Parking Availability` | Parking on site? | Categorical | Yes / No | Convenience |
| `Weekend Reservations` | Bookings on weekends | Numeric | 0 - 88 | Demand (weekend) |
| `Weekday Reservations` | Bookings on weekdays | Numeric | 0 - 88 | Demand (weekday) |
| `Revenue` | Revenue (target variable) | Numeric ($) | 184,709 - 1,531,868 | Business outcome we want to explain |

**Target variable:** `Revenue` (continuous, in dollars).
""")

code(r"""
# ---- Quality checks: missing values, duplicates, impossible values ----
rules = {
    "Rating": (1, 5),
    "Ambience Score": (1, 10),
    "Service Quality Score": (1, 10),
    "Seating Capacity": (1, 500),
    "Average Meal Price": (0, 1_000),
    "Weekend Reservations": (0, 1_000),
    "Weekday Reservations": (0, 1_000),
    "Marketing Budget": (0, np.inf),
    "Social Media Followers": (0, np.inf),
    "Revenue": (0, np.inf),
}
invalid = {
    col: int(((df[col] < lo) | (df[col] > hi)).sum())
    for col, (lo, hi) in rules.items()
}

checks = pd.DataFrame({
    "Check": [
        "Missing cells",
        "Rows with at least one missing value",
        "Duplicate rows",
        "Fully empty rows",
        "Values outside plausible ranges",
        "Negative numeric values",
        "Reservations greater than seating capacity",
    ],
    "Result": [
        int(df.isna().sum().sum()),
        int(df.isna().any(axis=1).sum()),
        int(df.duplicated().sum()),
        int(df.isna().all(axis=1).sum()),
        int(sum(invalid.values())),
        int((df.select_dtypes(include=np.number) < 0).sum().sum()),
        int(((df["Weekend Reservations"] > df["Seating Capacity"]) |
             (df["Weekday Reservations"] > df["Seating Capacity"])).sum()),
    ],
})
display(checks)

print("\nCategory counts")
for col in ["Location", "Cuisine", "Parking Availability"]:
    counts = df[col].value_counts().rename("count").to_frame()
    counts["share_%"] = (counts["count"] / len(df) * 100).round(2)
    print(f"\n{col}")
    display(counts)
""")

md(r"""
### What the overview tells us

* **8,368 restaurants, 17 columns** (13 numeric, 4 text).
* **No missing values, no duplicates, no impossible values.** The cleaning code below still implements a full imputation policy so the workflow can be reused on messier data.
* **The categories are suspiciously balanced.** The three locations each hold about one third of the data and the six cuisines each hold about one sixth. In a real market we would expect much more uneven groups.
* **`Name` is an ID**, not a feature - it should not be used in any model.
* **Every reservation is within seating capacity**, which is a good internal-consistency check.

This is a clean, well-behaved dataset - almost too clean. Keep that in mind when we reach the patterns: the data behaves like it was generated by rules rather than collected from the real world.
""")

code(r"""
# ---- Descriptive statistics ------------------------------------------
num_cols = df.select_dtypes(include=np.number).columns.tolist()

desc = df[num_cols].describe().T[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
desc["skew"] = df[num_cols].skew()
desc["missing"] = df[num_cols].isna().sum()
desc.index.name = "variable"

print("Descriptive statistics (mean vs median tells us about skew)")
display(desc.round(2))
""")

md(r"""
### Reading the statistics in plain English

| Variable | Typical value | Spread | What it means here |
|---|---|---|---|
| Revenue | Mean **$656,071**, median **$604,242** | SD $267,414 | The average is pulled up by a few very large venues; half the restaurants earn below $604K |
| Average Meal Price | Mean **$47.90** | SD $14.34 | Mid-priced restaurants; values sit in six $10-wide bands |
| Seating Capacity | Mean **60 seats** | SD 17.4 | Three size tiers: about 40, 60 and 80 seats |
| Marketing Budget | Mean **$3,218**, median **$2,847** | SD $1,825 | Right-skewed: a small number of big spenders stretch the mean |
| Social Media Followers | Mean **36,191**, median **32,519** | SD 18,630 | Same right-skewed shape as marketing |
| Rating | Mean **4.01** | SD 0.58 | Almost uniform between 3.0 and 5.0 - unusual for real ratings |
| Reservations | ~**29** weekend and **29** weekday | SD ~20 | Bookings scale with the number of seats |
| Scores (ambience, service) | Mean ~**5.5** of 10 | SD ~2.6 | Wide, even spread across the scale |

**Why this matters:** a mean far above the median (revenue, marketing, followers) signals right skew. For those variables, the median is the fairer "typical" value, and the boxplots in Section 2 will confirm the tail.
""")

md(r"""
---
## 2. Cleaning the data

The cleaning plan, in order:

1. **Missing values** - numeric columns: median imputation (robust to skew); text columns: most frequent value. (Nothing to fill here.)
2. **Duplicates** - drop exact duplicate rows. (None found.)
3. **Invalid values** - check ranges and logical rules such as "reservations cannot exceed seats". (None broken.)
4. **Outliers** - detect with the IQR rule and Z-scores, inspect them, then decide whether to keep, cap or remove.
5. **Feature engineering** - add the ratio columns that make the business questions answerable.
""")

code(r"""
# ---- 2.1 Missing values and duplicates --------------------------------
df_clean = df.copy()

missing_before = int(df_clean.isna().sum().sum())
imputed = {}

for col in df_clean.columns:
    if df_clean[col].isna().any():
        if pd.api.types.is_numeric_dtype(df_clean[col]):
            fill = df_clean[col].median()
            imputed[col] = ("median", fill)
        else:
            fill = df_clean[col].mode()[0]
            imputed[col] = ("mode", fill)
        df_clean[col] = df_clean[col].fillna(fill)

duplicates = int(df_clean.duplicated().sum())
df_clean = df_clean.drop_duplicates().reset_index(drop=True)

print(f"Missing cells before cleaning : {missing_before}")
print(f"Columns imputed               : {len(imputed)}")
print(f"Duplicate rows removed        : {duplicates}")
print(f"Rows after cleaning           : {len(df_clean):,}")

# ---- 2.2 Feature engineering -----------------------------------------
df_clean["Total Reservations"] = df_clean["Weekend Reservations"] + df_clean["Weekday Reservations"]
df_clean["Reservation Rate"] = df_clean["Total Reservations"] / df_clean["Seating Capacity"]
df_clean["Revenue per Seat"] = df_clean["Revenue"] / df_clean["Seating Capacity"]
df_clean["Marketing per Seat"] = df_clean["Marketing Budget"] / df_clean["Seating Capacity"]
df_clean["Revenue per Marketing Dollar"] = df_clean["Revenue"] / df_clean["Marketing Budget"]
df_clean["Seats x Price"] = df_clean["Seating Capacity"] * df_clean["Average Meal Price"]
df_clean["Rating Band"] = pd.cut(
    df_clean["Rating"], bins=[2.99, 3.5, 4.0, 4.5, 5.0],
    labels=["3.0-3.5", "3.5-4.0", "4.0-4.5", "4.5-5.0"],
)
df_clean["Price Band"] = pd.qcut(
    df_clean["Average Meal Price"], 5,
    labels=["Very low", "Low", "Mid", "High", "Very high"],
)

df = df_clean.copy()
print("\nNew engineered columns:")
print(["Total Reservations", "Reservation Rate", "Revenue per Seat",
       "Marketing per Seat", "Revenue per Marketing Dollar", "Seats x Price",
       "Rating Band", "Price Band"])
display(df[["Seating Capacity", "Average Meal Price", "Revenue", "Seats x Price",
            "Revenue per Seat", "Reservation Rate"]].head())
""")

code(r"""
# ---- 2.3 Outlier detection (IQR + Z-score) ---------------------------
outlier_rows = []

for col in num_cols:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_iqr = int(((df[col] < lower) | (df[col] > upper)).sum())
    n_z = int((np.abs(stats.zscore(df[col])) > 3).sum())
    outlier_rows.append({
        "variable": col,
        "Q1": q1,
        "Q3": q3,
        "lower fence": lower,
        "upper fence": upper,
        "IQR outliers": n_iqr,
        "IQR outliers %": round(n_iqr / len(df) * 100, 2),
        "|Z| > 3": n_z,
    })

outlier_table = pd.DataFrame(outlier_rows)
display(outlier_table.round(2))
print(f"\nTotal IQR outlier cells: {outlier_table['IQR outliers'].sum():,}")
""")

md(r"""
**What we see:** outliers appear in only three columns - Revenue (102 restaurants, 1.2%), Marketing Budget (389, 4.6%) and Followers (361, 4.3%). Price, seating, ratings, scores and reservations have none.

The boxplots below show what those tails look like. The key question is: *are these data-entry errors, or real large restaurants?*
""")

code(r"""
# ---- Figure 1: boxplots before any outlier treatment -----------------
box_cols = [
    ("Revenue", "Revenue ($)"),
    ("Marketing Budget", "Marketing budget ($)"),
    ("Social Media Followers", "Social media followers"),
    ("Average Meal Price", "Average meal price ($)"),
]

fig, axes = plt.subplots(2, 2, figsize=(13, 6.8))
for ax, (col, label) in zip(axes.ravel(), box_cols):
    sns.boxplot(
        x=df[col], ax=ax, color=SKY, width=0.42, linewidth=1.2,
        flierprops=dict(marker="o", markersize=3, markerfacecolor=CORAL,
                        markeredgecolor="none", alpha=0.6),
    )
    style_ax(ax, title=f"{col}", xlabel=label, ylabel="")
    if col != "Social Media Followers":
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(money))
    else:
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, p: f"{v/1000:.0f}K"))

fig.suptitle("Figure 1  |  Boxplots reveal skewed tails in money and audience variables",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.935, "Dots are observations beyond 1.5 x IQR. They are candidates, not proven errors.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.93])
save(fig, "fig01_outlier_boxplots.png")
plt.show()
""")

code(r"""
# ---- 2.4 Inspect the outliers before deciding ------------------------
q1, q3 = df["Revenue"].quantile([0.25, 0.75])
iqr = q3 - q1
df["Revenue Outlier"] = (df["Revenue"] < q1 - 1.5 * iqr) | (df["Revenue"] > q3 + 1.5 * iqr)

print("Do the revenue outliers look like errors or like big restaurants?\n")
cols = ["Name", "Location", "Cuisine", "Seating Capacity", "Average Meal Price",
        "Marketing Budget", "Rating", "Revenue"]
print("Largest revenue outliers:")
print(df[df["Revenue Outlier"]].nlargest(6, "Revenue")[cols].to_string(index=False))

print("\nTypical restaurant for comparison:")
print(df[~df["Revenue Outlier"]].sample(6, random_state=7)[cols].to_string(index=False))

print("\nAverage profile")
print(pd.DataFrame({
    "outliers": df[df["Revenue Outlier"]][["Seating Capacity", "Average Meal Price", "Marketing Budget"]].mean(),
    "all others": df[~df["Revenue Outlier"]][["Seating Capacity", "Average Meal Price", "Marketing Budget"]].mean(),
}).round(1))
""")

code(r"""
# ---- Figure 2: evidence that the outliers are genuine ----------------
# If a restaurant simply has more seats and a higher check, its revenue
# should sit on the same line as everyone else.
fig, ax = plt.subplots(figsize=(10.5, 5.8))

sns.scatterplot(
    data=df, x="Seats x Price", y="Revenue", hue="Revenue Outlier",
    palette={False: SKY, True: CORAL}, s=16, alpha=0.5, linewidth=0, ax=ax,
)

line_x = np.linspace(0, df["Seats x Price"].max() * 1.03, 100)
ratio = (df["Revenue"] / df["Seats x Price"]).median()
ax.plot(line_x, ratio * line_x, color=INK, lw=1.6, ls="--",
        label=f"same line: revenue = {ratio:.0f} x seats x price")

ax.set_xlim(0, df["Seats x Price"].max() * 1.03)
ax.set_ylim(0, df["Revenue"].max() * 1.08)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(money))
ax.yaxis.set_major_formatter(mtick.FuncFormatter(money))
style_ax(ax, "Figure 2  |  Flagged 'outliers' sit on exactly the same revenue line",
         "Seating capacity x average meal price", "Revenue")
ax.legend(loc="upper left", title="IQR outlier", title_fontsize=9)
fig.tight_layout()
save(fig, "fig02_outlier_evidence.png")
plt.show()
""")

code(r"""
# ---- 2.5 Sensitivity check: what would change if we removed them? ----
mask = ~df["Revenue Outlier"]

comparison = pd.DataFrame({
    "Pearson r with Revenue (all data)": [
        df["Revenue"].corr(df[c]) for c in
        ["Average Meal Price", "Seating Capacity", "Marketing Budget", "Social Media Followers", "Rating"]
    ],
    "Pearson r without revenue outliers": [
        df.loc[mask, "Revenue"].corr(df.loc[mask, c]) for c in
        ["Average Meal Price", "Seating Capacity", "Marketing Budget", "Social Media Followers", "Rating"]
    ],
}, index=["Average Meal Price", "Seating Capacity", "Marketing Budget",
          "Social Media Followers", "Rating"])

display(comparison.round(3))

print(f"Revenue outliers: {df['Revenue Outlier'].sum():,} ({df['Revenue Outlier'].mean()*100:.1f}% of rows)")
print(f"Mean revenue with outliers   : {usd(df['Revenue'].mean())}")
print(f"Mean revenue without outliers: {usd(df.loc[mask, 'Revenue'].mean())}")

# Would capping (winsorising at 1st/99th percentile) change the story?
cap_lo, cap_hi = df["Revenue"].quantile([0.01, 0.99])
capped = df["Revenue"].clip(cap_lo, cap_hi)
print(f"\nWinsorised revenue range: {usd(capped.min())} - {usd(capped.max())}")
print(f"Correlation of winsorised revenue with price : {capped.corr(df['Average Meal Price']):.3f}")
print(f"Correlation of raw revenue with price        : {df['Revenue'].corr(df['Average Meal Price']):.3f}")
""")

md(r"""
### Outlier decision - keep them, do not delete or cap them

| Question | Answer |
|---|---|
| Are they data-entry errors? | **No.** Every "outlier" has a plausible location, cuisine, seat count and price. |
| Are they on the same pattern as the rest? | **Yes.** In Figure 2 they lie on the same straight line as normal restaurants: revenue ≈ 229 x seats x price. |
| What would deleting them do? | Remove the largest, most profitable venues (90 seats, Japanese, Downtown). We would lose the top of the market and bias the analysis downwards. |
| What would capping them do? | Make every big restaurant look identical, hide the size effect, and weaken the strongest real relationship in the data. |
| **What we do instead** | **Keep them**, flag them (`Revenue Outlier`), use robust statistics (median, IQR), and repeat key correlations with and without them (table above). The conclusions do not change. |

The sensitivity table shows correlations move by less than 0.02 when the outliers are removed. That is the test of a robust finding: **the conclusion survives the cleaning decision.**

This is a deliberately mature choice. Outliers are not automatically "bad data"; the right question is whether they are *wrong* or simply *big*. Here they are big.
""")

md(r"""
---
## 3. Distributions - one variable at a time

A histogram shows the shape of a variable: where most values sit, whether there are one or several peaks, and whether the tails are long. This is where we start to see the hidden structure of the dataset.
""")

code(r"""
# ---- Figure 3: six histograms with mean / median ---------------------
hist_cols = [
    ("Rating", "Customer rating (1-5)", CORAL),
    ("Seating Capacity", "Seats per restaurant", TEAL),
    ("Average Meal Price", "Average spend per diner ($)", AMBER),
    ("Marketing Budget", "Marketing budget ($)", PLUM),
    ("Social Media Followers", "Social media followers", SKY),
    ("Revenue", "Revenue ($)", NAVY),
]

fig, axes = plt.subplots(2, 3, figsize=(15.5, 8.2))
for ax, (col, label, color) in zip(axes.ravel(), hist_cols):
    sns.histplot(df[col], bins=40, kde=True, color=color, alpha=0.72,
                 edgecolor="white", linewidth=0.4, ax=ax)
    ax.axvline(df[col].mean(), color=CORAL, ls="--", lw=1.5)
    ax.axvline(df[col].median(), color=INK, ls=":", lw=1.3)
    style_ax(ax, title=col, xlabel=label, ylabel="Restaurants")
    if col in ("Average Meal Price", "Marketing Budget", "Social Media Followers", "Revenue"):
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(money))
    if col == "Seating Capacity":
        ax.set_xticks([30, 40, 50, 60, 70, 80, 90])

fig.suptitle("Figure 3  |  Distributions: three uniform variables, two skewed ones and three size tiers",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.935, "Dashed line = mean, dotted line = median. KDE = smoothed density curve.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.925])
save(fig, "fig03_distributions.png")
plt.show()
""")

md(r"""
### What the shapes tell us

* **Rating is almost perfectly flat** between 3.0 and 5.0, with fewer observations exactly at 3.0 and 5.0. That is the signature of a *uniform random score rounded to one decimal* - not a real customer-satisfaction distribution, which normally peaks around 4.3. This is our first warning that ratings may carry little information.
* **Seating capacity has three clear peaks** at about 40, 60 and 80 seats, and the gaps between them are almost empty. Restaurants come in three sizes, not a smooth range.
* **Average meal price has six blocks**, one per cuisine (about $30, $35, $40, $50, $60, $70). Menus are priced by cuisine type.
* **Marketing budget and followers are right-skewed** (skew 1.13 and 1.08): most venues spend $2K-$4K, a few spend far more. Their shapes look almost identical.
* **Revenue is right-skewed too** (skew 0.74), with the mean ($656K) above the median ($604K), because a few large venues pull the average up.

These shapes are already hinting at the data's hidden rules. The next sections confirm them.
""")

md(r"""
---
## 4. Composition - bar charts and pie charts

Categorical columns are best compared with **bar charts** (magnitude) and **pie charts** (share of a total). We look at cuisine and location from both angles.
""")

code(r"""
# ---- Figure 4: cuisine economics -------------------------------------
cuisine_order = (df.groupby("Cuisine")["Average Meal Price"].mean()
                   .sort_values(ascending=False).index.tolist())

price_by_cui = df.groupby("Cuisine")["Average Meal Price"].mean().reindex(cuisine_order)
rev_by_cui = df.groupby("Cuisine")["Revenue"].mean().reindex(cuisine_order)
rps_by_cui = df.groupby("Cuisine")["Revenue per Seat"].mean().reindex(cuisine_order)
share_by_cui = df.groupby("Cuisine")["Revenue"].sum().reindex(cuisine_order)
share_by_cui = share_by_cui / share_by_cui.sum() * 100
colors_cui = [CUI_COLORS[c] for c in cuisine_order]

fig, axes = plt.subplots(2, 2, figsize=(14.5, 9))

b1 = axes[0, 0].bar(cuisine_order, price_by_cui, color=colors_cui, width=0.66)
axes[0, 0].bar_label(b1, labels=[f"${v:.0f}" for v in price_by_cui], padding=3, fontsize=9)
style_ax(axes[0, 0], "Average meal price by cuisine", "", "Average meal price ($)")
axes[0, 0].set_ylim(0, price_by_cui.max() * 1.16)
axes[0, 0].tick_params(axis="x", rotation=15)

b2 = axes[0, 1].bar(cuisine_order, rev_by_cui, color=colors_cui, width=0.66)
axes[0, 1].bar_label(b2, labels=[f"${v/1000:.0f}K" for v in rev_by_cui], padding=3, fontsize=9)
style_ax(axes[0, 1], "Average revenue by cuisine", "", "Average revenue ($)")
axes[0, 1].set_ylim(0, rev_by_cui.max() * 1.16)
axes[0, 1].yaxis.set_major_formatter(mtick.FuncFormatter(money))
axes[0, 1].tick_params(axis="x", rotation=15)

b3 = axes[1, 0].bar(cuisine_order, rps_by_cui, color=colors_cui, width=0.66)
axes[1, 0].bar_label(b3, labels=[f"${v/1000:.1f}K" for v in rps_by_cui], padding=3, fontsize=9)
style_ax(axes[1, 0], "Revenue per seat by cuisine", "", "Revenue per seat ($)")
axes[1, 0].set_ylim(0, rps_by_cui.max() * 1.16)
axes[1, 0].yaxis.set_major_formatter(mtick.FuncFormatter(money))
axes[1, 0].tick_params(axis="x", rotation=15)

wedges, _, autotexts = axes[1, 1].pie(
    share_by_cui, labels=[f"{c}\n{s:.1f}%" for c, s in share_by_cui.items()],
    colors=colors_cui, startangle=90, counterclock=False,
    autopct="%1.1f%%", pctdistance=0.72, labeldistance=1.15,
    wedgeprops=dict(edgecolor="white", linewidth=1.8),
    textprops=dict(fontsize=8.5, color=INK),
)
for t in autotexts:
    t.set_color("white")
    t.set_fontweight("bold")
    t.set_fontsize(8.5)
axes[1, 1].set_title("Revenue share by cuisine", loc="left")

fig.suptitle("Figure 4  |  Cuisine is a price ladder, and revenue follows it exactly",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.945, "All four panels use the same cuisine order (highest price first).",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.94])
save(fig, "fig04_cuisine.png")
plt.show()

print(pd.DataFrame({
    "average price": price_by_cui.round(2),
    "average revenue": rev_by_cui.round(0),
    "revenue per seat": rps_by_cui.round(0),
    "revenue share %": share_by_cui.round(1),
}))
""")

md(r"""
### Cuisine insight - price is the whole story

The ranking is identical in all three bar charts: **Japanese > French > Italian > American > Indian > Mexican**.

* Average price runs from **$30 (Mexican)** to **$70 (Japanese)**.
* Average revenue runs from **$427K** to **$938K** - a **2.2x** gap.
* Revenue per seat runs from **$7,096** to **$15,916** - also **2.2x**.
* Revenue share: Japanese 23.0%, French 21.4%, Italian 17.8%, American 14.6%, Indian 12.4%, Mexican 10.8%.

Because the number of restaurants per cuisine is nearly equal (1,344-1,433), this is not a sample-size effect. **Japanese and French restaurants earn more per seat simply because their average check is higher.** The pie chart shows the money: the two most expensive cuisines take 44% of all revenue.

This is one of the clearest patterns in the data - and it is our first clue that *average meal price* is a main driver of revenue.
""")

code(r"""
# ---- Figure 5: location composition ---------------------------------
loc_order = ["Downtown", "Suburban", "Rural"]
count_by_loc = df["Location"].value_counts().reindex(loc_order)
share_by_loc = df.groupby("Location")["Revenue"].sum().reindex(loc_order)
share_by_loc = share_by_loc / share_by_loc.sum() * 100
seats_by_loc = df.groupby("Location")["Seating Capacity"].mean().reindex(loc_order)
rev_by_loc = df.groupby("Location")["Revenue"].mean().reindex(loc_order)
colors_loc = [LOC_COLORS[l] for l in loc_order]

fig, axes = plt.subplots(2, 2, figsize=(14.5, 9))

w1, _, a1 = axes[0, 0].pie(
    count_by_loc, labels=[f"{l}\n{n:,}" for l, n in count_by_loc.items()],
    colors=colors_loc, startangle=90, counterclock=False,
    autopct="%1.1f%%", pctdistance=0.72, labeldistance=1.16,
    wedgeprops=dict(edgecolor="white", linewidth=1.8),
    textprops=dict(fontsize=9, color=INK),
)
for t in a1:
    t.set_color("white"); t.set_fontweight("bold")
axes[0, 0].set_title("Share of restaurants by location", loc="left")

w2, _, a2 = axes[0, 1].pie(
    share_by_loc, labels=[f"{l}\n{s:.1f}%" for l, s in share_by_loc.items()],
    colors=colors_loc, startangle=90, counterclock=False,
    autopct="%1.1f%%", pctdistance=0.72, labeldistance=1.16,
    wedgeprops=dict(edgecolor="white", linewidth=1.8),
    textprops=dict(fontsize=9, color=INK),
)
for t in a2:
    t.set_color("white"); t.set_fontweight("bold")
axes[0, 1].set_title("Share of total revenue by location", loc="left")

b1 = axes[1, 0].bar(loc_order, seats_by_loc, color=colors_loc, width=0.6)
axes[1, 0].bar_label(b1, labels=[f"{v:.0f}" for v in seats_by_loc], padding=3, fontsize=10)
style_ax(axes[1, 0], "Average seating capacity by location", "", "Seats")
axes[1, 0].set_ylim(0, seats_by_loc.max() * 1.18)

b2 = axes[1, 1].bar(loc_order, rev_by_loc, color=colors_loc, width=0.6)
axes[1, 1].bar_label(b2, labels=[f"${v/1000:.0f}K" for v in rev_by_loc], padding=3, fontsize=10)
style_ax(axes[1, 1], "Average revenue by location", "", "Average revenue ($)")
axes[1, 1].set_ylim(0, rev_by_loc.max() * 1.18)
axes[1, 1].yaxis.set_major_formatter(mtick.FuncFormatter(money))

fig.suptitle("Figure 5  |  Location is a size tier: downtown venues have twice the seats of rural ones",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.945, "Counts are equal (about one third each), but revenue share is not.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.94])
save(fig, "fig05_location.png")
plt.show()

print(pd.DataFrame({
    "restaurants": count_by_loc,
    "average seats": seats_by_loc.round(1),
    "average revenue": rev_by_loc.round(0),
    "revenue share %": share_by_loc.round(1),
}))
""")

md(r"""
### Location insight - big venues, not better locations

* The three locations hold almost the same number of restaurants (33.7%, 33.3%, 33.0%), but
* Downtown earns **44.5% of all revenue**, Suburban **32.8%** and Rural **22.6%**.
* The reason is visible in the bottom-left chart: average seating is **80 seats Downtown, 60 Suburban, 40 Rural**.
* Average revenue is **$866K / $647K / $450K** - almost exactly proportional to seat count.

Revenue per seat is nearly identical across locations (**$10,784 - $11,250**, a 4% spread). So "Downtown" is not a magic location that makes each customer spend more. **It is simply where the big restaurants are.** Any analysis that compares location without controlling for size will give location credit that belongs to capacity.

This is a classic **confounding variable**. We will test it formally in Q3.
""")
