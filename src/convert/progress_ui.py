import sys
import time

def mostrar_progresso(etapa:str, atual:int, total:int, barra_tamanho:int = 30):
    """
    Exibe um painel de progresso no terminal.
    
    etapa (str): Descrição da etapa atual
    atual (int): Quantidade já processada
    total (int): Quantidade total
    barra_tamanho (int): Largura da barra de progresso
    """

    if total == 0:
        total = 1  # evita divisão por zero

    porcentagem = int((atual / total) * 100)
    preenchido = int((porcentagem * barra_tamanho) / 100)
    vazio = barra_tamanho - preenchido

    barra = "█" * preenchido + "░" * vazio

    linha = (
        f"\r"
        f"[{barra}] {porcentagem:3d}% "
        f" | {atual}/{total} itens "
        f"| Etapa: {etapa} "
    )

    sys.stdout.write(linha)
    sys.stdout.flush()

    if atual == total:
        print("")  # quebra linha ao terminar


