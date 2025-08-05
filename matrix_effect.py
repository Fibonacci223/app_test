# --- Funzione effetto Matrix (modificata) ---
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
