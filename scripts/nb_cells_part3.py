"""Notebook cells, part 3: Q4-Q8, summary, deliverables, export."""

CELLS = []


def md(text):
    CELLS.append(("md", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n")))


md(r"""
---
### Q4. Do ratings, reviews, ambience and service matter?

**Question:** do better-rated, better-reviewed and better-designed restaurants earn more?

**Method:** compare revenue across rating bands, correlate every reputation variable with revenue, and check the unexpected link between ratings and marketing spend.
""")

code(r"""
# ---- Q4: reputation variables vs revenue -----------------------------
rating_band = df.groupby("Rating Band", observed=True).agg(
    revenue=("Revenue", "mean"), restaurants=("Revenue", "size")
)
rep_vars = ["Rating", "Number of Reviews", "Avg Review Length",
            "Ambience Score", "Service Quality Score", "Chef Experience Years"]
rep_corr = pd.Series({v: df[v].corr(df["Revenue"]) for v in rep_vars})
mq_rating = df.groupby("Marketing Quartile", observed=True)["Rating"].mean()

fig, axes = plt.subplots(1, 3, figsize=(16, 5.3))

bars = axes[0].bar(rating_band.index.astype(str), rating_band["revenue"],
                   color=[CORAL, AMBER, TEAL, SKY], width=0.62)
axes[0].bar_label(bars, labels=[f"${v/1000:.0f}K" for v in rating_band["revenue"]],
                  padding=3, fontsize=9)
axes[0].set_ylim(0, 820_000)
axes[0].yaxis.set_major_formatter(mtick.FuncFormatter(money))
style_ax(axes[0], "Average revenue by rating band", "Rating band", "Average revenue ($)")

colors = [TEAL if v > 0 else CORAL for v in rep_corr.values]
bars = axes[1].barh(rep_corr.index, rep_corr.values, color=colors, height=0.55)
axes[1].bar_label(bars, labels=[f"{v:+.3f}" for v in rep_corr.values], padding=4, fontsize=9)
axes[1].axvline(0, color=INK, lw=0.9)
axes[1].set_xlim(-0.06, 0.06)
style_ax(axes[1], "Correlation with revenue", "Pearson r", "")
axes[1].grid(axis="x", color=GRID)
axes[1].grid(axis="y", visible=False)

axes[2].plot(mq_rating.index.astype(str), mq_rating.values, marker="o",
             markersize=8, color=PLUM, lw=2.5)
for x, v in enumerate(mq_rating.values):
    axes[2].annotate(f"{v:.2f}", (x, v), textcoords="offset points", xytext=(0, 10),
                     ha="center", fontsize=9, color=INK)
axes[2].set_ylim(3.6, 4.4)
style_ax(axes[2], "Ratings rise with marketing spend", "Marketing quartile", "Average rating")
axes[2].tick_params(axis="x", rotation=12)

fig.suptitle("Figure 15  |  Reputation does not move revenue - but it does follow marketing",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.93, "Left: revenue is flat across rating bands. Middle: every reputation correlation is near zero. Right: ratings climb with marketing budget.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.9])
save(fig, "fig15_reputation.png")
plt.show()

display(rating_band.round(0))
print("\nRating by marketing quartile:")
print(mq_rating.round(3))
print(f"\nRating vs marketing budget: r = {df['Rating'].corr(df['Marketing Budget']):.3f}")
print(f"Rating vs followers:        r = {df['Rating'].corr(df['Social Media Followers']):.3f}")
""")

md(r"""
### Q4 findings - impressive scores, zero revenue effect

| Rating band | Restaurants | Average revenue |
|---|---|---|
| 3.0-3.5 | 2,269 | $651,952 |
| 3.5-4.0 | 2,080 | $660,952 |
| 4.0-4.5 | 2,092 | $655,579 |
| 4.5-5.0 | 1,927 | $656,184 |

The spread between the best and worst band is **1.4%** - noise. All correlations with revenue are effectively zero: rating **+0.010**, number of reviews **-0.008**, review length **-0.011**, ambience **+0.003**, service **+0.005**, chef experience **+0.027**.

**The strange part:** ratings are *not* random in every sense. They rise steadily with marketing spend - from **3.84** in the lowest marketing quartile to **4.20** in the highest (r = 0.26, and 0.30 after controlling for size). Restaurants that spend more on marketing get slightly better ratings.

**Why it happens:** in this dataset, revenue is generated from seats and price; ratings and experience scores sit outside that equation. Ratings look as if they were generated from a uniform random score plus a small marketing-related boost. A plausible real-world mechanism is that marketing generates more reviews and visibility, which nudges the average rating - but the data cannot prove that.

**What it means:** do not expect a revenue lift from a rating improvement *in this dataset*. Treat ratings as a reputation and retention metric, and investigate whether marketing's real benefit is reputational rather than immediate sales.

**Inputs:** `Rating`, `Number of Reviews`, `Avg Review Length`, `Ambience Score`, `Service Quality Score`, `Chef Experience Years`, `Marketing Budget`, `Revenue`.
**Outputs:** revenue by rating band, correlation bars, rating by marketing quartile.
""")

md(r"""
---
### Q5. Does a higher price reduce demand?

**Question:** in a normal market, raising prices loses customers. Is there any sign of that here, or do higher-priced restaurants keep their bookings?

**Method:** split restaurants into ten price deciles and compare revenue per seat and reservation rate.
""")

code(r"""
# ---- Q5: price vs demand ---------------------------------------------
df["Price Decile"] = pd.qcut(df["Average Meal Price"], 10, labels=False) + 1
price_stats = df.groupby("Price Decile").agg(
    average_price=("Average Meal Price", "mean"),
    revenue_per_seat=("Revenue per Seat", "mean"),
    reservation_rate=("Reservation Rate", "mean"),
    revenue=("Revenue", "mean"),
)

fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.4))

axes[0].plot(price_stats["average_price"], price_stats["revenue_per_seat"],
             marker="o", markersize=7, color=TEAL, lw=2.6)
axes[0].fill_between(price_stats["average_price"], price_stats["revenue_per_seat"],
                     color=TEAL, alpha=0.10)
axes[0].yaxis.set_major_formatter(mtick.FuncFormatter(money))
axes[0].xaxis.set_major_formatter(mtick.FuncFormatter(money))
r_rps = df["Average Meal Price"].corr(df["Revenue per Seat"])
axes[0].text(0.05, 0.9, f"r = {r_rps:.3f}", transform=axes[0].transAxes,
             fontsize=11, fontweight="bold", color=INK)
style_ax(axes[0], "Revenue per seat rises with price", "Average meal price ($)",
         "Revenue per seat ($)")

axes[1].plot(price_stats["average_price"], price_stats["reservation_rate"],
             marker="o", markersize=7, color=CORAL, lw=2.6)
axes[1].axhline(df["Reservation Rate"].mean(), color=MUTED, ls="--", lw=1.2,
                label=f"overall mean = {df['Reservation Rate'].mean():.2f}")
axes[1].set_ylim(0.8, 1.15)
axes[1].xaxis.set_major_formatter(mtick.FuncFormatter(money))
r_dem = df["Average Meal Price"].corr(df["Reservation Rate"])
axes[1].text(0.05, 0.12, f"r = {r_dem:.3f}", transform=axes[1].transAxes,
             fontsize=11, fontweight="bold", color=INK)
style_ax(axes[1], "...while booking intensity stays flat", "Average meal price ($)",
         "Reservations per seat")
axes[1].legend(loc="upper right")

fig.suptitle("Figure 16  |  Higher prices do not cost covers in this data",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.93, "Each point is one tenth of the restaurants, ordered by price.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.9])
save(fig, "fig16_price_demand.png")
plt.show()

display(price_stats.round(2))
print(f"Price vs total reservations: r = {df['Average Meal Price'].corr(df['Total Reservations']):.3f}")
print(f"Price vs reservation rate:   r = {df['Average Meal Price'].corr(df['Reservation Rate']):.3f}")
print(f"Reservations above seating capacity: "
      f"{int(((df['Weekend Reservations'] > df['Seating Capacity']) | (df['Weekday Reservations'] > df['Seating Capacity'])).sum())}")
""")

md(r"""
### Q5 findings - demand is price-insensitive here

* **Revenue per seat rises almost perfectly with price** (r = **0.999**): every extra $10 on the average check adds about **$2,200 of revenue per seat per year**.
* **Booking intensity is flat across price deciles** (r = **-0.03** for total bookings, **-0.02** for bookings per seat): the cheapest and most expensive restaurants both fill about **0.96-0.99 bookings per seat** across the week.
* **No reservation ever exceeds seating capacity**, so there is no sign of queues or unmet demand at high prices - and no sign of empty tables at low prices.

**Why it happens:** in this dataset, reservations were generated around capacity, not as a response to price. Price and demand are independent by construction. That makes price a "free" revenue lever in the data: raising it does not reduce covers.

**What it means:** a 10% price increase would raise revenue by roughly 10% with no volume loss *in this dataset*. A real restaurant should not assume that: price elasticity depends on competition, income, alternatives and quality perception, none of which are in the file. Treat this as a hypothesis to test with real transaction data, not a pricing recommendation.

**Inputs:** `Average Meal Price`, `Revenue`, `Revenue per Seat`, `Weekend/Weekday Reservations`, `Seating Capacity`.
**Outputs:** price-decile curves, correlations, consistency check.
""")

md(r"""
---
### Q6. Are there hidden restaurant segments?

**Question:** can we group restaurants into a small number of understandable business segments, instead of treating 8,368 rows as one market?

**Method:** K-means clustering on the two structural variables (standardised price and seats), with the elbow method to choose *k*. We then profile each cluster.
""")

code(r"""
# ---- Q6: K-means segmentation ----------------------------------------
feat_cols = ["Average Meal Price", "Seating Capacity"]
Z = (df[feat_cols] - df[feat_cols].mean()) / df[feat_cols].std()
Zv = Z.to_numpy(float)

ks = list(range(2, 9))
inertias = []
for k in ks:
    best_inertia = np.inf
    for seed in range(10):
        cents, lab = vq.kmeans2(Zv, k, iter=100, minit="++", seed=seed)
        if (lab < 0).any():
            continue
        d = ((Zv[:, None, :] - cents[None, :, :]) ** 2).sum(2).min(1).sum()
        best_inertia = min(best_inertia, d)
    inertias.append(best_inertia)

best = None
for seed in range(30):
    cents, lab = vq.kmeans2(Zv, 4, iter=200, minit="++", seed=seed)
    if (lab < 0).any():
        continue
    d = ((Zv[:, None, :] - cents[None, :, :]) ** 2).sum(2).min(1).sum()
    if best is None or d < best[0]:
        best = (d, lab)

df["Segment"] = best[1]

prof = df.groupby("Segment").agg(
    restaurants=("Revenue", "size"),
    seats=("Seating Capacity", "mean"),
    price=("Average Meal Price", "mean"),
    revenue=("Revenue", "mean"),
    revenue_per_seat=("Revenue per Seat", "mean"),
    marketing=("Marketing Budget", "mean"),
)
prof["share_%"] = prof["restaurants"] / len(df) * 100
prof["top_location"] = df.groupby("Segment")["Location"].agg(lambda s: s.value_counts().index[0])

med_seats = df["Seating Capacity"].median()
med_price = df["Average Meal Price"].median()
label_map = {}
for seg, row in prof.iterrows():
    size = "Large" if row["seats"] >= med_seats else "Compact"
    tier = "premium" if row["price"] >= med_price else "value"
    label_map[seg] = f"S{seg + 1}: {size} / {tier}"
df["Segment Label"] = df["Segment"].map(label_map)
prof["label"] = prof.index.map(label_map)

order = prof.sort_values("revenue", ascending=False).index.tolist()
seg_colors = dict(zip([label_map[s] for s in order], [NAVY, CORAL, TEAL, AMBER]))

fig, axes = plt.subplots(1, 3, figsize=(17, 5.4),
                         gridspec_kw={"width_ratios": [0.9, 1.15, 1]})

axes[0].plot(ks, inertias, marker="o", color=PLUM, lw=2.4)
axes[0].axvline(4, color=CORAL, ls="--", lw=1.4)
axes[0].annotate("k = 4 chosen", xy=(4, inertias[2]), xytext=(4.4, inertias[0] * 0.7),
                 fontsize=9, color=CORAL,
                 arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.2))
style_ax(axes[0], "Elbow curve", "Number of clusters (k)", "Within-cluster distance")
axes[0].set_xticks(ks)

for seg in order:
    sub = df[df["Segment"] == seg]
    axes[1].scatter(sub["Average Meal Price"], sub["Seating Capacity"], s=11,
                    alpha=0.42, color=seg_colors[label_map[seg]],
                    linewidth=0, label=label_map[seg])
axes[1].set_xlabel("Average meal price ($)")
axes[1].set_ylabel("Seating capacity (seats)")
axes[1].xaxis.set_major_formatter(mtick.FuncFormatter(money))
style_ax(axes[1], "The four segments are a price x size grid")
axes[1].legend(loc="upper left", fontsize=8, title="Segment", title_fontsize=8)

rev_sorted = prof.loc[order, "revenue"]
bars = axes[2].bar([label_map[s] for s in order], rev_sorted,
                   color=[seg_colors[label_map[s]] for s in order], width=0.64)
axes[2].bar_label(bars, labels=[f"${v/1000:.0f}K" for v in rev_sorted], padding=3, fontsize=9)
axes[2].set_ylim(0, rev_sorted.max() * 1.18)
axes[2].yaxis.set_major_formatter(mtick.FuncFormatter(money))
style_ax(axes[2], "Average revenue per segment", "", "Average revenue ($)")
axes[2].tick_params(axis="x", rotation=18)

fig.suptitle("Figure 17  |  Four understandable segments, and a 2.7x revenue ladder",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.93, "Segments are defined only by price and seats; revenue is the outcome, not an input.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.9])
save(fig, "fig17_segments.png")
plt.show()

display(prof[["label", "restaurants", "share_%", "seats", "price", "revenue",
              "revenue_per_seat", "top_location"]].round(1))
""")

md(r"""
### Q6 findings - the market is a 2x2 grid, not a mystery

| Segment | Restaurants | Avg seats | Avg price | Avg revenue | Revenue per seat |
|---|---|---|---|---|---|
| **S1: Large / premium** | 1,771 | 74.9 | $62.50 | **$1,053,753** | $14,070 |
| **S2: Large / value** | 2,419 | 75.5 | $37.10 | $641,237 | $8,491 |
| **S3: Compact / premium** | 1,796 | 44.2 | $62.60 | $631,370 | $14,288 |
| **S4: Compact / value** | 2,382 | 45.8 | $36.90 | $394,085 | $8,615 |

*(Exact counts and means are printed in the table above; they may differ by a few units if the clustering seed changes.)*

**The pattern:** four clear quadrants, and revenue falls in a **2.7x ladder** from Large/premium to Compact/value. The two middle segments earn almost the same ($641K vs $631K) from opposite strategies: **Large/value** sells many cheap covers; **Compact/premium** sells few expensive ones.

**Why it happens:** this is the same seats x price mechanism from Q1, now expressed as groups. Clustering simply rediscovers the two structural axes. The elbow curve has no sharp break - the data has no additional hidden dimensions beyond price and size.

**What it means:** segment-specific strategy:

* **Large / premium:** protect the price position; the risk is trading down.
* **Large / value:** volume game; small price changes move a lot of revenue.
* **Compact / premium:** highest revenue per seat; focus on turning tables and protecting quality.
* **Compact / value:** the most fragile; limited room to cut price, so growth must come from price mix or capacity.

**Inputs:** `Average Meal Price`, `Seating Capacity` (revenue used only for profiling, never for clustering).
**Outputs:** elbow curve, cluster labels, segment profiles and revenue ladder.
""")

md(r"""
---
### Q7. Which restaurants over- or under-perform?

**Question:** after accounting for seats and price, which restaurants earn more or less than expected - and are there genuine anomalies?

**Method:** fit the seats x price model, compute the percentage residual for each restaurant, and inspect the extremes.
""")

code(r"""
# ---- Q7: residual and anomaly analysis -------------------------------
fig, axes = plt.subplots(1, 2, figsize=(15, 5.6),
                         gridspec_kw={"width_ratios": [1, 1.2]})

sns.histplot(df["Residual %"], bins=50, kde=True, color=TEAL, alpha=0.65,
             edgecolor="white", linewidth=0.3, ax=axes[0])
axes[0].axvline(0, color=INK, lw=1.2)
axes[0].axvline(df["Residual %"].quantile(0.01), color=CORAL, ls="--", lw=1.1)
axes[0].axvline(df["Residual %"].quantile(0.99), color=CORAL, ls="--", lw=1.1)
axes[0].text(0.04, 0.9, f"95% of restaurants fall\nwithin +/- {df['Residual %'].quantile(0.975):.1f}%",
             transform=axes[0].transAxes, fontsize=9, color=INK)
style_ax(axes[0], "How far each restaurant is from the model",
         "Residual (% of predicted revenue)", "Restaurants")

axes[1].scatter(df["Predicted Revenue"], df["Revenue"], s=10, alpha=0.22,
                color=SKY, linewidth=0)
lims = np.array([df["Predicted Revenue"].min() * 0.9, df["Predicted Revenue"].max() * 1.05])
axes[1].plot(lims, lims, color=INK, lw=1.4, ls="--", label="expected")
axes[1].plot(lims, lims * 1.05, color=CORAL, lw=1.2, ls=":", label="+5%")
axes[1].plot(lims, lims * 0.95, color=CORAL, lw=1.2, ls=":", label="-5%")
axes[1].set_xlim(lims)
axes[1].set_ylim(lims)
axes[1].xaxis.set_major_formatter(mtick.FuncFormatter(money))
axes[1].yaxis.set_major_formatter(mtick.FuncFormatter(money))
style_ax(axes[1], "Every restaurant is close to its expected revenue",
         "Predicted revenue ($)", "Actual revenue ($)")
axes[1].legend(loc="lower right", fontsize=8)

fig.suptitle("Figure 18  |  No true anomalies: the largest deviation is about 5.6%",
             x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
fig.text(0.01, 0.93, "Residual = actual revenue minus the revenue expected from seats x price.",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=[0, 0, 1, 0.9])
save(fig, "fig18_residuals.png")
plt.show()

show_cols = ["Name", "Location", "Cuisine", "Seating Capacity", "Average Meal Price",
             "Revenue", "Residual %"]
fmt = {"Revenue": lambda v: f"${v:,.0f}", "Average Meal Price": lambda v: f"${v:,.2f}",
       "Residual %": lambda v: f"{v:+.2f}%"}
print("\nBiggest positive surprises (earn more than the model expects)")
print(df.nlargest(6, "Residual %")[show_cols].to_string(index=False, formatters=fmt))
print("\nBiggest negative surprises (earn less than the model expects)")
print(df.nsmallest(6, "Residual %")[show_cols].to_string(index=False, formatters=fmt))
print("\nResidual summary")
print(df["Residual %"].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).round(2).to_string())
""")

md(r"""
### Q7 findings - the "outliers" are scale, not anomalies

* The model's residuals are tiny: the interquartile range is about **-0.84% to +0.82%**, and 95% of restaurants fall within roughly **+/- 2.1%**.
* The biggest positive deviation is about **+5.6%**, the biggest negative about **-5.2%**. There is no restaurant that is dramatically over- or under-performing.
* The flagged high-revenue restaurants from Section 2 are **not** anomalies: they have 90 seats at $75, so the model expects their revenue to be high. Their residuals are ordinary.

**Why it happens:** revenue was generated as seat count x price with only about 2% multiplicative noise. Nothing else in the data (rating, service, marketing) moves revenue enough to create a genuine outlier.

**What it means:** if this were real data, residual analysis would be the right tool to flag venues for audit or to find best practices. Here it serves as a **data-quality check**: the absence of large residuals confirms that the dataset follows one simple rule and that no data-entry errors are hiding in the tail.

**Inputs:** `Revenue`, `Seating Capacity`, `Average Meal Price`.
**Outputs:** residual distribution, actual-vs-expected chart, ranked over/under-performers.
""")

md(r"""
---
### Q8. Is revenue concentrated in a few winners?

**Question:** in many markets, a small share of stores produces most of the revenue (the 80/20 rule). Is that true here?

**Method:** sort restaurants from highest to lowest revenue and plot the cumulative share (a Lorenz-style curve).
""")

code(r"""
# ---- Q8: revenue concentration ---------------------------------------
rev_sorted = np.sort(df["Revenue"].to_numpy(float))[::-1]
cum_share = np.cumsum(rev_sorted) / rev_sorted.sum() * 100
pct_stores = np.arange(1, len(rev_sorted) + 1) / len(rev_sorted) * 100

top10 = cum_share[int(len(rev_sorted) * 0.10) - 1]
top20 = cum_share[int(len(rev_sorted) * 0.20) - 1]
n = len(rev_sorted)
gini = (2 * np.sum(np.arange(1, n + 1) * np.sort(rev_sorted)) / (n * np.sum(rev_sorted))) - (n + 1) / n

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(pct_stores, cum_share, color=TEAL, lw=3, label="actual revenue curve")
ax.plot([0, 100], [0, 100], color=MUTED, lw=1.4, ls="--", label="perfect equality (45 degrees)")
ax.axhline(80, color=CORAL, lw=1, ls=":")
ax.axvline(20, color=CORAL, lw=1, ls=":")
ax.scatter([10, 20], [top10, top20], color=CORAL, s=55, zorder=5)
ax.annotate(f"top 10% of restaurants\n= {top10:.1f}% of revenue", xy=(10, top10),
            xytext=(24, 12), fontsize=9, color=INK,
            arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.1))
ax.annotate(f"top 20% = {top20:.1f}%", xy=(20, top20), xytext=(42, 24),
            fontsize=9, color=INK,
            arrowprops=dict(arrowstyle="->", color=CORAL, lw=1.1))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
style_ax(ax, "Figure 19  |  Revenue is spread evenly, not concentrated",
         "Share of restaurants, ranked from highest to lowest revenue (%)",
         "Cumulative share of revenue (%)")
ax.legend(loc="lower right")
ax.text(0.03, 0.88, f"Gini coefficient = {gini:.3f}\n(0 = perfect equality, 1 = one restaurant earns everything)",
        transform=ax.transAxes, fontsize=9, color=INK,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=GRID))
fig.tight_layout()
save(fig, "fig19_concentration.png")
plt.show()

print(f"Top 10% of restaurants earn {top10:.1f}% of revenue")
print(f"Top 20% of restaurants earn {top20:.1f}% of revenue")
print(f"Bottom 50% earn {100 - cum_share[int(len(rev_sorted) * 0.5) - 1]:.1f}% of revenue")
print(f"Gini coefficient: {gini:.4f}")
""")

md(r"""
### Q8 findings - no 80/20 rule in this market

* The **top 10%** of restaurants earn **18.4%** of revenue.
* The **top 20%** earn **33.0%**.
* The **bottom 50%** still earn about **33.9%** of revenue.
* The Gini coefficient is about **0.227** - moderate, and far from the 80/20 pattern (a pure 80/20 market would sit well above 0.6).

The curve bows only modestly away from the diagonal: the top fifth earn 33% instead of 20%, which is noticeable but nowhere near "a few winners take everything".

**Why it happens:** capacity is distributed in three even tiers (40/60/80 seats) and price in six even tiers, so revenue has no long tail of superstars. The largest restaurants earn about 8x the smallest, but they are a small, evenly spread group rather than a dominant elite.

**What it means:** a portfolio strategy makes sense here - the business is not dependent on a handful of flagship stores. In real restaurant data we would usually expect much stronger concentration, so this is another sign that the dataset is synthetic.

**Inputs:** `Revenue` only.
**Outputs:** cumulative revenue curve, top-10%/top-20% shares, Gini coefficient.
""")

md(r"""
---
## 7. Chart checklist - every required chart type

| Chart type | Where it appears | What it shows |
|---|---|---|
| **Bar chart** | Figures 4, 5, 9, 10, 12, 13, 14, 15, 17 | Average price and revenue by cuisine/location, R-squared, coefficients, marketing quartiles, segment revenue |
| **Line chart** | Figures 16, 17, 19 | Revenue per seat by price, reservation rate by price, elbow curve, cumulative revenue curve |
| **Pie chart** | Figures 4, 5 | Revenue share by cuisine; restaurant and revenue share by location |
| **Histogram** | Figures 3, 18 | Distributions of six numeric variables; residual distribution |
| **Scatter plot** | Figures 6, 7, 11, 15, 17, 18 | Revenue vs price/seats/marketing/followers; bubble chart; actual vs predicted; segments |
| **Boxplot** *(bonus)* | Figure 1 | Outlier scan on money and audience variables |
| **Heatmap** *(bonus)* | Figures 8, 14 | Correlation matrix; cuisine x location revenue per seat |

All charts use a consistent colour system, direct labels, readable axes and plain-English titles.
""")

md(r"""
---
## 8. Key insights - the whole story in eight points

1. **Revenue is almost completely explained by two columns.** `Revenue ≈ 229 x Seating Capacity x Average Meal Price`, with R-squared **0.9993** and a typical error of about **1.3%**. Seats alone explain 46%, price alone 47%, but their *product* explains virtually everything.
2. **Cuisine is a price ladder.** Average checks run from **$30 (Mexican)** to **$70 (Japanese)**, and revenue per seat runs from **$7,096** to **$15,916** in exactly the same order. Cuisine does not add anything beyond price.
3. **Location is a size tier in disguise.** Downtown restaurants earn 44.5% of revenue because they average **80 seats** versus **40** in Rural areas, not because each seat is more productive. Revenue per seat differs by only **4%** across locations.
4. **Marketing spend mostly tracks restaurant size.** The raw correlation with revenue is 0.365, but after controlling for seats and price it falls to **0.063**, and marketing adds only **0.02%** of explained variance. Bigger venues simply spend more.
5. **Followers are a duplicate of marketing budget.** Correlation **0.99**; followers ≈ 11.7 x budget. They add no independent information and should not be used as a KPI on their own.
6. **Ratings, reviews, ambience and service do not move revenue.** Every correlation is between -0.01 and +0.03, and revenue is flat across rating bands (1.4% spread). Ratings *do* rise with marketing spend (3.84 to 4.20), which is a reputation effect, not a sales one.
7. **Demand is price-insensitive in this data.** Reservations per seat stay at about **0.96-0.99** across all price levels (r = -0.02), so each $10 on the average check adds about **$2,200** of revenue per seat per year with no loss of covers.
8. **There are four structural segments and no hidden fifth dimension.** Large/premium, Large/value, Compact/premium and Compact/value form a **2.7x revenue ladder**. Revenue is only mildly concentrated (Gini ≈ 0.23, top 20% = 33%), and no restaurant is a true anomaly: the largest residual is only about 5.6%.

> **The one-sentence version:** in this dataset, revenue is a simple function of how many seats you have and what you charge per meal; everything else is either a proxy for those two things or noise.
""")

md(r"""
---
## 9. Inputs and outputs of the analysis

| Analysis | Inputs | Outputs | Business use |
|---|---|---|---|
| Data profiling | All 17 columns | Shape, types, missing values, duplicates, ranges, categorical counts | Know what is usable before analysing |
| Cleaning | All columns | Imputed values (0 needed), duplicate removal (0), range validation, outlier flags | Trustworthy dataset |
| Outlier assessment | Revenue, Marketing Budget, Followers, Price | IQR/Z-score table, boxplots, sensitivity table, keep/remove decision | Avoid deleting real high-value venues |
| Univariate distributions | 6 key numeric columns | Histograms, KDE, mean/median/skew | Spot uniform scores, size tiers, price bands |
| Categorical composition | Location, Cuisine, Revenue | Bar charts, pie charts, revenue shares | Compare markets and menus |
| Correlation analysis | 13 numeric columns | Correlation matrix, ranked correlations | Shortlist candidate drivers |
| Driver model (Q1) | Seats, price + 17 controls | R-squared comparison, standardised coefficients, predictive equation, residuals | Quantify what really drives revenue |
| Marketing test (Q2) | Marketing, followers, seats, price, revenue | Quartile profiles, partial correlations, incremental R-squared | Separate real effect from size confounding |
| Market test (Q3) | Cuisine, location, revenue, seats | Revenue per seat, heatmap, ANOVA | Choose price position vs location |
| Reputation test (Q4) | Rating, reviews, ambience, service, chef experience | Rating-band revenue, correlation bars, rating vs marketing | Decide whether to invest in reputation metrics |
| Price-demand test (Q5) | Price, reservations, revenue, seats | Price-decile curves, correlations | Test pricing power |
| Segmentation (Q6) | Price, seats (+ revenue for profiling) | Elbow curve, 4 segments, profiles, revenue ladder | Target strategies by segment |
| Anomaly analysis (Q7) | Revenue, seats, price | Residual distribution, over/under-performer lists | Audit candidates / best-practice search |
| Concentration (Q8) | Revenue | Cumulative curve, top-10/20% shares, Gini | Portfolio risk and dependency |
""")

md(r"""
---
## 10. Recommendations

**For the business (based strictly on this dataset):**

1. **Treat menu price positioning as the first revenue lever.** Revenue per seat is directly proportional to the average check. Moving from a $30 to a $70 average check more than doubles revenue per seat - provided the product supports the price.
2. **Treat capacity as the second lever.** Revenue scales linearly with seats. Location expansion should be evaluated by how many seats it adds, not by the label "Downtown".
3. **Do not approve marketing budget increases on the basis of this data.** The apparent return is a size artefact. Run a controlled test (matched venues, before/after, holdout group) before scaling spend.
4. **Stop reporting followers as a performance KPI.** They are 99% explained by budget; report revenue per marketing dollar and incremental revenue instead.
5. **Keep ratings as a reputation metric, not a revenue forecast.** They are unrelated to revenue here; investigate why marketing lifts ratings before treating that as a benefit.
6. **Use the four segments for differentiated targets.** Large/premium protects price; Large/value manages volume; Compact/premium maximises revenue per seat; Compact/value needs price-mix or capacity improvement.
7. **Do not worry about revenue concentration.** No small group of flagship stores carries the business, so portfolio risk is low.

**For the analysis / next data collection:**

* Add **time** (monthly revenue, campaigns, seasonality) to test causality and elasticity.
* Add **costs** (rent, food, labour) to move from revenue to profit.
* Track **campaign-level marketing** and acquisition cost instead of one annual budget.
* Collect **actual covers / footfall**, not just reservations capped by capacity.
* Add **competitor density and local income** to make location analysis meaningful.
""")

md(r"""
---
## 11. Limitations and honest caveats

* **The data looks simulated.** Revenue follows a near-perfect formula (R-squared 0.999), ratings are almost uniform, categories are perfectly balanced, and followers are a fixed multiple of budget. The insights are valid for *this file*, but they should not be generalised to the real restaurant industry without new evidence.
* **Cross-sectional only.** There is no time dimension, so we cannot observe change, seasonality or the effect of a campaign.
* **Revenue is not profit.** Costs, rent, food waste and labour are missing; a high-revenue restaurant can still lose money.
* **Correlation is not causation.** The regression shows association after controls, not proof that changing a lever changes the outcome.
* **Reservations are capped by capacity**, which limits what demand analysis can detect. There is no waiting list or walk-in data.
* **Outliers were kept deliberately.** They are genuine large venues and lie on the same revenue line; removing or capping them would bias the analysis. The sensitivity check confirms the conclusions are stable.
* **Average review length has no stated unit** (characters, words?), so it is interpreted only as a relative measure.
* **Only 17 columns.** Important drivers such as rent, competition, local income, staff quality and delivery sales are absent.
""")

md(r"""
---
## 12. LinkedIn post draft (deliverable)

> **Last month I was handed a spreadsheet, a deadline, and one instruction: "find something interesting."**
>
> 8,368 restaurants. 17 columns. No idea where to start.
>
> I expected the usual story: location wins, marketing pays off, ratings matter.
>
> The data disagreed.
>
> **1. Two columns did almost all the work.**
> Seats x average meal price explained 99.9% of revenue (R-squared = 0.999).
> Location, cuisine and marketing were mostly proxies for those two.
>
> **2. Marketing looked like the hero - until I controlled for size.**
> Raw correlation with revenue: 0.37.
> After adjusting for seats and price: 0.06.
> Bigger venues spend more and earn more. The budget was along for the ride.
>
> **3. Ratings and service scores barely touched revenue.**
> Correlations sat between -0.01 and +0.03.
> But ratings did climb with marketing spend (3.84 to 4.20).
> Marketing may buy reputation. Sales? Not here.
>
> I nearly put the first chart on a slide and called it a day. Glad I didn't.
>
> The lesson I'm taking from this task:
> **A correlation is a question, not a conclusion.**
>
> What I built: cleaning (missing values, duplicates, IQR/Z-score outliers), distributions, a price-elasticity test, K-means segmentation and a Lorenz curve.
>
> Tools: Python, Pandas, NumPy, Matplotlib, Seaborn, SciPy
> Dataset: 8,368 restaurants, 17 columns
>
> Your turn: what's the best "insight" you've caught that turned out to be an illusion?
>
> *Module 03 - Data Visualization. Notebook and charts in the comments.*
>
> #DataAnalytics #DataVisualization #Python #Pandas #Seaborn #Matplotlib #EDA #DataMining #Internship #PortfolioProject
""")

md(r"""
---
## 13. Conclusion

This notebook followed the full analyst workflow on `restaurant_data.csv`: profile, clean, describe, visualise, mine, explain.

The headline is simple: **revenue is a capacity-and-price equation**. Seats and average meal price explain 99.9% of the variation, while the variables that look most "insightful" - location, marketing, ratings, service - are either proxies for size/price or unrelated to the outcome.

The most valuable part of the exercise was not the highest R-squared; it was learning to **question a correlation**. Marketing looked like a strong lever (r = 0.37) until a partial correlation removed the size effect and it collapsed to 0.06. That single step changed the business conclusion.

The charts are saved in the `figures/` folder and the cleaned dataset is exported as `restaurant_data_clean.csv`, ready for a dashboard or a follow-up model.
""")

code(r"""
# ---- Export the cleaned data and confirm the figures ------------------
export_cols = [
    "Name", "Location", "Cuisine", "Rating", "Seating Capacity", "Average Meal Price",
    "Marketing Budget", "Social Media Followers", "Chef Experience Years",
    "Number of Reviews", "Avg Review Length", "Ambience Score", "Service Quality Score",
    "Parking Availability", "Weekend Reservations", "Weekday Reservations", "Revenue",
    "Total Reservations", "Reservation Rate", "Revenue per Seat", "Marketing per Seat",
    "Revenue per Marketing Dollar", "Seats x Price", "Rating Band", "Price Band",
    "Revenue Outlier", "Predicted Revenue", "Residual %", "Segment", "Segment Label",
]
df[export_cols].to_csv("restaurant_data_clean.csv", index=False)

print(f"Cleaned dataset saved: restaurant_data_clean.csv  ({len(df):,} rows x {len(export_cols)} columns)")
print("\nCharts saved in figures/:")
for name in sorted(os.listdir("figures")):
    if name.endswith(".png"):
        print("  -", name)
""")
