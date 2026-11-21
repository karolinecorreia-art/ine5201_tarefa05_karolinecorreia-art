# menu_principal.py: menu principal com dashboard e alerta de estoque baixo
import sqlite3

import FreeSimpleGUI as sg

import cadastro_produtos
import conexao
import consulta_estoque
import produtos
import registro_movimentacao
import relatorios
import validacoes as val


def montar_layout():
    botao = dict(size=(30, 2), font=("Helvetica", 11))
    return [
        [sg.Text("CONTROLE DE ESTOQUE", font=("Helvetica", 22, "bold"),
                 justification="center", expand_x=True)],
        [sg.Text("Dashboard", font=("Helvetica", 13, "bold"))],
        [sg.Text("", key="-D1-", size=(50, 1))],
        [sg.Text("", key="-D2-", size=(50, 1))],
        [sg.Text("", key="-D3-", size=(50, 1))],
        [sg.Text("", key="-ALERTA-", size=(50, 1), font=("Helvetica", 12, "bold"))],
        [sg.Button("Cadastro de Produtos", key="-CAD-", **botao),
         sg.Button("Consultar Estoque", key="-CON-", **botao)],
        [sg.Button("Registrar Entrada (compra)", key="-ENT-", **botao),
         sg.Button("Registrar Saída (venda/uso)", key="-SAI-", **botao)],
        [sg.Button("Relatórios", key="-REL-", **botao),
         sg.Button("Fazer Backup agora", key="-BKP-", **botao)],
        [sg.Button("Sair", size=(30, 1))],
    ]


def atualizar_dashboard(window, conn):
    r = produtos.resumo(conn)
    window["-D1-"].update(f"Produtos cadastrados: {r['produtos']}")
    window["-D2-"].update(f"Unidades em estoque: {r['unidades']}")
    window["-D3-"].update(f"Valor total em estoque: {val.formatar_moeda(r['valor'])}")
    if r["baixo"]:
        window["-ALERTA-"].update(f"ATENÇÃO: {r['baixo']} produto(s) com estoque baixo!",
                                  text_color="#FF5252")
    else:
        window["-ALERTA-"].update("Estoque dentro do nível mínimo.", text_color="#69F0AE")


def avisar_estoque_baixo(conn):
    baixos = produtos.estoque_baixo(conn)
    if not baixos:
        return
    linhas = [f"{p['codigo']} - {p['nome']} ({p['quantidade']}/{p['estoque_minimo']})"
              for p in baixos[:10]]
    if len(baixos) > 10:
        linhas.append(f"... e mais {len(baixos) - 10} produto(s).")
    sg.popup("Produtos com estoque baixo (quantidade/mínimo):", *linhas,
             title="Alerta de estoque baixo", keep_on_top=True)


def backup_manual(conn):
    try:
        destino = conexao.fazer_backup(conn)
    except (OSError, sqlite3.Error) as erro:
        sg.popup_error(f"Não foi possível criar o backup:\n{erro}", title="Erro",
                       keep_on_top=True)
        return
    sg.popup("Backup criado em:", destino, title="Backup", keep_on_top=True)


def executar(conn):
    window = sg.Window("Controle de Estoque - INE5201", montar_layout(),
                       finalize=True, element_justification="center")
    atualizar_dashboard(window, conn)
    avisar_estoque_baixo(conn)
    while True:
        evento, _ = window.read()
        if evento in (sg.WIN_CLOSED, "Sair"):
            break
        if evento == "-CAD-":
            cadastro_produtos.abrir(conn)
        elif evento == "-ENT-":
            registro_movimentacao.abrir(conn, "entrada")
        elif evento == "-SAI-":
            registro_movimentacao.abrir(conn, "saida")
        elif evento == "-CON-":
            consulta_estoque.abrir(conn)
        elif evento == "-REL-":
            relatorios.abrir(conn)
        elif evento == "-BKP-":
            backup_manual(conn)
        atualizar_dashboard(window, conn)
    window.close()
    