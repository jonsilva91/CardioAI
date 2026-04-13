import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path


# =========================
# CONFIGURACAO DE CAMINHOS
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
TXT_PATH = BASE_DIR / "documents" / "frases_pacientes.txt"
CSV_PATH = BASE_DIR / "documents" / "mapa_conhecimento.csv"
OUTPUT_PATH = BASE_DIR / "data" / "resultado_diagnostico.csv"


def normalizar_texto(texto: str) -> str:
    """
    Converte texto para minusculas, remove acentos e excesso de espacos.
    """
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^\w\s-]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def carregar_frases(caminho_txt: Path) -> list[str]:
    """
    Le o arquivo .txt com uma frase por linha.
    """
    if not caminho_txt.exists():
        raise FileNotFoundError(f"Arquivo de frases nao encontrado: {caminho_txt}")

    with caminho_txt.open("r", encoding="utf-8") as arquivo:
        frases = [linha.strip() for linha in arquivo if linha.strip()]

    if not frases:
        raise ValueError("O arquivo de frases esta vazio.")

    return frases


def carregar_mapa_conhecimento(caminho_csv: Path) -> list[dict]:
    """
    Le o CSV de ontologia:
    sintoma_1, sintoma_2, doenca_associada
    """
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo CSV nao encontrado: {caminho_csv}")

    registros = []
    with caminho_csv.open("r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            sintoma_1 = normalizar_texto(linha["sintoma_1"])
            sintoma_2 = normalizar_texto(linha["sintoma_2"])
            doenca = linha["doenca_associada"].strip()

            registros.append(
                {
                    "sintoma_1": sintoma_1,
                    "sintoma_2": sintoma_2,
                    "doenca_associada": doenca,
                }
            )

    if not registros:
        raise ValueError("O mapa de conhecimento esta vazio.")

    return registros


def analisar_frase(frase: str, mapa: list[dict]) -> dict:
    """
    Identifica sintomas na frase e sugere um diagnostico
    com base na quantidade de correspondencias encontradas.
    """
    frase_normalizada = normalizar_texto(frase)

    sintomas_encontrados = set()
    pontuacao_doencas = Counter()

    for registro in mapa:
        s1 = registro["sintoma_1"]
        s2 = registro["sintoma_2"]
        doenca = registro["doenca_associada"]

        encontrou_s1 = s1 in frase_normalizada
        encontrou_s2 = s2 in frase_normalizada

        if encontrou_s1:
            sintomas_encontrados.add(s1)
            pontuacao_doencas[doenca] += 1

        if encontrou_s2:
            sintomas_encontrados.add(s2)
            pontuacao_doencas[doenca] += 1

        # Bonus se os dois sintomas da mesma linha aparecerem juntos
        if encontrou_s1 and encontrou_s2:
            pontuacao_doencas[doenca] += 1

    if pontuacao_doencas:
        diagnostico_sugerido, score = pontuacao_doencas.most_common(1)[0]
    else:
        diagnostico_sugerido, score = "Nao identificado", 0

    return {
        "frase_original": frase,
        "frase_normalizada": frase_normalizada,
        "sintomas_identificados": "; ".join(sorted(sintomas_encontrados)) if sintomas_encontrados else "nenhum",
        "diagnostico_sugerido": diagnostico_sugerido,
        "pontuacao": score,
    }


def salvar_resultados(resultados: list[dict], caminho_saida: Path) -> None:
    """
    Salva os resultados em CSV.
    """
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    campos = [
        "frase_original",
        "frase_normalizada",
        "sintomas_identificados",
        "diagnostico_sugerido",
        "pontuacao",
    ]

    with caminho_saida.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(resultados)


def main() -> None:
    frases = carregar_frases(TXT_PATH)
    mapa = carregar_mapa_conhecimento(CSV_PATH)

    resultados = [analisar_frase(frase, mapa) for frase in frases]

    print("\n=== RESULTADOS DO DIAGNOSTICO ===\n")
    for i, resultado in enumerate(resultados, start=1):
        print(f"Paciente {i}:")
        print(f"Frase: {resultado['frase_original']}")
        print(f"Sintomas identificados: {resultado['sintomas_identificados']}")
        print(f"Diagnostico sugerido: {resultado['diagnostico_sugerido']}")
        print(f"Pontuacao: {resultado['pontuacao']}")
        print("-" * 60)

    salvar_resultados(resultados, OUTPUT_PATH)
    print(f"\nArquivo de resultados salvo em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
