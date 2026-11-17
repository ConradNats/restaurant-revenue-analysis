"""Step 4: k-means segments + remaining insight numbers."""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster import vq

df = pd.read_csv("restaurant_data.csv")
df["Total Reservations"] = df["Weekend Reservations"] + df["Weekday Reservations"]
df["Revenue per Seat"] = df["Revenue"] / df["Seating Capacity"]
df["Reservation Rate"] = df["Total Reservations"] / df["Seating Capacity"]

top10 = df["Revenue"].nlargest(int(len(df) * .1)).sum() / df["Revenue"].sum() * 100
top20 = df["Revenue"].nlargest(int(len(df) * .2)).sum() / df["Revenue"].sum() * 100
print(f"top10 share {top10:.1f}%  top20 share {top20:.1f}%")

def partial_corr(df, x, y, controls):
    Z = df[controls].astype(float)
    Z = (Z - Z.mean()) / Z.std(); Z.insert(0, "c", 1.0)
    A = np.asarray(Z, float)
    rx = np.asarray(df[x], float) - A @ np.linalg.lstsq(A, np.asarray(df[x], float), rcond=None)[0]
    ry = np.asarray(df[y], float) - A @ np.linalg.lstsq(A, np.asarray(df[y], float), rcond=None)[0]
    return stats.pearsonr(rx, ry)

print("partial rating~marketing | seats:", partial_corr(df, "Rating", "Marketing Budget", ["Seating Capacity"]))
print("partial rating~followers | seats:", partial_corr(df, "Rating", "Social Media Followers", ["Seating Capacity"]))
print("partial rating~marketing | seats,price:", partial_corr(df, "Rating", "Marketing Budget", ["Seating Capacity", "Average Meal Price"]))

for price_cut in [0]:
    pass

print("\nRevenue per seat by rating band:")
df["Band"] = pd.cut(df["Rating"], [2.99, 3.5, 4.0, 4.5, 5.0])
print(df.groupby("Band", observed=True)["Revenue per Seat"].agg(["mean", "std", "count"]).round(0))

feats = ["Average Meal Price", "Seating Capacity", "Marketing Budget", "Rating",
         "Reservation Rate", "Weekend Reservations"]
Z = (df[feats] - df[feats].mean()) / df[feats].std()
rng = np.random.default_rng(7)
best = None
for seed in range(30):
    cents, lab = vq.kmeans2(Z.values, 4, iter=200, minit="++", seed=seed)
    d = ((Z.values[:, None, :] - cents[None, :, :]) ** 2).sum(2).min(1).sum()
    if best is None or d < best[0]:
        best = (d, lab, cents)
lab, cents = best[1], best[2]
df["Segment"] = lab

prof = df.groupby("Segment").agg(
    n=("Revenue", "size"), revenue=("Revenue", "mean"), seats=("Seating Capacity", "mean"),
    price=("Average Meal Price", "mean"), marketing=("Marketing Budget", "mean"),
    rating=("Rating", "mean"), res_rate=("Reservation Rate", "mean"),
    rev_seat=("Revenue per Seat", "mean")).round(1)
prof["loc"] = df.groupby("Segment")["Location"].agg(lambda s: s.mode()[0])
prof["cuisine"] = df.groupby("Segment")["Cuisine"].agg(lambda s: s.mode()[0])
print("\n" + "=" * 70)
print(prof)
print("\ncrosstab location:\n", pd.crosstab(df["Segment"], df["Location"]))
print("\ncrosstab cuisine:\n", pd.crosstab(df["Segment"], df["Cuisine"]))
print("\nsegment revenue share:\n", (df.groupby("Segment")["Revenue"].sum() / df["Revenue"].sum() * 100).round(1))

print("\nprice vs reservations corr:", df["Average Meal Price"].corr(df["Total Reservations"]).round(4))
print("price vs reservation rate corr:", df["Average Meal Price"].corr(df["Reservation Rate"]).round(4))
print("\nrevenue per seat by cuisine/location min/max:",
      df.groupby(["Cuisine", "Location"])["Revenue per Seat"].mean().agg(["min", "max"]).round(0).to_dict())

print("\nmarketing $ per seat by location:")
print((df["Marketing Budget"] / df["Seating Capacity"]).groupby(df["Location"]).mean().round(1))

print("\ntop 5 over/under performers by ratio:")
df["Ratio"] = df["Revenue"] / (df["Seating Capacity"] * df["Average Meal Price"])
print(df.nlargest(5, "Ratio")[["Name", "Cuisine", "Location", "Ratio"]].round(1).to_string(index=False))
print(df.nsmallest(5, "Ratio")[["Name", "Cuisine", "Location", "Ratio"]].round(1).to_string(index=False))
print("\nRatio by name count:", df["Ratio"].describe().round(2).to_dict())
