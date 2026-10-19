"""
Script de consulta e inspeção das coleções e documentos no MongoDB Real (Atlas / Local).
Reproduz as consultas mongosh equivalentes para evidência da Fase 5 (IR ALÉM 2).
"""
import os
import json
from pathlib import Path
from bson import json_util
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega .env
env_paths = [
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent.parent / ".env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(p)

MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("MONGO_DATABASE", "cardioai_nosql")

def main():
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    lines = []
    lines.append("=" * 80)
    lines.append(" EVIDENCIA DE CONSULTA NOSQL MONGODB (EQUIVALENTE MONGOSH)")
    lines.append("=" * 80)
    masked_uri = MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI
    lines.append(f"Cluster / Host: {masked_uri}")
    lines.append(f"Database: {DB_NAME}\n")
    
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    
    # Ping de validacao
    client.admin.command('ping')
    lines.append("[STATUS] Conexao ativa com o cluster MongoDB Real!\n")
    
    collections = db.list_collection_names()
    lines.append(f">> db.getCollectionNames(): {collections}\n")
    
    for coll_name in collections:
        coll = db[coll_name]
        total_docs = coll.count_documents({})
        lines.append("-" * 80)
        lines.append(f" COLECAO: {coll_name} (Total de documentos: {total_docs})")
        lines.append(f" Comando: db.{coll_name}.find().sort({{_id: -1}}).limit(3)")
        lines.append("-" * 80)
        
        cursor = coll.find().sort("_id", -1).limit(3)
        docs = list(cursor)
        for idx, doc in enumerate(docs, 1):
            doc_str = json.dumps(json.loads(json_util.dumps(doc)), indent=2, ensure_ascii=False)
            lines.append(f"--- [Documento {idx} de {total_docs}] ---")
            lines.append(doc_str)
            lines.append("")
            
    lines.append("=" * 80)
    lines.append(" CONSULTA CONCLUIDA COM SUCESSO NO MONGODB REAL")
    lines.append("=" * 80)

    full_output = "\n".join(lines)
    print(full_output)

    txt_path = Path(__file__).resolve().parent / "consulta_mongo.txt"
    txt_path.write_text(full_output, encoding="utf-8")
    print(f"\n[INFO] Evidencia salva em: {txt_path}")

if __name__ == "__main__":
    main()
