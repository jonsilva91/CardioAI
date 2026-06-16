from __future__ import annotations

from typing import Any


def build_cnn_model(input_shape: tuple[int, int, int], num_classes: int) -> Any:
    """
    Constrói uma CNN simples para classificação de imagens de ECG.
    O import do TensorFlow é feito dentro da função para reduzir problemas
    de análise estática quando a dependência ainda não está instalada.
    """
    from tensorflow import keras

    model = keras.Sequential(
        [
            keras.layers.Input(shape=input_shape),
            keras.layers.Conv2D(32, (3, 3), activation="relu"),
            keras.layers.MaxPooling2D(),
            keras.layers.Conv2D(64, (3, 3), activation="relu"),
            keras.layers.MaxPooling2D(),
            keras.layers.Conv2D(128, (3, 3), activation="relu"),
            keras.layers.MaxPooling2D(),
            keras.layers.Flatten(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


