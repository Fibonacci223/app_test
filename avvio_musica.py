import os
import subprocess
import sys

def play_music_in_background(file_path):
    """
    Riproduce un file audio in background usando il modulo playsound.
    
    Args:
        file_path (str): Il percorso del file audio da riprodurre.
    """
    try:
        # Assicurati che il modulo playsound sia installato
        # (pip install playsound)
        
        # Su Windows: avvia in background senza console visibile
        if sys.platform.startswith("win"):
            subprocess.Popen(
                ["python", "-m", "playsound", file_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        # Su macOS e Linux: avvia in background senza bloccare il terminale
        else:
            subprocess.Popen(
                ["python3", "-m", "playsound", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        print(f"Riproduzione di '{file_path}' avviata in background.")

    except FileNotFoundError:
        print(f"Errore: Il file '{file_path}' non è stato trovato.")
    except Exception as e:
        print(f"Errore durante l'avvio della musica: {e}")

# Esempio di utilizzo (opzionale, per testare la funzione)
if __name__ == '__main__':
    # Percorso del file audio
    musica = "musica_1.mp3"
    play_music_in_background(musica)
    print("La musica dovrebbe essere in riproduzione. Premi Ctrl+C per uscire.")
    # Mantiene il programma in esecuzione per sentire la musica
    try:
        input() 
    except (KeyboardInterrupt, EOFError):
        print("\nChiusura del programma.")