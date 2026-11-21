# relatorios.py: relatórios visuais (gráfico), histórico e estoque baixo
import FreeSimpleGUI as sg

import exportacao
import movimentacoes
import produtos
import validacoes as val

CAB_HIST = ["Data", "Código", "Produto", "Categoria", "Tipo", "Qtd."]
CAB_BAIXO = ["Código", "Nome", "Categoria", "Qtd.", "Mínimo"]
OPCOES_GRAFICO = ["Valor em estoque por categoria (R$)", "Quantidade por produto (top 8)"]
LARGURA, ALTURA = 640, 320


def dados_grafico(conn, escolha):
    if escolha == OPCOES_GRAFICO[0]:
        return [(l["categoria"], l["valor"]) for l in produtos.valor_por_categoria(conn)[:8]]
    return [(l["nome"], l["quantidade"]) for l in produtos.quantidade_por_produto(conn, 8)]


def desenhar_grafico(grafico, dados):
    """Gráfico de barras desenhado no próprio FreeSimpleGUI (sem matplotlib)."""
    grafico.erase()
    if not dados or max(v for _, v in dados) <= 0:
        grafico.draw_text("Sem dados para exibir", (LARGURA / 2, ALTURA / 2),
                          color="black", font=("Helvetica", 14))
        return
    base, topo, esquerda = 45, 25, 30
    area = ALTURA - base - topo
    espaco = (LARGURA - esquerda - 20) / len(dados)
    largura_barra = espaco * 0.6
    maximo = max(v for _, v in dados)
    grafico.draw_line((esquerda, base), (LARGURA - 10, base), color="black", width=2)
    grafico.draw_line((esquerda, base), (esquerda, ALTURA - topo + 10), color="black", width=2)
    for i, (rotulo, valor) in enumerate(dados):
        x = esquerda + i * espaco + (espaco - largura_barra) / 2
        altura_barra = area * valor / maximo
        grafico.draw_rectangle((x, base + altura_barra), (x + largura_barra, base),
                               fill_color="#1F7A8C", line_color="black")
        grafico.draw_text(f"{valor:.0f}", (x + largura_barra / 2, base + altura_barra + 10),
                          color="black", font=("Helvetica", 8))
        grafico.draw_text(str(rotulo)[:10], (x + largura_barra / 2, base - 14),
                          color="black", font=("Helvetica", 8))


def atualizar_grafico(window, conn, escolha):
    desenhar_grafico(window["-GRAFICO-"], dados_grafico(conn, escolha))
    window["-TOTALREL-"].update("Valor total em estoque: "
                                + val.formatar_moeda(produtos.valor_total_estoque(conn)))


def linhas_historico(conn, valores):
    tipo = None if valores["-HTIPO-"] in ("", "Todos") else valores["-HTIPO-"]
    categoria = None if valores["-HCAT-"] in ("", "Todas") else valores["-HCAT-"]
    return [[m["data"], m["codigo"], m["nome"], m["categoria"], m["tipo"], m["quantidade"]]
            for m in movimentacoes.historico(conn, tipo, categoria)]


def linhas_baixo(conn):
    return [[p["codigo"], p["nome"], p["categoria"], p["quantidade"], p["estoque_minimo"]]
            for p in produtos.estoque_baixo(conn)]


def abrir(conn):
    categorias = ["Todas"] + produtos.listar_categorias(conn)
    aba_graficos = [
        [sg.Text("Gráfico:"),
         sg.Combo(OPCOES_GRAFICO, default_value=OPCOES_GRAFICO[0], key="-GRAF-",
                  readonly=True, enable_events=True, size=(40, 1))],
        [sg.Graph((LARGURA, ALTURA), (0, 0), (LARGURA, ALTURA),
                  background_color="white", key="-GRAFICO-")],
        [sg.Text("", key="-TOTALREL-", font=("Helvetica", 11, "bold"), size=(60, 1))],
    ]
    aba_historico = [
        [sg.Text("Tipo:"),
         sg.Combo(["Todos", "entrada", "saida"], default_value="Todos", key="-HTIPO-",
                  readonly=True, enable_events=True, size=(10, 1)),
         sg.Text("Categoria:"),
         sg.Combo(categorias, default_value="Todas", key="-HCAT-", readonly=True,
                  enable_events=True, size=(20, 1))],
        [sg.Table(linhas_historico(conn, {"-HTIPO-": "Todos", "-HCAT-": "Todas"}),
                  headings=CAB_HIST, key="-HTAB-", num_rows=14, auto_size_columns=False,
                  col_widths=[18, 10, 26, 14, 8, 6], justification="left")],
        [sg.Button("Exportar histórico (CSV)", key="-EXPH-")],
    ]
    aba_baixo = [
        [sg.Text("Produtos com quantidade igual ou abaixo do estoque mínimo:")],
        [sg.Table(linhas_baixo(conn), headings=CAB_BAIXO, key="-BTAB-", num_rows=14,
                  auto_size_columns=False, col_widths=[10, 28, 16, 6, 8],
                  justification="left")],
        [sg.Button("Exportar estoque baixo (CSV)", key="-EXPB-")],
    ]
    layout = [
        [sg.Text("Relatórios", font=("Helvetica", 16, "bold"))],
        [sg.TabGroup([[sg.Tab("Gráficos", aba_graficos),
                       sg.Tab("Histórico de movimentações", aba_historico),
                       sg.Tab("Estoque baixo", aba_baixo)]])],
        [sg.Button("Fechar")],
    ]
    window = sg.Window("Relatórios", layout, modal=True, finalize=True)
    atualizar_grafico(window, conn, OPCOES_GRAFICO[0])
    while True:
        evento, valores = window.read()
        if evento in (sg.WIN_CLOSED, "Fechar"):
            break
        if evento == "-GRAF-":
            atualizar_grafico(window, conn, valores["-GRAF-"])
        elif evento in ("-HTIPO-", "-HCAT-"):
            window["-HTAB-"].update(values=linhas_historico(conn, valores))
        elif evento == "-EXPH-":
            exportacao.exportar_com_dialogo(CAB_HIST, linhas_historico(conn, valores),
                                            "historico_movimentacoes.csv")
        elif evento == "-EXPB-":
            exportacao.exportar_com_dialogo(CAB_BAIXO, linhas_baixo(conn),
                                            "estoque_baixo.csv")
    window.close()