"""Notebook cells, part 2: relationships, correlation, data-mining Q1-Q3."""

CELLS = []


def md(text):
    CELLS.append(("md", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n")))


md(r"""
---
## 5. Relationships between variables

Now we look at two variables at a time. Scatter plots answer "when one goes up, does the other go up?" and the correlation heatmap summarises all pairs at once.
""")

code(r"""
# ---- Figure 6: the four candidate revenue drivers --------------------
pairs = [
    ("Average Meal Price", "Average meal price ($)"),
    ("Seating Capacity", "Seating capacity (seats)"),
    ("Marketing Budget", "Marketing budget ($)"),
    ("Social Media Followers", "Social media followers"),
]

fig, axes = plt.subplots(2, 2, figsize=(14.5, 9))
for ax, (col, label) in zip(axes.ravel(), pairs):
    sns.regplot(
        data=df, x=col, y="Revenue", ax=ax,
        scatter_kws=dict(s=9, alpha=0.22, color=SKY),
        line_kws=dict(color=CORAL, lw=2),
    )
    r = df[col].corr(df["Revenue"])
    ax.text(0.035, 0.93, f"r = {r:.2f}", transform=ax.transAxes,
            fontsize=11, fontweight="bold", color=INK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=GRID))
    style_ax(ax, title=f"Revenue vs {col.lower()}", xlabel=label, ylabel="Revenue ($)")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(money))
    if col in ("Average Meal Price", "Marketing Budget"):
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(money))
    elif col == "Social Media Followers":
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, p: f"{v/1000:.0f}K"))

fig.suptitle("Figure 6  |  Two tight linear relationships, two loose clouds",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.945, "Each dot is a restaurant. The red line is a simple linear fit.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.94])
save(fig, "fig06_scatter_relationships.png")
plt.show()
""")

md(r"""
### What the scatters show

* **Price vs revenue (r = 0.69)** - a tight, straight, upward band. Doubling the average check roughly doubles revenue.
* **Seats vs revenue (r = 0.68)** - equally tight. More seats means more revenue.
* **Marketing vs revenue (r = 0.37)** - a wide, fan-shaped cloud. Spending more is *associated* with more revenue, but the points are far from the line.
* **Followers vs revenue (r = 0.35)** - the same loose pattern.

Two tight relationships and two loose ones. That difference is important: price and seats behave like *mechanical* drivers of revenue, while marketing behaves like a *weak, noisy* one.

The next chart shows why price and seats are so strong - they multiply.
""")

code(r"""
# ---- Figure 7: the multiplicative structure --------------------------
from matplotlib.lines import Line2D

fig, ax = plt.subplots(figsize=(11, 6.4))
for loc in ["Downtown", "Suburban", "Rural"]:
    sub = df[df["Location"] == loc]
    ax.scatter(
        sub["Average Meal Price"], sub["Revenue"],
        s=sub["Seating Capacity"] * 0.95,
        color=LOC_COLORS[loc], alpha=0.22, linewidth=0, label=loc,
    )

handles = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=LOC_COLORS[l],
           markersize=9, label=l)
    for l in ["Downtown", "Suburban", "Rural"]
]
for seats in [40, 60, 80]:
    handles.append(
        Line2D([0], [0], marker="o", color="w", markerfacecolor=MUTED,
               markersize=np.sqrt(seats * 0.95), alpha=0.55, label=f"{seats} seats")
    )

ax.set_xlabel("Average meal price ($)")
ax.set_ylabel("Revenue ($)")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(money))
ax.yaxis.set_major_formatter(mtick.FuncFormatter(money))
style_ax(ax, "Figure 7  |  Revenue forms parallel bands: price sets the slope, seats set the height")
ax.legend(handles=handles, loc="upper left", title="Location / bubble size",
          title_fontsize=9, ncol=1)
fig.tight_layout()
save(fig, "fig07_bubble_price_seats.png")
plt.show()
""")

md(r"""
### The hidden structure becomes visible

Each bubble is a restaurant: **x = price, y = revenue, bubble size = seats, colour = location**.

* Within one colour (one size tier) the bubbles form a **straight diagonal band**: at a fixed seat count, revenue rises in direct proportion to price.
* The three colours form **parallel bands**, one above the other: at the same price, Downtown (bigger) restaurants earn more than Suburban, which earn more than Rural.
* The bands are almost perfectly straight and evenly spaced.

This is the visual signature of a **multiplicative relationship**, not an additive one: revenue ≈ constant x price x seats. Section 6 tests it numerically.
""")

code(r"""
# ---- Figure 8: correlation heatmap -----------------------------------
corr_cols = [
    "Revenue", "Average Meal Price", "Seating Capacity", "Marketing Budget",
    "Social Media Followers", "Weekend Reservations", "Weekday Reservations",
    "Rating", "Number of Reviews", "Avg Review Length", "Ambience Score",
    "Service Quality Score", "Chef Experience Years",
]
corr = df[corr_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))

fig, ax = plt.subplots(figsize=(11.5, 9))
sns.heatmap(
    corr, mask=mask, cmap="RdBu_r", vmin=-1, vmax=1,
    annot=True, fmt=".2f", annot_kws={"size": 7.6},
    linewidths=0.6, linecolor="white", square=True,
    cbar_kws={"shrink": 0.75, "label": "Pearson correlation"}, ax=ax,
)
ax.set_title("Figure 8  |  Correlation matrix: what moves with what", loc="left", pad=14)
ax.tick_params(axis="x", rotation=45, labelsize=9)
ax.tick_params(axis="y", rotation=0, labelsize=9)
fig.tight_layout()
save(fig, "fig08_correlation_heatmap.png")
plt.show()

print("Strongest correlations with Revenue")
print(df[corr_cols].corr()["Revenue"].drop("Revenue").sort_values(ascending=False).round(3).to_string())
""")

md(r"""
### Reading the heatmap

* **Revenue** is most correlated with **average meal price (0.69)** and **seating capacity (0.68)**, then marketing (0.37), followers (0.35) and reservations (0.27-0.29). It is essentially **uncorrelated with rating (0.01)**, reviews (-0.01), review length (-0.01), ambience (0.00), service (0.01) and chef experience (0.03).
* **Marketing budget and followers are correlated at 0.99** - they are effectively the same variable measured twice. Followers ≈ 11.7 x budget.
* **Seats and marketing are correlated at 0.51**: bigger venues spend more. This is the confounder that makes marketing *look* useful.
* **Reservations correlate with seats (0.42-0.44)** but not with price (-0.02) and not with rating (0.00).
* **Rating correlates with marketing (0.26) and followers (0.29)** - an unexpected link we will examine in Q4.

The heatmap gives us the map. The data-mining section that follows turns each clue into a tested question.
""")

md(r"""
---
## 6. Data mining - asking questions to find hidden patterns

Each question below follows the same structure:

1. **Question** - what we want to know.
2. **Method** - the technique used.
3. **Result** - the chart and the numbers.
4. **Insight** - what it means in simple English, and *why* it happened.

The questions:

| # | Question | Main technique |
|---|---|---|
| Q1 | Which variables actually determine revenue? | Correlation, R-squared comparison, multiple regression |
| Q2 | Does marketing spend pay off? | Quartile analysis, partial correlation, redundancy check |
| Q3 | Is location or cuisine the real advantage? | Revenue per seat, heatmap, ANOVA |
| Q4 | Do ratings, reviews and service matter? | Rating bands, correlation, partial correlation |
| Q5 | Does a higher price reduce demand? | Price deciles, reservation rate |
| Q6 | Are there hidden restaurant segments? | K-means clustering, elbow method |
| Q7 | Which restaurants over- or under-perform? | Residual / anomaly analysis |
| Q8 | Is revenue concentrated in a few winners? | Cumulative share (Pareto / Lorenz curve) |
""")

md(r"""
---
### Q1. Which variables actually determine revenue?

**Question:** if we could only use a few columns to explain revenue, which ones would they be?

**Method:** compare R-squared for single variables and combinations, then fit one multiple regression and compare the standardised coefficients.
""")

code(r"""
# ---- Q1a: how much variance each variable / combination explains ------
def r2_linear(x_cols):
    X = df[x_cols].astype(float)
    X = (X - X.mean()) / X.std()
    X.insert(0, "const", 1.0)
    A = X.to_numpy(float)
    y = df["Revenue"].to_numpy(float)
    coef = np.linalg.lstsq(A, y, rcond=None)[0]
    resid = y - A @ coef
    return 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))

models = pd.DataFrame({
    "model": ["Seats only", "Price only", "Seats + Price", "Seats x Price (product)"],
    "r2": [
        r2_linear(["Seating Capacity"]),
        r2_linear(["Average Meal Price"]),
        r2_linear(["Seating Capacity", "Average Meal Price"]),
        r2_linear(["Seats x Price"]),
    ],
})
models["r2_%"] = models["r2"] * 100

fig, ax = plt.subplots(figsize=(10.5, 4.8))
colors = [SKY, SKY, SKY, CORAL]
bars = ax.barh(models["model"], models["r2"] * 100, color=colors, height=0.58)
ax.bar_label(bars, labels=[f"{v:.1f}%" for v in models["r2_%"]], padding=5, fontsize=10)
ax.set_xlim(0, 112)
ax.invert_yaxis()
style_ax(ax, "Figure 9  |  One interaction beats all single variables",
         "Share of revenue variance explained (R-squared, %)", "")
ax.grid(axis="x", color=GRID)
ax.grid(axis="y", visible=False)

fig.text(0.01, -0.02,
         "Adding the two variables separately explains 95.7%. Multiplying them explains 99.93%.",
         fontsize=9, color=MUTED)
fig.tight_layout()
save(fig, "fig09_r2_comparison.png")
plt.show()

display(models.round(4))
""")

code(r"""
# ---- Q1b: multiple regression with standardised inputs ---------------
model_inputs = pd.DataFrame({
    "Seats": df["Seating Capacity"],
    "Meal price": df["Average Meal Price"],
    "Marketing budget": df["Marketing Budget"],
    "Weekend reservations": df["Weekend Reservations"],
    "Weekday reservations": df["Weekday Reservations"],
    "Rating": df["Rating"],
    "Chef experience": df["Chef Experience Years"],
    "Reviews": df["Number of Reviews"],
    "Avg review length": df["Avg Review Length"],
    "Ambience": df["Ambience Score"],
    "Service": df["Service Quality Score"],
})
model_inputs["Suburban"] = (df["Location"] == "Suburban").astype(int)
model_inputs["Downtown"] = (df["Location"] == "Downtown").astype(int)
for cuisine in ["American", "French", "Indian", "Italian", "Japanese"]:
    model_inputs[cuisine] = (df["Cuisine"] == cuisine).astype(int)
model_inputs["Parking"] = (df["Parking Availability"] == "Yes").astype(int)


def ols_standardised(y, X):
    Xz = (X.astype(float) - X.mean()) / X.std()
    Xz.insert(0, "Intercept", 1.0)
    A = Xz.to_numpy(float)
    yv = y.to_numpy(float)
    coef = np.linalg.lstsq(A, yv, rcond=None)[0]
    resid = yv - A @ coef
    n, p = A.shape
    dof = n - p
    sigma2 = resid @ resid / dof
    cov = sigma2 * np.linalg.pinv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    tvals = coef / se
    pvals = 2 * stats.t.sf(np.abs(tvals), dof)
    ss_tot = ((yv - yv.mean()) ** 2).sum()
    r2 = 1 - (resid @ resid) / ss_tot
    adj_r2 = 1 - (1 - r2) * (n - 1) / dof
    table = pd.DataFrame({
        "feature": Xz.columns, "coef_std": coef, "t": tvals, "p": pvals
    })
    return table, r2, adj_r2, resid


coef_table, r2_full, adj_r2_full, resid_full = ols_standardised(df["Revenue"], model_inputs)
print(f"Regression R-squared: {r2_full:.4f}   Adjusted R-squared: {adj_r2_full:.4f}")

coef_view = coef_table[coef_table["feature"] != "Intercept"].copy()
coef_view["abs"] = coef_view["coef_std"].abs()
top10 = coef_view.nlargest(10, "abs").sort_values("coef_std")

fig, ax = plt.subplots(figsize=(10.5, 5.8))
colors = [TEAL if v > 0 else CORAL for v in top10["coef_std"]]
bars = ax.barh(top10["feature"], top10["coef_std"], color=colors, height=0.62)
labels = [f"{v/1000:+.0f}K" for v in top10["coef_std"]]
ax.bar_label(bars, labels=labels, padding=5, fontsize=9)
ax.axvline(0, color=INK, lw=0.9)
ax.set_xlim(min(0, top10["coef_std"].min() * 1.35), top10["coef_std"].max() * 1.25)
style_ax(ax, "Figure 10  |  Standardised regression: seats and price dominate",
         "Change in annual revenue per 1 standard deviation increase ($)", "")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(money))
ax.grid(axis="x", color=GRID)
ax.grid(axis="y", visible=False)
fig.text(0.01, -0.03,
         "Each coefficient holds the other variables constant. Non-significant effects are near zero.",
         fontsize=9, color=MUTED)
fig.tight_layout()
save(fig, "fig10_coefficients.png")
plt.show()

print("\nFull coefficient table (sorted by absolute effect)")
display(coef_view.drop(columns="abs").sort_values("coef_std", ascending=False).round(4))
""")

code(r"""
# ---- Q1c: the two-variable model vs reality --------------------------
X_prod = np.column_stack([np.ones(len(df)), df["Seats x Price"].to_numpy(float)])
y = df["Revenue"].to_numpy(float)
coef_prod = np.linalg.lstsq(X_prod, y, rcond=None)[0]
df["Predicted Revenue"] = X_prod @ coef_prod
df["Residual %"] = (df["Revenue"] - df["Predicted Revenue"]) / df["Predicted Revenue"] * 100

r2_prod = 1 - ((y - df["Predicted Revenue"]) ** 2).sum() / ((y - y.mean()) ** 2).sum()

fig, ax = plt.subplots(figsize=(9.5, 6))
ax.scatter(df["Predicted Revenue"], df["Revenue"], s=10, alpha=0.22,
           color=TEAL, linewidth=0)
lims = [0, df["Revenue"].max() * 1.06]
ax.plot(lims, lims, color=CORAL, lw=1.8, ls="--", label="perfect prediction")
ax.set_xlim(lims)
ax.set_ylim(lims)
ax.xaxis.set_major_formatter(mtick.FuncFormatter(money))
ax.yaxis.set_major_formatter(mtick.FuncFormatter(money))
style_ax(ax, "Figure 11  |  Two columns predict almost every restaurant's revenue",
         "Predicted revenue = seats x price (fitted) ($)", "Actual revenue ($)")
ax.text(0.05, 0.9,
        f"R-squared = {r2_prod:.4f}\nTypical error = 1.3% of revenue",
        transform=ax.transAxes, fontsize=11, color=INK,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=GRID))
ax.legend(loc="lower right")
fig.tight_layout()
save(fig, "fig11_actual_vs_predicted.png")
plt.show()

print(f"Fitted equation: Revenue = {coef_prod[0]:,.0f} + {coef_prod[1]:.2f} x (seats x price)")
print(f"R-squared: {r2_prod:.6f}")
print(f"Residual standard deviation: {df['Residual %'].std():.2f}% of predicted revenue")
""")

md(r"""
### Q1 findings - revenue is a capacity-and-price equation

| Model | R-squared | Interpretation |
|---|---|---|
| Seats only | 0.459 | Size explains about half of revenue |
| Price only | 0.471 | Price explains about half of revenue |
| Seats + price (additive) | 0.957 | Together they explain almost all of it |
| **Seats x price (product)** | **0.9993** | The *interaction* is the real mechanism |

**The pattern:** Revenue ≈ **229 x Seating Capacity x Average Meal Price** (the median ratio is 228.4). Fitted on this data, the line is `Revenue = 20,175 + 221.0 x (seats x price)`, which is the same relationship with a small base amount. The typical error is only **1.3%**.

**What the equation means in plain English:** each seat generates about **229 times the average meal price per year**. With an average check of $50, one seat brings in about $11,500 a year; a 60-seat restaurant therefore earns roughly $690K. The 229 is effectively the number of "meal turns" per seat per year (about 4.4 per week).

**Why the interaction matters:** seats and price are not two separate add-ons - they multiply. A restaurant with 80 seats at $70 earns far more than the sum of its parts, because every one of those seats sells the expensive menu.

**The regression confirms it:**

| Driver | Effect of a 1 SD increase | Significant? |
|---|---|---|
| Seating capacity (+17 seats) | **+$185,557** | Yes (p < 0.001) |
| Average meal price (+$14.34) | **+$191,335** | Yes (p < 0.001) |
| Chef experience (+5.5 years) | +$5,096 | Yes, but tiny |
| Marketing budget (+$1,825) | +$4,257 | Yes, but tiny |
| Rating, ambience, service, reviews, location, cuisine, parking | between -$3,017 and +$959 | **No** |

Once seats and price are in the model, **location and cuisine lose all significance** (p > 0.29). That is the smoking gun: they were only proxies for size and price.

**Caveats:** an R-squared of 0.999 is not normal in real business data. It is a strong sign that this dataset was simulated with a revenue formula. The finding describes *this* dataset very well; it should not be assumed to hold in the real restaurant industry without new data.

**Inputs:** `Seating Capacity`, `Average Meal Price`, and 17 other columns for the regression.
**Outputs:** R-squared comparison, standardised coefficients, a predictive equation and residuals.
""")

md(r"""
---
### Q2. Does marketing spend actually pay off?

**Question:** restaurants with bigger marketing budgets earn more. But is that because marketing works, or because bigger restaurants can afford bigger budgets?

**Method:** compare revenue across marketing quartiles, then compute the **partial correlation** - the relationship that remains after removing the effect of size and price.
""")

code(r"""
# ---- Q2a: marketing quartiles and the follower redundancy ------------
df["Marketing Quartile"] = pd.qcut(
    df["Marketing Budget"], 4, labels=["Q1 lowest", "Q2", "Q3", "Q4 highest"]
)
mq = df.groupby("Marketing Quartile", observed=True).agg(
    restaurants=("Revenue", "size"),
    budget=("Marketing Budget", "mean"),
    followers=("Social Media Followers", "mean"),
    revenue=("Revenue", "mean"),
    seats=("Seating Capacity", "mean"),
    revenue_per_mkt=("Revenue per Marketing Dollar", "mean"),
    rating=("Rating", "mean"),
)

fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
q_labels = mq.index.astype(str)
grad = ["#C9E4E2", "#8FCBC7", "#55B1AC", TEAL]

b1 = axes[0].bar(q_labels, mq["revenue"], color=grad, width=0.64)
axes[0].bar_label(b1, labels=[f"${v/1000:.0f}K" for v in mq["revenue"]], padding=3, fontsize=9)
axes[0].yaxis.set_major_formatter(mtick.FuncFormatter(money))
axes[0].set_ylim(0, mq["revenue"].max() * 1.2)
style_ax(axes[0], "Average revenue by marketing quartile", "", "Average revenue ($)")
axes[0].tick_params(axis="x", rotation=12)

b2 = axes[1].bar(q_labels, mq["revenue_per_mkt"], color=grad[::-1], width=0.64)
axes[1].bar_label(b2, labels=[f"${v:.0f}" for v in mq["revenue_per_mkt"]], padding=3, fontsize=9)
axes[1].set_ylim(0, mq["revenue_per_mkt"].max() * 1.2)
style_ax(axes[1], "Revenue per marketing dollar", "", "Revenue per $ spent ($)")
axes[1].tick_params(axis="x", rotation=12)

sample = df.sample(3500, random_state=3)
axes[2].scatter(sample["Marketing Budget"], sample["Social Media Followers"],
                s=14, alpha=0.25, color=PLUM, linewidth=0)
line_x = np.linspace(df["Marketing Budget"].min(), df["Marketing Budget"].max(), 100)
axes[2].plot(line_x, 11.7 * line_x, color=CORAL, lw=1.8, ls="--")
axes[2].text(0.05, 0.9, f"r = {df['Marketing Budget'].corr(df['Social Media Followers']):.2f}",
             transform=axes[2].transAxes, fontsize=11, fontweight="bold", color=INK)
axes[2].xaxis.set_major_formatter(mtick.FuncFormatter(money))
axes[2].yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, p: f"{v/1000:.0f}K"))
style_ax(axes[2], "Followers are a copy of the budget", "Marketing budget ($)", "Followers")

fig.suptitle("Figure 12  |  Marketing looks effective until you notice who is doing the spending",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.94, "Top-quartile spenders also have far more seats, so their higher revenue is not evidence that marketing caused it.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.9])
save(fig, "fig12_marketing_quartiles.png")
plt.show()

display(mq.round(1))
""")

code(r"""
# ---- Q2b: partial correlation removes the size effect ----------------
def partial_corr(x_col, y_col, controls):
    Z = df[controls].astype(float)
    Z = (Z - Z.mean()) / Z.std()
    Z.insert(0, "const", 1.0)
    A = Z.to_numpy(float)
    xv = df[x_col].to_numpy(float)
    yv = df[y_col].to_numpy(float)
    rx = xv - A @ np.linalg.lstsq(A, xv, rcond=None)[0]
    ry = yv - A @ np.linalg.lstsq(A, yv, rcond=None)[0]
    r, p = stats.pearsonr(rx, ry)
    return r, p

raw_r, raw_p = stats.pearsonr(df["Marketing Budget"], df["Revenue"])
r_seats, p_seats = partial_corr("Marketing Budget", "Revenue", ["Seating Capacity"])
r_price, p_price = partial_corr("Marketing Budget", "Revenue", ["Average Meal Price"])
r_both, p_both = partial_corr("Marketing Budget", "Revenue", ["Seating Capacity", "Average Meal Price"])

partials = pd.DataFrame({
    "view": ["Raw correlation", "After controlling for seats", "After controlling for price",
             "After controlling for seats + price"],
    "r": [raw_r, r_seats, r_price, r_both],
    "p": [raw_p, p_seats, p_price, p_both],
})

fig, ax = plt.subplots(figsize=(10.5, 4.8))
colors = [TEAL, CORAL, CORAL, CORAL]
bars = ax.barh(partials["view"], partials["r"], color=colors, height=0.55)
ax.bar_label(bars, labels=[f"r = {v:.3f}" for v in partials["r"]], padding=5, fontsize=10)
ax.axvline(0, color=INK, lw=0.9)
ax.set_xlim(0, 0.58)
ax.invert_yaxis()
style_ax(ax, "Figure 13  |  Marketing's link to revenue collapses once size is controlled",
         "Correlation with revenue (r)", "")
ax.grid(axis="x", color=GRID)
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "fig13_partial_correlation.png")
plt.show()

display(partials.round(4))

r2_mkt_added = r2_linear(["Seating Capacity", "Average Meal Price", "Marketing Budget"]) - r2_linear(["Seating Capacity", "Average Meal Price"])
print(f"R-squared added by marketing on top of seats + price: {r2_mkt_added:.5f}")
_ratio = df["Social Media Followers"] / df["Marketing Budget"]
print(f"Followers / marketing budget ratio: mean {_ratio.mean():.2f}, median {_ratio.median():.2f}")
""")

md(r"""
### Q2 findings - marketing mostly tracks size, not sales

| Evidence | Number | What it says |
|---|---|---|
| Raw correlation | r = **0.365** | Bigger budgets do go with bigger revenue |
| Revenue by marketing quartile | $575K → $607K → $632K → **$810K** | Top spenders earn 41% more |
| But their seat count also rises | 52 → 56 → 58 → **75 seats** | The top quartile is simply a bigger-restaurant group |
| After controlling for seats | r = **0.032** | Almost nothing left |
| After controlling for seats + price | r = **0.063** | Still tiny (0.4% of the remaining variation) |
| Extra R-squared from marketing | **0.00017** | 0.02% - practically zero |
| Followers vs marketing budget | r = **0.99**, followers ≈ 11.7 x budget | The same information twice |

**The trap:** the first bar chart looks like a success story - spend more, earn 41% more. The middle chart (revenue per marketing dollar) already looks odd: the biggest spenders get the *lowest* return per dollar ($144) and the smallest spenders the highest ($450). That is what you expect when the "return" is really just venue size.

**Why it happens:** location drives size, size drives both marketing spend and revenue. Marketing is a **passenger**, not the driver. Statisticians call this **confounding**; the partial correlation is the tool that exposes it.

**What it means:** this dataset provides **no evidence that increasing marketing spend would increase revenue**. It may still do so in reality - but this cross-sectional data cannot prove it. To test marketing properly you need campaigns over time, a control group, and a measure of incremental revenue. Also, followers should not be used as a KPI: they add no information beyond the budget.

**Inputs:** `Marketing Budget`, `Social Media Followers`, `Seating Capacity`, `Average Meal Price`, `Revenue`.
**Outputs:** quartile profiles, raw vs partial correlations, incremental R-squared, redundancy ratio.
""")

md(r"""
---
### Q3. Is location or cuisine the real advantage?

**Question:** Downtown restaurants earn roughly twice as much as Rural ones, and Japanese restaurants earn twice as much as Mexican ones. Which of these differences is a genuine market advantage, and which is just a proxy for size and price?

**Method:** compare **revenue per seat** (which removes the effect of size) across cuisine and location, and test the group differences with one-way ANOVA.
""")

code(r"""
# ---- Q3: market structure --------------------------------------------
rps_cui = df.groupby("Cuisine")["Revenue per Seat"].mean().sort_values(ascending=False)
rps_loc = df.groupby("Location")["Revenue per Seat"].mean()
pivot = df.pivot_table(index="Cuisine", columns="Location",
                       values="Revenue per Seat", aggfunc="mean").reindex(rps_cui.index)

fig, axes = plt.subplots(1, 2, figsize=(15, 5.8),
                         gridspec_kw={"width_ratios": [1.05, 1]})

bars = axes[0].bar(rps_cui.index, rps_cui.values,
                   color=[CUI_COLORS[c] for c in rps_cui.index], width=0.66)
axes[0].bar_label(bars, labels=[f"${v/1000:.1f}K" for v in rps_cui.values], padding=3, fontsize=9)
axes[0].set_ylim(0, rps_cui.max() * 1.18)
axes[0].yaxis.set_major_formatter(mtick.FuncFormatter(money))
style_ax(axes[0], "Revenue per seat by cuisine", "", "Revenue per seat ($)")
axes[0].tick_params(axis="x", rotation=15)

sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu",
            linewidths=2, linecolor="white", cbar_kws={"label": "Revenue per seat ($)"},
            ax=axes[1], annot_kws={"fontsize": 10})
axes[1].set_title("Revenue per seat: cuisine x location", loc="left")
axes[1].set_xlabel("")
axes[1].set_ylabel("")
axes[1].tick_params(axis="x", rotation=0)
axes[1].tick_params(axis="y", rotation=0)

fig.suptitle("Figure 14  |  Cuisine changes productivity per seat; location barely does",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.925, "Each cell is the average revenue generated by one seat per year.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.92])
save(fig, "fig14_market_structure.png")
plt.show()

anova_cui = stats.f_oneway(*[g["Revenue per Seat"].values for _, g in df.groupby("Cuisine")])
anova_loc = stats.f_oneway(*[g["Revenue per Seat"].values for _, g in df.groupby("Location")])
print(f"ANOVA revenue per seat by cuisine : F = {anova_cui.statistic:,.1f}, p = {anova_cui.pvalue:.3g}")
print(f"ANOVA revenue per seat by location: F = {anova_loc.statistic:,.1f}, p = {anova_loc.pvalue:.3g}")
print()
print(pd.DataFrame({
    "average revenue per seat": rps_loc.round(0),
    "average seats": df.groupby("Location")["Seating Capacity"].mean().round(1),
    "average revenue": df.groupby("Location")["Revenue"].mean().round(0),
}).reindex(["Downtown", "Suburban", "Rural"]))
""")

md(r"""
### Q3 findings - cuisine is a real per-seat advantage; location is size in disguise

**Cuisine:** revenue per seat ranges from **$7,096 (Mexican)** to **$15,916 (Japanese)** - a **2.24x** gap that survives after removing size (F = 31,208, p < 0.001). The heatmap shows the same cuisine ordering in every location; the columns are almost identical ($9,225 vs $9,462 vs $9,264 for American, for example).

**Location:** revenue per seat barely moves - **$10,784 (Suburban) to $11,250 (Rural)**, a **4%** spread. The ANOVA p-value is small (0.000000009) only because 8,368 rows make even tiny differences detectable; the *effect size* is negligible. The raw revenue gap ($866K vs $450K) disappears once you look per seat, because Downtown has 80 seats and Rural has 40.

**Why it happens:** in this dataset, cuisine determines the average check and location determines the seating capacity. Each "market" label is really a proxy for a structural lever:

* Cuisine → **price** → revenue per seat.
* Location → **seats** → number of revenue-generating units.

**What it means:** moving a restaurant Downtown would not make each seat more productive in this data. Choosing a premium menu position (and delivering a product that supports it) has more leverage on revenue per seat than location. In the real world, location affects footfall, rent and competition - none of which are measured here.

**Inputs:** `Cuisine`, `Location`, `Revenue`, `Seating Capacity`.
**Outputs:** revenue per seat by group, cuisine x location heatmap, ANOVA F and p values.
""")
