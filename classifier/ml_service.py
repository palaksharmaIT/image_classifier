"""
ml_service.py
--------------
Standalone utility service for image classification inference AND
Grad-CAM visual explanations, both using MobileNetV2 (ImageNet weights).
"""
from __future__ import annotations

import numpy as np
import tensorflow as tf
from PIL import Image
import matplotlib.cm as cm
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    preprocess_input,
    decode_predictions,
)
from tensorflow.keras.preprocessing import image as keras_image

_model = None
_TARGET_SIZE = (224, 224)
_LAST_CONV_LAYER = "out_relu"


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


def generate_gradcam_overlay(image_path: str, alpha: float = 0.45) -> Image.Image:
    model = _get_model()

    grad_model = tf.keras.models.Model(
        model.inputs, [model.get_layer(_LAST_CONV_LAYER).output, model.output]
    )

    img_array = _preprocess(image_path)

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        top_index = tf.argmax(predictions[0])
        class_channel = predictions[:, top_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    heatmap = heatmap.numpy()

    original = Image.open(image_path).convert("RGB")
    orig_w, orig_h = original.size

    heatmap_img = Image.fromarray(np.uint8(heatmap * 255)).resize((orig_w, orig_h))
    heatmap_arr = np.array(heatmap_img)

    colored_heatmap = cm.jet(heatmap_arr / 255.0)[:, :, :3]
    colored_heatmap = np.uint8(colored_heatmap * 255)

    original_arr = np.array(original)
    overlay = np.uint8(colored_heatmap * alpha + original_arr * (1 - alpha))

    return Image.fromarray(overlay)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python ml_service.py <image_path>")
        sys.exit(1)
    for pred in classify_image(sys.argv[1]):
        print(f"{pred['label']:<30} {pred['confidence']:.2f}%")