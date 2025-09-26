import threading
import random
import time
import argparse

class ContaBancaria:
    def __init__(self, id_conta, saldo_inicial):
        self.id = id_conta
        self.saldo = saldo_inicial
        self.lock = threading.Lock()

def transferencia_worker(contas, num_transferencias, use_locks):
    for _ in range(num_transferencias):
        c1_idx, c2_idx = random.sample(range(len(contas)), 2)
        
        conta_origem_idx = min(c1_idx, c2_idx)
        conta_destino_idx = max(c1_idx, c2_idx)

        conta_origem = contas[conta_origem_idx]
        conta_destino = contas[conta_destino_idx]
        
        valor = random.randint(1, 100)

        if use_locks:
            with conta_origem.lock:
                with conta_destino.lock:
                    if conta_origem.saldo >= valor:
                        conta_origem.saldo -= valor
                        conta_destino.saldo += valor
        else: 
            saldo_origem = conta_origem.saldo
            time.sleep(0.001) 
            if saldo_origem >= valor:
                conta_origem.saldo = saldo_origem - valor
                conta_destino.saldo += valor


def main():
    parser = argparse.ArgumentParser(description="Simulador de Transferências Bancárias")
    parser.add_argument('-n', '--contas', type=int, default=10, help='Número de contas.')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Número de threads.')
    parser.add_argument('--no-lock', action='store_true', help='Executar sem travas para demonstrar condição de corrida.')
    args = parser.parse_args()

    num_contas = args.contas
    num_threads = args.threads
    use_locks = not args.no_lock
    
    contas = [ContaBancaria(i, 1000) for i in range(num_contas)]
    soma_inicial = sum(c.saldo for c in contas)
    
    print(f"Executando com {'TRAVAS' if use_locks else 'SEM TRAVAS'}")
    print(f"Soma global inicial: {soma_inicial}")
    
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=transferencia_worker, args=(contas, 100, use_locks))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()

    soma_final = sum(c.saldo for c in contas)
    
    print(f"Soma global final: {soma_final}")
    
    try:
        assert soma_inicial == soma_final
        print("ASSERT: A soma global do dinheiro permaneceu constante. [CORRETO]")
    except AssertionError:
        print("ASSERTION ERROR: A soma global do dinheiro foi alterada! [INCORRETO]")

if __name__ == "__main__":
    main()