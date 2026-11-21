# movimentacoes.py: entradas, saídas e histórico
import sqlite3
from datetime import datetime


def registrar(conn, codigo, tipo, quantidade):
    """Registra uma entrada (compra) ou saída (venda/uso).
    A quantidade do produto é atualizada pelo trigger do banco."""
    if tipo not in ("entrada", "saida"):
        raise ValueError("Tipo de movimentação inválido.")
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    produto = conn.execute("SELECT quantidade FROM produtos WHERE codigo = ?",
                           (codigo,)).fetchone()
    if produto is None:
        raise ValueError("Produto não encontrado.")
    if tipo == "saida" and quantidade > produto["quantidade"]:
        raise ValueError(f"Estoque insuficiente: disponível {produto['quantidade']}, "
                         f"solicitado {quantidade}.")
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute("INSERT INTO movimentacoes (produto_codigo, tipo, quantidade, data) "
                     "VALUES (?, ?, ?, ?)", (codigo, tipo, quantidade, data))
        conn.commit()
    except sqlite3.DatabaseError as erro:
        conn.rollback()
        raise ValueError(str(erro)) from None


def historico(conn, tipo=None, categoria=None, limite=None):
    """Histórico de movimentações, da mais recente para a mais antiga."""
    sql = ("SELECT m.id, m.data AS data, p.codigo AS codigo, p.nome AS nome, "
           "p.categoria AS categoria, m.tipo AS tipo, m.quantidade AS quantidade "
           "FROM movimentacoes m JOIN produtos p ON p.codigo = m.produto_codigo")
    condicoes, parametros = [], []
    if tipo:
        condicoes.append("m.tipo = ?")
        parametros.append(tipo)
    if categoria:
        condicoes.append("p.categoria = ?")
        parametros.append(categoria)
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    sql += " ORDER BY m.id DESC"
    if limite:
        sql += " LIMIT ?"
        parametros.append(limite)
    return conn.execute(sql, parametros).fetchall()