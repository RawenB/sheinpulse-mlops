from pathlib import Path
import pandas as pd


RAW_PATH = Path("data/raw/transactions.parquet")
OUTPUT_DIR = Path("models")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    df = pd.read_parquet(RAW_PATH)

    interactions = df[["customer_id", "article_id"]].dropna().copy()
    interactions = interactions.drop_duplicates()

    customer_history = (
        interactions.groupby("customer_id")["article_id"]
        .apply(list)
        .reset_index()
    )

    article_customers = (
        interactions.groupby("article_id")["customer_id"]
        .apply(list)
        .reset_index()
    )

    article_popularity = (
        interactions["article_id"]
        .value_counts()
        .reset_index()
    )
    article_popularity.columns = ["article_id", "purchase_count"]

    customer_history.to_parquet(OUTPUT_DIR / "customer_history.parquet", index=False)
    article_customers.to_parquet(OUTPUT_DIR / "article_customers.parquet", index=False)
    article_popularity.to_parquet(OUTPUT_DIR / "article_popularity.parquet", index=False)

    print("Recommender files created")
    print("Saved customer_history.parquet")
    print("Saved article_customers.parquet")
    print("Saved article_popularity.parquet")


if __name__ == "__main__":
    main()