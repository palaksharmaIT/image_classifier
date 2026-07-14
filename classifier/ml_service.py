import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    preprocess_input,
    decode_predictions,
)
from tensorflow.keras.preprocessing import image as keras_image

_model = None
_TARGET_SIZE = (224, 224)


def _get_model():
    global _model
    if _model is None:
        _model = MobileNetV2(weights="imagenet")
    return _model


def _preprocess(image_path: str) -> np.ndarray:
    img = keras_image.load_img(image_path, target_size=_TARGET_SIZE)
    array = keras_image.img_to_array(img)
    array = np.expand_dims(array, axis=0)
    array = preprocess_input(array)
    return array


def classify_image(image_path: str, top_k: int = 3) -> list[dict]:
    model = _get_model()
    processed = _preprocess(image_path)

    raw_predictions = model.predict(processed, verbose=0)
    decoded = decode_predictions(raw_predictions, top=top_k)[0]

    results = []
    for _class_id, human_label, probability in decoded:
        results.append({
            "label": human_label.replace("_", " ").title(),
            "confidence": round(float(probability) * 100, 2),
        })
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python ml_service.py <image_path>")
        sys.exit(1)
    for pred in classify_image(sys.argv[1]):
        print(f"{pred['label']:<30} {pred['confidence']:.2f}%")