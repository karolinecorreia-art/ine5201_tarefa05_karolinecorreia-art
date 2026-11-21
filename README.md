# Jogo da Forca com Interface Gráfica

*INE5201 - Introdução à Ciência da Computação com Python*
Universidade Federal de Santa Catarina (UFSC) | Prof. Rafael Novo da Rosa
*Tarefa 03* | Prazo: 24/11/2026

## Autoras

| Nome | GitHub |
|---|---|
| Karoline de Quadros Correia | [@karolinecorreia-art](https://github.com/karolinecorreia-art) |
| Letícia Olivo Colognese | [@leticiacolognese-max](https://github.com/leticiacolognese-max) |

## Sobre o projeto

Sistema de controle de estoque com interface gráfica (FreeSimpleGUI) e banco de dados SQLite. Permite cadastrar produtos, registrar entradas (compra) e saídas (venda/uso), consultar o estoque, filtrar por categoria, gerar relatórios visuais, exportar em CSV e receber alertas de estoque baixo.

## Requisitos da tarefa e onde foram atendidos

### Interface gráfica

| Requisito | Situação | Onde está |
|---|---|---|
| Menu principal com navegação | Atendido | `menu_principal.py` |
| Cadastro de produtos (código, nome, categoria, preço) | Atendido | `cadastro_produtos.py` |
| Registro de entradas (compra) | Atendido | `registro_movimentacao.py` |
| Registro de saídas (venda/uso) | Atendido | `registro_movimentacao.py` |
| Consulta de estoque atual | Atendido | `consulta_estoque.py` |
| Relatórios visuais | Atendido | `relatorios.py` (gráfico de barras, histórico e estoque baixo) |
| Alerta de estoque baixo | Atendido | popup ao abrir e após saídas, banner no menu e linhas vermelhas na consulta |

### Banco de dados SQLite

| Requisito | Situação | Onde está |
|---|---|---|
| Tabela `produtos` | Atendido | `banco.sql` |
| Tabela `movimentacoes` | Atendido | `banco.sql` |
| Relacionamento entre tabelas | Atendido | chave estrangeira `produto_codigo` |
| Trigger para atualizar a quantidade (opcional) | Atendido | `trg_atualiza_quantidade` em `banco.sql` |

### Funcionalidades

| Requisito | Situação | Onde está |
|---|---|---|
| Validação de código único | Atendido | `produtos.cadastrar()` e chave primária |
| Validação de quantidade (não negativa) | Atendido | `validacoes.validar_quantidade()` e triggers |
| Cálculo de valor total em estoque | Atendido | `produtos.valor_total_estoque()` e consulta |
| Histórico de movimentações | Atendido | `movimentacoes.historico()` e aba do relatório |
| Filtro por categoria | Atendido | consulta de estoque e histórico |
| Exportação de relatório (CSV) | Atendido | `exportacao.py` |

## Uso do GitHub Copilot

O GitHub Copilot (extensão e Copilot Chat no VS Code) foi usado como apoio em duas etapas:

1. **Durante o desenvolvimento:** para tirar dúvidas sobre os triggers do `banco.sql` e sobre o uso de parâmetros `?` nas consultas SQL.
2. **Na revisão final:** O Copilot Chat analisou o projeto e devolveu 8 grupos de sugestões de melhoria (print em `screenshots/13_copilot.png`). Cada sugestão foi avaliada, e só foram aplicadas as que melhoravam o sistema sem aumentar o risco de erros ou fugir do escopo da tarefa.

### Sugestões do Copilot e decisões tomadas

| # | Sugestão do Copilot | Decisão | O que foi feito |
|---|---|---|---|
| 1 | Reforçar a integridade do banco | Aplicada em parte | Colunas obrigatórias (`NOT NULL`) e regras `CHECK` no `banco.sql`: preço maior que zero, quantidades não negativas, tipo `entrada` ou `saida`. **Não aplicada:** "estoque mínimo maior que a quantidade", porque todo produto novo começa com quantidade 0 e a regra bloquearia o cadastro; e a normalização de categorias, fora do escopo. |
| 2 | Movimentações seguras contra concorrência | Aplicada | O registro usa uma única transação com `BEGIN IMMEDIATE` (conferência do saldo e inserção juntas). O trigger continua como segunda camada de proteção. |
| 3 | Melhorar o tratamento de erros | Aplicada | Erros do SQLite viram mensagens claras (banco em uso, inacessível, fechado ou regra recusada). Se o backup automático falhar ao sair, o usuário é avisado. |
| 4 | Ampliar os testes | Aplicada | Os testes passaram de 10 para 23: atualização e exclusão, produto inexistente, quantidade inválida, restrições do banco, backup, CSV com acentos e banco bloqueado. |
| 5 | Melhorar a interface | Aplicada em parte | O botão **Registrar** só é habilitado com produto e quantidade válidos, a tela de saída mostra o máximo disponível e salvar alterações pede confirmação. **Não aplicadas:** ordenação por coluna e paginação do histórico. |
| 6 | Expandir os relatórios | Aplicada em parte | A categoria vazia aparece sempre como "Sem categoria". **Não aplicadas:** valores financeiros de entradas e saídas (a tabela `movimentacoes` não guarda o preço da época, então os valores sairiam errados), filtro por período e gráfico ao longo do tempo. |
| 7 | Backups mais confiáveis | Aplicada em parte | O backup não sobrescreve arquivos criados no mesmo segundo e o arquivo gerado é validado (não vazio e íntegro). **Não aplicadas:** restauração pela interface e escolha da pasta de destino. |
| 8 | Melhorar a documentação | Aplicada | README com instalação, execução, testes, tabelas, diagrama, localização do banco e dos backups. |

### Aprendizados com o uso do Copilot

- As sugestões são um ponto de partida e **precisam ser avaliadas**: uma delas (estoque mínimo menor ou igual à quantidade) quebraria o cadastro de produtos novos.
- O Copilot ajudou a enxergar um problema real, o intervalo entre conferir o saldo e registrar a saída, que foi resolvido com a transação.
- Todas as mudanças foram testadas com os testes automatizados antes de serem commitadas.

## Regras de integridade do banco

| Regra | Onde é garantida |
|---|---|
| Código único e obrigatório | Chave primária (`PRIMARY KEY NOT NULL`) |
| Nome e preço obrigatórios, preço maior que zero | `NOT NULL` e `CHECK(preco > 0)` |
| Quantidade e estoque mínimo nunca negativos | `CHECK(quantidade >= 0)` e `CHECK(estoque_minimo >= 0)` |
| Tipo da movimentação só `entrada` ou `saida` | `CHECK(tipo IN ('entrada', 'saida'))` |
| Movimentação sempre ligada a um produto existente | Chave estrangeira (`FOREIGN KEY`) |
| Produto com movimentações não pode ser excluído | `ON DELETE RESTRICT` |
| Saída maior que o estoque é recusada | Trigger `trg_saida_sem_estoque` e conferência no Python |

## Localização do banco e dos backups

- **Banco de dados:** `estoque.db`, na pasta do projeto, criado automaticamente a partir do `banco.sql` (não vai para o GitHub).
- **Backups:** pasta `backups/`, com um arquivo `estoque_AAAAMMDD_HHMMSS.db` criado ao sair do sistema e pelo botão **Fazer Backup agora**. Os 10 mais recentes são mantidos.
- Para começar do zero, feche o sistema, apague `estoque.db` e rode o programa de novo.


### Bônus

| Item | Situação |
|---|---|
| Dashboard com indicadores | Atendido (menu principal) |
| Backup automático do banco | Atendido (ao sair e pelo botão do menu, pasta `backups/`) |
| Gráficos de estoque | Atendido (barras desenhadas com o FreeSimpleGUI) |

## Diagrama do banco de dados

```mermaid
erDiagram
    PRODUTOS ||--o{ MOVIMENTACOES : "tem"
    PRODUTOS {
        TEXT codigo PK
        TEXT nome
        TEXT categoria
        REAL preco
        INTEGER quantidade
        INTEGER estoque_minimo
    }
    MOVIMENTACOES {
        INTEGER id PK
        TEXT produto_codigo FK
        TEXT tipo
        INTEGER quantidade
        TIMESTAMP data
    }
```

Um produto pode ter várias movimentações. Cada movimentação pertence a um único produto.

### Triggers

| Trigger | Função |
|---|---|
| `trg_movimentacao_quantidade_valida` | Recusa movimentação com quantidade menor ou igual a zero |
| `trg_saida_sem_estoque` | Recusa saída maior que o estoque, então a quantidade nunca fica negativa |
| `trg_atualiza_quantidade` | Soma ou subtrai a quantidade do produto a cada movimentação |

## Requisitos para executar

- Python 3.10 ou superior (com tkinter e sqlite3, já incluídos)
- FreeSimpleGUI (compatível com a sintaxe do PySimpleGUI)

## Como instalar e executar (Windows)

```
git clone https://github.com/karolinecorreia-art/ine5201-tarefa05-karolinecorreia-art.git
cd ine5201-tarefa05-karolinecorreia-art
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install FreeSimpleGUI
.\.venv\Scripts\python.exe main.py
```

O banco `estoque.db` é criado automaticamente na primeira execução, a partir do `banco.sql`. Para carregar produtos de exemplo (opcional):

```
.\.venv\Scripts\python.exe dados_exemplo.py
```

## Testes automatizados

```
.\.venv\Scripts\python.exe -m unittest teste_estoque -v
```

Resultado esperado: todos os testes terminam com `OK`.

## Estrutura do projeto

```
ine5201-tarefa05-karolinecorreia-art/
├── main.py                    # Ponto de entrada
├── estoque_gui.py             # Arquivo principal (tema, banco, backup e menu)
├── banco.sql                  # Script SQL (tabelas e triggers)
├── conexao.py                 # Conexão com o SQLite e backup
├── produtos.py                # CRUD de produtos e consultas
├── movimentacoes.py           # Entradas, saídas e histórico
├── menu_principal.py          # Menu com dashboard
├── cadastro_produtos.py       # Tela de cadastro
├── registro_movimentacao.py   # Telas de entrada e saída
├── consulta_estoque.py        # Consulta e filtro por categoria
├── relatorios.py              # Gráfico, histórico e estoque baixo
├── validacoes.py              # Validações de entrada
├── exportacao.py              # Exportação CSV
├── dados_exemplo.py           # Produtos de exemplo (opcional)
├── teste_estoque.py           # Testes automatizados
├── screenshots/               # Capturas de tela
└── README.md
```

## Uso do GitHub Copilot

(Preencha com o que realmente aconteceu. Exemplos de itens: o que foi pedido ao Copilot Chat, o que ele sugeriu, o que foi aceito, o que foi corrigido ou recusado e por quê, e qual foi o resultado no projeto.)

- **Pedido 1:** ...
- **Sugestão do Copilot:** ...
- **O que fizemos com ela:** ...

## Screenshots

### Menu principal
![Menu principal](screenshots/01_menu.png)

### Cadastro de produtos
![Cadastro de produtos](screenshots/02_cadastro_produtos.png)
![Cadastro de produtos com valor nulo](screenshots/02_1_cadastro_valor_0.png)
![Cadastro de produtos com letras](screenshots/02_2_cadastro_valor_letra.png)
![Confirmação para excluir produto](screenshots/02_3_confirmacao_exclusao.png)
![Exclusão de produto negada](screenshots/02_4_exclusao_negada.png)
![Atualização de produto](screenshots/02_5_produto_atualizado.png)
![Cadastro de produto existente](screenshots/02_cadastro_existente.png)

### Registro de entrada
![Entrada](screenshots/03_saida_resgistrada.png)
![Entrada realizada](screenshots/03_entreda_realizada.png)

### Registro de saída
![Registro de saída](screenshots/registro_saida.png).png)
![Estoque insuficiente](screenshots/03_estoque_insuficiente.png).png)
![Saída com número negativo](screenshots/03_saida_negativo).png)

### Alerta de estoque baixo
![Alerta no menu principal](screenshots/05_alerta_estoque_baixo.png)
![Alerta no registro de entrada](screenshots/03_1_estoque_baixo.png)

### Consulta de estoque
![Consulta de estoque](screenshots/04_consulta_estoque.png)
![Consulta de estoque específico](screenshots/04_estoque_especifico.png)

### Relatórios
![Gráfico](screenshots/06_relatorios_grafico1.png)
![Gráfico - Qtde. de produtos](screenshots/06_relatorios_grafico2.png)
![Histórico de movimentação](screenshots/06_relatorios_historico_mov.png)
![Estoque baixo](screenshots/06_relatorios_estoque_baixo.png)

### Exportação CSV
![CSV](screenshots/exportacao_csv.png)
![Tabela Excel - Histórico de movimentação](screenshots/07_excel_historico_mov.png)
![Tabela Excel - Estoque baixo](screenshots/07_excel_estoque_baixo.png)

### Backup
![Backup criado](screenshots/08_backup_criado.png)

### Testes automatizados
![Testes](screenshots/09_testes.png)

### GitHub Copilot
![Copilot](screenshots/10_copilot.png)

## Organização do trabalho em dupla

O repositório foi desenvolvido pela dupla como colaboradoras no GitHub, usando git pull antes de cada alteração e git push ao final, com commits em diferentes momentos do desenvolvimento. Além do GitHub Copilot, utilizamos o Claude (Anthropic) como na configuração do VS Code, do Git e do GitHub, para a revisão do nosso código e também para entender quais dados precisam estar no README. 

## Licença e uso

Projeto acadêmico, desenvolvido para a disciplina INE5201 (UFSC).
