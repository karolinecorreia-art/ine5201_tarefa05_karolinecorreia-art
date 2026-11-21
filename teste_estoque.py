# teste_estoque.py: testes automatizados do banco e das validações
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
        self.conn = conexao.iniciar_banco(os.path.join(self.pasta.name, "teste.db"))
        produtos.cadastrar(self.conn, "A1", "Caneta", "Papelaria", 2.5, 5)

    def tearDown(self):
        self.conn.close()
        self.pasta.cleanup()

    def quantidade(self):
        return produtos.buscar(self.conn, "A1")["quantidade"]

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


if __name__ == "__main__":
    unittest.main()