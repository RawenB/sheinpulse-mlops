from pathlib import Path

import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor


DATA_PATH = Path("data/processed/weekly_demand.parquet")
mlflow.set_experiment("SheinPulse-Demand-Modeling")


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ]
    )


def evaluate(y_true, y_pred) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    r2 = r2_score(y_true, y_pred)
    return {"MAE": float(mae), "RMSE": float(rmse), "R2": float(r2)}


def run_one_model(run_name: str, model, X_train, X_test, y_train, y_test, preprocessor, register: bool) -> dict:
    pipe = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )

    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("dataset_path", str(DATA_PATH))
        mlflow.log_param("model_name", model.__class__.__name__)

        if hasattr(model, "get_params"):
            mlflow.log_params(model.get_params())

        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)

        metrics = evaluate(y_test, preds)
        for k, v in metrics.items():
            mlflow.log_metric(k, v)

        if register:
            mlflow.sklearn.log_model(
                sk_model=pipe,
                artifact_path="model",
                registered_model_name="sheinpulse_model",
            )
        else:
            mlflow.sklearn.log_model(sk_model=pipe, artifact_path="model")

    return metrics


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH.resolve()}")

    df = pd.read_parquet(DATA_PATH)

    target = "demand"
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in dataset")

    # Keep features that make sense for modeling
    drop_cols = [c for c in ["t_dat"] if c in df.columns]  # just in case
    X = df.drop(columns=[target] + drop_cols)
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    preprocessor = build_preprocessor(X_train)

    candidates = [
        ("RandomForest_v2", RandomForestRegressor(
            n_estimators=500,
            random_state=42,
            n_jobs=-1
        )),
        ("GradientBoosting_v2", GradientBoostingRegressor(
            random_state=42
        )),
    ]

    results = []
    for run_name, model in candidates:
        metrics = run_one_model(
            run_name=run_name,
            model=model,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            preprocessor=preprocessor,
            register=False,
        )
        results.append((run_name, metrics))

    best_run_name, best_metrics = min(results, key=lambda x: x[1]["RMSE"])

    best_model = None
    for rn, m in candidates:
        if rn == best_run_name:
            best_model = m
            break

    run_one_model(
        run_name=f"{best_run_name}_REGISTERED",
        model=best_model,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        preprocessor=preprocessor,
        register=True,
    )

    print("Training finished.")
    print("Best model:", best_run_name)
    print("Best metrics:", best_metrics)


if __name__ == "__main__":
    main()