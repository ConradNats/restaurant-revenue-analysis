"""Step 1: Look at the data before touching it. Prints a full profile to the console."""
import pandas as pd
import numpy as np

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 50)

df = pd.read_csv("restaurant_data.csv")

print("=" * 90)
print("SHAPE:", df.shape)
print("=" * 90)
print("\nDTYPES / NON-NULL / UNIQUE")
prof = pd.DataFrame({
    "dtype": df.dtypes.astype(str),
    "non_null": df.notna().sum(),
    "missing": df.isna().sum(),
    "missing_%": (df.isna().mean() * 100).round(2),
    "unique": df.nunique(),
})
print(prof)

print("\n" + "=" * 90)
print("NUMERIC DESCRIBE")
print("=" * 90)
print(df.describe().T.round(3))

print("\n" + "=" * 90)
print("CATEGORICAL COUNTS")
print("=" * 90)
for c in df.select_dtypes(include=["object", "string"]).columns:
    print(f"\n--- {c} ({df[c].nunique()} unique) ---")
    print(df[c].value_counts(dropna=False).to_string())

print("\n" + "=" * 90)
print("DUPLICATED ROWS:", df.duplicated().sum())
print("FULLY EMPTY ROWS:", df.isna().all(axis=1).sum())
print("=" * 90)

num = df.select_dtypes(include=np.number)
print("\nCORRELATION WITH REVENUE (Pearson / Spearman)")
print(pd.DataFrame({
    "pearson": num.corr()["Revenue"],
    "spearman": num.corr(method="spearman")["Revenue"],
}).sort_values("pearson", ascending=False).round(3))

print("\nCORRELATION MATRIX (Pearson)")
print(num.corr().round(2))

print("\n" + "=" * 90)
print("GROUP MEANS")
print("=" * 90)
for c in ["Location", "Cuisine", "Parking Availability"]:
    print(f"\n--- Revenue & price by {c} ---")
    print(df.groupby(c, dropna=False).agg(
        n=("Revenue", "size"),
        revenue_mean=("Revenue", "mean"),
        revenue_median=("Revenue", "median"),
        price_mean=("Average Meal Price", "mean"),
        rating_mean=("Rating", "mean"),
        seating_mean=("Seating Capacity", "mean"),
        marketing_mean=("Marketing Budget", "mean"),
        followers_mean=("Social Media Followers", "mean"),
    ).round(2))

print("\n" + "=" * 90)
print("VALUE RANGES THAT LOOK SUSPICIOUS")
print("=" * 90)
print("Rating              :", df["Rating"].min(), "-", df["Rating"].max())
print("Ambience Score       :", df["Ambience Score"].min(), "-", df["Ambience Score"].max())
print("Service Quality Score:", df["Service Quality Score"].min(), "-", df["Service Quality Score"].max())
print("Avg Meal Price       :", df["Average Meal Price"].min(), "-", df["Average Meal Price"].max())
print("Revenue              :", df["Revenue"].min(), "-", df["Revenue"].max())
print("Marketing Budget     :", df["Marketing Budget"].min(), "-", df["Marketing Budget"].max())
print("Followers            :", df["Social Media Followers"].min(), "-", df["Social Media Followers"].max())
print("Reviews              :", df["Number of Reviews"].min(), "-", df["Number of Reviews"].max())
print("Chef Experience      :", df["Chef Experience Years"].min(), "-", df["Chef Experience Years"].max())
print("Seating              :", df["Seating Capacity"].min(), "-", df["Seating Capacity"].max())

print("\n" + "=" * 90)
print("OUTLIER SCAN (IQR rule, 1.5x)")
print("=" * 90)
rows = []
for c in num.columns:
    q1, q3 = df[c].quantile([.25, .75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_out = ((df[c] < lo) | (df[c] > hi)).sum()
    rows.append([c, round(q1, 2), round(q3, 2), round(lo, 2), round(hi, 2), n_out,
                 round(n_out / len(df) * 100, 2)])
print(pd.DataFrame(rows, columns=["column", "Q1", "Q3", "lower", "upper", "n_outliers", "pct"]).to_string(index=False))

print("\n" + "=" * 90)
print("EXTREME ROWS (Revenue top / bottom 5)")
print("=" * 90)
cols = ["Name", "Location", "Cuisine", "Rating", "Average Meal Price", "Marketing Budget",
        "Social Media Followers", "Seating Capacity", "Revenue"]
print(df.nlargest(5, "Revenue")[cols].to_string(index=False))
print()
print(df.nsmallest(5, "Revenue")[cols].to_string(index=False))

print("\n" + "=" * 90)
print("RESERVATIONS")
print("=" * 90)
df["total_res"] = df["Weekend Reservations"] + df["Weekday Reservations"]
print(df[["Weekend Reservations", "Weekday Reservations", "total_res"]].describe().round(2))
print("\nWeekend vs weekday correlation with Revenue:")
print(df[["Weekend Reservations", "Weekday Reservations", "total_res"]].corrwith(df["Revenue"]).round(3))
