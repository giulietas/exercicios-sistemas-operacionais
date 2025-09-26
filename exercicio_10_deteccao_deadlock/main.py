import threading
import time
import argparse

thread_states = {}
state_lock = threading.Lock()

def update_state(thread_name, status, resource=None):
    with state_lock:
        thread_states[thread_name] = {
            "status": status,
            "resource": resource,
            "timestamp": time.time()
        }

def worker_deadlock(lock1, lock2):
    name = threading.current_thread().name
    print(f"[{name}] Iniciada.")
    
    update_state(name, "Tentando adquirir", lock1.name)
    lock1.acquire()
    update_state(name, "Adquiriu", lock1.name)
    print(f"[{name}] Adquiriu o Lock {lock1.name}.")
    
    time.sleep(1) 
    
    update_state(name, "Tentando adquirir", lock2.name)
    lock2.acquire() 
    update_state(name, "Adquiriu", lock2.name)
    print(f"[{name}] Adquiriu o Lock {lock2.name}.")
    
    time.sleep(1)
    
    lock2.release()
    lock1.release()
    update_state(name, "Finalizada", None)
    print(f"[{name}] Finalizada.")

def worker_corrected(lock1, lock2):
    name = threading.current_thread().name
    print(f"[{name}] Iniciada.")
    
    locks = sorted([lock1, lock2], key=lambda x: x.name)
    
    update_state(name, "Tentando adquirir", locks[0].name)
    locks[0].acquire()
    update_state(name, "Adquiriu", locks[0].name)
    print(f"[{name}] Adquiriu o Lock {locks[0].name}.")
    
    time.sleep(0.5)
    
    update_state(name, "Tentando adquirir", locks[1].name)
    locks[1].acquire()
    update_state(name, "Adquiriu", locks[1].name)
    print(f"[{name}] Adquiriu o Lock {locks[1].name}.")
    
    time.sleep(1)
    
    locks[1].release()
    locks[0].release()
    update_state(name, "Finalizada", None)
    print(f"[{name}] Finalizada.")

def watchdog(timeout):
    print("[WATCHDOG] Iniciado.")
    time.sleep(timeout) 
    
    while True:
        with state_lock:
            now = time.time()
            stuck_threads = []
            for name, state in thread_states.items():
                if state["status"] != "Finalizada" and (now - state["timestamp"]) > timeout:
                    stuck_threads.append((name, state))

            if len(stuck_threads) > 1: 
                print("\n" + "="*20)
                print("[WATCHDOG] DEADLOCK POTENCIAL DETECTADO!")
                print(f"Ausência de progresso por mais de {timeout} segundos.")
                for name, state in stuck_threads:
                    print(f"  - Thread '{name}' está travada no estado '{state['status']}'")
                    print(f"    (tentando adquirir o recurso '{state['resource']}')")
                print("="*20 + "\n")
                return 
        
        with state_lock:
            if all(s["status"] == "Finalizada" for s in thread_states.values()):
                print("[WATCHDOG] Todas as threads terminaram corretamente. Sem deadlock.")
                return
        
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Detecção e Correção de Deadlock")
    parser.add_argument('-m', '--mode', choices=['deadlock', 'corrected'], required=True)
    parser.add_argument('-t', '--timeout', type=int, default=3, help="Timeout do watchdog.")
    args = parser.parse_args()

    lock_A = threading.Lock(); lock_A.name = "RECURSO_A"
    lock_B = threading.Lock(); lock_B.name = "RECURSO_B"

    if args.mode == 'deadlock':
        print("--- MODO DEADLOCK ---")
        t1 = threading.Thread(target=worker_deadlock, args=(lock_A, lock_B), name="Thread-1")
        t2 = threading.Thread(target=worker_deadlock, args=(lock_B, lock_A), name="Thread-2")
    else:
        print("--- MODO CORRIGIDO ---")
        t1 = threading.Thread(target=worker_corrected, args=(lock_A, lock_B), name="Thread-1")
        t2 = threading.Thread(target=worker_corrected, args=(lock_B, lock_A), name="Thread-2")
    
    wd = threading.Thread(target=watchdog, args=(args.timeout,), name="Watchdog")
    wd.daemon = True 

    wd.start()
    t1.start()
    t2.start()

    t1.join(timeout=args.timeout + 5)
    t2.join(timeout=args.timeout + 5)

    if t1.is_alive() or t2.is_alive():
        print("\nThreads de trabalho não finalizaram. O deadlock provavelmente ocorreu.")
    else:
        print("\nThreads de trabalho finalizaram.")


if __name__ == "__main__":
    main()