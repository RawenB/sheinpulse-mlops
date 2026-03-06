import mlflow.pyfunc


MODEL_URI = "models:/sheinpulse_model@production"


def load_model():
    return mlflow.pyfunc.load_model(MODEL_URI)