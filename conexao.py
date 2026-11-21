# conexao.py: conexão com o SQLite, criação das tabelas e backup
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(BASE_DIR, "estoque.db")
CAMINHO_SQL = os.path.join(BASE_DIR, "banco.sql")
PASTA_BACKUP = os.path.join(BASE_DIR, "backups")


def conectar(caminho=CAMINHO_BANCO):
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_tabelas(conn):
    """Executa o script banco.sql (usa IF NOT EXISTS, então é seguro repetir)."""
    with open(CAMINHO_SQL, "r", encoding="utf-8") as arquivo:
        conn.executescript(arquivo.read())
    conn.commit()


def iniciar_banco(caminho=CAMINHO_BANCO):
    conn = conectar(caminho)
    criar_tabelas(conn)
    return conn


def fazer_backup(conn, pasta=PASTA_BACKUP, manter=10):
    """Copia o banco para backups/estoque_AAAAMMDD_HHMMSS.db e guarda os 10 últimos."""
    os.makedirs(pasta, exist_ok=True)
    nome = datetime.now().strftime("estoque_%Y%m%d_%H%M%S.db")
    destino = os.path.join(pasta, nome)
    copia = sqlite3.connect(destino)
    try:
        conn.backup(copia)
    finally:
        copia.close()
    antigos = sorted(f for f in os.listdir(pasta)
                     if f.startswith("estoque_") and f.endswith(".db"))
    for arquivo in antigos[:-manter]:
        os.remove(os.path.join(pasta, arquivo))
    return destino