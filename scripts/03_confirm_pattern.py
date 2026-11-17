"""Step 3: confirm the hidden generating pattern and remaining numbers."""
import numpy as np
import pandas as pd
from scipy import stats

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 50)

df = pd.read_csv("restaurant_data.csv")
df["Seats_x_Price"] = df["Seating Capacity"] * df["Average Meal Price"]
df["Ratio"] = df["Revenue"] / df["Seats_x_Price"]
df["Total Reservations"] = df["Weekend Reservations"] + df["Weekday Reservations"]
df["Revenue per Seat"] = df["Revenue"] / df["Seating Capacity"]

print("REVENUE / (SEATS x PRICE) distribution")
print(df["Ratio"].describe().round(3))
print("cv:", (df["Ratio"].std() / df["Ratio"].mean()).round(4))

print("\nRevenue per seat by price (should be linear):")
bins = pd.cut(df["Average Meal Price"], 6)
print(df.groupby(bins, observed=True).agg(n=("Revenue", "size"),
                                          price=("Average Meal Price", "mean"),
                                          rev_per_seat=("Revenue per Seat", "mean")).round(1))

print("\nRevenue per seat by location:")
print(df.groupby("Location").agg(rev_per_seat_mean=("Revenue per Seat", "mean"),
                                 rev_per_seat_std=("Revenue per Seat", "std"),
                                 price=("Average Meal Price", "mean"),
                                 seats=("Seating Capacity", "mean"),
                                 weekend=("Weekend Reservations", "mean"),
                                 weekday=("Weekday Reservations", "mean")).round(2))

print("\nReservations vs seating cap:")
print("max weekend <= max seats:", df["Weekend Reservations"].max(), df["Seating Capacity"].max())
print("weekend > seats rows:", (df["Weekend Reservations"] > df["Seating Capacity"]).sum())
print("weekday > seats rows:", (df["Weekday Reservations"] > df["Seating Capacity"]).sum())
print("weekend/seat describe:", (df["Weekend Reservations"] / df["Seating Capacity"]).describe().round(3).to_dict())
print("weekday/seat describe:", (df["Weekday Reservations"] / df["Seating Capacity"]).describe().round(3).to_dict())

print("\nMarketing budget / followers by location:")
print(df.groupby("Location")[["Marketing Budget", "Social Media Followers"]].mean().round(0))

print("\nSeating by location:")
print(df.groupby("Location")["Seating Capacity"].describe().round(2))
print("\nPrice by cuisine:")
print(df.groupby("Cuisine")["Average Meal Price"].describe().round(2))

print("\nAmbience/Service vs rating correlation:",
      df["Ambience Score"].corr(df["Rating"]).round(3), df["Service Quality Score"].corr(df["Rating"]).round(3))
print("reviews vs revenue:", df["Number of Reviews"].corr(df["Revenue"]).round(3))
print("reviews vs rating:", df["Number of Reviews"].corr(df["Rating"]).round(3))
print("chef exp vs rating:", df["Chef Experience Years"].corr(df["Rating"]).round(3))

# models
def ols_r2(X, y):
    Xz = (X - X.mean()) / X.std()
    Xz.insert(0, "const", 1.0)
    A = np.asarray(Xz, float); b = np.asarray(y, float)
    coef = np.linalg.lstsq(A, b, rcond=None)[0]
    resid = b - A @ coef
    r2 = 1 - resid @ resid / ((b - b.mean()) @ (b - b.mean()))
    return r2, resid

y = df["Revenue"]
r2a, _ = ols_r2(df[["Seating Capacity"]], y)
r2b, _ = ols_r2(df[["Average Meal Price"]], y)
r2c, _ = ols_r2(df[["Seating Capacity", "Average Meal Price"]], y)
r2d, res = ols_r2(df[["Seats_x_Price"]], y)
print(f"\nR2 seats only={r2a:.4f} price only={r2b:.4f} seats+price={r2c:.4f} seats*price={r2d:.6f}")
print("residual std seats*price:", res.std().round(2), " as % of mean revenue:", (res.std() / y.mean() * 100).round(2))

print("\nResidual % (seats*price model) describe:")
print(pd.Series(res / y * 100).describe(percentiles=[.01, .05, .25, .5, .75, .95, .99]).round(2))

print("\nMean ratio by cuisine (revenue per $ of seats*price):")
print(df.groupby("Cuisine")["Ratio"].agg(["mean", "std"]).round(2))

print("\nWeekend vs weekday reservations equal-ish?",
      "mean diff:", (df["Weekend Reservations"] - df["Weekday Reservations"]).mean().round(3),
      "corr:", df["Weekend Reservations"].corr(df["Weekday Reservations"]).round(3))
print("both 0 rows:", ((df["Weekend Reservations"] == 0) & (df["Weekday Reservations"] == 0)).sum())

print("\nParking vs location:")
print(pd.crosstab(df["Location"], df["Parking Availability"], normalize="index").round(3))

print("\nRating vs marketing quartile:")
df["MQ"] = pd.qcut(df["Marketing Budget"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
print(df.groupby("MQ", observed=True).agg(rating=("Rating", "mean"), seats=("Seating Capacity", "mean"),
                                          followers=("Social Media Followers", "mean")).round(2))

print("\nTop 5 rows by revenue with ratio:")
print(df.nlargest(5, "Revenue")[["Name", "Location", "Cuisine", "Seating Capacity", "Average Meal Price", "Revenue", "Ratio"]].round(1).to_string(index=False))

print("\nRevenue totals:", df["Revenue"].sum(), "mean*count:", df["Revenue"].mean() * len(df))
