-- banco.sql: criação do banco de dados do Sistema de Controle de Estoque
-- INE5201 - Tarefa 05

CREATE TABLE IF NOT EXISTS produtos (
    codigo TEXT PRIMARY KEY NOT NULL CHECK(length(trim(codigo)) > 0),
    nome TEXT NOT NULL CHECK(length(trim(nome)) > 0),
    categoria TEXT,
    preco REAL NOT NULL CHECK(preco > 0),
    quantidade INTEGER NOT NULL DEFAULT 0 CHECK(quantidade >= 0),
    estoque_minimo INTEGER NOT NULL DEFAULT 5 CHECK(estoque_minimo >= 0)
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_codigo TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
    quantidade INTEGER NOT NULL CHECK(quantidade > 0),
    data TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_codigo) REFERENCES produtos(codigo) ON DELETE RESTRICT
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