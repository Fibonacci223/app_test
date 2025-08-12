import sys
import os
import tkinter as tk
import threading
import time
import tkinter.font as tkfont
import subprocess
import re

# Ho incluso qui le funzioni di utilità che non sono classi
# per renderlo un unico file autonomo.
# Se hai file separati come 'matrix_effect.py' e 'ciphers.py',
# dovrai assicurarti che siano nella stessa directory.

# Importa le funzioni dai moduli esterni (assumendo che esistano)
try:
    from matrix_effect import run_matrix_effect
    from ciphers import (
        caesar_ascii,
        caesar_cipher,
        atbash_cipher,
        affine_decrypt_bruteforce,
        decode_morse,
        encode_to_morse
    )
except ImportError as e:
    print(f"Errore: Impossibile importare moduli necessari. Assicurati che 'matrix_effect.py' e 'ciphers.py' esistano. Dettagli: {e}")
    sys.exit(1)

# --- Funzioni di utilità ---
def run_script(script_path):
    print(f"DEBUG: TENTATIVO DI AVVIARE LO SCRIPT: {script_path}")
    try:
        subprocess.Popen(['pythonw', script_path], creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"DEBUG: Script {script_path} avviato con successo.")
        return True
    except FileNotFoundError:
        print(f"ERRORE DEBUG: File non trovato per lo script {script_path}")
        return False
    except Exception as e:
        print(f"ERRORE DEBUG: Eccezione durante l'avvio di {script_path}: {e}")
        return False

def show_and_run_2(master_app):
    """Mostra la GUI e avvia 2.pyw in un thread separato dopo un ritardo."""
    master_app.deiconify()

    def delayed_run():
        time.sleep(1)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_2_path = os.path.join(current_dir, "2.pyw")
        run_script(script_2_path)

    threading.Thread(target=delayed_run, daemon=True).start()

def smooth_scroll(widget, target, cursor_target, steps=100, delay=10):
    widget._scroll_interrupt = False
    widget._is_scrolling = True
    widget._scroll_target = target
    current = widget.yview()[0]
    delta = (target - current) / steps

    def step(i=0):
        if widget._scroll_interrupt:
            widget.yview_moveto(widget._scroll_target)
            widget.mark_set("insert", cursor_target)
            widget._is_scrolling = False
            return
        if i >= steps:
            widget.yview_moveto(widget._scroll_target)
            widget.mark_set("insert", cursor_target)
            widget._is_scrolling = False
            return

        nonlocal current
        current += delta
        widget.yview_moveto(current)
        widget.after(delay, step, i + 1)

    step()

def scroll_both_up(event=None):
    widget = event.widget
    if hasattr(widget, '_is_scrolling') and widget._is_scrolling:
        return "break"
    if widget.term2:
        smooth_scroll(widget, target=0.0, cursor_target="1.0")
        smooth_scroll(widget.term2, target=0.0, cursor_target="1.0")
    elif widget.term1:
        smooth_scroll(widget.term1, target=0.0, cursor_target="1.0")
        smooth_scroll(widget, target=0.0, cursor_target="1.0")
    return "break"

def scroll_both_down(event=None):
    widget = event.widget
    if hasattr(widget, '_is_scrolling') and widget._is_scrolling:
        return "break"
    if widget.term2:
        smooth_scroll(widget, target=1.0, cursor_target="end-1c")
        smooth_scroll(widget.term2, target=1.0, cursor_target="end-1c")
    elif widget.term1:
        smooth_scroll(widget.term1, target=1.0, cursor_target="end-1c")
        smooth_scroll(widget, target=1.0, cursor_target="end-1c")
    return "break"

def interrupt_all_processes(terminal1, terminal2):
    if hasattr(terminal1, '_is_scrolling') and terminal1._is_scrolling:
        terminal1._scroll_interrupt = True
    if terminal2:
        if hasattr(terminal2, '_is_scrolling') and terminal2._is_scrolling:
            terminal2._scroll_interrupt = True
        if terminal2.typing_thread and terminal2.typing_thread.is_alive():
            terminal2.skip_typing = True

def make_printable(text: str) -> str:
    """Sostituisce i caratteri ASCII non stampabili con '?'."""
    return ''.join(c if 32 <= ord(c) <= 126 else '?' for c in text)

def all_shifts(self, text):
    results = []
    text_processed = text
    colon_pos = len("[A=25, B=25]") + 1
    if text_processed.strip():
        results.append("")
        results.append("----------------------- Caesar Cipher - Alphabetical Shifts -----------------------")
        for shift in range(26):
            shifted_text = caesar_cipher(text_processed, shift)
            label = f"[Shift {shift:2d}]"
            results.append(f"{label.ljust(colon_pos)} : {shifted_text}")
        results.append("")
        results.append("-------------------------- Caesar Cipher - ASCII Shifts --------------------------")
        for shift in range(1, 255):
            shifted_text = caesar_ascii(text_processed, shift)
            printable_text = make_printable(shifted_text)
            label = f"[ASCII +{shift:3d}]"
            results.append(f"{label.ljust(colon_pos)} : {printable_text}")
        results.append("")
        results.append("---------------------------- Atbash Cipher -----------------------------")
        atbash_label = "[_ATBASH_] "
        atbash_text = atbash_cipher(text_processed)
        results.append(f"{atbash_label.ljust(colon_pos)}: {atbash_text}")
        results.append("")
        results.append("----------------------- Affine Cipher - Brute Force ------------------------")
        for a, b, decrypted in affine_decrypt_bruteforce(text_processed):
            label = f"[A={a:2d}, B={b:2d}]"
            results.append(f"{label.ljust(colon_pos)} : {decrypted}")
    return '\n'.join(results)

# --- Funzioni di verifica del formato ---
def is_binary_string(s):
    clean_s = s.strip().replace(" ", "")
    return all(c in '01' for c in clean_s) and bool(clean_s)

def is_octal_string(s):
    clean_s = s.strip()
    return all(c in '01234567' for c in clean_s) and bool(clean_s)

def is_hex_string(s):
    clean_s = s.strip().replace(" ", "").lower()
    if clean_s.startswith('0x'):
        clean_s = clean_s[2:]
    elif clean_s.startswith('#'):
        clean_s = clean_s[1:]
    if not clean_s:
        return False
    return all(c in '0123456789abcdef' for c in clean_s)

# --- Funzioni di decodifica ---
def decode_from_binary(binary_string: str) -> str:
    clean_string = binary_string.strip()
    output = []
    bytes_list = clean_string.split(' ')
    decoded_numbers = []
    decoded_text = ""
    for b in bytes_list:
        if not b:
            continue
        try:
            number = int(b, 2)
            decoded_numbers.append(str(number))
            ascii_char = chr(number) if 0 <= number <= 255 else '?'
            decoded_text += ascii_char
        except (ValueError, IndexError):
            return "[ERRORE] : La stringa binaria è mal formattata o contiene byte non validi."
    if not decoded_numbers:
        return "[ERRORE] : La stringa binaria è vuota o non valida."
    output.append(f"[__BINARIO__]: {' '.join(decoded_numbers)}")
    output.append("")
    output.append(f"[_BIN ASCII_]: {make_printable(decoded_text)}")
    return '\n'.join(output)

def decode_from_octal(octal_string: str) -> str:
    clean_string = octal_string.strip()
    output = []
    octal_list = clean_string.split(' ')
    decoded_numbers = []
    decoded_text = ""
    for o in octal_list:
        if not o:
            continue
        try:
            number = int(o, 8)
            decoded_numbers.append(str(number))
            ascii_char = chr(number) if 0 <= number <= 255 else '?'
            decoded_text += ascii_char
        except (ValueError, IndexError):
            return "[ERRORE] : La stringa ottale è mal formattata o contiene byte non validi."
    if not decoded_numbers:
        return "[ERRORE] : La stringa ottale è vuota o non valida."
    output.append(f"[__ OTTALE__]: {' '.join(decoded_numbers)}")
    output.append("")
    output.append(f"[_OTT ASCII_]: {make_printable(decoded_text)}")
    return '\n'.join(output)

def decode_from_hex(hex_string: str) -> str:
    clean_string = hex_string.strip()
    output = []
    hex_list = clean_string.split(' ')
    decoded_numbers = []
    decoded_text = ""
    for h in hex_list:
        if not h:
            continue
        try:
            number = int(h, 16)
            decoded_numbers.append(str(number))
            ascii_char = chr(number) if 0 <= number <= 255 else '?'
            decoded_text += ascii_char
        except (ValueError, IndexError):
            return "[ERRORE] : La stringa esadecimale è mal formattata o contiene byte non validi."
    if not decoded_numbers:
        return "[ERRORE] : La stringa esadecimale è vuota o non valida."
    output.append(f"[__ESADECIMALE__]: {' '.join(decoded_numbers)}")
    output.append("")
    output.append(f"[__ESAD. ASCII__]: {make_printable(decoded_text)}")
    return '\n'.join(output)

# --- Classi dei terminali ---
class Terminal1(tk.Text):
    def __init__(self, master, prompt, on_enter, term2=None, **kwargs):
        super().__init__(master, **kwargs)
        self.prompt = prompt
        self.on_enter = on_enter
        self.term2 = term2
        self.configure(fg="lime", bg="black", insertbackground="lime", font=("Courier New", 14),
                       undo=False, wrap="word", bd=2, relief="solid", highlightthickness=2,
                       highlightbackground="black", highlightcolor="lime")
        self.insert("1.0", "Microsoft Windows [Versione 10.0.26100.4652]\n(c) Microsoft Corporation. Tutti i diritti riservati.\n\n")
        self.insert("end", prompt)
        self.prompt_index = self.index("end-1c")
        self.tag_add("readonly", "1.0", self.prompt_index)
        self.tag_add("prompt", f"{self.prompt_index} linestart", self.prompt_index)
        self.tag_config("readonly", foreground="lime")
        self.tag_config("prompt", foreground="lime")
        self.bind("<Key>", self.on_key)
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Return>", self.on_return)
        self.bind("<Button-3>", self.on_right_click)
        self.mark_set("insert", self.prompt_index)
        self.focus_set()
        self.command_history = []
        self.history_index = None
        self.bind("<Control-Up>", scroll_both_up)
        self.bind("<Control-Down>", scroll_both_down)
        self._is_scrolling = False

    def is_selection_readonly(self):
        try:
            sel_start, sel_end = self.index("sel.first"), self.index("sel.last")
            ranges = self.tag_ranges("readonly")
            return any(self.compare(sel_start, "<", ranges[i+1]) and
                       self.compare(sel_end, ">", ranges[i])
                       for i in range(0, len(ranges), 2))
        except tk.TclError:
            return False

    def on_right_click(self, event):
        try:
            if self.tag_ranges("sel"):
                self.event_generate("<<Copy>>")
        except tk.TclError:
            pass
        try:
            text = self.clipboard_get()
            if self.compare(self.index("insert"), ">=", self.prompt_index):
                self.insert(self.index("insert"), text)
        except tk.TclError:
            pass
        return "break"

    def on_key(self, event):
        if event.keysym in ("Left", "Right", "Prior", "Next", "Home", "End"):
            if self.compare(self.index("insert"), "<", self.prompt_index):
                return None
            else:
                return "break"
        if event.keysym == "space":
            if (hasattr(self, '_is_scrolling') and self._is_scrolling) or \
               (self.term2 and (hasattr(self.term2, '_is_scrolling') and self.term2._is_scrolling or \
                                self.term2.typing_thread and self.term2.typing_thread.is_alive())):
                interrupt_all_processes(self, self.term2)
            else:
                self.insert("insert", " ")
            return "break"
        if event.keysym == "Up":
            self.show_previous_command()
            return "break"
        elif event.keysym == "Down":
            self.show_next_command()
            return "break"
        if self.compare(self.index("insert"), "<", self.prompt_index):
            self.mark_set("insert", self.prompt_index)
            return "break"
        if event.keysym in ("BackSpace", "Delete") and self.compare(self.index("insert"), "<=", self.prompt_index):
            return "break"
        if self.is_selection_readonly():
            return "break"
        return None

    def on_click(self, event):
        if self.compare(self.index(f"@{event.x},{event.y}"), "<", self.prompt_index):
            self.mark_set("insert", self.prompt_index)
            return "break"

    def on_drag(self, event):
        if self.compare(self.index(f"@{event.x},{event.y}"), "<", self.prompt_index):
            self.mark_set("insert", self.prompt_index)
            return "break"

    def on_return(self, event):
        cmd = self.get(self.prompt_index, "insert lineend").strip()
        self.config(state="normal")
        self.delete(self.prompt_index, "end")
        if cmd:
            self.command_history.append(cmd)
        self.history_index = None
        self.on_enter(cmd)
        return "break"

    def insert_prompt(self):
        last_line_index = self.index("end-2c linestart")
        last_line_text = self.get(last_line_index, "end-2c lineend")
        if last_line_text.strip() == self.prompt.strip():
            self.delete(last_line_index, "end-2c lineend +1c")
        self.insert("end", "\n" + self.prompt)
        self.prompt_index = self.index("end-1c")
        self.tag_add("readonly", "1.0", self.prompt_index)
        self.tag_add("prompt", f"{self.prompt_index} linestart", self.prompt_index)
        self.tag_config("readonly", foreground="lime")
        self.tag_config("prompt", foreground="lime")
        self.mark_set("insert", self.prompt_index)
        self.see("end")

    def show_previous_command(self):
        if not self.command_history:
            return
        if self.history_index is None:
            self.history_index = len(self.command_history) - 1
        elif self.history_index > 0:
            self.history_index -= 1
        self.replace_current_line(self.command_history[self.history_index])

    def show_next_command(self):
        if not self.command_history or self.history_index is None:
            return
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.replace_current_line(self.command_history[self.history_index])
        else:
            self.history_index = None
            self.replace_current_line("")

    def replace_current_line(self, text):
        self.delete(self.prompt_index, "insert lineend")
        self.insert(self.prompt_index, text)
        self.mark_set("insert", self.index(f"{self.prompt_index}+{len(text)}c"))

class Terminal2(tk.Text):
    def __init__(self, master, prompt, term1=None, **kwargs):
        super().__init__(master, **kwargs)
        self.prompt = prompt
        self.term1 = term1
        self.configure(fg="lime", bg="black", insertbackground="lime", font=("Courier New", 14),
                       undo=False, wrap="word", bd=2, relief="solid", highlightthickness=2,
                       highlightbackground="black")
        self.clear_and_insert_prompt() # Chiama la nuova funzione per inizializzare il terminale
        self.mark_set("insert", self.prompt_index)
        self.typing_thread = None
        self.skip_typing = False
        self.bind("<Key>", self.on_key_terminal2)
        self.bind("<Button-3>", self.on_right_click)
        self._is_scrolling = False
        self.history = []
        self.history_index = None
        self.bind("<Return>", self.on_enter)
        self.bind("<Control-Up>", scroll_both_up)
        self.bind("<Control-Down>", scroll_both_down)
        
    def on_right_click(self, event):
        try:
            if self.tag_ranges("sel"):
                self.event_generate("<<Copy>>")
        except tk.TclError:
            pass
        return "break"

    def on_key_terminal2(self, event):
        return "break"

    def clear_and_insert_prompt(self):
        self.config(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", "Terminale2 Ready\n\n")
        self.insert("end", self.prompt)
        self.prompt_index = self.index("end-1c")
        self.mark_set("insert", self.prompt_index)
        self.see("end")

    def type_text(self, text, delay=0.03):
        if self.typing_thread and self.typing_thread.is_alive():
            self.skip_typing = True
        self.skip_typing = False
        self.config(state="normal")
        self.insert("end", "\n\n")
        self.see("end")

        def run_typing():
            self.config(state="normal")
            for c in text:
                if self.skip_typing:
                    remaining = text[text.index(c):]
                    self.insert("end", remaining)
                    self.see("end")
                    break
                self.insert("end", c)
                self.see("end")
                time.sleep(delay)
            self.mark_set("insert", self.index("end-1c"))
        self.typing_thread = threading.Thread(target=run_typing, daemon=True)
        self.typing_thread.start()

    def get_current_line(self):
        return self.get(self.prompt_index, "end-1c")

    def on_enter(self, event):
        input_text = self.get_current_line().strip()
        if not input_text:
            return "break"
        self.history.append(input_text)
        self.history_index = len(self.history)
        self.insert("end", '\n')
        try:
            if is_binary_string(input_text):
                decoded_output = decode_from_binary(input_text)
                self.type_text(f"\n{decoded_output}")
            elif is_octal_string(input_text):
                decoded_output = decode_from_octal(input_text)
                self.type_text(f"\n{decoded_output}")
            elif is_hex_string(input_text):
                decoded_output = decode_from_hex(input_text)
                self.type_text(f"\n{decoded_output}")
            else:
                is_morse_format = all(c in ['.', '-', ' '] for c in input_text)
                if is_morse_format:
                    decoded_text = decode_morse(input_text)
                    if '?' not in decoded_text and decoded_text.strip():
                        output = f"\n[__DECODED__]: {decoded_text}"
                        self.type_text(output)
                    else:
                        output = f"\n[ERRORE]\nCodice Morse non valido o contenente caratteri non riconosciuti."
                        self.type_text(output)
                else:
                    output_ciphers = all_shifts(self, input_text)
                    self.type_text(f"\n{output_ciphers}")
        except ValueError:
            self.insert("end", "Errore: formato non valido\n")
            self.insert("end", self.prompt)
            self.see("end")
        return "break"

# --- Funzione per avviare l'app in modo sequenziale ---
def start_app():
    root = tk.Tk()
    root.title("Fake Desktop Terminal")
    root.configure(bg="black")
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    root.withdraw()

    def close_and_run_all_scripts(event=None):
        print("DEBUG: Tasto 'Esc' premuto. Avvio degli script di arresto e chiusura dell'app.")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path_music = os.path.join(current_dir, "arresto_musica.py")
        run_script(script_path_music)
        script_path_2 = os.path.join(current_dir, "2.pyw")
        run_script(script_path_2)
        root.destroy()
    
    root.bind("<Escape>", close_and_run_all_scripts)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_1_path = os.path.join(current_dir, "1.pyw")
    if run_script(script_1_path):
        print("DEBUG: 1.pyw avviato con successo.")
    else:
        print("ERRORE DEBUG: Fallito l'avvio di 1.pyw.")
    
    try:
        authenticated = run_matrix_effect(root)
    except (ImportError, FileNotFoundError):
        print("AVVISO: File 'matrix_effect.py' non trovato. Bypass autenticazione.")
        authenticated = True
    
    if authenticated:
        print("Autenticazione riuscita, avvio della GUI...")
        root.deiconify()
        root.attributes("-fullscreen", True)

        def do_nothing(event=None):
            return "break"
        
        root.bind("<KeyPress-Win_L>", do_nothing)
        root.bind("<KeyPress-Win_R>", do_nothing)

        PROMPT1 = "Terminale1@fakedesktop:~$ "
        PROMPT2 = "Terminale2@fakedesktop:~$ "

        button_frame = tk.Frame(root, bg="black")
        button_frame.pack(side="top", fill="x", pady=5)

        mode_var = tk.StringVar(value="Tutti gli Shift")
        def toggle_mode():
            if mode_var.get() == "Tutti gli Shift":
                mode_var.set("Modalità Intelligente")
                toggle_btn.config(text="Modalità: Modalità Intelligente")
            else:
                mode_var.set("Tutti gli Shift")
                toggle_btn.config(text="Modalità: Tutti gli Shift")

        toggle_btn = tk.Button(button_frame, text="Modalità: Tutti gli Shift", command=toggle_mode,
                               bg="black", fg="lime", font=("Courier New", 12), relief="raised", bd=3)
        toggle_btn.pack(side="top", pady=5)

        terminal_frame = tk.Frame(root, bg="black")
        terminal_frame.pack(side="top", fill="both", expand=True)

        def switch_to_term1(event=None):
            terminal1.focus_set()
            terminal1.config(highlightbackground="lime")
            terminal2.config(highlightbackground="black")
            return "break"

        def switch_to_term2(event=None):
            terminal2.focus_set()
            terminal2.config(highlightbackground="lime")
            terminal1.config(highlightbackground="black")
            return "break"
            
        terminal1 = Terminal1(terminal_frame, PROMPT1, None)
        terminal2 = Terminal2(terminal_frame, PROMPT2, terminal1)
        terminal1.term2 = terminal2
        terminal1.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        terminal2.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        terminal1.focus_set()
        terminal1.config(highlightbackground="lime")
        terminal2.config(highlightbackground="black")
        
        terminal1.bind("<Control-Left>", switch_to_term1)
        terminal1.bind("<Control-Right>", switch_to_term2)
        terminal2.bind("<Control-Left>", switch_to_term1)
        terminal2.bind("<Control-Right>", switch_to_term2)
        
        terminal1.bind("<FocusIn>", switch_to_term1)
        terminal2.bind("<FocusIn>", switch_to_term2)

        setattr(Terminal2, "all_shifts", all_shifts)

        def on_command(cmd):
            cmd_stripped = cmd.strip()
            if not cmd_stripped:
                terminal1.insert_prompt()
                return
            
            terminal2.clear_and_insert_prompt()

            if is_binary_string(cmd_stripped):
                decoded_output = decode_from_binary(cmd_stripped)
                terminal2.type_text(f"\n{decoded_output}")
            elif is_octal_string(cmd_stripped):
                decoded_output = decode_from_octal(cmd_stripped)
                terminal2.type_text(f"\n{decoded_output}")
            elif is_hex_string(cmd_stripped):
                decoded_output = decode_from_hex(cmd_stripped)
                terminal2.type_text(f"\n{decoded_output}")
            else:
                is_morse_format = all(c in ['.', '-', ' '] for c in cmd_stripped)
                if is_morse_format:
                    decoded_text = decode_morse(cmd_stripped)
                    if '?' not in decoded_text and decoded_text.strip():
                        output = f"\n[__DECODED__]: {decoded_text}"
                        terminal2.type_text(output)
                    else:
                        output = f"\n[ERRORE]\nCodice Morse non valido o contenente caratteri non riconosciuti."
                        terminal2.type_text(output)
                else:
                    output_ciphers = all_shifts(terminal2, cmd_stripped)
                    terminal2.type_text(f"\n{output_ciphers}")
            
            terminal1.insert_prompt()

        terminal1.on_enter = on_command
        
        show_and_run_2(root)
        
        root.mainloop()

    else:
        print("Autenticazione fallita o utente ha annullato.")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path_music = os.path.join(current_dir, "arresto_musica.py")
        run_script(script_path_music)
        script_path_2 = os.path.join(current_dir, "2.pyw")
        run_script(script_path_2)

        sys.exit()

if __name__ == '__main__':
    start_app()