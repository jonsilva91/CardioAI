from __future__ import annotations

from pathlib import Path

from dataset import DatasetConfig, build_datasets
from model import build_cnn_model


def main() -> None:
    project_root = Path(__file__).resolve().parents[3]
    data_dir = project_root / "data" / "raw" / "ecg_images"
    output_dir = project_root / "phases" / "fase04_cnn_ecg" / "outputs" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    config = DatasetConfig(data_dir=data_dir, image_size=(256, 256), batch_size=16)

    train_ds, val_ds, class_names = build_datasets(config)

    model = build_cnn_model(
        input_shape=(256, 256, 3),
        num_classes=len(class_names),
    )

    history = model.fit(train_ds, validation_data=val_ds, epochs=5)

    model_path = output_dir / "cnn_ecg_model.keras"
    model.save(model_path)

    print("Treinamento concluído.")
    print(f"Classes: {class_names}")
    print(f"Modelo salvo em: {model_path}")
    print(f"Histórico disponível em memória: {list(history.history.keys())}")


if __name__ == "__main__":
    main()

# Made with Bob
