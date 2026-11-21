# dados_exemplo.py: popula o banco com produtos de exemplo (pode rodar mais de uma vez)
import conexao
import movimentacoes
import produtos

# (código, nome, categoria, preço, estoque mínimo, entrada inicial, saída)
EXEMPLOS = [
    ("CAN001", "Caneta Azul", "Papelaria", 2.50, 20, 100, 30),
    ("CAD001", "Caderno 96 folhas", "Papelaria", 14.90, 10, 40, 33),
    ("PAP001", "Papel A4 (resma)", "Papelaria", 28.00, 5, 25, 3),
    ("MOU001", "Mouse USB", "Informática", 35.00, 5, 15, 8),
    ("TEC001", "Teclado ABNT2", "Informática", 59.90, 5, 12, 9),
    ("PEN001", "Pen drive 32GB", "Informática", 32.00, 5, 30, 10),
    ("CAB001", "Cabo HDMI 2m", "Informática", 22.50, 5, 20, 2),
    ("CAF001", "Café 500g", "Alimentos", 18.00, 10, 60, 25),
    ("ACU001", "Açúcar 1kg", "Alimentos", 5.50, 10, 80, 50),
    ("DET001", "Detergente 500ml", "Limpeza", 3.20, 15, 70, 60),
]


def main():
    conn = conexao.iniciar_banco()
    for codigo, nome, categoria, preco, minimo, entrada, saida in EXEMPLOS:
        try:
            produtos.cadastrar(conn, codigo, nome, categoria, preco, minimo)
        except ValueError:
            continue                      # já existe: não repete as movimentações
        movimentacoes.registrar(conn, codigo, "entrada", entrada)
        movimentacoes.registrar(conn, codigo, "saida", saida)
    conn.close()
    print("Dados de exemplo inseridos.")


if __name__ == "__main__":
    main()