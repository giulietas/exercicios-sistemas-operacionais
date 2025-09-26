import threading
import time
import random
import argparse

class Philosopher(threading.Thread):
    def __init__(self, id, left_fork, right_fork, solution_type, dining_room=None):
        super().__init__()
        self.id = id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.solution_type = solution_type
        self.dining_room = dining_room 
        self.meals_eaten = 0
        self.running = True

    def run(self):
        while self.running:
            print(f"Filósofo {self.id} está pensando.")
            time.sleep(random.uniform(1, 3))
            
            if self.solution_type == 'order':
                self.pickup_forks_ordered()
            elif self.solution_type == 'semaphore':
                self.pickup_forks_semaphore()
            
            print(f"Filósofo {self.id} está comendo.")
            time.sleep(random.uniform(1, 2))
            self.meals_eaten += 1
            
            self.putdown_forks()

    def pickup_forks_ordered(self):
        first_fork, second_fork = sorted([self.left_fork, self.right_fork], key=id)
        
        print(f"Filósofo {self.id} tentando pegar o garfo {first_fork.id}.")
        first_fork.acquire()
        print(f"Filósofo {self.id} pegou o garfo {first_fork.id}.")
        print(f"Filósofo {self.id} tentando pegar o garfo {second_fork.id}.")
        second_fork.acquire()
        print(f"Filósofo {self.id} pegou o garfo {second_fork.id}.")

    def pickup_forks_semaphore(self):
        print(f"Filósofo {self.id} tentando entrar na sala de jantar.")
        self.dining_room.acquire()
        print(f"Filósofo {self.id} entrou na sala de jantar.")
        
        self.left_fork.acquire()
        print(f"Filósofo {self.id} pegou o garfo esquerdo ({self.left_fork.id}).")
        self.right_fork.acquire()
        print(f"Filósofo {self.id} pegou o garfo direito ({self.right_fork.id}).")

    def putdown_forks(self):
        self.left_fork.release()
        self.right_fork.release()
        print(f"Filósofo {self.id} largou os garfos.")
        if self.solution_type == 'semaphore':
            self.dining_room.release()
            print(f"Filósofo {self.id} saiu da sala de jantar.")

def main():
    parser = argparse.ArgumentParser(description="O Jantar dos Filósofos")
    parser.add_argument('-s', '--solution', choices=['order', 'semaphore'], required=True, help="Solução para evitar deadlock: 'order' ou 'semaphore'.")
    parser.add_argument('-d', '--duration', type=int, default=15, help="Duração da simulação em segundos.")
    args = parser.parse_args()

    num_philosophers = 5
    forks = [threading.Lock() for _ in range(num_philosophers)]
    for i, fork in enumerate(forks): fork.id = i 
    
    philosophers = []
    dining_room = None
    if args.solution == 'semaphore':
        dining_room = threading.Semaphore(num_philosophers - 1)

    for i in range(num_philosophers):
        left_fork = forks[i]
        right_fork = forks[(i + 1) % num_philosophers]
        p = Philosopher(i, left_fork, right_fork, args.solution, dining_room)
        philosophers.append(p)
        p.start()

    print(f"Simulação iniciada com a solução '{args.solution}' por {args.duration} segundos.")
    time.sleep(args.duration)

    for p in philosophers:
        p.running = False
    for p in philosophers:
        p.join()

    print("\n--- Resultados da Simulação ---")
    total_meals = 0
    for p in philosophers:
        print(f"Filósofo {p.id} comeu {p.meals_eaten} vezes.")
        total_meals += p.meals_eaten
    print(f"Total de refeições servidas: {total_meals}")

if __name__ == "__main__":
    main()