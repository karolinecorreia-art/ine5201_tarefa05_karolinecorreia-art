# produtos.py: CRUD de produtos, filtros e consultas
import sqlite3

import conexao


def cadastrar(conn, codigo, nome, categoria, preco, estoque_minimo=5):
    if buscar(conn, codigo) is not None:       # validação de código único
        raise ValueError(f"Já existe um produto com o código {codigo}.")
    try:
        conn.execute(
            "INSERT INTO produtos (codigo, nome, categoria, preco, quantidade, "
            "estoque_minimo) VALUES (?, ?, ?, ?, 0, ?)",
            (codigo, nome, categoria, preco, estoque_minimo))
        conn.commit()
    except sqlite3.Error as erro:
        conexao.desfazer(conn)
        raise ValueError(conexao.mensagem_erro(erro)) from None


def buscar(conn, codigo):
    return conn.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,)).fetchone()


def listar(conn, categoria=None, busca=None):
    """Lista produtos, com filtro opcional por categoria e por código/nome."""
    sql = "SELECT * FROM produtos"
    condicoes, parametros = [], []
    if categoria:
        condicoes.append("categoria = ?")
        parametros.append(categoria)
    if busca:
        condicoes.append("(codigo LIKE ? OR nome LIKE ?)")
        parametros += [f"%{busca}%", f"%{busca}%"]
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    sql += " ORDER BY nome COLLATE NOCASE"
    return conn.execute(sql, parametros).fetchall()


def listar_categorias(conn):
    linhas = conn.execute(
        "SELECT DISTINCT categoria FROM produtos "
        "WHERE categoria IS NOT NULL AND categoria != '' "
        "ORDER BY categoria COLLATE NOCASE").fetchall()
    return [linha[0] for linha in linhas]


def atualizar(conn, codigo, nome, categoria, preco, estoque_minimo):
    try:
        cursor = conn.execute(
            "UPDATE produtos SET nome = ?, categoria = ?, preco = ?, estoque_minimo = ? "
            "WHERE codigo = ?", (nome, categoria, preco, estoque_minimo, codigo))
        conn.commit()
    except sqlite3.Error as erro:
        conexao.desfazer(conn)
        raise ValueError(conexao.mensagem_erro(erro)) from None
    if cursor.rowcount == 0:
        raise ValueError("Produto não encontrado.")


def excluir(conn, codigo):
    try:
        cursor = conn.execute("DELETE FROM produtos WHERE codigo = ?", (codigo,))
        conn.commit()
    except sqlite3.IntegrityError:
        conexao.desfazer(conn)
        raise ValueError("Este produto possui movimentações e não pode ser excluído.") from None
    except sqlite3.Error as erro:
        conexao.desfazer(conn)
        raise ValueError(conexao.mensagem_erro(erro)) from None
    if cursor.rowcount == 0:
        raise ValueError("Produto não encontrado.")


def valor_total_estoque(conn, categoria=None):
    """Soma de preço x quantidade de todos os produtos (ou de uma categoria)."""
    sql = "SELECT COALESCE(SUM(preco * quantidade), 0) FROM produtos"
    parametros = []
    if categoria:
        sql += " WHERE categoria = ?"
        parametros.append(categoria)
    return conn.execute(sql, parametros).fetchone()[0]


def estoque_baixo(conn):
    """Produtos com quantidade igual ou abaixo do estoque mínimo."""
    return conn.execute(
        "SELECT * FROM produtos WHERE quantidade <= estoque_minimo "
        "ORDER BY quantidade, nome COLLATE NOCASE").fetchall()


def valor_por_categoria(conn):
    """Valor em estoque por categoria; categorias vazias aparecem como 'Sem categoria'."""
    return conn.execute(
        "SELECT COALESCE(NULLIF(TRIM(categoria), ''), 'Sem categoria') AS categoria, "
        "COALESCE(SUM(preco * quantidade), 0) AS valor "
        "FROM produtos GROUP BY 1 ORDER BY valor DESC").fetchall()


def quantidade_por_produto(conn, limite=8):
    return conn.execute(
        "SELECT nome, quantidade FROM produtos "
        "ORDER BY quantidade DESC, nome COLLATE NOCASE LIMIT ?", (limite,)).fetchall()


def resumo(conn):
    """Indicadores do dashboard."""
    linha = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(quantidade), 0), "
        "COALESCE(SUM(preco * quantidade), 0), "
        "COALESCE(SUM(CASE WHEN quantidade <= estoque_minimo THEN 1 ELSE 0 END), 0) "
        "FROM produtos").fetchone()
    return {"produtos": linha[0], "unidades": linha[1],
            "valor": linha[2], "baixo": linha[3]}