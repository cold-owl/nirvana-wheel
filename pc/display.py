
import pygame
import math
import time

WIDTH, HEIGHT = 1100, 700
FPS = 60

BG = (12, 15, 27)
GOLD = (232, 190, 100)
WHITE = (245, 240, 225)

PATHS = {
    "green": {
        "name": "RIGHT VIEW",
        "description": "See the world with clarity and wisdom.",
        "color": (35, 190, 100),
    },
    "blue": {
        "name": "RIGHT INTENTION",
        "description": "Cultivate thoughts of kindness and goodwill.",
        "color": (55, 135, 245),
    },
    "yellow": {
        "name": "RIGHT SPEECH",
        "description": "Speak truthfully, kindly and meaningfully.",
        "color": (245, 205, 55),
    },
    "red": {
        "name": "RIGHT ACTION",
        "description": "Act with compassion and do no harm.",
        "color": (225, 65, 65),
    },
    "violet": {
        "name": "RIGHT LIVELIHOOD",
        "description": "Choose a way of life that does not harm others.",
        "color": (155, 85, 220),
    },
    "purple": {
        "name": "RIGHT CONCENTRATION",
        "description": "Develop deep focus and mental stillness.",
        "color": (105, 65, 190),
    },
    "orange": {
        "name": "RIGHT MINDFULNESS",
        "description": "Be aware of the present moment.",
        "color": (245, 135, 40),
    },
    "brown": {
        "name": "RIGHT EFFORT",
        "description": "Build good qualities and overcome harmful ones.",
        "color": (145, 90, 55),
    },
}

ORDER = list(PATHS.keys())

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nirvana Wheel")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("georgia", 42, bold=True)
font_subtitle = pygame.font.SysFont("georgia", 22)
font_path = pygame.font.SysFont("georgia", 42, bold=True)
font_desc = pygame.font.SysFont("arial", 23)
font_small = pygame.font.SysFont("arial", 17)


def draw_text(text, font, color, center):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))


def draw_background():
    screen.fill(BG)

    for radius in (280, 295, 310):
        pygame.draw.circle(
            screen, (55, 48, 39),
            (WIDTH // 2, 355), radius, 1
        )

    draw_text(
        "THE NIRVANA WHEEL",
        font_title, GOLD, (WIDTH // 2, 55)
    )

    draw_text(
        "Discover your path through the Dharma",
        font_subtitle, WHITE, (WIDTH // 2, 105)
    )


def draw_wheel(angle):
    cx, cy = WIDTH // 2, 355
    radius = 235
    segment = 2 * math.pi / len(ORDER)

    for i, key in enumerate(ORDER):
        start = angle + i * segment
        end = start + segment

        points = [(cx, cy)]

        for j in range(41):
            a = start + (end - start) * j / 40
            points.append((
                cx + math.cos(a) * radius,
                cy + math.sin(a) * radius
            ))

        pygame.draw.polygon(
            screen, PATHS[key]["color"], points
        )
        pygame.draw.polygon(screen, GOLD, points, 2)

        mid = (start + end) / 2
        text_pos = (
            cx + math.cos(mid) * radius * 0.67,
            cy + math.sin(mid) * radius * 0.67
        )

        label = font_small.render(key.upper(), True, WHITE)
        screen.blit(label, label.get_rect(center=text_pos))

    pygame.draw.circle(screen, GOLD, (cx, cy), 48)
    pygame.draw.circle(screen, BG, (cx, cy), 40)
    draw_text("DHARMA", font_small, GOLD, (cx, cy))

    # Fixed pointer on right side
    pygame.draw.polygon(
        screen, GOLD,
        [
            (cx + radius + 12, cy),
            (cx + radius + 38, cy - 17),
            (cx + radius + 38, cy + 17)
        ]
    )


def show_result(colour):
    colour = colour.lower().strip()

    if colour not in PATHS:
        print("Display does not recognise colour:", colour)
        return

    index = ORDER.index(colour)
    segment = 2 * math.pi / len(ORDER)

    # Segment centre must finish at the fixed right-hand pointer.
    target_angle = -(index + 0.5) * segment

    # Start from a random orientation and make several rotations.
    start_angle = target_angle + 2 * math.pi * 7 + 0.8
    final_angle = target_angle

    duration = 5.0
    start_time = time.monotonic()

    # Lottery spinning animation
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        elapsed = time.monotonic() - start_time
        progress = min(elapsed / duration, 1.0)

        eased = 1 - (1 - progress) ** 4
        angle = start_angle + (final_angle - start_angle) * eased

        draw_background()
        draw_wheel(angle)

        draw_text(
            "THE WHEEL IS REVEALING YOUR PATH...",
            font_subtitle, GOLD, (WIDTH // 2, 635)
        )

        pygame.display.flip()
        clock.tick(FPS)

        if progress >= 1:
            break

    # Result reveal
    result = PATHS[colour]
    reveal_start = time.monotonic()

    while time.monotonic() - reveal_start < 8:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        draw_background()

        pygame.draw.circle(
            screen, result["color"], (WIDTH // 2, 245), 48
        )
        pygame.draw.circle(
            screen, GOLD, (WIDTH // 2, 245), 58, 3
        )

        draw_text(
            "YOUR EIGHTFOLD PATH",
            font_subtitle, WHITE, (WIDTH // 2, 340)
        )

        draw_text(
            result["name"],
            font_path, result["color"], (WIDTH // 2, 410)
        )

        draw_text(
            result["description"],
            font_desc, WHITE, (WIDTH // 2, 480)
        )

        draw_text(
            "CARRY THIS WISDOM WITH YOU",
            font_small, GOLD, (WIDTH // 2, 565)
        )

        pygame.display.flip()
        clock.tick(FPS)
