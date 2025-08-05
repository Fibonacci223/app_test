
import pygame
import random
import sys
import os
import tkinter as tk
import threading
import time
import tkinter.font as tkfont
import subprocess
import re

MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
    '...--': '3', '....-': '4', '.....': '5', '-....': '6',
    '--...': '7', '---..': '8', '----.': '9',
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '-.-.--': '!',
    '-..-.': '/', '.--.-.': '@', '---...': ':', '-.-.-.': ';',
    '-....-': '-', '..-.-.': '+', '...-..-': '$',
    '-.--.': '(', '-.--.-': ')', '.-..-.': '"'
}

REVERSE_MORSE_DICT = {value: key for key, value in MORSE_CODE_DICT.items()}

def decode_morse(morse_code: str) -> str:
    if not morse_code.strip():
        return ""

    valid_chars = set(['.', '-', ' '])
    if not all(c in valid_chars for c in morse_code):
        return "?"

    words = re.split(r'\s{3,}', morse_code.strip())
    decoded_words = []
    for word in words:
        letters = word.split(' ')
        decoded_letters = [MORSE_CODE_DICT.get(letter, '?') for letter in letters]
        decoded_words.append(''.join(decoded_letters))

    return ' '.join(decoded_words)

def encode_to_morse(text: str) -> str:
    morse_list = []

    for word in text.upper().split():
        morse_word = []
        for char in word:
            if char in REVERSE_MORSE_DICT:
                morse_word.append(REVERSE_MORSE_DICT[char])
            else:
                morse_word.append('?')
        morse_list.append(' '.join(morse_word))

    return '   '.join(morse_list)

def run_script(script_path):
    print(f"Avvio dello script {script_path}...")
    try:
        subprocess.Popen(['pythonw', script_path], creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"Script {script_path} avviato.")
        return True
    except FileNotFoundError:
        print(f"Errore: Impossibile trovare il file {script_path}")
        return False
    except Exception as e:
        print(f"Errore generico durante l'avvio di {script_path}: {e}")
        return False

def run_matrix_effect(master_app):
    FONT_SIZE = 20
    CHARS = '01アイウエオカキクケコサシスセソタチツテト'
    FPS = 60
    TRAIL_LENGTH = 10
    TRAIL_COLORS = [
        (180, 255, 180),
        (100, 255, 100),
        (0, 200, 0),
        (0, 150, 0),
        (0, 100, 0),
        (0, 50, 0),
    ]

    try:
        pygame.init()
        info = pygame.display.Info()
        WIDTH, HEIGHT = info.current_w, info.current_h
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Matrix Effect PRO")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("consolas", FONT_SIZE, bold=True)
        columns = int(WIDTH / FONT_SIZE)

        streams = []
        for i in range(columns):
            x = i * FONT_SIZE
            y = random.randint(-HEIGHT, 0)
            speed = random.randint(4, 10)
            length = random.randint(8, TRAIL_LENGTH)
            streams.append({
                'x': x,
                'y': y,
                'speed': speed,
                'length': length,
                'chars': [random.choice(CHARS) for _ in range(TRAIL_LENGTH)],
            })

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                   (event.type == pygame.KEYDOWN) or \
                   (event.type == pygame.MOUSEBUTTONDOWN):
                    running = False
                    break

            screen.fill((0, 0, 0))

            for stream in streams:
                x = stream['x']
                y = stream['y']
                for i in range(stream['length']):
                    char = random.choice(CHARS) if random.random() > 0.9 else stream['chars'][i % len(stream['chars'])]
                    color_index = i if i < len(TRAIL_COLORS) else -1
                    color = TRAIL_COLORS[color_index]
                    char_surface = font.render(char, True, color)
                    screen.blit(char_surface, (x, y - i * FONT_SIZE))

                stream['y'] += stream['speed']

                if stream['y'] - stream['length'] * FONT_SIZE > HEIGHT:
                    stream['y'] = random.randint(-HEIGHT // 2, 0)
                    stream['speed'] = random.randint(4, 10)
                    stream['length'] = random.randint(6, TRAIL_LENGTH)
                    stream['chars'] = [random.choice(CHARS) for _ in range(TRAIL_LENGTH)]

            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()
        master_app.after(100, show_and_run_2, master_app)

def show_and_run_2(master_app):
    master_app.deiconify()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_2_path = os.path.join(current_dir, "2.pyw")
    run_script(script_2_path)

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
            widget.see("insert")
            widget._is_scrolling = False
            return
        if i >= steps:
            widget.yview_moveto(widget._scroll_target)
            widget.mark_set("insert", cursor_target)
            widget.see("insert")
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

def caesar_cipher(text, shift):
    result = ""
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result += chr((ord(c) - base + shift) % 26 + base)
        else:
            result += c
    return result

def atbash_cipher(text):
    result = ""
    for c in text:
        if c.isalpha():
            if c.isupper():
                result += chr(ord('Z') - (ord(c) - ord('A')))
            else:
                result += chr(ord('z') - (ord(c) - ord('a')))
        else:
            result += c
    return result

def affine_decrypt_bruteforce(ciphertext):
    valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    risultati = []
    for a in valid_a:
        a_inv = None
        for i in range(26):
            if (a * i) % 26 == 1:
                a_inv = i
                break
        if a_inv is None:
            continue
        for b in range(26):
            plaintext = ""
            for char in ciphertext:
                if char.isalpha():
                    y = ord(char.upper()) - ord('A')
                    x = (a_inv * (y - b)) % 26
                    plaintext += chr(x + ord('A'))
                else:
                    plaintext += char
            risultati.append((a, b, plaintext))
    return risultati

def separator_with_title(title, width=85, pattern="-"):
    title = f" {title} "
    title_len = len(title)
    if title_len >= width:
        return title[:width]
    total_padding = width - title_len
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding

    def build_side(pad_len):
        times = pad_len // len(pattern) + 1
        return (pattern * times)[:pad_len]

    left_line = build_side(left_padding)
    right_line = build_side(right_padding)
    return left_line + title + right_line

def all_shifts(self, text):
    results = []
    text_processed = ''.join(c for c in text.upper() if c.isalpha() or c == ' ')

    colon_pos = len("[Shift 25]") - 10
    colon_pos -= 1

    if text_processed:
        for shift in range(26):
            shifted_text = caesar_cipher(text_processed, shift).upper()
            label = f"[Shift {shift:2d}]"
            results.append(f"{label.ljust(colon_pos)} : {shifted_text}")

        results.append("")
        atbash_label = "[_ATBASH_] "
        results.append(f"{atbash_label.ljust(colon_pos)}: {atbash_cipher(text_processed)}")
        results.append("")
        results.append(separator_with_title("Affine Cipher - Brute Force"))

        for a, b, decrypted in affine_decrypt_bruteforce(text_processed):
            label = f"[A={a:2d}, B={b:2d}]"
            results.append(f"{label.ljust(colon_pos)} : {decrypted.upper()}")

    return '\n'.join(results)

def decode_from_binary(binary_string: str) -> str:
    clean_string = binary_string.strip()

    if ' ' in clean_string:
        bytes = clean_string.split(' ')
        decoded_numbers = []
        decoded_text = ""
        for b in bytes:
            try:
                number = int(b, 2)
                decoded_numbers.append(str(number))
                ascii_char = chr(number) if 0 <= number <= 255 else '?'
                decoded_text += ascii_char
            except (ValueError, IndexError):
                return "[ERRORE] : La stringa binaria è mal formattata o contiene byte non validi."

        return f"[__BINARIO__]: {' '.join(decoded_numbers)} (Testo: {decoded_text})"

    else:
        try:
            if not clean_string:
                return "[ERRORE] : La stringa binaria è vuota."

            number = int(clean_string, 2)
            ascii_char = chr(number) if 0 <= number <= 255 else 'N/A'
            return f"[__BINARIO__]: {number} (Testo: {ascii_char})"
        except ValueError:
            return "[ERRORE] : La stringa binaria non è formattata correttamente."

def decode_from_octal(octal_string: str) -> str:
    try:
        clean_string = ''.join(c for c in octal_string if c in '01234567')
        if not clean_string:
            return "[ERRORE] : La stringa ottale è vuota o non valida."

        number = int(clean_string, 8)
        ascii_char = chr(number) if 0 <= number <= 255 else 'N/A'
        return f"[__ OTTALE__]: {number} (Testo: {ascii_char})"
    except ValueError:
        return "[ERRORE] : La stringa ottale non è formattata correttamente."

def decode_from_hex(hex_string: str) -> str:
    clean_string = hex_string.strip()

    if clean_string.startswith('0x') or clean_string.startswith('0X'):
        clean_string = clean_string[2:]
    elif clean_string.startswith('#'):
        clean_string = clean_string[1:]

    if not all(c in '0123456789abcdefABCDEF' for c in clean_string):
        return "[ERRORE] : La stringa esadecimale contiene caratteri non validi."

    if not clean_string:
        return "[ERRORE] : La stringa esadecimale è vuota."

    try:
        number = int(clean_string, 16)
        ascii_char = chr(number) if 0 <= number <= 255 else 'N/A'
        return f"[__ESADECIMALE__]: {number} (Testo: {ascii_char})"
    except ValueError:
        return "[ERRORE] : La stringa esadecimale non è formattata correttamente."

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

        self.mark_set("insert", self.prompt_index)
        self.focus_set()
        self.command_history = []
        self.history_index = None
        self.bind("<Control-Up>", scroll_both_up)
        self.bind("<Control-Down>", scroll_both_down)
        self._is_scrolling = False
        self.bind("<Button-3>", self.handle_right_click)

    def is_selection_readonly(self):
        try:
            sel_start, sel_end = self.index("sel.first"), self.index("sel.last")
            ranges = self.tag_ranges("readonly")
            return any(self.compare(sel_start, "<", ranges[i+1]) and
                       self.compare(sel_end, ">", ranges[i])
                       for i in range(0, len(ranges), 2))
        except tk.TclError:
            return False

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

    def handle_right_click(self, event):
        try:
            if self.tag_ranges("sel"):
                self.event_generate("<<Copy>>")
                return "break"
        except tk.TclError:
            pass
            
        if self.compare(self.index("@%s,%s" % (event.x, event.y)), ">=", self.prompt_index):
            self.mark_set("insert", self.index("@%s,%s" % (event.x, event.y)))
            self.event_generate("<<Paste>>")
            
        return "break"

class Terminal2(tk.Text):
    def __init__(self, master, prompt, term1=None, **kwargs):
        super().__init__(master, **kwargs)
        self.prompt = prompt
        self.term1 = term1
        self.configure(fg="lime", bg="black", insertbackground="lime", font=("Courier New", 14),
                       undo=False, wrap="word", bd=2, relief="solid", highlightthickness=2,
                       highlightbackground="black")
        self.insert("1.0", "Terminale2 Ready\n\n")
        self.insert("end", prompt)
        self.prompt_index = self.index("end-1c")
        self.mark_set("insert", self.prompt_index)
        self.typing_thread = None
        self.skip_typing = False

        self.bind("<Key>", lambda e: "break")
        self.bind("<Control-v>", lambda e: "break")
        self.bind("<<Paste>>", lambda e: "break")

        self._is_scrolling = False
        self.history = []
        self.history_index = None
        self.bind("<Return>", self.on_enter)
        self.bind("<Control-Up>", scroll_both_up)
        self.bind("<Control-Down>", scroll_both_down)
        self.bind("<Button-3>", self.handle_right_click_copy_only)

    def handle_right_click_copy_only(self, event):
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
        self.insert("end", self.prompt)
        self.prompt_index = self.index("end-1c")
        self.mark_set("insert", self.prompt_index)
        self.see("end")

    def type_text(self, text, delay=0.03):
        if self.typing_thread and self.typing_thread.is_alive():
            self.skip_typing = True
        self.skip_typing = False
        self.clear_and_insert_prompt()

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
            if input_text.startswith("0b"):
                bits = input_text[2:].replace(" ", "")
                if len(bits) % 8 == 0:
                    ascii_output = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
                    value = int(bits, 2)
                else:
                    value = int(bits, 2)
                    ascii_output = chr(value) if 0 <= value <= 255 else ''

                self.insert("end", f"Binario: {bits}\n")
                self.insert("end", f"Decimale: {value}\n")
                if ascii_output:
                    self.insert("end", f"ASCII: {ascii_output}\n")

            elif input_text.startswith("0o"):
                value = int(input_text[2:], 8)
                ascii_output = chr(value) if 0 <= value <= 255 else ''
                self.insert("end", f"Ottale: {input_text[2:]}\n")
                self.insert("end", f"Decimale: {value}\n")
                if ascii_output:
                    self.insert("end", f"ASCII: {ascii_output}\n")

            elif input_text.startswith("0x"):
                value = int(input_text[2:], 16)
                ascii_output = chr(value) if 0 <= value <= 255 else ''
                self.insert("end", f"Esadecimale: {input_text[2:]}\n")
                self.insert("end", f"Decimale: {value}\n")
                if ascii_output:
                    self.insert("end", f"ASCII: {ascii_output}\n")

            elif all(c in "01" for c in input_text):
                bits = input_text.replace(" ", "")
                if len(bits) % 8 == 0:
                    ascii_output = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
                    value = int(bits, 2)
                else:
                    value = int(bits, 2)
                    ascii_output = chr(value) if 0 <= value <= 255 else ''
                self.insert("end", f"Binario: {bits}\n")
                self.insert("end", f"Decimale: {value}\n")
                if ascii_output:
                    self.insert("end", f"ASCII: {ascii_output}\n")

            elif all(c in "01234567" for c in input_text):
                value = int(input_text, 8)
                ascii_output = chr(value) if 0 <= value <= 255 else ''
                self.insert("end", f"Ottale: {input_text}\n")
                self.insert("end", f"Decimale: {value}\n")
                if ascii_output:
                    self.insert("end", f"ASCII: {ascii_output}\n")

            elif input_text.isdigit():
                value = int(input_text)
                ascii_output = chr(value) if 0 <= value <= 255 else ''
                self.insert("end", f"Decimale: {input_text}\n")
                if ascii_output:
                    self.insert("end", f"ASCII: {ascii_output}\n")

            else:
                ascii_output = input_text
                self.insert("end", f"Testo: {input_text}\n")
                self.insert("end", f"ASCII codes: {' '.join(str(ord(c)) for c in input_text)}\n")
                self.insert("end", f"Binario: {' '.join(format(ord(c), '08b') for c in input_text)}\n")
                self.insert("end", f"Ottale: {' '.join(format(ord(c), '03o') for c in input_text)}\n")
                self.insert("end", f"Esadecimale: {' '.join(format(ord(c), '02x') for c in input_text)}\n")
                self.insert("end", self.prompt)
                self.see("end")
                return "break"

            self.insert("end", self.prompt)
            self.see("end")

        except ValueError:
            self.insert("end", "Errore: formato non valido\n")
            self.insert("end", self.prompt)
            self.see("end")

        return "break"

def avvia_gui():
    root = tk.Tk()
    root.title("Fake Desktop Terminal")
    root.configure(bg="black")

    root.withdraw()

    root.attributes("-fullscreen", True)

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

    def is_hex_string(s):
        s = s.strip().lower()
        if s.startswith('0x'):
            s = s[2:]
        elif s.startswith('#'):
            s = s[1:]

        if not s:
            return False

        return all(c in '0123456789abcdef' for c in s)

    def is_binary_string(s):
        clean_s = s.strip().replace(" ", "")
        return all(c in '01' for c in clean_s) and clean_s

    def is_octal_string(s):
        clean_s = s.strip()
        return all(c in '01234567' for c in clean_s) and any(c in '01234567' for c in clean_s)

    def on_command(cmd):
        cmd_stripped = cmd.strip()

        if not cmd_stripped:
            terminal1.insert_prompt()
            return

        if is_binary_string(cmd_stripped):
            decoded_output = decode_from_binary(cmd_stripped)
            terminal2.type_text(f"\n\n{decoded_output}")
        elif is_octal_string(cmd_stripped):
            decoded_output = decode_from_octal(cmd_stripped)
            terminal2.type_text(f"\n\n{decoded_output}")
        elif is_hex_string(cmd_stripped):
            decoded_output = decode_from_hex(cmd_stripped)
            terminal2.type_text(f"\n\n{decoded_output}")
        else:
            is_morse = all(c in ['.', '-', ' '] for c in cmd_stripped)
            if is_morse:
                decoded_text = decode_morse(cmd_stripped)
                if '?' not in decoded_text and decoded_text.strip():
                    output = f"\n\n[__DECODED__]: {decoded_text}"
                    terminal2.type_text(output)
                else:
                    output = f"\n\n[ERRORE]\nCodice Morse non valido o contenente caratteri non riconosciuti."
                    terminal2.type_text(output)
            else:
                output_ciphers = all_shifts(terminal2, cmd_stripped)
                terminal2.type_text(f"\n\n{output_ciphers}")

        terminal1.insert_prompt()

    terminal1.on_enter = on_command

    return terminal1, terminal2, root, terminal_frame, button_frame

if __name__ == '__main__':
    app = avvia_gui()[2]
    thread = threading.Thread(target=run_matrix_effect, args=(app,), daemon=True)
    thread.start()
    app.mainloop()
 