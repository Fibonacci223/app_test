import tkinter as tk
import threading
import time

#Scroll------------------------------------------------------------------------------------------------------------

def smooth_scroll(widget, target, steps=100, delay=10):
    widget._scroll_interrupt = False  # Reset flag

    current = widget.yview()[0]
    delta = (target - current) / steps

    def step(i=0):
        nonlocal current
        if widget._scroll_interrupt:
            widget.yview_moveto(target)  # Salta direttamente al punto finale
            return
        if i >= steps:
            widget.yview_moveto(target)
            return
        current += delta
        widget.yview_moveto(current)
        widget.after(delay, step, i + 1)

    step()   


# Scrolla entrambi i terminali associati (term1 e term2) verso l'inizio
def scroll_both_up(event=None):
    widget = event.widget
    smooth_scroll(widget, target=0.0)  # Scrolla il widget principale
    if hasattr(widget, 'term2') and widget.term2:
        smooth_scroll(widget.term2, target=0.0)  # Scrolla anche term2, se esiste
    elif hasattr(widget, 'term1') and widget.term1:
        smooth_scroll(widget.term1, target=0.0)  # Altrimenti scrolla term1
    return "break"


# Scrolla entrambi i terminali associati verso la fine
def scroll_both_down(event=None):
    widget = event.widget
    smooth_scroll(widget, target=1.0)  # Scrolla il widget principale
    if hasattr(widget, 'term2') and widget.term2:
        smooth_scroll(widget.term2, target=1.0)
    elif hasattr(widget, 'term1') and widget.term1:
        smooth_scroll(widget.term1, target=1.0)
    return "break"

#Copia-------------------------------------------------------------------------------------------------------------

# Gestisce il click destro su un Text widget: copia se c'è selezione, incolla se no (solo su terminal1)

def handle_right_click(text_widget, event, terminal1, prompt_index=None):
    try:
        if text_widget.tag_ranges("sel"):
            # Se c'è una selezione, copia negli appunti
            selected = text_widget.get("sel.first", "sel.last")
            text_widget.clipboard_clear()
            text_widget.clipboard_append(selected)
        else:
            # Nessuna selezione: incolla negli appunti
            clip = text_widget.clipboard_get()
            if text_widget == terminal1:
                # Calcola la posizione in base al punto cliccato
                index = text_widget.index(f"@{event.x},{event.y}")
                # Incolla solo se siamo oltre il prompt (se definito)
                if prompt_index is None or text_widget.compare(index, ">=", prompt_index):
                    text_widget.insert(index, clip)
                    text_widget.see("insert")
    except tk.TclError:
        # Errore gestito silenziosamente
        pass
    return "break"

#Scrolla il widget--------------------------------------------------------------------------------------------------

# Scrolla il widget all'inizio (riga 1.0)
def scroll_to_top(event=None):
    widget = event.widget
    widget.yview_moveto(0)  # Sposta la vista in alto
    widget.mark_set("insert", "1.0")  # Posiziona il cursore all'inizio
    widget.see("insert")  # Assicura che sia visibile
    return "break"


# Scrolla il widget alla fine (fine del testo)

def scroll_to_bottom(event=None):
    widget = event.widget
    widget.yview_moveto(1)  # Sposta la vista in basso
    widget.mark_set("insert", "end-1c")  # Imposta il cursore alla fine (1 carattere prima di 'end')
    widget.see("insert")  # Assicura che sia visibile
    if hasattr(widget, "history_index"):
        widget.history_index = None  # Resetta eventuale indice di cronologia
    return "break"


#Cifrario-----------------------------------------------------------------------------------------------------------

# Cifrario di Cesare: sposta le lettere dell'alfabeto di 'shift' posizioni
def caesar_cipher(text, shift):
    result = ""
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result += chr((ord(c) - base + shift) % 26 + base)
        else:
            result += c  # Caratteri non alfabetici rimangono invariati
    return result


# Cifrario di Atbash: sostituisce ogni lettera con il suo "opposto" nell'alfabeto
def atbash_cipher(text):
    result = ""
    for c in text:
        if c.isalpha():
            if c.isupper():
                result += chr(ord('Z') - (ord(c) - ord('A')))
            else:
                result += chr(ord('z') - (ord(c) - ord('a')))
        else:
            result += c  # Caratteri non alfabetici rimangono invariati
    return result


# Brute force per cifratura affine: prova tutte le combinazioni valide di (a, b)
def affine_encrypt_bruteforce(plaintext):
    valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]  # Valori coprimi con 26
    risultati = []

    for a in valid_a:
        for b in range(26):
            ciphertext = ""
            for char in plaintext:
                if char.isalpha():
                    x = ord(char.upper()) - ord('A')  # Converti in indice alfabetico
                    y = (a * x + b) % 26  # Formula affine
                    ciphertext += chr(y + ord('A'))
                else:
                    ciphertext += char
            risultati.append((a, b, ciphertext))  # Salva risultato

    return risultati


# Brute force per decifratura affine: prova tutte le chiavi (a, b)
def affine_decrypt_bruteforce(ciphertext):
    valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    risultati = []

    for a in valid_a:
        a_inv = None
        # Calcolo dell'inverso moltiplicativo di a modulo 26
        for i in range(26):
            if (a * i) % 26 == 1:
                a_inv = i
                break
        if a_inv is None:
            continue  # Salta se non esiste l'inverso

        for b in range(26):
            plaintext = ""
            for char in ciphertext:
                if char.isalpha():
                    y = ord(char.upper()) - ord('A')
                    x = (a_inv * (y - b)) % 26  # Formula inversa affine
                    plaintext += chr(x + ord('A'))
                else:
                    plaintext += char
            risultati.append((a, b, plaintext))  # Salva risultato

    return risultati

#Grafica-------------------------------------------------------------------------------------

# Crea una riga con un titolo centrato tra caratteri decorativi (pattern)
def separator_with_title(title, width=85, pattern="-"):
    title = f" {title} "
    title_len = len(title)

    if title_len >= width:
        return title[:width]  # Troncamento se il titolo è troppo lungo

    total_padding = width - title_len
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding

    # Costruisce i bordi decorativi a sinistra e destra
    def build_side(pad_len):
        times = pad_len // len(pattern) + 1
        return (pattern * times)[:pad_len]

    left_line = build_side(left_padding)
    right_line = build_side(right_padding)

    return left_line + title + right_line



#BRUTEFORCE SHIFT -------------------------------------------------------------------------
# Metodo da associare a Terminal2: restituisce tutte le 26 varianti shiftate e la cifratura Atbash


def all_shifts(self, text):
    results = []
    text = text.upper()

    colon_pos = len("[Shift 25]") - 10  # posizione base del ":"
    colon_pos -= 1  # sposto di uno a sinistra

    for shift in range(26):
        shifted_text = caesar_cipher(text, shift).upper()
        label = f"[Shift {shift:2d}]"
        results.append(f"{label.ljust(colon_pos)} : {shifted_text}")

    results.append("")  # Riga vuota

    # Sezione Atbash
    atbash_label = "[_ATBASH_] "
    results.append(f"{atbash_label.ljust(colon_pos)}: {atbash_cipher(text)}")

    results.append("")  # Riga vuota
    results.append(separator_with_title("Affine Cipher - Brute Force"))

    # Sezione Affine Brute Force
    for a, b, decrypted in affine_decrypt_bruteforce(text):
        label = f"[A={a:2d}, B={b:2d}]"
        results.append(f"{label.ljust(colon_pos)} : {decrypted.upper()}")

    return '\n'.join(results)

# Terminale 1---------------------------------------------------------------------------------------------
 
# Terminale 1

class Terminal1(tk.Text):
    def __init__(self, master, prompt, on_enter, term2=None, **kwargs):
        super().__init__(master, **kwargs)
        self.prompt = prompt
        self.on_enter = on_enter
        self.term2 = term2
        self.configure(
                        fg="lime",
                        bg="black",
                        insertbackground="lime",
                        font=("Courier New", 14),
                        undo=False,
                        wrap="word",
                        bd=2,
                        relief="solid",
                        highlightthickness=2,
                        highlightbackground="black",  # bordo base spento (nero)
                        highlightcolor="lime" )   
        self.insert("1.0", "Microsoft Windows [Versione 10.0.26100.4652]\n"
                    "(c) Microsoft Corporation. Tutti i diritti riservati.\n\n")
        self.insert("end", prompt)
        self.prompt_index = self.index("end-1c")
        self.tag_add("readonly", "1.0", self.prompt_index)
        self.tag_add(
            "prompt", f"{self.prompt_index} linestart", self.prompt_index)
        self.tag_config("readonly", foreground="lime")
        self.tag_config("prompt", foreground="lime")
        self.bind("<Key>", self.on_key)
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Return>", self.on_return)
        self.bind("<Control-x>", lambda e: "break")
        self.bind("<Control-c>", lambda e: None)
        self.bind("<Control-v>", lambda e: "break")
        self.bind("<Button-3>", lambda e: handle_right_click(self,
                  e, terminal1=self, prompt_index=self.prompt_index))
        self.mark_set("insert", self.prompt_index)
        self.focus_set()

        self.command_history = []
        self.history_index = None
        self.bind("<Control-Up>", scroll_both_up)
        self.bind("<Control-Down>", scroll_both_down)
        

    def is_selection_readonly(self):
        try:
            sel_start, sel_end = self.index(
                "sel.first"), self.index("sel.last")
            ranges = self.tag_ranges("readonly")
            return any(self.compare(sel_start, "<", ranges[i+1]) and
                       self.compare(sel_end, ">", ranges[i])
                       for i in range(0, len(ranges), 2))
        except tk.TclError:
            return False

    def on_key(self, event):
        if self.compare(self.index("insert"), "<", self.prompt_index):
            self.mark_set("insert", self.prompt_index)
            return "break"
        if event.keysym in ("BackSpace", "Delete") and self.compare(self.index("insert"), "<=", self.prompt_index):
            return "break"
        if event.keysym in ("Left", "Prior", "Home") and self.compare(self.index("insert"), "<=", self.prompt_index):
            return "break"
        if self.is_selection_readonly():
            return "break"

        if event.keysym == "space":
            interrupted = False

            # Interrompe typing su Terminal2
            if self.term2 and self.term2.typing_thread and self.term2.typing_thread.is_alive():
                self.term2.skip_typing = True
                interrupted = True

            # Interrompe scroll fluido su entrambi
            for term in (self, getattr(self, "term2", None)):
                if term and hasattr(term, "_scroll_interrupt"):
                    term._scroll_interrupt = True
                    interrupted = True

            # Inserisci lo spazio nel punto corrente del cursore
            self.insert("insert", " ")

            # Sposta il cursore dopo lo spazio inserito
            self.mark_set("insert", self.index("insert + 1c"))

            return "break"  # Blocca evento originale, perché abbiamo gestito tutto

        if event.keysym == "Up":
            if event.state & 0x4:  # Ctrl
                return scroll_to_top(event)
            else:
                self.show_previous_command()  # <-- corretto
                return "break"
        elif event.keysym == "Down":
            if event.state & 0x4:  # Ctrl
                return scroll_to_bottom(event)
            else:
                self.show_next_command()  # <-- corretto
                return "break"

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
        self.tag_add(
            "prompt", f"{self.prompt_index} linestart", self.prompt_index)
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
        self.mark_set("insert", self.index(
            f"{self.prompt_index}+{len(text)}c"))

 # Terminale 2------------------------------------------------------------------------------------
 
# Terminale 2
 
class Terminal2(tk.Text):
    def __init__(self, master, prompt, **kwargs):
        super().__init__(master, **kwargs)
        self.prompt = prompt
        self.configure(
            fg="lime",
            bg="black",
            insertbackground="lime",
            font=("Courier New", 14),
            undo=False,
            wrap="word",
            bd=2,
            relief="solid",
            highlightthickness=2,
            highlightbackground="lime"
        )
        self.insert("1.0", "Terminale2 Ready\n\n")
        self.insert("end", prompt)
        self.prompt_index = self.index("end-1c")
        self.tag_config("readonly", foreground="lime")
        self.mark_set("insert", self.prompt_index)
        self.typing_thread = None
        self.skip_typing = False

        # Blocca qualsiasi input da tastiera (modifica) ma permette selezione/copia
        self.bind("<Key>", self.on_key_terminal2)
        self.bind("<Control-v>", lambda e: "break")   # Blocca incolla
        self.bind("<Button-2>", lambda e: "break")    # Blocca incolla con mouse centrale (Linux)
        
        # Mantieni i bind esistenti
        self.bind("<Button-3>", lambda e: handle_right_click(self, e, terminal1=None))
        self.bind("<Control-Up>", scroll_both_up)
        self.bind("<Control-Down>", scroll_both_down)

    def clear_and_insert_prompt(self):
        self.config(state="normal")  # necessario per modifiche programmatiche
        self.delete("1.0", "end")
        self.insert("end", self.prompt)
        self.prompt_index = self.index("end-1c")
        self.mark_set("insert", self.prompt_index)
        self.see("end")
        # NON disabilitiamo lo stato per permettere selezione/copia

    def type_text(self, text, delay=0.03):
        if self.typing_thread and self.typing_thread.is_alive():
            self.skip_typing = True

        self.skip_typing = False
        self.clear_and_insert_prompt()

        def run_typing():
            # Configurazione "normale" per permettere insert
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
            # Rimaniamo in stato normale per permettere selezione e copia

        self.typing_thread = threading.Thread(target=run_typing)
        self.typing_thread.daemon = True
        self.typing_thread.start()
    def on_key_terminal2(self, event):
        if event.keysym == "space":
            # ✅ Interrompi scrittura simulata se attiva
            if self.typing_thread and self.typing_thread.is_alive():
                self.skip_typing = True

            # ✅ Interrompi scroll fluido se in corso su entrambi
            for term in (self, getattr(self, "term1", None)):
                if term and hasattr(term, "_scroll_interrupt"):
                    term._scroll_interrupt = True
                    term.yview_moveto(1.0)  # 🔽 Forza il salto alla fine

            return "break"  # Impedisce l'inserimento dello spazio

        return "break"  # Blocca tutti gli altri tasti (puoi rimuoverlo per permettere altri comandi)

 #(Gui)----------------------------------------------------------------------------------------------------------
def avvia_gui():
    root = tk.Tk()
    root.title("Fake Desktop Terminal")
    root.configure(bg="black")
    root.attributes("-fullscreen", True)
    

    PROMPT1 = "Terminale1@fakedesktop:~$ "
    PROMPT2 = "Terminale2@fakedesktop:~$ "

    frame = tk.Frame(root, bg="black")
    frame.pack(side="top", fill="both", expand=True)

    mode_var = tk.StringVar(value="Tutti gli Shift")

    def toggle_mode():
        if mode_var.get() == "Tutti gli Shift":
            mode_var.set("Modalità Intelligente")
            toggle_btn.config(text="Modalità: Modalità Intelligente")
        else:
            mode_var.set("Tutti gli Shift")
            toggle_btn.config(text="Modalità: Tutti gli Shift")

    toggle_btn = tk.Button(root, text="Modalità: Tutti gli Shift", command=toggle_mode,
                           bg="black", fg="lime", font=("Courier New", 12), relief="raised", bd=3)
    toggle_btn.pack(side="top", pady=5)

    terminal1 = Terminal1(frame, PROMPT1, None)
    terminal2 = Terminal2(frame, PROMPT2)

    terminal1.term2 = terminal2

    terminal1.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    terminal2.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    terminal2.term1 = terminal1

    def switch_to_term1(event=None):
        terminal1.focus_set()
        terminal1.config(highlightbackground="lime")   # bordo acceso
        terminal2.config(highlightbackground="black")  # bordo spento
        return "break"

    def switch_to_term2(event=None):
        terminal2.focus_set()
        terminal2.config(highlightbackground="lime")
        terminal1.config(highlightbackground="black")
        return "break"

    root.bind("<Control-Left>", switch_to_term1)
    root.bind("<Control-Right>", switch_to_term2)


 # Bind focus per aggiornare bordo anche con click mouse
    terminal1.bind("<FocusIn>", lambda e: (
        terminal1.config(highlightbackground="lime"),
        terminal2.config(highlightbackground="black")
    ))
    terminal2.bind("<FocusIn>", lambda e: (
        terminal2.config(highlightbackground="lime", highlightcolor="lime"),
        terminal1.config(highlightbackground="black")
))
    terminal2.bind("<FocusOut>", lambda e: (
    terminal2.config(highlightbackground="black"),
))
    # Collego il metodo all_shifts corretto a Terminal2
    setattr(Terminal2, "all_shifts", all_shifts)

    def on_command(cmd):
        if not cmd.strip():
            terminal1.insert_prompt()
            return

        mode_text = f"Modalità attiva: {mode_var.get()}\n\n"

        if mode_var.get() == "Tutti gli Shift":
            text = terminal2.all_shifts(cmd)
        else:
            text = cmd

        terminal2.type_text(mode_text + text)  # ⌨️ Simulazione digitazione

        terminal1.insert_prompt()

    terminal1.on_enter = on_command



 # Collego il metodo all_shifts corretto a Terminal2
    setattr(Terminal2, "all_shifts", all_shifts)

    def on_command(cmd):
        if not cmd.strip():
            terminal1.insert_prompt()
            return

        mode_text = f"Modalità attiva: {mode_var.get()}\n\n"

        if mode_var.get() == "Tutti gli Shift":
            text = terminal2.all_shifts(cmd)
        else:
            text = cmd

        terminal2.type_text(mode_text + text)  # ⌨️ Simulazione digitazione

        terminal1.insert_prompt()

    terminal1.on_enter = on_command

   
    root.mainloop()


if __name__ == "__main__":
    avvia_gui()