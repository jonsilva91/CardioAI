from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix

from dataset import DatasetConfig, build_datasets


def main() -> None:
    from tensorflow import keras

    project_root = Path(__file__).resolve().parents[3]
    data_dir = project_root / "data" / "raw" / "ecg_images"
    model_path = project_root / "phases" / "fase04_cnn_ecg" / "outputs" / "models" / "cnn_ecg_model.keras"
    figure_path = project_root / "phases" / "fase04_cnn_ecg" / "outputs" / "figures" / "confusion_matrix.png"
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    config = DatasetConfig(data_dir=data_dir, image_size=(256, 256), batch_size=16)
    _, val_ds, class_names = build_datasets(config)

    model = keras.models.load_model(model_path)

    y_true = np.concatenate([labels.numpy() for _, labels in val_ds], axis=0)
    y_prob = model.predict(val_ds)
    y_pred = np.argmax(y_prob, axis=1)

    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=class_names, digits=4)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(cmap="Blues", xticks_rotation=45)
    plt.tight_layout()
    plt.savefig(figure_path, dpi=200)

    print("Avaliação concluída.")
    print(report)
    print(f"Matriz de confusão salva em: {figure_path}")


if __name__ == "__main__":
    main()

# Made with Bob
