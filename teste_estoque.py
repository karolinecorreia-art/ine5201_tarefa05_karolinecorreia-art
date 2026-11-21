# teste_estoque.py: testes automatizados do banco, das validações e do backup
import os
import sqlite3
import tempfile
import unittest

import conexao
import exportacao
import movimentacoes
import produtos
import validacoes as val


class TesteEstoque(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "teste.db")
        self.conn = conexao.iniciar_banco(self.caminho)
        produtos.cadastrar(self.conn, "A1", "Caneta", "Papelaria", 2.5, 5)

    def tearDown(self):
        self.conn.close()
        self.pasta.cleanup()

    def quantidade(self):
        return produtos.buscar(self.conn, "A1")["quantidade"]

    # ----- regras principais -----
    def test_codigo_unico(self):
        with self.assertRaises(ValueError):
            produtos.cadastrar(self.conn, "A1", "Outra", "Papelaria", 1.0, 5)

    def test_entrada_aumenta_quantidade(self):
        movimentacoes.registrar(self.conn, "A1", "entrada", 10)
        self.assertEqual(self.quantidade(), 10)

    def test_saida_diminui_quantidade(self):
        movimentacoes.registrar(self.conn, "A1", "entrada", 10)
        movimentacoes.registrar(self.conn, "A1", "saida", 4)
        self.assertEqual(self.quantidade(), 6)

    def test_saida_maior_que_estoque_e_recusada(self):
        movimentacoes.registrar(self.conn, "A1", "entrada", 3)
        with self.assertRaises(ValueError):
            movimentacoes.registrar(self.conn, "A1", "saida", 5)
        self.assertEqual(self.quantidade(), 3)
        self.assertFalse(self.conn.in_transaction)   # a transação foi desfeita

    def test_trigger_impede_saida_sem_estoque(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO movimentacoes (produto_codigo, tipo, "
                              "quantidade) VALUES ('A1', 'saida', 1)")

    def test_valor_total_e_estoque_baixo(self):
        movimentacoes.registrar(self.conn, "A1", "entrada", 4)
        self.assertAlmostEqual(produtos.valor_total_estoque(self.conn), 10.0)
        self.assertEqual([p["codigo"] for p in produtos.estoque_baixo(self.conn)], ["A1"])

    def test_historico_com_filtros(self):
        movimentacoes.registrar(self.conn, "A1", "entrada", 5)
        movimentacoes.registrar(self.conn, "A1", "saida", 2)
        self.assertEqual(len(movimentacoes.historico(self.conn)), 2)
        self.assertEqual(len(movimentacoes.historico(self.conn, tipo="saida")), 1)
        self.assertEqual(len(movimentacoes.historico(self.conn, categoria="Outra")), 0)

    def test_nao_exclui_produto_com_movimentacao(self):
        movimentacoes.registrar(self.conn, "A1", "entrada", 1)
        with self.assertRaises(ValueError):
            produtos.excluir(self.conn, "A1")

    def test_validacoes(self):
        self.assertEqual(val.validar_codigo(" ab-1 "), "AB-1")
        self.assertEqual(val.validar_preco("12,50"), 12.5)
        self.assertEqual(val.validar_categoria("  "), "Sem categoria")
        with self.assertRaises(ValueError):
            val.validar_quantidade("-3")
        with self.assertRaises(ValueError):
            val.validar_quantidade("abc")
        with self.assertRaises(ValueError):
            val.validar_preco("0")

    def test_exportar_csv(self):
        caminho = os.path.join(self.pasta.name, "r.csv")
        exportacao.exportar_csv(caminho, ["Codigo", "Nome"], [["A1", "Caneta"]])
        with open(caminho, encoding="utf-8-sig") as arquivo:
            self.assertEqual(arquivo.read().splitlines(), ["Codigo;Nome", "A1;Caneta"])

    # ----- atualização e exclusão de produtos -----
    def test_atualizar_produto(self):
        produtos.atualizar(self.conn, "A1", "Caneta Azul", "Escritório", 3.0, 8)
        p = produtos.buscar(self.conn, "A1")
        self.assertEqual((p["nome"], p["categoria"], p["preco"], p["estoque_minimo"]),
                         ("Caneta Azul", "Escritório", 3.0, 8))

    def test_atualizar_produto_inexistente(self):
        with self.assertRaises(ValueError):
            produtos.atualizar(self.conn, "ZZZ", "X", "Y", 1.0, 1)

    def test_excluir_produto_sem_movimentacao(self):
        produtos.excluir(self.conn, "A1")
        self.assertIsNone(produtos.buscar(self.conn, "A1"))

    def test_excluir_produto_inexistente(self):
        with self.assertRaises(ValueError):
            produtos.excluir(self.conn, "ZZZ")

    # ----- movimentações inválidas -----
    def test_movimentacao_produto_inexistente(self):
        with self.assertRaises(ValueError):
            movimentacoes.registrar(self.conn, "ZZZ", "entrada", 1)
        self.assertFalse(self.conn.in_transaction)

    def test_movimentacao_quantidade_invalida(self):
        for quantidade in (0, -1):
            with self.subTest(quantidade=quantidade):
                with self.assertRaises(ValueError):
                    movimentacoes.registrar(self.conn, "A1", "entrada", quantidade)

    def test_movimentacao_tipo_invalido(self):
        with self.assertRaises(ValueError):
            movimentacoes.registrar(self.conn, "A1", "venda", 1)

    # ----- restrições do banco -----
    def test_banco_recusa_valores_invalidos(self):
        comandos = [
            "INSERT INTO produtos (codigo, nome, preco) VALUES ('B1', 'X', -1)",
            "INSERT INTO produtos (codigo, nome, preco) VALUES ('B2', 'X', 0)",
            "INSERT INTO produtos (codigo, nome, preco, quantidade) VALUES ('B3', 'X', 1, -1)",
            "INSERT INTO produtos (codigo, nome, preco, estoque_minimo) VALUES ('B4', 'X', 1, -1)",
            "INSERT INTO produtos (codigo, preco) VALUES ('B5', 1)",
            "INSERT INTO movimentacoes (tipo, quantidade) VALUES ('entrada', 1)",
            "INSERT INTO movimentacoes (produto_codigo, tipo, quantidade) VALUES ('A1', 'venda', 1)",
            "INSERT INTO movimentacoes (produto_codigo, tipo, quantidade) VALUES ('ZZZ', 'entrada', 1)",
        ]
        for comando in comandos:
            with self.subTest(comando=comando):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.conn.execute(comando)
                self.conn.rollback()

    def test_historico_tipo_e_categoria(self):
        produtos.cadastrar(self.conn, "B1", "Grampeador", "Escritório", 20.0, 2)
        movimentacoes.registrar(self.conn, "A1", "entrada", 5)
        movimentacoes.registrar(self.conn, "A1", "saida", 1)
        movimentacoes.registrar(self.conn, "B1", "entrada", 3)
        combinado = movimentacoes.historico(self.conn, tipo="entrada", categoria="Papelaria")
        self.assertEqual(len(combinado), 1)
        self.assertEqual(combinado[0]["codigo"], "A1")
        self.assertEqual(len(movimentacoes.historico(self.conn, tipo="entrada")), 2)
        self.assertEqual(len(movimentacoes.historico(self.conn, categoria="Escritório")), 1)

    # ----- backup -----
    def test_backup_valido_e_sem_sobrescrever(self):
        pasta = os.path.join(self.pasta.name, "bkp")
        primeiro = conexao.fazer_backup(self.conn, pasta)
        segundo = conexao.fazer_backup(self.conn, pasta)      # mesmo segundo, na maioria das vezes
        self.assertNotEqual(primeiro, segundo)
        self.assertEqual(len(os.listdir(pasta)), 2)
        self.assertTrue(conexao.backup_valido(primeiro))
        copia = conexao.conectar(primeiro)
        try:
            self.assertIsNotNone(produtos.buscar(copia, "A1"))
        finally:
            copia.close()

    def test_backup_mantem_apenas_os_mais_recentes(self):
        pasta = os.path.join(self.pasta.name, "bkp")
        for _ in range(4):
            conexao.fazer_backup(self.conn, pasta, manter=2)
        self.assertEqual(len(os.listdir(pasta)), 2)

    # ----- exportação e banco bloqueado -----
    def test_exportar_csv_com_acentos(self):
        caminho = os.path.join(self.pasta.name, "acentos.csv")
        exportacao.exportar_csv(caminho, ["Código", "Descrição"], [["A1", "Café açucarado"]])
        with open(caminho, encoding="utf-8-sig") as arquivo:
            self.assertEqual(arquivo.read().splitlines(),
                             ["Código;Descrição", "A1;Café açucarado"])

    def test_banco_bloqueado_gera_mensagem_clara(self):
        outra = conexao.conectar(self.caminho, timeout=0.1)
        self.conn.execute("BEGIN IMMEDIATE")          # esta conexão trava o banco
        try:
            with self.assertRaises(ValueError) as contexto:
                movimentacoes.registrar(outra, "A1", "entrada", 1)
            self.assertIn("em uso", str(contexto.exception))
        finally:
            self.conn.rollback()
            outra.close()


if __name__ == "__main__":
    unittest.main()