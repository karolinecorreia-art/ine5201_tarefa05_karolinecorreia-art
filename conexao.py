# conexao.py: conexão com o SQLite, criação das tabelas, backup e mensagens de erro
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(BASE_DIR, "estoque.db")
CAMINHO_SQL = os.path.join(BASE_DIR, "banco.sql")
PASTA_BACKUP = os.path.join(BASE_DIR, "backups")


def conectar(caminho=CAMINHO_BANCO, timeout=5.0):
    conn = sqlite3.connect(caminho, timeout=timeout)
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


def desfazer(conn):
    """Rollback que nunca levanta erro (útil dentro de tratamentos de exceção)."""
    try:
        conn.rollback()
    except sqlite3.Error:
        pass


def mensagem_erro(erro):
    """Traduz um erro do SQLite para uma mensagem clara para o usuário."""
    if isinstance(erro, sqlite3.IntegrityError):
        return f"Os dados foram recusados pelas regras do banco de dados: {erro}"
    if isinstance(erro, sqlite3.OperationalError):
        texto = str(erro).lower()
        if "locked" in texto or "busy" in texto:
            return ("O banco de dados está em uso por outra janela ou programa. "
                    "Feche as outras instâncias do sistema e tente novamente.")
        return f"Não foi possível acessar o banco de dados: {erro}"
    if isinstance(erro, sqlite3.ProgrammingError):
        return "A conexão com o banco de dados está fechada."
    return f"Erro no banco de dados: {erro}"


def backup_valido(caminho):
    """Confere se o arquivo de backup existe, não está vazio e passa na verificação."""
    if not os.path.exists(caminho) or os.path.getsize(caminho) == 0:
        return False
    try:
        copia = sqlite3.connect(caminho)
        try:
            return copia.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            copia.close()
    except sqlite3.Error:
        return False


def fazer_backup(conn, pasta=PASTA_BACKUP, manter=10):
    """Copia o banco para backups/estoque_AAAAMMDD_HHMMSS.db e guarda os mais recentes.
    Se já existir um backup no mesmo segundo, cria outro arquivo (sufixo _1, _2...)."""
    os.makedirs(pasta, exist_ok=True)
    base = datetime.now().strftime("estoque_%Y%m%d_%H%M%S")
    destino = os.path.join(pasta, base + ".db")
    numero = 1
    while os.path.exists(destino):
        destino = os.path.join(pasta, f"{base}_{numero}.db")
        numero += 1
    copia = sqlite3.connect(destino)
    try:
        conn.backup(copia)
    finally:
        copia.close()
    if not backup_valido(destino):
        os.remove(destino)
        raise OSError("O arquivo de backup gerado está vazio ou inválido.")
    antigos = sorted(f for f in os.listdir(pasta)
                     if f.startswith("estoque_") and f.endswith(".db"))
    for arquivo in antigos[:-manter]:
        os.remove(os.path.join(pasta, arquivo))
    return destino