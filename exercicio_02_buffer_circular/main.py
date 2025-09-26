import threading
import time
import random
import argparse
from collections import deque

buffer = None
buffer_lock = threading.Lock()
empty_slots = None
filled_slots = None

total_wait_time_producer = 0
total_wait_time_consumer = 0
items_produced = 0
items_consumed = 0

class CircularBuffer:
    def __init__(self, size):
        self.buffer = deque(maxlen=size)
    
    def add(self, item):
        self.buffer.append(item)
    
    def remove(self):
        return self.buffer.popleft()

def producer(id, num_items):
    global total_wait_time_producer, items_produced
    for i in range(num_items):
        item = f"item-{id}-{i}"
        
        start_wait = time.time()
        empty_slots.acquire() 
        wait_time = time.time() - start_wait
        total_wait_time_producer += wait_time
        
        with buffer_lock:
            buffer.add(item)
            items_produced += 1
            print(f"Produtor {id} produziu {item} | Buffer: {list(buffer.buffer)}")
        
        filled_slots.release() 
        time.sleep(random.uniform(0.01, 0.1))

def consumer(id, num_items):
    global total_wait_time_consumer, items_consumed
    for _ in range(num_items):
        start_wait = time.time()
        filled_slots.acquire() 
        wait_time = time.time() - start_wait
        total_wait_time_consumer += wait_time
        
        with buffer_lock:
            item = buffer.remove()
            items_consumed += 1
            print(f"Consumidor {id} consumiu {item} | Buffer: {list(buffer.buffer)}")

        empty_slots.release() 
        time.sleep(random.uniform(0.05, 0.15))

def main():
    parser = argparse.ArgumentParser(description="Buffer Circular com Produtores e Consumidores")
    parser.add_argument('-s', '--size', type=int, default=10, help='Tamanho do buffer.')
    parser.add_argument('-p', '--producers', type=int, default=2, help='Número de produtores.')
    parser.add_argument('-c', '--consumers', type=int, default=2, help='Número de consumidores.')
    parser.add_argument('-n', '--num_items', type=int, default=5, help='Itens por produtor/consumidor.')
    args = parser.parse_args()

    global buffer, empty_slots, filled_slots
    buffer = CircularBuffer(args.size)
    empty_slots = threading.Semaphore(args.size)
    filled_slots = threading.Semaphore(0)

    threads = []
    start_time = time.time()

    for i in range(args.producers):
        thread = threading.Thread(target=producer, args=(i, args.num_items))
        threads.append(thread)
        thread.start()

    for i in range(args.consumers):
        thread = threading.Thread(target=consumer, args=(i, int(args.num_items * args.producers / args.consumers)))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n--- Estatísticas ---")
    print(f"Tamanho do Buffer: {args.size}")
    throughput = items_consumed / total_time
    avg_wait_p = total_wait_time_producer / items_produced if items_produced > 0 else 0
    avg_wait_c = total_wait_time_consumer / items_consumed if items_consumed > 0 else 0
    
    print(f"Tempo total de execução: {total_time:.2f}s")
    print(f"Throughput: {throughput:.2f} itens/segundo")
    print(f"Tempo médio de espera (produtores): {avg_wait_p:.4f}s")
    print(f"Tempo médio de espera (consumidores): {avg_wait_c:.4f}s")

if __name__ == "__main__":
    main()