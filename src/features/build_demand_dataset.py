import pandas as pd
from pathlib import Path
import numpy as np


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main():
    transactions = pd.read_parquet(RAW_DIR / "transactions.parquet")

    transactions["t_dat"] = pd.to_datetime(transactions["t_dat"], errors="coerce")
    transactions = transactions.dropna(subset=["t_dat", "article_id"])

    transactions["year"] = transactions["t_dat"].dt.year.astype(int)
    transactions["week"] = transactions["t_dat"].dt.isocalendar().week.astype(int)

    weekly = (
        transactions
        .groupby(["article_id", "year", "week"])
        .size()
        .reset_index(name="demand")
        .sort_values(["article_id", "year", "week"])
        .reset_index(drop=True)
    )

    weekly["week_sin"] = np.sin(2 * np.pi * weekly["week"] / 52.0)
    weekly["week_cos"] = np.cos(2 * np.pi * weekly["week"] / 52.0)

    grp = weekly.groupby("article_id")["demand"]

    weekly["lag_1"] = grp.shift(1).fillna(0)
    weekly["lag_2"] = grp.shift(2).fillna(0)
    weekly["lag_4"] = grp.shift(4).fillna(0)

    demand_prev = grp.shift(1)

    weekly["roll_mean_4"] = demand_prev.groupby(weekly["article_id"]).transform(
        lambda s: s.rolling(4).mean()
    ).fillna(0)

    weekly["roll_std_4"] = demand_prev.groupby(weekly["article_id"]).transform(
        lambda s: s.rolling(4).std()
    ).fillna(0)

    weekly["roll_mean_8"] = demand_prev.groupby(weekly["article_id"]).transform(
        lambda s: s.rolling(8).mean()
    ).fillna(0)

    weekly["roll_std_8"] = demand_prev.groupby(weekly["article_id"]).transform(
        lambda s: s.rolling(8).std()
    ).fillna(0)

    out_path = PROCESSED_DIR / "weekly_demand.parquet"
    weekly.to_parquet(out_path, index=False)

    print("Processed forecasting dataset created")
    print("Rows:", len(weekly))
    print("Saved to:", out_path)


if __name__ == "__main__":
    main()