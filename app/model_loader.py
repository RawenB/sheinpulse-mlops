from pathlib import Path
import mlflow.pyfunc

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_URI = BASE_DIR / "mlruns" / "2" / "models" / "m-10f34da9edac4da38fd77489352c5908" / "artifacts"

def load_model():
    return mlflow.pyfunc.load_model(str(MODEL_URI))