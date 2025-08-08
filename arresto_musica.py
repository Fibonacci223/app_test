import psutil
import os
import signal

def terminate_playsound_process():
    """
    Trova e termina il processo Python che esegue 'playsound'.
    """
    print("Ricerca e terminazione del processo 'playsound'...")

    # Itera su tutti i processi attivi
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Controlla se il processo è Python e se nella sua riga di comando c'è 'playsound'
            if proc.name() in ['python.exe', 'python3.exe'] and 'playsound' in " ".join(proc.cmdline()):
                pid = proc.info['pid']
                print(f"Trovato processo 'playsound' con PID: {pid}")

                # Termina il processo
                os.kill(pid, signal.SIGTERM)
                print(f"Processo con PID {pid} terminato con successo.")
                return

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Ignora i processi che non possono essere acceduti o che sono già terminati
            continue
            
    print("Nessun processo 'playsound' attivo trovato.")


if __name__ == "__main__":
    terminate_playsound_process()