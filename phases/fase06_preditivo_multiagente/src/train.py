"""Módulo de treinamento e avaliação de modelos preditivos para pico de risco.

Compara Regressão Logística (Baseline com StandardScaler) e Random Forest Classifier,
gerando métricas clínicas completas, matriz de confusão, gráfico de importância de features,
validação cruzada estratificada e persistência do melhor modelo em formato joblib.
"""

import sys
from datetime import datetime
from pathlib import Path
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Garante suporte a UTF-8 no stdout do Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.config import (
    DATASET_CSV_PATH,
    FEATURES,
    FIGURES_DIR,
    MODEL_JOBLIB_PATH,
    RANDOM_SEED,
)
from src.data_generation import salvar_base_sintetica


def carregar_dados() -> tuple[pd.DataFrame, pd.Series]:
    """Carrega o dataset sintético, gerando-o se não existir."""
    if not DATASET_CSV_PATH.exists():
        print("Arquivo de dados não encontrado. Gerando base sintética...")
        df = salvar_base_sintetica()
    else:
        df = pd.read_csv(DATASET_CSV_PATH)

    X = df[FEATURES]
    y = df["pico_risco"]
    return X, y


def plotar_matriz_confusao(cm: np.ndarray, nome_modelo: str, caminho_png: Path) -> None:
    """Gera e salva o gráfico da matriz de confusão formatada."""
    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation="nearest", cmap="Blues")
    plt.title(f"Matriz de Confusão - {nome_modelo}", fontsize=12, fontweight="bold", pad=12)
    plt.colorbar()

    classes = ["Sem Pico (0)", "Pico de Risco (1)"]
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, fontsize=10)
    plt.yticks(tick_marks, classes, fontsize=10)

    # Adiciona os números e porcentagens em cada quadrante
    total = np.sum(cm)
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            pct = (val / total) * 100
            label = f"{val}\n({pct:.1f}%)"
            plt.text(
                j,
                i,
                label,
                horizontalalignment="center",
                verticalalignment="center",
                color="white" if val > thresh else "black",
                fontsize=11,
                fontweight="bold",
            )

    plt.ylabel("Classe Real", fontsize=11)
    plt.xlabel("Classe Prevista", fontsize=11)
    plt.tight_layout()
    caminho_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(caminho_png, dpi=300)
    plt.close()


def plotar_importancia_features(importancias: np.ndarray, features: list[str], caminho_png: Path) -> None:
    """Gera e salva o gráfico de importância das variáveis do Random Forest."""
    indices = np.argsort(importancias)
    sorted_features = [features[i] for i in indices]
    sorted_importances = importancias[indices]

    plt.figure(figsize=(8, 6))
    bars = plt.barh(range(len(sorted_features)), sorted_importances, color="#1f77b4", edgecolor="#0d47a1")
    plt.yticks(range(len(sorted_features)), sorted_features, fontsize=10)
    plt.xlabel("Importância Relativa (Gini Importance)", fontsize=11)
    plt.title("Importância das Features - Random Forest Classifier", fontsize=12, fontweight="bold", pad=12)

    # Exibe os valores nas barras
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + 0.005,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.3f}",
            va="center",
            ha="left",
            fontsize=9,
            color="#333333",
        )

    plt.xlim(0, max(sorted_importances) * 1.15)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    caminho_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(caminho_png, dpi=300)
    plt.close()


def treinar_e_avaliar() -> dict:
    """Executa o pipeline completo de treinamento, avaliação e persistência."""
    print("=" * 70)
    print("🚀 INICIANDO TREINAMENTO - CARDIOAI FASE 6")
    print("=" * 70)

    X, y = carregar_dados()

    # Divisão estratificada 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_SEED
    )
    print(f"📊 Amostras Treino: {len(X_train)} | Teste: {len(X_test)}")

    # 1. Modelo Baseline: Regressão Logística com Normalização StandardScaler
    print("\n[1/3] Treinando Regressão Logística (Baseline)...")
    pipe_lr = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)),
    ])
    pipe_lr.fit(X_train, y_train)
    y_pred_lr = pipe_lr.predict(X_test)

    acc_lr = accuracy_score(y_test, y_pred_lr)
    prec_lr = precision_score(y_test, y_pred_lr, pos_label=1, zero_division=0)
    rec_lr = recall_score(y_test, y_pred_lr, pos_label=1, zero_division=0)
    f1_lr = f1_score(y_test, y_pred_lr, pos_label=1, zero_division=0)

    # 2. Modelo Principal: Random Forest Classifier
    print("\n[2/3] Treinando Random Forest (200 estimadores)...")
    rf_clf = RandomForestClassifier(n_estimators=200, random_state=RANDOM_SEED)
    rf_clf.fit(X_train, y_train)
    y_pred_rf = rf_clf.predict(X_test)

    acc_rf = accuracy_score(y_test, y_pred_rf)
    prec_rf = precision_score(y_test, y_pred_rf, pos_label=1, zero_division=0)
    rec_rf = recall_score(y_test, y_pred_rf, pos_label=1, zero_division=0)
    f1_rf = f1_score(y_test, y_pred_rf, pos_label=1, zero_division=0)
    cm_rf = confusion_matrix(y_test, y_pred_rf)

    # 3. Validação Cruzada Estratificada (5 Folds) para o Random Forest
    print("\n[3/3] Executando Validação Cruzada (5 Folds Stratified)...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    cv_acc = cross_val_score(rf_clf, X, y, cv=cv, scoring="accuracy")
    cv_f1 = cross_val_score(rf_clf, X, y, cv=cv, scoring="f1")

    # Comparativo no Terminal
    print("\n" + "=" * 70)
    print("📈 COMPARAÇÃO DE MODELOS (CONJUNTO DE TESTE - 20%):")
    print("=" * 70)
    print(f"{'Métrica':<20} | {'Regressão Logística':<20} | {'Random Forest':<20}")
    print("-" * 70)
    print(f"{'Acurácia':<20} | {acc_lr:<20.4f} | {acc_rf:<20.4f}")
    print(f"{'Precisão (Classe 1)':<20} | {prec_lr:<20.4f} | {prec_rf:<20.4f}")
    print(f"{'Recall (Classe 1)':<20} | {rec_lr:<20.4f} | {rec_rf:<20.4f}")
    print(f"{'F1-Score (Classe 1)':<20} | {f1_lr:<20.4f} | {f1_rf:<20.4f}")
    print("-" * 70)
    print(f"Validação Cruzada RF (5-folds): Acurácia = {cv_acc.mean():.4f} ± {cv_acc.std():.4f} | F1 = {cv_f1.mean():.4f} ± {cv_f1.std():.4f}")

    print("\n📋 Relatório de Classificação Detalhado (Random Forest):")
    print(classification_report(y_test, y_pred_rf, target_names=["Sem Pico (0)", "Pico de Risco (1)"]))

    # Salva Gráficos
    cm_png_path = FIGURES_DIR / "matriz_confusao.png"
    feat_png_path = FIGURES_DIR / "importancia_features.png"
    plotar_matriz_confusao(cm_rf, "Random Forest Classifier", cm_png_path)
    plotar_importancia_features(rf_clf.feature_importances_, FEATURES, feat_png_path)
    print(f"🖼️ Matriz de confusão salva em: {cm_png_path}")
    print(f"🖼️ Gráfico de importância de features salvo em: {feat_png_path}")

    # Seleção do modelo vencedor: foco em F1 e Recall da Classe 1
    # Em cenários de saúde, Falso Negativo (deixar de identificar pico de risco) é crítico
    melhor_modelo = rf_clf if f1_rf >= f1_lr else pipe_lr
    nome_vencedor = "RandomForestClassifier" if f1_rf >= f1_lr else "LogisticRegressionPipeline"

    # Pacote com metadados para persistência
    artefato_salvo = {
        "model": melhor_modelo,
        "model_name": nome_vencedor,
        "features": FEATURES,
        "metrics": {
            "accuracy": float(acc_rf),
            "precision_class_1": float(prec_rf),
            "recall_class_1": float(rec_rf),
            "f1_class_1": float(f1_rf),
            "cv_accuracy_mean": float(cv_acc.mean()),
            "cv_accuracy_std": float(cv_acc.std()),
            "cv_f1_mean": float(cv_f1.mean()),
            "cv_f1_std": float(cv_f1.std()),
            "confusion_matrix": cm_rf.tolist(),
        },
        "trained_at": datetime.now().isoformat(),
        "sklearn_version": sklearn.__version__,
    }

    MODEL_JOBLIB_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artefato_salvo, MODEL_JOBLIB_PATH)
    print(f"\n💾 Modelo salvo com sucesso em: {MODEL_JOBLIB_PATH}")
    print(f"🏆 Modelo escolhido: {nome_vencedor} (F1 = {f1_rf:.4f})")
    print("=" * 70)

    return artefato_salvo


if __name__ == "__main__":
    treinar_e_avaliar()
