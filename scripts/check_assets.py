#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de validacao de assets - CardioIA Fase 1
Verifica a integridade e completude dos dados (numerico, textual, visual)
"""

import os
import csv
from pathlib import Path

def check_dataset_csv():
    """Valida dataset numérico (CSV)"""
    print("\n=== VALIDACAO DE DADOS NUMERICOS ===")
    csv_file = 'data/pacientes_cardio.csv'

    if not os.path.exists(csv_file):
        print(f"[ERRO] Arquivo encontrado: {csv_file}")
        return False

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        num_rows = len(rows) - 1  # Excluir header
        num_cols = len(rows[0]) if rows else 0

        print(f"[OK] Arquivo: {csv_file}")
        print(f"     Linhas: {num_rows} (requerido: min 100)")
        print(f"     Colunas: {num_cols}")
        print(f"     Tamanho: {os.path.getsize(csv_file) / 1024:.1f} KB")

        if num_rows >= 100:
            print(f"[PASS] Dataset atende requisito minimo de 100 linhas")
            return True
        else:
            print(f"[FAIL] Dataset abaixo do minimo (100 linhas)")
            return False

    except Exception as e:
        print(f"[ERRO] Erro ao ler CSV: {e}")
        return False

def check_textual_data():
    """Valida dados textuais (TXT)"""
    print("\n=== VALIDACAO DE DADOS TEXTUAIS ===")
    txt_dir = 'assets/docs'

    if not os.path.isdir(txt_dir):
        print(f"[ERRO] Diretorio nao encontrado: {txt_dir}")
        return False

    txt_files = [f for f in os.listdir(txt_dir) if f.endswith('.txt')]

    print(f"[OK] Diretorio: {txt_dir}")
    print(f"     Arquivos .txt encontrados: {len(txt_files)} (requerido: min 2)")

    for txt_file in txt_files:
        filepath = os.path.join(txt_dir, txt_file)
        filesize = os.path.getsize(filepath) / 1024
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = len(f.readlines())
        print(f"     - {txt_file}: {lines} linhas, {filesize:.1f} KB")

    if len(txt_files) >= 2:
        print(f"[PASS] Atende requisito de minimo 2 arquivos textuais")
        return True
    else:
        print(f"[FAIL] Abaixo do minimo (2 arquivos)")
        return False

def check_visual_data():
    """Valida dados visuais (imagens)"""
    print("\n=== VALIDACAO DE DADOS VISUAIS ===")
    img_dir = 'data/images'

    if not os.path.isdir(img_dir):
        print(f"[ERRO] Diretorio nao encontrado: {img_dir}")
        return False

    # Contar imagens com extensoes validas
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    img_files = [f for f in os.listdir(img_dir)
                 if os.path.splitext(f)[1].lower() in valid_extensions]

    total_size = sum(os.path.getsize(os.path.join(img_dir, f)) for f in img_files)

    print(f"[OK] Diretorio: {img_dir}")
    print(f"     Imagens encontradas: {len(img_files)} (requerido: min 100)")
    print(f"     Tamanho total: {total_size / 1024:.1f} KB")

    # Amostra de arquivos
    if img_files:
        print(f"     Exemplos: {', '.join(img_files[:3])}")

    if len(img_files) >= 100:
        print(f"[PASS] Atende requisito de minimo 100 imagens")
        return True
    else:
        print(f"[FAIL] Abaixo do minimo (100 imagens)")
        return False

def check_directory_structure():
    """Valida estrutura de diretorios"""
    print("\n=== VALIDACAO DE ESTRUTURA ===")

    required_dirs = ['data', 'data/images', 'assets', 'assets/docs', 'src', 'scripts', 'config', 'document']

    all_exist = True
    for dir_path in required_dirs:
        exists = os.path.isdir(dir_path)
        status = "[OK]" if exists else "[ERRO]"
        print(f"{status} {dir_path}")
        all_exist = all_exist and exists

    return all_exist

def main():
    """Executa todas as validacoes"""
    print("=" * 60)
    print("CardioIA - Validacao de Assets (Fase 1)")
    print("=" * 60)

    results = {
        'estrutura': check_directory_structure(),
        'numericos': check_dataset_csv(),
        'textuais': check_textual_data(),
        'visuais': check_visual_data()
    }

    print("\n" + "=" * 60)
    print("RESUMO DE VALIDACAO")
    print("=" * 60)

    for check_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {check_name.capitalize()}")

    all_pass = all(results.values())

    print("=" * 60)
    if all_pass:
        print("[SUCESSO] Todos os requisitos atendidos!")
    else:
        print("[ATENCAO] Alguns requisitos nao foram atendidos")
    print("=" * 60)

    return 0 if all_pass else 1

if __name__ == '__main__':
    exit(main())
