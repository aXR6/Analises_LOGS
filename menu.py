#!/usr/bin/env python3
"""Menu central para iniciar e finalizar funcionalidades do projeto."""

import subprocess
import sys
import signal
import os

processes = {
    "coletor": None,
    "painel_tui": None,
    "painel_web": None,
    "nids": None,
    "sniffer": None,
}

device_type = os.environ.get("DEVICE_TYPE", "cpu")
net_interface = os.environ.get("NET_INTERFACE", "")

def handle_sigint(signum, frame):
    """Ignora CTRL+C e orienta o usuario a usar o menu."""
    print("\nUse o menu para encerrar as funcionalidades.")

signal.signal(signal.SIGINT, handle_sigint)


def iniciar(nome: str, modulo: str, quiet: bool = False) -> None:
    """Inicia um modulo Python se nao estiver rodando."""
    proc = processes.get(nome)
    if proc and proc.poll() is None:
        print(f"{nome} ja esta em execucao.")
        return
    if not quiet:
        print(f"Iniciando {nome}...")
    stdout = subprocess.DEVNULL if quiet else None
    stderr = subprocess.DEVNULL if quiet else None
    processes[nome] = subprocess.Popen(
        [sys.executable, "-m", modulo], stdout=stdout, stderr=stderr
    )


def iniciar_web() -> None:
    """Inicia o painel web de forma silenciosa."""
    iniciar("painel_web", "log_analyzer.web_panel", quiet=True)


def iniciar_coleta() -> None:
    """Inicia coletor de logs e monitor de rede."""
    if not net_interface:
        selecionar_interface()
        if not net_interface:
            return
    iniciar("sniffer", "log_analyzer.net_sniffer")
    iniciar("coletor", "log_analyzer.collector")
    iniciar("nids", "log_analyzer.network_nids")


def finalizar_coleta() -> None:
    """Finaliza coletor de logs e monitor de rede."""
    finalizar("sniffer")
    finalizar("coletor")
    finalizar("nids")


def finalizar(nome: str) -> None:
    """Finaliza o processo associado ao nome informado."""
    proc = processes.get(nome)
    if proc and proc.poll() is None:
        print(f"Finalizando {nome}...")
        proc.terminate()
        proc.wait()
    else:
        print(f"{nome} nao esta em execucao.")


def alternar_dispositivo() -> None:
    """Alterna entre CPU e GPU para os modulos futuros."""
    global device_type
    device_type = "cuda" if device_type == "cpu" else "cpu"
    os.environ["DEVICE_TYPE"] = device_type
    print(f"Dispositivo definido para: {device_type}")


def selecionar_interface() -> None:
    """Lista interfaces de rede e define a escolhida para captura."""
    global net_interface
    try:
        interfaces = os.listdir('/sys/class/net')
    except Exception:
        interfaces = []
    if not interfaces:
        print("Nenhuma interface encontrada.")
        return
    print("Interfaces disponiveis:")
    for idx, iface in enumerate(interfaces, 1):
        print(f"{idx}. {iface}")
    escolha = input("Selecione o numero da interface: ").strip()
    try:
        num = int(escolha)
        net_interface = interfaces[num - 1]
    except (ValueError, IndexError):
        print("Opcao invalida.")
        return
    os.environ['NET_INTERFACE'] = net_interface
    print(f"Interface definida para monitoramento: {net_interface}")


def menu() -> None:
    """Exibe o menu principal e processa as escolhas do usuario."""
    opcoes = {
        "1": (iniciar_coleta,),
        "2": (finalizar_coleta,),
        "3": (iniciar, "painel_tui", "log_analyzer.tui_panel"),
        "4": (finalizar, "painel_tui"),
        "5": (iniciar_web,),
        "6": (finalizar, "painel_web"),
        "7": (alternar_dispositivo,),
        "8": (selecionar_interface,),
    }

    def status(nome: str) -> str:
        proc = processes.get(nome)
        return "(ativo)" if proc and proc.poll() is None else "(parado)"

    while True:
        print("\nMenu Principal")
        print(f"1. Iniciar Coletor/NIDS {status('coletor')}")
        print("2. Finalizar Coletor/NIDS")
        print(f"3. Iniciar Painel TUI {status('painel_tui')}")
        print("4. Finalizar Painel TUI")
        print(f"5. Iniciar Painel Web {status('painel_web')}")
        print("6. Finalizar Painel Web")
        print(f"7. Alternar CPU/GPU (atual: {device_type})")
        print(f"8. Selecionar interface de rede (atual: {net_interface or 'nenhuma'})")
        print("9. Sair")
        escolha = input("Selecione uma opcao: ").strip()
        if escolha == "9":
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
