"""Step 2: deeper numbers used to write accurate insights."""
import numpy as np
import pandas as pd
from scipy import stats

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 60)

df = pd.read_csv("restaurant_data.csv")
df["Total Reservations"] = df["Weekend Reservations"] + df["Weekday Reservations"]
df["Revenue per Seat"] = df["Revenue"] / df["Seating Capacity"]
df["Marketing per Seat"] = df["Marketing Budget"] / df["Seating Capacity"]
df["Reservation Load"] = df["Total Reservations"] / df["Seating Capacity"]
df["Revenue per Marketing $"] = df["Revenue"] / df["Marketing Budget"]
df["Followers per Review"] = df["Social Media Followers"] / df["Number of Reviews"]

print("=" * 80, "\nREVENUE SHARE\n", "=" * 80)
for c in ["Location", "Cuisine", "Parking Availability"]:
    t = df.groupby(c)["Revenue"].agg(["sum", "mean", "count"])
    t["share_%"] = t["sum"] / t["sum"].sum() * 100
    print(f"\n{c}\n", t.round(2))

print("\n" + "=" * 80, "\nREVENUE PER SEAT BY CUISINE x LOCATION\n", "=" * 80)
print(df.pivot_table(index="Cuisine", columns="Location", values="Revenue per Seat", aggfunc="mean").round(1))
print("\nBy cuisine:")
print(df.groupby("Cuisine").agg(revenue_per_seat=("Revenue per Seat", "mean"),
                                price=("Average Meal Price", "mean"),
                                seats=("Seating Capacity", "mean")).round(2))

print("\n" + "=" * 80, "\nMARKETING / FOLLOWERS / RATING\n", "=" * 80)
df["Marketing Quartile"] = pd.qcut(df["Marketing Budget"], 4, labels=["Q1 low", "Q2", "Q3", "Q4 high"])
print(df.groupby("Marketing Quartile", observed=True).agg(
    n=("Revenue", "size"), budget=("Marketing Budget", "mean"), followers=("Social Media Followers", "mean"),
    revenue=("Revenue", "mean"), rev_per_mkt=("Revenue per Marketing $", "mean"),
    rating=("Rating", "mean"), seats=("Seating Capacity", "mean")).round(2))

print("\nrating vs marketing budget pearson:", stats.pearsonr(df["Rating"], df["Marketing Budget"]))
print("rating vs followers pearson:", stats.pearsonr(df["Rating"], df["Social Media Followers"]))
print("followers vs budget pearson:", stats.pearsonr(df["Social Media Followers"], df["Marketing Budget"]))
print("followers/budget ratio:", (df["Social Media Followers"] / df["Marketing Budget"]).describe().round(3).to_dict())

print("\nrating band vs revenue:")
df["Rating Band"] = pd.cut(df["Rating"], [2.99, 3.5, 4.0, 4.5, 5.0], labels=["3.0-3.5", "3.5-4.0", "4.0-4.5", "4.5-5.0"])
print(df.groupby("Rating Band", observed=True).agg(n=("Revenue", "size"), revenue=("Revenue", "mean"),
                                                   price=("Average Meal Price", "mean"),
                                                   seats=("Seating Capacity", "mean")).round(1))

print("\n" + "=" * 80, "\nCORRELATIONS: reservations / price / seating\n", "=" * 80)
print(df[["Average Meal Price", "Seating Capacity", "Weekend Reservations", "Weekday Reservations",
          "Total Reservations", "Revenue", "Rating"]].corr().round(3))

# ---------------- OLS with dummies ----------------
def build_X(d, include_marketing=True):
    X = pd.DataFrame(index=d.index)
    X["Seating"] = d["Seating Capacity"]
    X["MealPrice"] = d["Average Meal Price"]
    if include_marketing:
        X["Marketing"] = d["Marketing Budget"]
    X["WeekendRes"] = d["Weekend Reservations"]
    X["WeekdayRes"] = d["Weekday Reservations"]
    X["Rating"] = d["Rating"]
    X["ChefExp"] = d["Chef Experience Years"]
    X["Reviews"] = d["Number of Reviews"]
    X["Ambience"] = d["Ambience Score"]
    X["Service"] = d["Service Quality Score"]
    X["AvgReviewLen"] = d["Avg Review Length"]
    for loc in ["Suburban", "Downtown"]:
        X[f"Loc_{loc}"] = (d["Location"] == loc).astype(float)
    for cui in ["American", "French", "Indian", "Italian", "Japanese"]:
        X[f"Cui_{cui}"] = (d["Cuisine"] == cui).astype(float)
    X["Parking"] = (d["Parking Availability"] == "Yes").astype(float)
    return X

def ols(y, X):
    Xz = (X - X.mean()) / X.std()
    Xz.insert(0, "Intercept", 1.0)
    A = np.asarray(Xz, float)
    b = np.asarray(y, float)
    coef, *_ = np.linalg.lstsq(A, b, rcond=None)
    resid = b - A @ coef
    n, p = A.shape
    dof = n - p
    sigma2 = resid @ resid / dof
    cov = sigma2 * np.linalg.inv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    t = coef / se
    pval = 2 * (1 - stats.t.cdf(np.abs(t), dof))
    r2 = 1 - (resid @ resid) / ((b - b.mean()) @ (b - b.mean()))
    adj = 1 - (1 - r2) * (n - 1) / dof
    return pd.DataFrame({"coef_std": coef, "t": t, "p": pval}, index=Xz.columns), r2, adj, resid

y = df["Revenue"]
X_full = build_X(df, True)
res_full, r2f, adjf, resid_full = ols(y, X_full)
print("\n" + "=" * 80, f"\nOLS FULL  R2={r2f:.4f} adjR2={adjf:.4f}\n", "=" * 80)
print(res_full.round(4).sort_values("coef_std", ascending=False))

X_nomkt = build_X(df, False)
_, r2n, adjn, _ = ols(y, X_nomkt)
print(f"\nOLS without marketing: R2={r2n:.4f} (drop {r2f - r2n:.4f})")

# core model: seats * price interaction
df["Seats_x_Price"] = df["Seating Capacity"] * df["Average Meal Price"]
print("\nRevenue correlation with Seats x Price:", df["Revenue"].corr(df["Seats_x_Price"]).round(4))
print("Revenue per seat correlation with price:", df["Revenue per Seat"].corr(df["Average Meal Price"]).round(4))

# partial correlation marketing vs revenue | seats, price
def partial_corr(df, x, y, controls):
    Z = df[controls].astype(float)
    Z = (Z - Z.mean()) / Z.std()
    Z.insert(0, "const", 1.0)
    A = np.asarray(Z, float)
    rx = np.asarray(df[x], float) - A @ np.linalg.lstsq(A, np.asarray(df[x], float), rcond=None)[0]
    ry = np.asarray(df[y], float) - A @ np.linalg.lstsq(A, np.asarray(df[y], float), rcond=None)[0]
    r, p = stats.pearsonr(rx, ry)
    return r, p

for ctrl in [["Seating Capacity"], ["Average Meal Price"], ["Seating Capacity", "Average Meal Price"]]:
    r, p = partial_corr(df, "Marketing Budget", "Revenue", ctrl)
    print(f"partial corr marketing~revenue | {ctrl}: r={r:.3f}, p={p:.2e}")
r, p = partial_corr(df, "Social Media Followers", "Revenue", ["Seating Capacity", "Average Meal Price"])
print(f"partial corr followers~revenue | seats,price: r={r:.3f}, p={p:.2e}")

# ---------------- location / cuisine tests ----------------
print("\n" + "=" * 80, "\nGROUP TESTS\n", "=" * 80)
for c in ["Location", "Cuisine"]:
    groups = [g["Revenue per Seat"].values for _, g in df.groupby(c)]
    F, p = stats.f_oneway(*groups)
    print(f"ANOVA revenue-per-seat by {c}: F={F:.1f}, p={p:.3g}")

print("\nRevenue per seat by location:")
print(df.groupby("Location").agg(revenue_per_seat=("Revenue per Seat", ["mean", "std"]),
                                 price=("Average Meal Price", "mean"),
                                 load=("Reservation Load", "mean")).round(2))

# ---------------- k-means segments ----------------
feats = ["Average Meal Price", "Seating Capacity", "Marketing Budget", "Rating",
         "Reservation Load", "Weekend Reservations"]
Z = (df[feats] - df[feats].mean()) / df[feats].std()
rng = np.random.default_rng(42)
best = None
for seed in range(20):
    cents, lab = stats.cluster.vq.kmeans2(Z.values, 4, iter=100, minit="++", seed=seed)
    d = ((Z.values[:, None, :] - cents[None, :, :]) ** 2).sum(2).min(1).sum()
    if best is None or d < best[0]:
        best = (d, lab, cents)
lab = best[1]
df["Segment"] = ["Segment " + str(i + 1) for i in lab]
print("\n" + "=" * 80, "\nK-MEANS (k=4) PROFILES\n", "=" * 80)
prof = df.groupby("Segment").agg(
    n=("Revenue", "size"),
    revenue=("Revenue", "mean"),
    seats=("Seating Capacity", "mean"),
    price=("Average Meal Price", "mean"),
    marketing=("Marketing Budget", "mean"),
    rating=("Rating", "mean"),
    reservations=("Total Reservations", "mean"),
    rev_per_seat=("Revenue per Seat", "mean"),
    location=("Location", lambda s: s.mode()[0]),
    cuisine=("Cuisine", lambda s: s.mode()[0]),
).round(1)
print(prof)
print("\nsegment x location share:")
print(pd.crosstab(df["Segment"], df["Location"], normalize="index").round(2))
print("\nsegment x cuisine share:")
print(pd.crosstab(df["Segment"], df["Cuisine"], normalize="index").round(2))

# ---------------- anomalies ----------------
pred = np.asarray(y) - np.asarray(resid_full)
df["Predicted"] = pred
df["Residual"] = np.asarray(resid_full)
df["Residual_%"] = df["Residual"] / df["Predicted"] * 100
print("\n" + "=" * 80, "\nRESIDUAL OUTLIERS\n", "=" * 80)
cols = ["Name", "Location", "Cuisine", "Seating Capacity", "Average Meal Price", "Marketing Budget",
        "Rating", "Revenue", "Predicted", "Residual_%"]
print("\nTop 8 over-performers:")
print(df.nlargest(8, "Residual_%")[cols].round(1).to_string(index=False))
print("\nTop 8 under-performers:")
print(df.nsmallest(8, "Residual_%")[cols].round(1).to_string(index=False))
print("\nResidual_% describe:", df["Residual_%"].describe().round(2).to_dict())
print("residual skew:", stats.skew(df["Residual"]).round(3), "kurtosis:", stats.kurtosis(df["Residual"]).round(3))

# ---------------- counts for charts ----------------
print("\n" + "=" * 80, "\nMISC\n", "=" * 80)
print("restaurants with 0 weekend reservations:", (df["Weekend Reservations"] == 0).sum())
print("restaurants with 0 weekday reservations:", (df["Weekday Reservations"] == 0).sum())
print("both zero:", ((df["Weekend Reservations"] == 0) & (df["Weekday Reservations"] == 0)).sum())
print("weekend > weekday:", (df["Weekend Reservations"] > df["Weekday Reservations"]).sum())
print("avg weekend vs weekday:", df["Weekend Reservations"].mean().round(2), df["Weekday Reservations"].mean().round(2))
print("total reservations correlation with revenue:", df["Total Reservations"].corr(df["Revenue"]).round(3))
print("revenue quartiles:", df["Revenue"].quantile([0, .25, .5, .75, 1]).round(0).to_dict())
top10 = df["Revenue"].nlargest(int(len(df) * 0.1)).sum() / df["Revenue"].sum() * 100
print(f"top 10% restaurants revenue share: {top10:.1f}%")
print("parking t-test revenue:", stats.ttest_ind(df.loc[df["Parking Availability"] == "Yes", "Revenue"],
                                               df.loc[df["Parking Availability"] == "No", "Revenue"], equal_var=False))
print("\nRevenue per marketing dollar by cuisine:")
print(df.groupby("Cuisine")["Revenue per Marketing $"].mean().round(2))
print("\nRevenue per seat by location/cuisine (rounded):")
print(df.pivot_table(index="Cuisine", columns="Location", values="Revenue per Seat", aggfunc="mean").round(0))

X_core = df[["Seating Capacity", "Average Meal Price"]].copy()
X_core["Seats_x_Price"] = df["Seats_x_Price"]
_, r2c, _, _ = ols(y, X_core)
print(f"\nR2 seats+price+interaction = {r2c:.4f}")
X_core2 = df[["Seating Capacity", "Average Meal Price"]]
_, r2c2, _, _ = ols(y, X_core2)
print(f"R2 seats+price = {r2c2:.4f}")
df[["Name", "Location", "Cuisine", "Revenue", "Predicted", "Residual", "Residual_%", "Segment"]].to_csv("outputs_model.csv", index=False)
