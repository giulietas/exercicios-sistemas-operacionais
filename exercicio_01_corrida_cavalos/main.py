import threading
import random
import time
import argparse

placar = []
vencedor = None
distancia_corrida = 100

winner_lock = threading.Lock()
placar_lock = threading.Lock()

def cavalo_thread(num_cavalo, barreira):
    global vencedor
    posicao = 0
    print(f"Cavalo {num_cavalo} pronto na largada.")
    
    barreira.wait()

    while posicao < distancia_corrida:
        passo = random.randint(1, 15)
        posicao += passo
        time.sleep(random.uniform(0.1, 0.3))
        print(f"Cavalo {num_cavalo} está na posição {posicao}")

    with winner_lock:
        if vencedor is None:
            vencedor = num_cavalo
            print(f"\nO Cavalo {num_cavalo} cruzou a linha de chegada primeiro!\n")
    
    with placar_lock:
        placar.append(num_cavalo)

def main():
    parser = argparse.ArgumentParser(description="Corrida de Cavalos com Threads")
    parser.add_argument('-t', '--threads', type=int, default=5, help='Número de cavalos (threads).')
    parser.add_argument('-d', '--distancia', type=int, default=100, help='Distância da corrida.')
    args = parser.parse_args()

    num_cavalos = args.threads
    global distancia_corrida
    distancia_corrida = args.distancia
    
    barreira = threading.Barrier(num_cavalos + 1)
    
    aposta = int(input(f"Em qual cavalo (1 a {num_cavalos}) você aposta? "))

    threads = []
    for i in range(1, num_cavalos + 1):
        thread = threading.Thread(target=cavalo_thread, args=(i, barreira))
        threads.append(thread)
        thread.start()
        
    print("\nTodos os cavalos estão se preparando...")
    time.sleep(2)
    print("A CORRIDA VAI COMEÇAR!\n")
    barreira.wait() 

    for thread in threads:
        thread.join()

    print("\n--- RESULTADO FINAL ---")
    print(f"O vencedor é o Cavalo {vencedor}!")
    if aposta == vencedor:
        print("Parabéns, você ganhou a aposta!")
    else:
        print(f"Você apostou no Cavalo {aposta} e perdeu.")

    print("\nPlacar final:")
    for i, cavalo_num in enumerate(placar):
        print(f"{i+1}º lugar: Cavalo {cavalo_num}")

if __name__ == "__main__":
    main()