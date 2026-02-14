from datasets import load_dataset
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

DATASET_NAME = "dinhlnd1610/HM-Personalized-Fashion-Recommendations"


def save_split(dataset, name, n_rows=None):
    if n_rows:
        dataset = dataset.select(range(min(n_rows, len(dataset))))

    df = dataset.to_pandas()
    output_path = RAW_DIR / f"{name}.parquet"
    df.to_parquet(output_path, index=False)
    print(f"{name} saved with {len(df)} rows")


def main():
    configs = ["articles", "customers", "transactions"]

    for config in configs:
        print(f"Loading {config} dataset")
        ds = load_dataset(DATASET_NAME, config)
        split = ds["train"]

        sample_size = 50000 if config == "transactions" else None
        save_split(split, config, sample_size)

    print("Download finished")


if __name__ == "__main__":
    main()
