import threading
import time
import argparse

thread_states = {}
state_lock = threading.Lock()

def update_state(thread_name, status, resource_name=None):
    with state_lock:
        thread_states[thread_name] = {
            "status": status,
            "resource": resource_name, 
            "timestamp": time.time()
        }

def worker_deadlock(lock1, lock1_name, lock2, lock2_name):
    name = threading.current_thread().name
    print(f"[{name}] Iniciada.")
    
    update_state(name, "Tentando adquirir", lock1_name)
    lock1.acquire()
    update_state(name, "Adquiriu", lock1_name)
    print(f"[{name}] Adquiriu o Lock {lock1_name}.")
    
    time.sleep(1) 
    
    update_state(name, "Tentando adquirir", lock2_name)
    lock2.acquire() 
    update_state(name, "Adquiriu", lock2_name)
    print(f"[{name}] Adquiriu o Lock {lock2_name}.")
    
    time.sleep(1)
    
    lock2.release()
    lock1.release()
    update_state(name, "Finalizada")
    print(f"[{name}] Finalizada.")

def worker_corrected(lock1, lock1_name, lock2, lock2_name):
    name = threading.current_thread().name
    print(f"[{name}] Iniciada.")
    
    locks_to_acquire = sorted([(lock1_name, lock1), (lock2_name, lock2)], key=lambda x: x[0])
    
    first_lock_name, first_lock = locks_to_acquire[0]
    second_lock_name, second_lock = locks_to_acquire[1]

    update_state(name, "Tentando adquirir", first_lock_name)
    first_lock.acquire()
    update_state(name, "Adquiriu", first_lock_name)
    print(f"[{name}] Adquiriu o Lock {first_lock_name}.")
    
    time.sleep(0.5)
    
    update_state(name, "Tentando adquirir", second_lock_name)
    second_lock.acquire()
    update_state(name, "Adquiriu", second_lock_name)
    print(f"[{name}] Adquiriu o Lock {second_lock_name}.")
    
    time.sleep(1)
    
    second_lock.release()
    first_lock.release()
    update_state(name, "Finalizada")
    print(f"[{name}] Finalizada.")

def watchdog(timeout):
    print("[WATCHDOG] Iniciado.")
    time.sleep(timeout) 
    
    worker_threads = {t.name for t in threading.enumerate() if t.name.startswith("Thread-")}

    while True:
        with state_lock:
            now = time.time()
            stuck_threads = []
            
            if all(thread_states.get(name, {}).get("status") == "Finalizada" for name in worker_threads):
                print("[WATCHDOG] Todas as threads terminaram corretamente. Sem deadlock.")
                return

            for name, state in thread_states.items():
                if state["status"] != "Finalizada" and (now - state["timestamp"]) > timeout:
                    stuck_threads.append((name, state))

            if len(stuck_threads) > 1:
                print("\n" + "="*20)
                print("[WATCHDOG] DEADLOCK POTENCIAL DETECTADO!")
                print(f"Ausência de progresso por mais de {timeout} segundos.")
                for name, state in stuck_threads:
                    print(f"  - Thread '{name}' está travada no estado '{state['status']}'")
                    if state['resource']:
                        print(f"    (esperando pelo recurso '{state['resource']}')")
                print("="*20 + "\n")
                return
        
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Detecção e Correção de Deadlock")
    parser.add_argument('-m', '--mode', choices=['deadlock', 'corrected'], required=True)
    parser.add_argument('-t', '--timeout', type=int, default=3, help="Timeout do watchdog.")
    args = parser.parse_args()

    lock_A = threading.Lock()
    lock_B = threading.Lock()
    lock_A_name = "RECURSO_A"
    lock_B_name = "RECURSO_B"

    if args.mode == 'deadlock':
        print("--- MODO DEADLOCK ---")
        t1 = threading.Thread(target=worker_deadlock, args=(lock_A, lock_A_name, lock_B, lock_B_name), name="Thread-1")
        t2 = threading.Thread(target=worker_deadlock, args=(lock_B, lock_B_name, lock_A, lock_A_name), name="Thread-2")
    else:
        print("--- MODO CORRIGIDO ---")
        t1 = threading.Thread(target=worker_corrected, args=(lock_A, lock_A_name, lock_B, lock_B_name), name="Thread-1")
        t2 = threading.Thread(target=worker_corrected, args=(lock_B, lock_B_name, lock_A, lock_A_name), name="Thread-2")
    
    wd = threading.Thread(target=watchdog, args=(args.timeout,), name="Watchdog")
    
    wd.start()
    t1.start()
    t2.start()

    t1.join()
    t2.join()
    wd.join()

    print("\nSimulação finalizada.")

if __name__ == "__main__":
    main()