import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main():
    transactions = pd.read_parquet(RAW_DIR / "transactions.parquet")

    transactions["t_dat"] = pd.to_datetime(transactions["t_dat"])

    transactions["year"] = transactions["t_dat"].dt.year
    transactions["week"] = transactions["t_dat"].dt.isocalendar().week

    weekly_demand = (
        transactions
        .groupby(["article_id", "year", "week"])
        .size()
        .reset_index(name="demand")
    )

    weekly_demand.to_parquet(PROCESSED_DIR / "weekly_demand.parquet", index=False)

    print("Processed dataset created")
    print("Rows:", len(weekly_demand))


if __name__ == "__main__":
    main()
