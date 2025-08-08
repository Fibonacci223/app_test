import pygame
import random
import time
import sys
import subprocess
import os

def run_matrix_effect(master_app):
    # --- Configurazione del tuo codice Matrix (rimane invariata) ---
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
        (0, 80, 0),
    ]

    CORRECT_PASSWORD = "accesso"
    SHOW_INPUT_AFTER = 5
    MAX_PASSWORD_LENGTH = 35

    pygame.init()
    
    # --- Avvio della musica con playsound (Integrato) ---
    try:
        file_audio = "musica_1.mp3"
        if sys.platform.startswith("win"):
            subprocess.Popen(
                ["python", "-m", "playsound", file_audio],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            subprocess.Popen(
                ["python3", "-m", "playsound", file_audio],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        print("Musica avviata per l'effetto Matrix.")
    except Exception as e:
        print(f"Errore: Impossibile avviare la musica. Assicurati che 'musica_1.mp3' e il modulo 'playsound' esistano. Errore: {e}")
    # --- Fine blocco musica ---

    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Matrix Effect PRO")
    clock = pygame.time.Clock()
    
    # ... (Il resto del tuo codice per l'effetto Matrix continua qui) ...
    # ... (Tutto il ciclo while e la logica di input) ...
    
    font = pygame.font.SysFont("consolas", FONT_SIZE, bold=True)
    custom_font_path = "ShareTechMono-Regular.ttf"
    try:
        input_font = pygame.font.Font(custom_font_path, 40)
        password_font = pygame.font.SysFont("Arial", 25)
    except pygame.error:
        print(f"Warning: Font file '{custom_font_path}' not found. Using default.")
        input_font = pygame.font.SysFont("consolas", 40)
        password_font = pygame.font.SysFont("Arial", 25)
    
    columns = WIDTH // FONT_SIZE

    input_box_height = 45
    input_active = False
    password = ""
    error_timer = 0
    cursor_timer = time.time()
    cursor_visible = True

    streams = []
    for i in range(columns):
        x = i * FONT_SIZE
        y = random.randint(-HEIGHT, 0)
        speed = random.randint(4, 10)
        length = random.randint(6, TRAIL_LENGTH)
        chars = [random.choice(CHARS) for _ in range(length)]
        streams.append({'x': x, 'y': y, 'speed': speed, 'length': length, 'chars': chars})

    start_time = time.time()
    running = True
    authenticated = False
    
    fade_alpha = 0
    text_alpha = 0
    fade_speed = 3
    fade_in_complete = False

    while running:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            
            if input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if password == CORRECT_PASSWORD:
                        authenticated = True
                        running = False
                    else:
                        password = ""
                        error_timer = now + 1.5
                elif event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                elif event.unicode.isprintable():
                    if len(password) < MAX_PASSWORD_LENGTH:
                        password += event.unicode
                cursor_timer = now
                cursor_visible = True

        screen.fill((0, 0, 0))

        for stream in streams:
            x, y = stream['x'], stream['y']
            for i in range(stream['length']):
                char = random.choice(CHARS) if random.random() > 0.9 else stream['chars'][i % len(stream['chars'])]
                color = TRAIL_COLORS[i] if i < len(TRAIL_COLORS) else TRAIL_COLORS[-1]
                char_surface = font.render(char, True, color)
                screen.blit(char_surface, (x, y - i * FONT_SIZE))

            stream['y'] += stream['speed']

            if stream['y'] - stream['length'] * FONT_SIZE > HEIGHT:
                stream['y'] = random.randint(-HEIGHT // 2, 0)
                stream['speed'] = random.randint(4, 10)
                stream['length'] = random.randint(6, TRAIL_LENGTH)
                stream['chars'] = [random.choice(CHARS) for _ in range(stream['length'])]

        if now - start_time >= SHOW_INPUT_AFTER:
            fade_alpha = min(fade_alpha + fade_speed, 180)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, fade_alpha))
            screen.blit(overlay, (0, 0))
            
            if fade_alpha == 180:
                fade_in_complete = True
        
        if fade_in_complete:
            if not input_active:
                pygame.key.set_repeat(300, 30)
                input_active = True
                
            text_alpha = min(text_alpha + fade_speed, 255)

            text_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

            label_text = "AUTHENTICATION REQUIRED"
            label_width, _ = input_font.size(label_text)
            input_box_width = label_width + 40
            input_box = pygame.Rect(WIDTH // 2 - input_box_width // 2, HEIGHT // 2 - input_box_height // 2, input_box_width, input_box_height)
            
            s = pygame.Surface((input_box.width + 12, input_box.height + 12), pygame.SRCALPHA)
            s.fill((0, 120, 0, int(255 * (0.5 + 0.5 * abs(1 - (now * 2) % 2)))))
            text_surface.blit(s, (input_box.x - 6, input_box.y - 6))
            pygame.draw.rect(text_surface, (0, 255, 0), input_box, 1)

            label_y = input_box.y - 60

            if error_timer > now:
                err_text = "ERROR – UNAUTHORIZED ACCESS"
                glitch_color = (random.randint(150, 255), random.randint(0, 50), random.randint(0, 50))
                err_surface = input_font.render(err_text, True, glitch_color)
                err_width, err_height = err_surface.get_size()
                err_x = WIDTH // 2 - err_width // 2

                shadow_surface = input_font.render(err_text, True, (100, 0, 0))
                text_surface.blit(shadow_surface, (err_x + random.randint(-4, 4), label_y + random.randint(-4, 4)))

                block_height = 5
                for i in range(0, err_height, block_height):
                    block_rect = pygame.Rect(0, i, err_width, block_height)
                    glitch_x = random.randint(-8, 8)
                    glitch_y = random.randint(-4, 4)
                    text_surface.blit(err_surface, (err_x + glitch_x, label_y + i + glitch_y), block_rect)

                glitch_rect_color = (random.randint(150, 255), 0, 0)
                pygame.draw.rect(text_surface, glitch_rect_color, input_box.move(random.randint(-5, 5), random.randint(-5, 5)), 2)

                if random.random() > 0.7:
                    flicker_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    flicker_surface.fill((255, 0, 0, random.randint(10, 50)))
                    text_surface.blit(flicker_surface, (0, 0))
            else:
                prefix_text = "> "
                prefix_width, _ = input_font.size(prefix_text)
                prefix_x = input_box.x - prefix_width
                
                shadow_prefix = input_font.render(prefix_text, True, (0, 100, 0))
                text_surface.blit(shadow_prefix, (prefix_x + 2, label_y + 2))
                prefix_surface = input_font.render(prefix_text, True, (0, 255, 0))
                text_surface.blit(prefix_surface, (prefix_x, label_y))

                main_label_x = input_box.x + (input_box.width - label_width) // 2

                shadow_label = input_font.render(label_text, True, (0, 100, 0))
                text_surface.blit(shadow_label, (main_label_x + 2, label_y + 2))
                label_surface = input_font.render(label_text, True, (0, 255, 0))
                text_surface.blit(label_surface, (main_label_x, label_y))

            if error_timer <= now:
                pw_char_width, _ = password_font.size("●")
                space_for_chars = input_box.width - 20
                visible_char_limit = min(int(space_for_chars / pw_char_width), 35) if pw_char_width > 0 else 35
                display_password = password[-visible_char_limit:] if len(password) > visible_char_limit else password
                pw_text = "●" * len(display_password)
                pw_width, _ = password_font.size(pw_text)
                text_x = input_box.x + 10
                text_y = input_box.y + 9
                shadow_surface = password_font.render(pw_text, True, (0, 100, 0))
                text_surface.blit(shadow_surface, (text_x + 2, text_y + 2))
                password_surface = password_font.render(pw_text, True, (0, 255, 0))
                text_surface.blit(password_surface, (text_x, text_y))

                if now - cursor_timer > 0.5:
                    cursor_visible = not cursor_visible
                    cursor_timer = now
                if cursor_visible:
                    cursor_pos = (text_x + pw_width, text_y)
                    pygame.draw.line(text_surface, (0, 255, 0), cursor_pos, (cursor_pos[0], cursor_pos[1] + input_box_height - 24), 2)
            
            text_surface.set_alpha(text_alpha)
            screen.blit(text_surface, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)
    
    return authenticated

if __name__ == '__main__':
    print("Avvio dell'effetto Matrix...")
    authenticated = run_matrix_effect(None)
    
    if authenticated:
        print("Autenticazione riuscita! Avvio del programma principale...")
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            main_program_path = os.path.join(current_dir, "main.py")
            
            print(f"Tentativo di avviare: {main_program_path}")
            
            subprocess.Popen(["python", main_program_path])
            
        except FileNotFoundError:
            print("ERRORE CRITICO: Impossibile trovare il file 'main.py' al percorso specificato.")
        except Exception as e:
            print(f"ERRORE: Si è verificato un problema durante l'avvio del programma principale: {e}")
            
    else:
        print("Autenticazione fallita o chiusa. Il programma principale non verrà avviato.")
    
    pygame.quit()
    sys.exit()