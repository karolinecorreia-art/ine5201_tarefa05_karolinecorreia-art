# movimentacoes.py: entradas, saídas e histórico
import sqlite3
from datetime import datetime

import conexao


def registrar(conn, codigo, tipo, quantidade):
    """Registra uma entrada (compra) ou saída (venda/uso).

    A conferência do saldo e o registro acontecem na mesma transação, protegida
    por BEGIN IMMEDIATE: nenhuma outra instância consegue alterar o banco no meio
    do processo. A quantidade do produto é atualizada pelo trigger, que também
    recusa saídas sem estoque (segunda camada de proteção).
    """
    if tipo not in ("entrada", "saida"):
        raise ValueError("Tipo de movimentação inválido.")
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn.execute("BEGIN IMMEDIATE")
        produto = conn.execute("SELECT quantidade FROM produtos WHERE codigo = ?",
                               (codigo,)).fetchone()
        if produto is None:
            raise ValueError("Produto não encontrado.")
        if tipo == "saida" and quantidade > produto["quantidade"]:
            raise ValueError(f"Estoque insuficiente: disponível {produto['quantidade']}, "
                             f"solicitado {quantidade}.")
        conn.execute("INSERT INTO movimentacoes (produto_codigo, tipo, quantidade, data) "
                     "VALUES (?, ?, ?, ?)", (codigo, tipo, quantidade, data))
        conn.commit()
    except ValueError:
        conexao.desfazer(conn)
        raise
    except sqlite3.Error as erro:
        conexao.desfazer(conn)
        raise ValueError(conexao.mensagem_erro(erro)) from None


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