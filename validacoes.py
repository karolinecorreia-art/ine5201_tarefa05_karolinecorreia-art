# validacoes.py: validações de entrada e formatação
import math
import re

PADRAO_CODIGO = re.compile(r"[A-Z0-9_-]{1,20}")


def validar_codigo(texto):
    codigo = texto.strip().upper()
    if not codigo:
        raise ValueError("Informe o código do produto.")
    if not PADRAO_CODIGO.fullmatch(codigo):
        raise ValueError("Código inválido: use de 1 a 20 caracteres entre letras, "
                         "números, '-' e '_' (sem espaços).")
    return codigo


def validar_nome(texto):
    nome = " ".join(texto.split())
    if not nome:
        raise ValueError("Informe o nome do produto.")
    if len(nome) > 60:
        raise ValueError("O nome deve ter no máximo 60 caracteres.")
    return nome


def validar_categoria(texto):
    categoria = " ".join(texto.split())
    if len(categoria) > 30:
        raise ValueError("A categoria deve ter no máximo 30 caracteres.")
    return categoria or "Sem categoria"


def validar_preco(texto):
    try:
        preco = float(str(texto).strip().replace(",", "."))
    except ValueError:
        raise ValueError("Preço inválido: digite um número, por exemplo 12,50.") from None
    if not math.isfinite(preco) or preco <= 0:
        raise ValueError("O preço deve ser maior que zero.")
    return round(preco, 2)


def validar_quantidade(texto, minimo=1, rotulo="Quantidade"):
    """Quantidade inteira e nunca negativa. minimo=1 exige pelo menos 1."""
    try:
        quantidade = int(str(texto).strip())
    except ValueError:
        raise ValueError(f"O campo {rotulo} deve ser um número inteiro.") from None
    if quantidade < 0:
        raise ValueError(f"O campo {rotulo} não pode ser negativo.")
    if quantidade < minimo:
        raise ValueError(f"O campo {rotulo} deve ser maior que zero.")
    return quantidade


def formatar_moeda(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_decimal(valor):
    return f"{valor:.2f}".replace(".", ",")