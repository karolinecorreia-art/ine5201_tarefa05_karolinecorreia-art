# cadastro_produtos.py: tela de cadastro (código, nome, categoria, preço)
import FreeSimpleGUI as sg

import produtos
import validacoes as val

CABECALHO = ["Código", "Nome", "Categoria", "Preço", "Qtd.", "Mín."]
ERRO, OK = "#FF5252", "#69F0AE"


def montar_linhas(lista):
    return [[p["codigo"], p["nome"], p["categoria"], val.formatar_moeda(p["preco"]),
             p["quantidade"], p["estoque_minimo"]] for p in lista]


def ler_formulario(valores):
    codigo = val.validar_codigo(valores["-COD-"])
    nome = val.validar_nome(valores["-NOME-"])
    categoria = val.validar_categoria(valores["-CAT-"])
    preco = val.validar_preco(valores["-PRECO-"])
    minimo = val.validar_quantidade(valores["-MIN-"], minimo=0, rotulo="Estoque mínimo")
    return codigo, nome, categoria, preco, minimo


def limpar(window, conn):
    window["-COD-"].update("", disabled=False)
    window["-NOME-"].update("")
    window["-CAT-"].update("", values=produtos.listar_categorias(conn))
    window["-PRECO-"].update("")
    window["-MIN-"].update("5")
    window["-CADASTRAR-"].update(disabled=False)
    window["-SALVAR-"].update(disabled=True)
    window["-EXCLUIR-"].update(disabled=True)


def recarregar(window, conn):
    lista = produtos.listar(conn)
    window["-TAB-"].update(values=montar_linhas(lista))
    return lista


def confirmar_salvar():
    return sg.popup_yes_no("Salvar as alterações deste produto?", title="Confirmar",
                           keep_on_top=True) == "Yes"


def abrir(conn):
    lista = produtos.listar(conn)
    layout = [
        [sg.Text("Cadastro de Produtos", font=("Helvetica", 16, "bold"))],
        [sg.Text("Código:", size=(14, 1)), sg.Input(key="-COD-", size=(20, 1))],
        [sg.Text("Nome:", size=(14, 1)), sg.Input(key="-NOME-", size=(40, 1))],
        [sg.Text("Categoria:", size=(14, 1)),
         sg.Combo(produtos.listar_categorias(conn), key="-CAT-", size=(30, 1), readonly=False)],
        [sg.Text("Preço (R$):", size=(14, 1)), sg.Input(key="-PRECO-", size=(14, 1))],
        [sg.Text("Estoque mínimo:", size=(14, 1)), sg.Input("5", key="-MIN-", size=(8, 1))],
        [sg.Button("Cadastrar", key="-CADASTRAR-"),
         sg.Button("Salvar alterações", key="-SALVAR-", disabled=True),
         sg.Button("Excluir", key="-EXCLUIR-", disabled=True),
         sg.Button("Limpar", key="-LIMPAR-"), sg.Button("Fechar")],
        [sg.Text("", key="-MSG-", size=(70, 2))],
        [sg.Text("Produtos cadastrados (clique em uma linha para editar ou excluir):")],
        [sg.Table(montar_linhas(lista), headings=CABECALHO, key="-TAB-", num_rows=10,
                  auto_size_columns=False, col_widths=[10, 28, 16, 12, 6, 6],
                  justification="left", enable_events=True,
                  select_mode=sg.TABLE_SELECT_MODE_BROWSE)],
    ]
    window = sg.Window("Cadastro de Produtos", layout, modal=True, finalize=True)
    while True:
        evento, valores = window.read()
        if evento in (sg.WIN_CLOSED, "Fechar"):
            break
        if evento == "-LIMPAR-":
            limpar(window, conn)
            window["-MSG-"].update("")
        elif evento == "-TAB-" and valores["-TAB-"]:
            p = lista[valores["-TAB-"][0]]
            window["-COD-"].update(p["codigo"], disabled=True)
            window["-NOME-"].update(p["nome"])
            window["-CAT-"].update(p["categoria"])
            window["-PRECO-"].update(val.formatar_decimal(p["preco"]))
            window["-MIN-"].update(str(p["estoque_minimo"]))
            window["-CADASTRAR-"].update(disabled=True)
            window["-SALVAR-"].update(disabled=False)
            window["-EXCLUIR-"].update(disabled=False)
            window["-MSG-"].update("Editando o produto selecionado.", text_color=OK)
        elif evento in ("-CADASTRAR-", "-SALVAR-"):
            if evento == "-SALVAR-" and not confirmar_salvar():
                continue
            try:
                dados = ler_formulario(valores)
                if evento == "-CADASTRAR-":
                    produtos.cadastrar(conn, *dados)
                    mensagem = "Produto cadastrado com sucesso!"
                else:
                    produtos.atualizar(conn, *dados)
                    mensagem = "Produto atualizado com sucesso!"
            except ValueError as erro:
                window["-MSG-"].update(str(erro), text_color=ERRO)
                continue
            lista = recarregar(window, conn)
            limpar(window, conn)
            window["-MSG-"].update(mensagem, text_color=OK)
        elif evento == "-EXCLUIR-":
            codigo = valores["-COD-"]
            if sg.popup_yes_no(f"Excluir o produto {codigo}?", title="Confirmar",
                               keep_on_top=True) != "Yes":
                continue
            try:
                produtos.excluir(conn, codigo)
            except ValueError as erro:
                window["-MSG-"].update(str(erro), text_color=ERRO)
                continue
            lista = recarregar(window, conn)
            limpar(window, conn)
            window["-MSG-"].update("Produto excluído.", text_color=OK)
    window.close()