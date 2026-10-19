"""Script orquestrador para executar todos os casos com o LLM real e gravar os relatórios em reports/execucoes/."""

import os
import subprocess
import sys
from pathlib import Path

# Garante suporte seguro a UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

FASE06_DIR = Path(__file__).resolve().parent.parent
REPORTS_EXEC_DIR = FASE06_DIR / "reports" / "execucoes"
REPORTS_EXEC_DIR.mkdir(parents=True, exist_ok=True)

ENV = os.environ.copy()
ENV["PYTHONIOENCODING"] = "utf-8"


def rodar_comando(cmd: list[str], nome_arquivo_saida: str, entrada: str | None = None) -> str:
    print(f"\n======================================================================")
    print(f"🚀 EXECUTANDO: {' '.join(cmd)}")
    print(f"======================================================================")

    proc = subprocess.run(
        cmd,
        cwd=str(FASE06_DIR),
        input=entrada,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENV
    )

    saida_completa = proc.stdout
    if proc.stderr:
        saida_completa += "\n" + proc.stderr

    print(saida_completa)

    caminho_saida = REPORTS_EXEC_DIR / nome_arquivo_saida
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(saida_completa.strip() + "\n")

    print(f"✅ Salvo em: {caminho_saida}")

    if proc.returncode != 0 and "guardrail" not in nome_arquivo_saida:
        print(f"❌ Comando falhou com código de retorno: {proc.returncode}")
        sys.exit(proc.returncode)

    return saida_completa


def main() -> None:
    alvos = sys.argv[1:] if len(sys.argv) > 1 else ["todos"]

    if "todos" in alvos or "novo" in alvos:
        # 1. novo_caso.json
        rodar_comando(
            [sys.executable, "-m", "src.agents_system.main", "--paciente", "data/exemplos/novo_caso.json"],
            "novo_caso.txt"
        )

    if "todos" in alvos or "baixo" in alvos:
        # 2. caso_baixo_risco.json
        rodar_comando(
            [sys.executable, "-m", "src.agents_system.main", "--paciente", "data/exemplos/caso_baixo_risco.json"],
            "caso_baixo_risco.txt"
        )

    if "todos" in alvos or "moderado" in alvos:
        # 3. caso_moderado_risco.json
        rodar_comando(
            [sys.executable, "-m", "src.agents_system.main", "--paciente", "data/exemplos/caso_moderado_risco.json"],
            "caso_moderado_risco.txt"
        )

    if "todos" in alvos or "interativo" in alvos:
        # 4. Modo interativo com novo_caso.json
        entrada_interativa = "por que o plano de contingência foi acionado?\nsair\n"
        rodar_comando(
            [sys.executable, "-m", "src.agents_system.main", "--paciente", "data/exemplos/novo_caso.json", "--interativo"],
            "interativo_novo_caso.txt",
            entrada=entrada_interativa
        )

    if "todos" in alvos or "guardrail" in alvos:
        # 5. Demonstração real do Guardrail
        rodar_comando(
            [sys.executable, "scripts/demo_guardrail.py"],
            "guardrail.txt"
        )

    print("\n🎉 EXECUÇÃO CONCLUÍDA COM SUCESSO!")


if __name__ == "__main__":
    main()
