import threading
import queue
import time
import random
import argparse

# sinaliza o fim do fluxo de dados
POISON_PILL = None

def estagio_captura(fila_saida, n_itens):
    print("[CAPTURA] Iniciada.")
    for i in range(n_itens):
        item = f"Dado-{i}"
        time.sleep(random.uniform(0.05, 0.1))
        fila_saida.put(item)
        print(f"[CAPTURA] Gerou '{item}'")
    fila_saida.put(POISON_PILL) 
    print("[CAPTURA] Finalizada.")

def estagio_processamento(fila_entrada, fila_saida):
    print("[PROCESSAMENTO] Iniciado.")
    while True:
        item = fila_entrada.get()
        if item is POISON_PILL:
            fila_saida.put(POISON_PILL) 
            break
        
        print(f"[PROCESSAMENTO] Processando '{item}'...")
        processed_item = item.upper()
        time.sleep(random.uniform(0.1, 0.2))
        fila_saida.put(processed_item)
        print(f"[PROCESSAMENTO] Enviou '{processed_item}'")
    print("[PROCESSAMENTO] Finalizado.")

def estagio_gravacao(fila_entrada, n_itens):
    print("[GRAVAÇÃO] Iniciada.")
    itens_gravados = 0
    while True:
        item = fila_entrada.get()
        if item is POISON_PILL:
            break
        
        print(f"[GRAVAÇÃO] Gravando '{item}' no disco.")
        # Simula I/O
        time.sleep(random.uniform(0.02, 0.05))
        itens_gravados += 1

    print("[GRAVAÇÃO] Finalizada.")
    print(f"\nProtocolo de encerramento limpo concluído.")
    print(f"Total de itens gerados: {n_itens}")
    print(f"Total de itens gravados: {itens_gravados}")
    assert n_itens == itens_gravados
    print("ASSERT: Nenhum item foi perdido.")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Processamento com 3 Threads.")
    parser.add_argument('-n', '--itens', type=int, default=20, help='Número de itens a processar.')
    parser.add_argument('-s', '--size', type=int, default=5, help='Tamanho das filas limitadas.')
    args = parser.parse_args()

    fila1 = queue.Queue(maxsize=args.size)
    fila2 = queue.Queue(maxsize=args.size)

    thread_captura = threading.Thread(target=estagio_captura, args=(fila1, args.itens))
    thread_proc = threading.Thread(target=estagio_processamento, args=(fila1, fila2))
    thread_grav = threading.Thread(target=estagio_gravacao, args=(fila2, args.itens))

    thread_captura.start()
    thread_proc.start()
    thread_grav.start()

    thread_captura.join()
    thread_proc.join()
    thread_grav.join()

    print("\nPipeline finalizado com sucesso.")

if __name__ == "__main__":
    main()