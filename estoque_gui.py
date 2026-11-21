# estoque_gui.py: arquivo principal do Sistema de Controle de Estoque
import sqlite3

import FreeSimpleGUI as sg

import conexao
import menu_principal


def main():
    sg.theme("DarkTeal9")          # para mudar o visual, troque o nome do tema
    try:
        conn = conexao.iniciar_banco()
    except (OSError, sqlite3.Error) as erro:
        sg.popup_error("Não foi possível abrir o banco de dados:", str(erro),
                       title="Erro", keep_on_top=True)
        return
    try:
        menu_principal.executar(conn)
    finally:
        try:
            conexao.fazer_backup(conn)      # backup automático ao sair
        except (OSError, sqlite3.Error) as erro:
            sg.popup_error("Atenção: o backup automático falhou.", str(erro),
                           title="Backup", keep_on_top=True)
        conn.close()


if __name__ == "__main__":
    main()