# estoque_gui.py: arquivo principal do Sistema de Controle de Estoque
import sqlite3

import FreeSimpleGUI as sg

import conexao
import menu_principal


def main():
    sg.theme("DarkTeal9")          # para mudar o visual, troque o nome do tema
    conn = conexao.iniciar_banco()
    try:
        menu_principal.executar(conn)
    finally:
        try:
            conexao.fazer_backup(conn)      # backup automático ao sair
        except (OSError, sqlite3.Error):
            pass
        conn.close()


if __name__ == "__main__":
    main()