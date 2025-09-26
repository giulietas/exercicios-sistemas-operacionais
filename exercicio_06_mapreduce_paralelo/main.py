import threading
import random
import time
import argparse
from collections import Counter

total_sum = 0
total_histogram = Counter()
lock = threading.Lock()

def create_dummy_file(filename, num_integers):
    print(f"Criando arquivo de teste '{filename}' com {num_integers} inteiros...")
    with open(filename, 'w') as f:
        for _ in range(num_integers):
            f.write(f"{random.randint(1, 1000)}\n")
    print("Arquivo criado.")

def map_worker(data_chunk):
    local_sum = sum(data_chunk)
    local_histogram = Counter(data_chunk)
    
    with lock:
        global total_sum, total_histogram
        total_sum += local_sum
        total_histogram.update(local_histogram)

def main():
    parser = argparse.ArgumentParser(description="MapReduce paralelo para soma e histograma.")
    parser.add_argument('-f', '--file', type=str, default='large_integers.txt', help='Arquivo de entrada.')
    parser.add_argument('-n', '--numbers', type=int, default=1000000, help='Números a serem gerados no arquivo.')
    args = parser.parse_args()
    
    create_dummy_file(args.file, args.numbers)

    with open(args.file, 'r') as f:
        all_numbers = [int(line.strip()) for line in f]

    for p in [1, 2, 4, 8]:
        global total_sum, total_histogram
        total_sum = 0
        total_histogram = Counter()
        
        print(f"\n--- Executando com P = {p} threads ---")
        start_time = time.time()
        
        threads = []
        chunk_size = len(all_numbers) // p
        for i in range(p):
            start_index = i * chunk_size
            end_index = (i + 1) * chunk_size if i != p - 1 else len(all_numbers)
            chunk = all_numbers[start_index:end_index]
            
            thread = threading.Thread(target=map_worker, args=(chunk,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
            
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Soma total: {total_sum}")
        print(f"Tempo de execução: {duration:.4f} segundos")
        if 'baseline' not in locals():
            baseline = duration
        
        speedup = baseline / duration
        print(f"Speedup em relação a P=1: {speedup:.2f}x")

if __name__ == "__main__":
    main()