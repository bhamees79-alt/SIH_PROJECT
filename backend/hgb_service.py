
import joblib
from member1.hgb_inference import predict_activity

MODEL_PATH = "member1/hgb_spatial_best.joblib"

model = joblib.load(MODEL_PATH)


def predict_sequence(sequence):
    """
    Run Member 1 HGB inference on one
    32-frame × 206-feature sequence.
    """

    result = predict_activity(sequence, model)

    return {
        "activity": result["activity"],
        "confidence": result["confidence"],
        "label": result["label"]
    }
