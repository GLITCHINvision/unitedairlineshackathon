
import pandas as pd
import numpy as np

# File paths
flights_fp = "data/Flight Level Data.csv"
pnr_fp = "data/PNR Flight Level Data.csv"
remarks_fp = "data/PNR Remark Level Data.csv"
bags_fp = "data/Bag Level Data.csv"
airports_fp = "data/Airports Data.csv"

# Load datasets
flights = pd.read_csv(flights_fp)
pnr = pd.read_csv(pnr_fp)
remarks = pd.read_csv(remarks_fp)
bags = pd.read_csv(bags_fp)
airports = pd.read_csv(airports_fp)

# ----------------- Feature Engineering -----------------

# 1. Flight delay (mins)
flights["departure_delay"] = (
    pd.to_datetime(flights["actual_departure_datetime_local"]) - 
    pd.to_datetime(flights["scheduled_departure_datetime_local"])
).dt.total_seconds() / 60

# 2. Ground time stress
flights["ground_time_stress"] = (
    flights["scheduled_ground_time_minutes"] - flights["minimum_turn_minutes"]
)

# 3. Passenger load per flight
pnr_grouped = pnr.groupby(["flight_number", "scheduled_departure_date_local"]).agg({
    "total_pax":"sum",
    "lap_child_count":"sum",
    "is_child":"sum",
    "basic_economy_pax":"sum",
    "is_stroller_user":"sum"
}).reset_index()

# 4. Special service requests count
remarks_grouped = remarks.groupby(["flight_number", "pnr_creation_date"]).size().reset_index(name="ssr_count")

# 5. Bags (checked vs transfer)
bags_grouped = bags.groupby(["flight_number","scheduled_departure_date_local","bag_type"]).size().unstack(fill_value=0).reset_index()
bags_grouped["transfer_ratio"] = bags_grouped.get("Transfer",0) / (bags_grouped.get("Checked",0)+1)

# ----------------- Merge Features -----------------

df = flights.merge(pnr_grouped, on=["flight_number","scheduled_departure_date_local"], how="left")
df = df.merge(bags_grouped, on=["flight_number","scheduled_departure_date_local"], how="left")
df = df.merge(remarks_grouped, left_on=["flight_number","scheduled_departure_date_local"],
              right_on=["flight_number","pnr_creation_date"], how="left")

# Fill NaN
df = df.fillna(0)

# ----------------- Difficulty Score -----------------
# Weighted scoring system
df["difficulty_score"] = (
    df["departure_delay"].clip(lower=0)/10 +
    df["ground_time_stress"].apply(lambda x: 1 if x<0 else 0)*5 +
    df["total_pax"]/100 +
    df["ssr_count"]*2 +
    df["transfer_ratio"]*10
)

# Daily Ranking
df["rank"] = df.groupby("scheduled_departure_date_local")["difficulty_score"].rank("dense", ascending=False)

# Classification into Easy / Medium / Difficult (tertiles)
def classify(rank, total):
    if rank <= total/3: return "Difficult"
    elif rank <= 2*total/3: return "Medium"
    else: return "Easy"

df["class"] = df.groupby("scheduled_departure_date_local")["rank"].transform(
    lambda r: [classify(x, len(r)) for x in r]
)

# Save output
df.to_csv("test_yourname.csv", index=False)
print("✅ Difficulty scores computed and saved to test_yourname.csv")
