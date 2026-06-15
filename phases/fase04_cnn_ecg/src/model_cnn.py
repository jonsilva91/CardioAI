"""
Módulo para construção de CNN do zero para classificação de imagens de ECG.
"""
from __future__ import annotations

from typing import Any


def build_cnn_model(input_shape: tuple[int, int, int], num_classes: int) -> Any:
    """
    Constrói uma CNN simples do zero para classificação de imagens de ECG.
    
    Arquitetura:
    - 3 blocos Conv2D + MaxPooling2D
    - Dropout para regularização
    - Camadas Dense para classificação
    - Softmax para saída multiclasse
    
    Args:
        input_shape: Formato da imagem de entrada (altura, largura, canais)
        num_classes: Número de classes para classificação
        
    Returns:
        Modelo Keras compilado
    """
    from tensorflow import keras

    model = keras.Sequential(
        [
            keras.layers.Input(shape=input_shape),
            
            # Bloco 1
            keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.2),
            
            # Bloco 2
            keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.2),
            
            # Bloco 3
            keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.3),
            
            # Classificador
            keras.layers.Flatten(),
            keras.layers.Dense(256, activation="relu"),
            keras.layers.Dropout(0.4),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(num_classes, activation="softmax"),
        ],
        name="CNN_ECG_Scratch"
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    return model


def build_cnn_with_augmentation(input_shape: tuple[int, int, int], num_classes: int) -> Any:
    """
    Constrói uma CNN com data augmentation integrada.
    
    Args:
        input_shape: Formato da imagem de entrada (altura, largura, canais)
        num_classes: Número de classes para classificação
        
    Returns:
        Modelo Keras compilado com augmentation
    """
    from tensorflow import keras

    model = keras.Sequential(
        [
            keras.layers.Input(shape=input_shape),
            
            # Data Augmentation
            keras.layers.RandomFlip("horizontal"),
            keras.layers.RandomRotation(0.1),
            keras.layers.RandomZoom(0.1),
            
            # Bloco 1
            keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.2),
            
            # Bloco 2
            keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.2),
            
            # Bloco 3
            keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.3),
            
            # Classificador
            keras.layers.Flatten(),
            keras.layers.Dense(256, activation="relu"),
            keras.layers.Dropout(0.4),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(num_classes, activation="softmax"),
        ],
        name="CNN_ECG_Augmented"
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    return model


# Made with Bob