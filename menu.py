#!/usr/bin/env python3
"""Menu central para iniciar e finalizar funcionalidades do projeto."""

import subprocess
import sys
import signal

processes = {
    "coletor": None,
    "painel_tui": None,
    "painel_web": None,
}

def handle_sigint(signum, frame):
    """Ignora CTRL+C e orienta o usuario a usar o menu."""
    print("\nUse o menu para encerrar as funcionalidades.")

signal.signal(signal.SIGINT, handle_sigint)


def iniciar(nome: str, modulo: str) -> None:
    """Inicia um modulo Python se nao estiver rodando."""
    proc = processes.get(nome)
    if proc and proc.poll() is None:
        print(f"{nome} ja esta em execucao.")
        return
    print(f"Iniciando {nome}...")
    processes[nome] = subprocess.Popen([sys.executable, "-m", modulo])


def finalizar(nome: str) -> None:
    """Finaliza o processo associado ao nome informado."""
    proc = processes.get(nome)
    if proc and proc.poll() is None:
        print(f"Finalizando {nome}...")
        proc.terminate()
        proc.wait()
    else:
        print(f"{nome} nao esta em execucao.")


def menu() -> None:
    """Exibe o menu principal e processa as escolhas do usuario."""
    opcoes = {
        "1": (iniciar, "coletor", "log_analyzer.collector"),
        "2": (finalizar, "coletor"),
        "3": (iniciar, "painel_tui", "log_analyzer.tui_panel"),
        "4": (finalizar, "painel_tui"),
        "5": (iniciar, "painel_web", "log_analyzer.web_panel"),
        "6": (finalizar, "painel_web"),
    }

    while True:
        print("\nMenu Principal")
        print("1. Iniciar Coletor")
        print("2. Finalizar Coletor")
        print("3. Iniciar Painel TUI")
        print("4. Finalizar Painel TUI")
        print("5. Iniciar Painel Web")
        print("6. Finalizar Painel Web")
        print("7. Sair")
        escolha = input("Selecione uma opcao: ").strip()
        if escolha == "7":
            for nome in list(processes.keys()):
                finalizar(nome)
            print("Encerrando menu...")
            break
        acao = opcoes.get(escolha)
        if not acao:
            print("Opcao invalida.")
            continue
        func = acao[0]
        args = acao[1:]
        func(*args)

if __name__ == "__main__":
    menu()
