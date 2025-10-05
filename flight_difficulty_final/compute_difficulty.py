import pandas as pd
import numpy as np


DATA_DIR = "data/"

flights = pd.read_csv(f"{DATA_DIR}Flight Level Data.csv", low_memory=False)
pnr = pd.read_csv(f"{DATA_DIR}PNR Flight Level Data.csv", low_memory=False)
remarks = pd.read_csv(f"{DATA_DIR}PNR Remark Level Data.csv", low_memory=False)
bags = pd.read_csv(f"{DATA_DIR}Bag Level Data.csv", low_memory=False)
airports = pd.read_csv(f"{DATA_DIR}Airports Data.csv", low_memory=False)



flights["actual_departure_datetime_local"] = pd.to_datetime(flights["actual_departure_datetime_local"], errors="coerce")
flights["scheduled_departure_datetime_local"] = pd.to_datetime(flights["scheduled_departure_datetime_local"], errors="coerce")

flights["departure_delay"] = (
    (flights["actual_departure_datetime_local"] - flights["scheduled_departure_datetime_local"])
    .dt.total_seconds() / 60
).fillna(0).clip(lower=0)


flights["ground_time_stress"] = flights["scheduled_ground_time_minutes"] - flights["minimum_turn_minutes"]


pnr_grouped = (
    pnr.groupby(["flight_number", "scheduled_departure_date_local"], as_index=False)
       .agg({
            "total_pax": "sum",
            "lap_child_count": "sum",
            "is_child": "sum",
            "basic_economy_pax": "sum",
            "is_stroller_user": "sum"
       })
)


remarks_grouped = (
    remarks.groupby(["flight_number", "pnr_creation_date"], as_index=False)
           .size()
           .rename(columns={"size": "ssr_count"})
)


bags_grouped = (
    bags.groupby(["flight_number", "scheduled_departure_date_local", "bag_type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
)


bags_grouped["transfer_ratio"] = bags_grouped.get("Transfer", 0) / (bags_grouped.get("Checked", 0) + 1)


df = (
    flights.merge(pnr_grouped, on=["flight_number", "scheduled_departure_date_local"], how="left")
           .merge(bags_grouped, on=["flight_number", "scheduled_departure_date_local"], how="left")
           .merge(
               remarks_grouped,
               left_on=["flight_number", "scheduled_departure_date_local"],
               right_on=["flight_number", "pnr_creation_date"],
               how="left"
           )
)

df = df.fillna(0)


df["difficulty_score"] = (
    df["departure_delay"] / 10 +                               # scaled delay
    (df["ground_time_stress"] < 0).astype(int) * 5 +           # short turnaround penalty
    df["total_pax"] / 100 +                                    # passenger load
    df["ssr_count"] * 2 +                                      # SSR impact
    df["transfer_ratio"] * 10                                  # baggage complexity
)


df["rank"] = df.groupby("scheduled_departure_date_local")["difficulty_score"] \
               .rank("dense", ascending=False)


df["class"] = (
    df.groupby("scheduled_departure_date_local")["difficulty_score"]
      .transform(lambda x: pd.qcut(x, q=3, labels=["Easy", "Medium", "Difficult"]))
)


output_path = "flight_difficulty_score.csv"
df.to_csv(output_path, index=False)

print(f" Flight difficulty scores computed successfully and saved to '{output_path}'")

