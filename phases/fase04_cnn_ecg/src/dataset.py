from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tensorflow.keras import layers, utils


@dataclass
class DatasetConfig:
    data_dir: Path
    image_size: tuple[int, int] = (256, 256)
    batch_size: int = 16
    validation_split: float = 0.2
    seed: int = 42


def build_datasets(config: DatasetConfig):
    """
    Cria datasets de treino e validação a partir de uma estrutura:
    data/raw/ecg_images/<classe>/*.png
    """
    if not config.data_dir.exists():
        raise FileNotFoundError(
            f"Diretório de dados não encontrado: {config.data_dir}"
        )

    train_ds = utils.image_dataset_from_directory(
        config.data_dir,
        validation_split=config.validation_split,
        subset="training",
        seed=config.seed,
        image_size=config.image_size,
        batch_size=config.batch_size,
    )

    val_ds = utils.image_dataset_from_directory(
        config.data_dir,
        validation_split=config.validation_split,
        subset="validation",
        seed=config.seed,
        image_size=config.image_size,
        batch_size=config.batch_size,
    )

    class_names = train_ds.class_names

    normalization = layers.Rescaling(1.0 / 255)

    train_ds = train_ds.map(lambda x, y: (normalization(x), y)).prefetch(1)
    val_ds = val_ds.map(lambda x, y: (normalization(x), y)).prefetch(1)

    return train_ds, val_ds, class_names

# Made with Bob
