# registro_movimentacao.py: telas de entrada (compra) e saída (venda/uso)
import FreeSimpleGUI as sg

import movimentacoes
import produtos
import validacoes as val

TITULOS = {"entrada": "Registro de Entrada (compra)",
           "saida": "Registro de Saída (venda/uso)"}
ROTULOS = {"entrada": "Entrada", "saida": "Saída"}
CABECALHO = ["Data", "Código", "Produto", "Tipo", "Qtd."]
ERRO, OK, AVISO = "#FF5252", "#69F0AE", "#FFB74D"


def opcoes_produtos(conn):
    return [f"{p['codigo']} - {p['nome']}" for p in produtos.listar(conn)]


def codigo_da_opcao(opcao):
    return opcao.split(" - ", 1)[0]


def linhas_recentes(conn, tipo):
    return [[m["data"], m["codigo"], m["nome"], m["tipo"], m["quantidade"]]
            for m in movimentacoes.historico(conn, tipo=tipo, limite=10)]


def texto_saldo(conn, opcao, tipo):
    if not opcao:
        return "Selecione um produto."
    p = produtos.buscar(conn, codigo_da_opcao(opcao))
    if p is None:
        return ""
    texto = (f"Estoque atual: {p['quantidade']} | Mínimo: {p['estoque_minimo']} | "
             f"Preço: {val.formatar_moeda(p['preco'])}")
    if tipo == "saida":
        texto += f" | Máximo para saída: {p['quantidade']}"
    return texto


def verificar_entrada(conn, tipo, valores):
    """Devolve None se dá para registrar ou o motivo pelo qual ainda não dá."""
    if not valores["-PROD-"]:
        return "Selecione um produto."
    texto = valores["-QTD-"].strip()
    if not texto:
        return "Digite a quantidade."
    try:
        quantidade = val.validar_quantidade(texto)
    except ValueError as erro:
        return str(erro)
    if tipo == "saida":
        produto = produtos.buscar(conn, codigo_da_opcao(valores["-PROD-"]))
        if produto is not None and quantidade > produto["quantidade"]:
            return f"Estoque insuficiente: o máximo para saída é {produto['quantidade']}."
    return None


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
        [sg.Text("Selecione um produto.", key="-SALDO-", size=(95, 1))],
        [sg.Text("Quantidade:", size=(12, 1)),
         sg.Input(key="-QTD-", size=(12, 1), enable_events=True)],
        [sg.Text("", key="-MSG-", size=(80, 2))],
        [sg.Button("Registrar", key="-REG-", disabled=True), sg.Button("Fechar")],
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
        if evento in ("-PROD-", "-QTD-"):
            window["-SALDO-"].update(texto_saldo(conn, valores["-PROD-"], tipo))
            motivo = verificar_entrada(conn, tipo, valores)
            window["-REG-"].update(disabled=motivo is not None)
            if motivo and valores["-QTD-"].strip():
                window["-MSG-"].update(motivo, text_color=AVISO)
            else:
                window["-MSG-"].update("")
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
            window["-SALDO-"].update(texto_saldo(conn, valores["-PROD-"], tipo))
            window["-QTD-"].update("")
            window["-REG-"].update(disabled=True)
            window["-TAB-"].update(values=linhas_recentes(conn, tipo))
            window["-MSG-"].update(f"{ROTULOS[tipo]} registrada! "
                                   f"Novo estoque: {produto['quantidade']}", text_color=OK)
            if tipo == "saida" and produto["quantidade"] <= produto["estoque_minimo"]:
                sg.popup("ALERTA DE ESTOQUE BAIXO",
                         f"{produto['nome']}: restam {produto['quantidade']} "
                         f"(mínimo {produto['estoque_minimo']}).",
                         title="Estoque baixo", keep_on_top=True)
    window.close()