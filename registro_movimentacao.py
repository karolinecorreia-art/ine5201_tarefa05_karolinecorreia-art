# registro_movimentacao.py: telas de entrada (compra) e saída (venda/uso)
import FreeSimpleGUI as sg

import movimentacoes
import produtos
import validacoes as val

TITULOS = {"entrada": "Registro de Entrada (compra)",
           "saida": "Registro de Saída (venda/uso)"}
ROTULOS = {"entrada": "Entrada", "saida": "Saída"}
CABECALHO = ["Data", "Código", "Produto", "Tipo", "Qtd."]
ERRO, OK = "#FF5252", "#69F0AE"


def opcoes_produtos(conn):
    return [f"{p['codigo']} - {p['nome']}" for p in produtos.listar(conn)]


def codigo_da_opcao(opcao):
    return opcao.split(" - ", 1)[0]


def linhas_recentes(conn, tipo):
    return [[m["data"], m["codigo"], m["nome"], m["tipo"], m["quantidade"]]
            for m in movimentacoes.historico(conn, tipo=tipo, limite=10)]


def texto_saldo(conn, opcao):
    if not opcao:
        return "Selecione um produto."
    p = produtos.buscar(conn, codigo_da_opcao(opcao))
    if p is None:
        return ""
    return (f"Estoque atual: {p['quantidade']} | Mínimo: {p['estoque_minimo']} | "
            f"Preço: {val.formatar_moeda(p['preco'])}")


def abrir(conn, tipo):
    opcoes = opcoes_produtos(conn)
    if not opcoes:
        sg.popup_error("Cadastre ao menos um produto antes de registrar movimentações.",
                       title="Sem produtos", keep_on_top=True)
        return
    layout = [
        [sg.Text(TITULOS[tipo], font=("Helvetica", 16, "bold"))],
        [sg.Text("Produto:", size=(12, 1)),
         sg.Combo(opcoes, key="-PROD-", readonly=True, enable_events=True, size=(45, 1))],
        [sg.Text("Selecione um produto.", key="-SALDO-", size=(70, 1))],
        [sg.Text("Quantidade:", size=(12, 1)), sg.Input(key="-QTD-", size=(12, 1))],
        [sg.Text("", key="-MSG-", size=(70, 2))],
        [sg.Button("Registrar", key="-REG-"), sg.Button("Fechar")],
        [sg.Text("Últimas movimentações deste tipo:")],
        [sg.Table(linhas_recentes(conn, tipo), headings=CABECALHO, key="-TAB-",
                  num_rows=8, auto_size_columns=False,
                  col_widths=[18, 10, 28, 8, 6], justification="left")],
    ]
    window = sg.Window(TITULOS[tipo], layout, modal=True, finalize=True)
    while True:
        evento, valores = window.read()
        if evento in (sg.WIN_CLOSED, "Fechar"):
            break
        if evento == "-PROD-":
            window["-SALDO-"].update(texto_saldo(conn, valores["-PROD-"]))
        elif evento == "-REG-":
            try:
                if not valores["-PROD-"]:
                    raise ValueError("Selecione um produto.")
                quantidade = val.validar_quantidade(valores["-QTD-"])
                codigo = codigo_da_opcao(valores["-PROD-"])
                movimentacoes.registrar(conn, codigo, tipo, quantidade)
            except ValueError as erro:
                window["-MSG-"].update(str(erro), text_color=ERRO)
                continue
            produto = produtos.buscar(conn, codigo)
            window["-MSG-"].update(f"{ROTULOS[tipo]} registrada! "
                                   f"Novo estoque: {produto['quantidade']}", text_color=OK)
            window["-SALDO-"].update(texto_saldo(conn, valores["-PROD-"]))
            window["-QTD-"].update("")
            window["-TAB-"].update(values=linhas_recentes(conn, tipo))
            if tipo == "saida" and produto["quantidade"] <= produto["estoque_minimo"]:
                sg.popup("ALERTA DE ESTOQUE BAIXO",
                         f"{produto['nome']}: restam {produto['quantidade']} "
                         f"(mínimo {produto['estoque_minimo']}).",
                         title="Estoque baixo", keep_on_top=True)
    window.close()