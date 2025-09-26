import threading
import time
import random
import argparse
from collections import deque

buffer = None
buffer_lock = threading.Lock()
empty_slots = None
filled_slots = None

stop_event = threading.Event()

buffer_occupation_log = []

class CircularBuffer:
    def __init__(self, size):
        self.buffer = deque(maxlen=size)
    def add(self, item): self.buffer.append(item)
    def remove(self): return self.buffer.popleft()
    def __len__(self): return len(self.buffer)

def producer(id):
    while not stop_event.is_set():
        item = f"item-{id}-{random.randint(100, 999)}"
        
        acquired = empty_slots.acquire(timeout=0.5)
        
        if not acquired:
            print(f"[PRODUTOR {id}] BACKPRESSURE! Buffer cheio. Desacelerando...")
            time.sleep(1) 
            continue

        if stop_event.is_set():
            empty_slots.release() 
            break
        
        with buffer_lock:
            buffer.add(item)
            print(f"Produtor {id} produziu {item} | Ocupação: {len(buffer)}")
        
        filled_slots.release()
        time.sleep(random.uniform(0.01, 0.05))

def consumer(id):
    while not stop_event.is_set():
        if random.random() < 0.1:
            print(f"[CONSUMIDOR {id}] Ocioso por um momento...")
            time.sleep(random.uniform(1, 3))

        acquired = filled_slots.acquire(timeout=0.5)
        if not acquired: continue

        if stop_event.is_set():
            filled_slots.release()
            break

        with buffer_lock:
            item = buffer.remove()
            print(f"Consumidor {id} consumiu {item} | Ocupação: {len(buffer)}")

        empty_slots.release()
        time.sleep(random.uniform(0.1, 0.3))

def monitor_buffer():
    while not stop_event.is_set():
        with buffer_lock:
            buffer_occupation_log.append(len(buffer))
        time.sleep(0.2)

def main():
    parser = argparse.ArgumentParser(description="Buffer com Backpressure")
    parser.add_argument('-s', '--size', type=int, default=10, help='Tamanho do buffer.')
    parser.add_argument('-p', '--producers', type=int, default=3, help='Número de produtores.')
    parser.add_argument('-c', '--consumers', type=int, default=2, help='Número de consumidores.')
    parser.add_argument('-d', '--duration', type=int, default=20, help='Duração da simulação.')
    args = parser.parse_args()

    global buffer, empty_slots, filled_slots
    buffer = CircularBuffer(args.size)
    empty_slots = threading.Semaphore(args.size)
    filled_slots = threading.Semaphore(0)

    threads = []
    
    for i in range(args.producers):
        threads.append(threading.Thread(target=producer, args=(i,)))
    for i in range(args.consumers):
        threads.append(threading.Thread(target=consumer, args=(i,)))
    threads.append(threading.Thread(target=monitor_buffer))

    for t in threads: t.start()
    
    print(f"Simulação rodando por {args.duration} segundos...")
    time.sleep(args.duration)
    
    print("\nParando todas as threads...")
    stop_event.set()
    
    for t in threads: t.join()
        
    print("\nSimulação finalizada.")
    print("Log de ocupação do buffer (amostras):")
    print(buffer_occupation_log)

if __name__ == "__main__":
    main()