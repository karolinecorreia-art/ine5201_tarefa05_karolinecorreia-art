# exportacao.py: exportação de relatórios em CSV
import csv


def exportar_csv(caminho, cabecalho, linhas):
    """Grava o CSV com ';' e utf-8-sig, para abrir direto no Excel em português."""
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    return caminho


def exportar_com_dialogo(cabecalho, linhas, nome_padrao):
    """Abre a janela 'Salvar como' e exporta. Devolve o caminho ou None."""
    import FreeSimpleGUI as sg
    caminho = sg.popup_get_file(
        "Salvar relatório como", save_as=True, default_extension=".csv",
        default_path=nome_padrao, file_types=(("Arquivo CSV", "*.csv"),),
        no_window=True)
    if not caminho:
        return None
    try:
        exportar_csv(caminho, cabecalho, linhas)
    except OSError as erro:
        sg.popup_error(f"Não foi possível salvar o arquivo:\n{erro}",
                       title="Erro", keep_on_top=True)
        return None
    sg.popup("Relatório exportado com sucesso!", caminho,
             title="Exportação", keep_on_top=True)
    return caminho