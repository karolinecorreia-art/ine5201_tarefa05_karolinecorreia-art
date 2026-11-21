-- banco.sql: criação do banco de dados do Sistema de Controle de Estoque
-- INE5201 - Tarefa 05

CREATE TABLE IF NOT EXISTS produtos (
    codigo TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    categoria TEXT,
    preco REAL NOT NULL,
    quantidade INTEGER DEFAULT 0,
    estoque_minimo INTEGER DEFAULT 5
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_codigo TEXT,
    tipo TEXT CHECK(tipo IN ('entrada', 'saida')),
    quantidade INTEGER NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_codigo) REFERENCES produtos(codigo)
);

-- Trigger: a quantidade da movimentação deve ser maior que zero
CREATE TRIGGER IF NOT EXISTS trg_movimentacao_quantidade_valida
BEFORE INSERT ON movimentacoes
WHEN NEW.quantidade <= 0
BEGIN
    SELECT RAISE(ABORT, 'A quantidade deve ser maior que zero.');
END;

-- Trigger: não permite saída maior que o estoque (quantidade nunca fica negativa)
CREATE TRIGGER IF NOT EXISTS trg_saida_sem_estoque
BEFORE INSERT ON movimentacoes
WHEN NEW.tipo = 'saida'
 AND NEW.quantidade > (SELECT quantidade FROM produtos WHERE codigo = NEW.produto_codigo)
BEGIN
    SELECT RAISE(ABORT, 'Estoque insuficiente para esta saída.');
END;

-- Trigger: atualiza a quantidade do produto automaticamente
CREATE TRIGGER IF NOT EXISTS trg_atualiza_quantidade
AFTER INSERT ON movimentacoes
BEGIN
    UPDATE produtos
    SET quantidade = quantidade +
        CASE NEW.tipo WHEN 'entrada' THEN NEW.quantidade ELSE -NEW.quantidade END
    WHERE codigo = NEW.produto_codigo;
END;