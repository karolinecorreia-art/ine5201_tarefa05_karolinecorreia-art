# consulta_estoque.py: consulta do estoque atual, com filtro por categoria
import FreeSimpleGUI as sg

import exportacao
import produtos
import validacoes as val

CABECALHO = ["Código", "Nome", "Categoria", "Preço", "Qtd.", "Mín.",
             "Valor total", "Situação"]


def esta_baixo(p):
    return p["quantidade"] <= p["estoque_minimo"]


def montar_linhas(lista):
    linhas, cores = [], []
    for i, p in enumerate(lista):
        linhas.append([p["codigo"], p["nome"], p["categoria"],
                       val.formatar_moeda(p["preco"]), p["quantidade"],
                       p["estoque_minimo"], val.formatar_moeda(p["preco"] * p["quantidade"]),
                       "ESTOQUE BAIXO" if esta_baixo(p) else "OK"])
        if esta_baixo(p):
            cores.append((i, "white", "#B71C1C"))
    return linhas, cores


def linhas_csv(lista):
    linhas = [[p["codigo"], p["nome"], p["categoria"], val.formatar_decimal(p["preco"]),
               p["quantidade"], p["estoque_minimo"],
               val.formatar_decimal(p["preco"] * p["quantidade"]),
               "ESTOQUE BAIXO" if esta_baixo(p) else "OK"] for p in lista]
    total = sum(p["preco"] * p["quantidade"] for p in lista)
    linhas.append(["TOTAL", "", "", "", "", "", val.formatar_decimal(total), ""])
    return linhas


def filtrar(conn, valores):
    categoria = None if valores["-CAT-"] in ("", "Todas") else valores["-CAT-"]
    busca = valores["-BUSCA-"].strip() or None
    return produtos.listar(conn, categoria, busca)


def atualizar(window, lista):
    linhas, cores = montar_linhas(lista)
    window["-TAB-"].update(values=linhas, row_colors=cores)
    total = sum(p["preco"] * p["quantidade"] for p in lista)
    baixos = sum(1 for p in lista if esta_baixo(p))
    window["-TOTAL-"].update(f"Itens listados: {len(lista)} | Com estoque baixo: {baixos} | "
                             f"Valor total em estoque: {val.formatar_moeda(total)}")


def abrir(conn):
    categorias = ["Todas"] + produtos.listar_categorias(conn)
    linhas, cores = montar_linhas(produtos.listar(conn))
    layout = [
        [sg.Text("Consulta de Estoque Atual", font=("Helvetica", 16, "bold"))],
        [sg.Text("Categoria:"),
         sg.Combo(categorias, default_value="Todas", key="-CAT-", readonly=True,
                  enable_events=True, size=(22, 1)),
         sg.Text("Buscar (código ou nome):"),
         sg.Input(key="-BUSCA-", size=(24, 1), enable_events=True)],
        [sg.Table(linhas, headings=CABECALHO, key="-TAB-", num_rows=14,
                  auto_size_columns=False, col_widths=[10, 24, 14, 12, 6, 6, 14, 15],
                  justification="left", row_colors=cores)],
        [sg.Text("", key="-TOTAL-", font=("Helvetica", 11, "bold"), size=(90, 1))],
        [sg.Button("Exportar CSV", key="-EXP-"), sg.Button("Fechar")],
    ]
    window = sg.Window("Consulta de Estoque", layout, modal=True, finalize=True)
    atualizar(window, produtos.listar(conn))
    while True:
        evento, valores = window.read()
        if evento in (sg.WIN_CLOSED, "Fechar"):
            break
        if evento in ("-CAT-", "-BUSCA-"):
            atualizar(window, filtrar(conn, valores))
        elif evento == "-EXP-":
            exportacao.exportar_com_dialogo(CABECALHO, linhas_csv(filtrar(conn, valores)),
                                            "estoque_atual.csv")
    window.close()