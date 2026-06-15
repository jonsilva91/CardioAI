"""
Módulo para construção de modelos com Transfer Learning para classificação de ECG.
"""
from __future__ import annotations

from typing import Any, Literal


def build_transfer_model(
    input_shape: tuple[int, int, int],
    num_classes: int,
    base_model: Literal["mobilenetv2", "vgg16", "resnet50"] = "mobilenetv2",
    trainable_base: bool = False,
) -> Any:
    """
    Constrói um modelo usando Transfer Learning com modelos pré-treinados no ImageNet.
    
    Estratégia:
    - Carrega modelo pré-treinado sem a camada de classificação (include_top=False)
    - Congela a base convolucional (opcional)
    - Adiciona GlobalAveragePooling2D
    - Adiciona camadas Dense para classificação customizada
    
    Args:
        input_shape: Formato da imagem de entrada (altura, largura, canais)
        num_classes: Número de classes para classificação
        base_model: Modelo base a ser usado ("mobilenetv2", "vgg16", "resnet50")
        trainable_base: Se True, permite treinar a base convolucional
        
    Returns:
        Modelo Keras compilado
    """
    from tensorflow import keras
    from tensorflow.keras import applications

    # Seleciona o modelo base
    if base_model == "mobilenetv2":
        base = applications.MobileNetV2(
            input_shape=input_shape,
            include_top=False,
            weights="imagenet"
        )
    elif base_model == "vgg16":
        base = applications.VGG16(
            input_shape=input_shape,
            include_top=False,
            weights="imagenet"
        )
    elif base_model == "resnet50":
        base = applications.ResNet50(
            input_shape=input_shape,
            include_top=False,
            weights="imagenet"
        )
    else:
        raise ValueError(f"Modelo base não suportado: {base_model}")
    
    # Congela a base convolucional
    base.trainable = trainable_base
    
    # Constrói o modelo completo
    model = keras.Sequential(
        [
            keras.layers.Input(shape=input_shape),
            
            # Pré-processamento específico do modelo
            _get_preprocessing_layer(base_model),
            
            # Base convolucional pré-treinada
            base,
            
            # Pooling global
            keras.layers.GlobalAveragePooling2D(),
            
            # Classificador customizado
            keras.layers.Dense(256, activation="relu"),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(num_classes, activation="softmax"),
        ],
        name=f"Transfer_{base_model.upper()}"
    )
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    return model


def _get_preprocessing_layer(base_model: str) -> Any:
    """
    Retorna a camada de pré-processamento adequada para cada modelo base.
    
    Args:
        base_model: Nome do modelo base
        
    Returns:
        Camada de pré-processamento Keras
    """
    from tensorflow.keras import applications
    
    if base_model == "mobilenetv2":
        return applications.mobilenet_v2.preprocess_input
    elif base_model == "vgg16":
        return applications.vgg16.preprocess_input
    elif base_model == "resnet50":
        return applications.resnet50.preprocess_input
    else:
        # Fallback: normalização padrão
        from tensorflow import keras
        return keras.layers.Rescaling(1.0 / 255)


def fine_tune_model(model: Any, num_layers_to_unfreeze: int = 20) -> Any:
    """
    Realiza fine-tuning descongelando as últimas camadas da base convolucional.
    
    Args:
        model: Modelo já treinado
        num_layers_to_unfreeze: Número de camadas a desconglar do final
        
    Returns:
        Modelo modificado para fine-tuning
    """
    from tensorflow import keras
    
    # Identifica a base convolucional (geralmente a segunda camada)
    base_model = None
    for layer in model.layers:
        if isinstance(layer, keras.Model):
            base_model = layer
            break
    
    if base_model is None:
        raise ValueError("Não foi possível identificar a base convolucional no modelo")
    
    # Descongela as últimas camadas
    base_model.trainable = True
    for layer in base_model.layers[:-num_layers_to_unfreeze]:
        layer.trainable = False
    
    # Recompila com learning rate menor para fine-tuning
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.00001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    return model


def build_ensemble_model(
    input_shape: tuple[int, int, int],
    num_classes: int,
) -> list[Any]:
    """
    Constrói múltiplos modelos para ensemble learning.
    
    Args:
        input_shape: Formato da imagem de entrada
        num_classes: Número de classes
        
    Returns:
        Lista de modelos para ensemble
    """
    models = []
    
    # MobileNetV2
    models.append(build_transfer_model(
        input_shape, num_classes, base_model="mobilenetv2"
    ))
    
    # VGG16
    models.append(build_transfer_model(
        input_shape, num_classes, base_model="vgg16"
    ))
    
    # ResNet50
    models.append(build_transfer_model(
        input_shape, num_classes, base_model="resnet50"
    ))
    
    return models


# Made with Bob