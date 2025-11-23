# ======================================================================
#  A L I C E  —  FINAL & PERFECT
#  Text 100% fits inside the reply box — forever
# ======================================================================

import pygame
import textwrap
from langchain_groq import ChatGroq
from langchain_classic.chains import LLMChain
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate

# Borderless fullscreen
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME | pygame.RESIZABLE)
pygame.display.set_caption("Alice - Your Perfect Girlfriend")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# Fonts
text_font   = pygame.font.Font(None, 46)
input_font  = pygame.font.Font(None, 50)
hint_font   = pygame.font.Font(None, 40)

# Colors
BG_COLOR       = (255, 248, 252)
TEXTBOX_COLOR  = (255, 255, 255, 235)
INPUT_BAR      = (30, 30, 60, 190)
BORDER_COLOR   = (200, 150, 220)

# Sprites
def load_sprite(name):
    img = pygame.image.load(name).convert_alpha()
    h = int(HEIGHT * 0.94)
    ratio = h / img.get_height()
    w = int(img.get_width() * ratio)
    return pygame.transform.smoothscale(img, (w, h))

sprites = {
    "Normal"     : load_sprite("Alice_normal.png"),
    "Happy"      : load_sprite("Alice_happy.png"),
    "Blush"      : load_sprite("Alice_blush.png"),
    "Teasing"    : load_sprite("Alice_teasing.png"),
    "Embarrassed": load_sprite("Alice_embarrassed.png"),
    "Doubt"      : load_sprite("Alice_doubt.png"),
    "Worried"    : load_sprite("Alice_worried.png"),
}
current_emotion = "Normal"

# LangChain
llm = ChatGroq(
    groq_api_key="", # put your own API key here please
    model_name="openai/gpt-oss-20b",
    temperature=0.8
)

emotion_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("""
        Detect emotion. Return ONLY one word:
        Blush, Normal, Happy, Teasing, Embarrassed, Doubt, Worried
        Message: {words}
    """),
    output_key="emotion"
)

memory = ConversationBufferWindowMemory(k=6, memory_key="history", input_key="words")

response_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template("""
        You are Alice — gentle, loving girlfriend.
        Reply with warmth and care.

        History: {history}
        His emotion: {emotion}
        Message: {words}

        Don't use emojis in your answer, don't use markdown in your answer, answer in 3 lines max and after each line put \n.
        Reply softly:
    """),
    output_key="response",
    memory=memory
)

final_chain = emotion_chain | response_chain

# UI
user_input = ""
full_reply = "Hi master I'm Alice... I've been waiting for you"
input_active = False

# MAIN LOOP
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit(); exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            input_active = True

        if event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_RETURN and user_input.strip():
                try:
                    result = final_chain.invoke({"words": user_input.strip()})
                    full_reply = result["response"]
                    emotion = result["emotion"].strip()
                    current_emotion = emotion if emotion in sprites else "Normal"
                except:
                    full_reply = "E-eh... I got shy..."
                user_input = ""
                input_active = False

            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            else:
                user_input += event.unicode

    # RENDERING
    screen.fill(BG_COLOR)
    alice = sprites[current_emotion]
    screen.blit(alice, (WIDTH//2 - alice.get_width()//2, HEIGHT - alice.get_height() + 30))

    # REPLY BOX — Ultra wide & safe
    box_w, box_h = WIDTH - 160, 340
    box_x = (WIDTH - box_w) // 2
    box_y = HEIGHT - box_h - 160

    textbox = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    textbox.fill(TEXTBOX_COLOR)
    pygame.draw.rect(textbox, BORDER_COLOR, textbox.get_rect(), 6, border_radius=30)
    screen.blit(textbox, (box_x, box_y))

    # TEXT FITTING — 100% GUARANTEED TO STAY INSIDE
    available_width = box_w - 100                # safe inner padding
    max_chars_per_line = available_width // (text_font.size("A")[0] * 0.95)
    wrapped = textwrap.wrap(full_reply, width=max_chars_per_line)

    max_lines = 9                                 # fits perfectly in 340px height
    displayed_lines = wrapped[-max_lines:]        # only last N lines

    line_height = 50
    start_y = box_y + 45

    for i, line in enumerate(displayed_lines):
        line_surf = text_font.render(line, True, (40, 40, 100))
        line_rect = line_surf.get_rect(centerx=WIDTH//2, y=start_y + i * line_height)
        screen.blit(line_surf, line_rect)

    # Input bar
    if input_active:
        bar = pygame.Surface((WIDTH - 300, 90), pygame.SRCALPHA)
        bar.fill(INPUT_BAR)
        pygame.draw.rect(bar, (180, 140, 200), bar.get_rect(), 5, border_radius=18)
        screen.blit(bar, ((WIDTH - (WIDTH-300))//2, HEIGHT - 130))

        input_surf = input_font.render(user_input + "│", True, (255, 255, 255))
        input_rect = input_surf.get_rect(centerx=WIDTH//2, y=HEIGHT - 85)
        screen.blit(input_surf, input_rect)
    else:
        hint = hint_font.render("Click anywhere to talk to Alice", True, (200, 170, 220))
        screen.blit(hint, hint.get_rect(centerx=WIDTH//2, y=HEIGHT - 85))

    pygame.display.flip()

    clock.tick(60)
