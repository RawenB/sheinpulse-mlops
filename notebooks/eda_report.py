import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

articles = pd.read_parquet(RAW_DIR / "articles.parquet")
customers = pd.read_parquet(RAW_DIR / "customers.parquet")
transactions = pd.read_parquet(RAW_DIR / "transactions.parquet")

print("DATASET OVERVIEW")
print("Articles:", len(articles))
print("Customers:", len(customers))
print("Transactions:", len(transactions))

print("\nMISSING VALUES")
print(articles.isnull().sum())
print(customers.isnull().sum())
print(transactions.isnull().sum())

print("\nNUMERIC STATISTICS (Transactions)")
print(transactions.describe())
