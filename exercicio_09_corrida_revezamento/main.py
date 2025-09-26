import threading
import time
import argparse
import random

rounds_completed = 0
rounds_lock = threading.Lock()
stop_event = threading.Event()

def team_member(id, barrier, team_size):
    global rounds_completed
    
    while not stop_event.is_set():
        print(f"Membro {id} está correndo sua parte...")
        time.sleep(random.uniform(0.5, 2.0 / team_size)) 
        print(f"Membro {id} chegou à barreira.")
        
        try:
            wait_result = barrier.wait(timeout=5.0)
            
            if wait_result == 0:
                with rounds_lock:
                    rounds_completed += 1
                print("\n--- BARREIRA QUEBRADA! Equipe avançando para a próxima rodada. ---\n")

        except threading.BrokenBarrierError:
            print(f"Membro {id} saindo pois a barreira quebrou.")
            break
        except TimeoutError:
             print(f"Membro {id} timed out. A equipe falhou nesta rodada.")
             barrier.reset() 


def main():
    parser = argparse.ArgumentParser(description="Corrida de Revezamento com Barreiras")
    parser.add_argument('-k', '--team_size', type=int, default=4, help='Tamanho da equipe (K threads).')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Duração da simulação em segundos.')
    args = parser.parse_args()

    team_size = args.team_size
    
    barrier = threading.Barrier(team_size)
    
    threads = []
    for i in range(team_size):
        thread = threading.Thread(target=team_member, args=(i + 1, barrier, team_size))
        threads.append(thread)
        thread.start()

    print(f"Corrida de revezamento com {team_size} membros iniciada. Duração: {args.duration}s.")
    start_time = time.time()
    
    while time.time() - start_time < args.duration:
        time.sleep(1)

    print("\n--- TEMPO ESGOTADO ---")
    stop_event.set()
    if barrier.n_waiting > 0:
        barrier.abort()
        
    for thread in threads:
        thread.join()

    print(f"\nSimulação finalizada.")
    print(f"A equipe de {team_size} membros completou {rounds_completed} rodadas em {args.duration} segundos.")
    print(f"Taxa: {rounds_completed / args.duration * 60:.2f} rodadas por minuto.")


if __name__ == "__main__":
    main()