import threading
import queue
import time
import sys
import argparse

POISON_PILL = None

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def worker(task_queue):
    thread_id = threading.get_ident()
    print(f"Worker {thread_id} iniciado.")
    while True:
        task = task_queue.get()
        if task is POISON_PILL:
            task_queue.task_done()
            break
        
        try:
            n = int(task)
            result = fib(n)
            print(f"Worker {thread_id}: fib({n}) = {result}")
        except (ValueError, TypeError):
            print(f"Worker {thread_id}: Tarefa inválida '{task}' ignorada.")
        
        task_queue.task_done()
    print(f"Worker {thread_id} finalizado.")

def main():
    parser = argparse.ArgumentParser(description="Pool de Threads processando tarefas da entrada padrão.")
    parser.add_argument('-t', '--threads', type=int, default=4, help='Número de threads no pool.')
    args = parser.parse_args()

    num_threads = args.threads
    task_queue = queue.Queue()

    pool = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(task_queue,))
        thread.start()
        pool.append(thread)

    print(f"Pool de {num_threads} threads criado. Digite números para calcular Fibonacci (um por linha).")
    print("Pressione Ctrl+D (Linux/macOS) ou Ctrl+Z+Enter (Windows) para finalizar.")

    for line in sys.stdin:
        task = line.strip()
        if task:
            task_queue.put(task)
            
    print("\nEOF detectado. Finalizando o pool...")

    for _ in range(num_threads):
        task_queue.put(POISON_PILL)

    task_queue.join()

    for thread in pool:
        thread.join()

    print("Todas as tarefas foram processadas. Pool finalizado.")

if __name__ == "__main__":
    main()