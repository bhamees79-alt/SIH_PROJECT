
import numpy as np

LABEL_MAP = {
    0: "RETRIEVE_COTTON",
    1: "PLACE_COTTON",
    2: "HANDLE_SEEDS",
    3: "PLACE_SEEDS",
    4: "TAKE_DROPPER",
    5: "ADD_WATER"
}

SPATIAL_INDICES = list(range(70)) + list(range(196, 206))


def make_spatial_features(sequence):
    """
    Convert one 32-frame, 206-feature sequence
    into the 320-feature HGB input.
    """

    spatial = sequence[:, SPATIAL_INDICES]

    mean_features = np.mean(spatial, axis=0)
    std_features = np.std(spatial, axis=0)
    min_features = np.min(spatial, axis=0)
    max_features = np.max(spatial, axis=0)

    features = np.concatenate([
        mean_features,
        std_features,
        min_features,
        max_features
    ])

    return features


def predict_activity(sequence, model):
    """
    Predict activity from one 32-frame sequence.

    Input:
        sequence: numpy array with shape (32, 206)

    Output:
        dictionary containing activity, confidence and label.
    """

    features = make_spatial_features(sequence)
    features = features.reshape(1, -1)

    probabilities = model.predict_proba(features)[0]

    label = int(np.argmax(probabilities))
    confidence = float(probabilities[label])

    activity = LABEL_MAP[label]

    return {
        "activity": activity,
        "confidence": confidence,
        "label": label
    }
