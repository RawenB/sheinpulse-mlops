import pandas as pd
df = pd.read_parquet("data/processed/weekly_demand.parquet")
print(df.columns)
print(df.head())