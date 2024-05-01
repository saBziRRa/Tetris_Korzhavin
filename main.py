import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import pygame
from datetime import datetime

#Константы
FIELD_WIDTH = 10
FIELD_HEIGHT = 20
CELL_SIZE = 30
PREVIEW_SIZE = 5
PREVIEW_CELL_SIZE = 30
WHITE_CELL = "#ffffff"
SHAPES = [
    [[1, 1, 1, 1]],  #Палка
    [[1, 1], [1, 1]],  #Квадрат
    [[1, 0, 0], [1, 1, 1]],  #L
    [[0, 0, 1], [1, 1, 1]],  #L зеркальная
    [[1, 1, 0], [0, 1, 1]],  #Z
    [[0, 1, 1], [1, 1, 0]]   #Z зеркальная
]
COLORS = ['cyan', 'purple', 'red', 'green', 'yellow', 'blue', 'orange']

class Tetris:
    def __init__(self, master):
        pygame.mixer.init()
        self.master = master
        self.master.title("Tetris")
        self.background_image = Image.open("img/fon2.png")
        self.master.resizable(False, False)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_canvas = tk.Canvas(self.master, width=self.background_image.width, height=self.background_image.height)
        self.background_canvas.pack(fill="both", expand=True)
        self.background_canvas.create_image(0, 0, anchor="nw", image=self.background_photo)
        self.start_game_button = tk.Button(self.background_canvas, text="Начать игру", command=self.start_game, font=("Arial", 20), bg="lightgray", fg="black")
        self.start_game_button.pack(pady=200, padx=100)
        self.bottom_frame = tk.Frame(self.master)
        self.speed = 500
        self.line_clear_sound = pygame.mixer.Sound("sound/line_clear.wav")
        self.game_over_sound = pygame.mixer.Sound("sound/game_over.wav")
        self.master.bind('<Key>', self.start_game)
        self.master.focus_set()

    def start_game(self):
        pass

    def init_game(self):
        self.new_shape()
        self.next_shape = random.choice(SHAPES)
        self.move_down_auto()
        self.preview_canvas.config(bg="white")
        self.update_time()

    def show_remaining_time(self):
        self.remaining_time_label = tk.Label(self.frame, text="Оставшееся время:")
        self.remaining_time_label.pack(side=tk.TOP, pady=10)
        self.update_remaining_time()

    def update_remaining_time(self):
        remaining_time = 60 - (time.time() - self.start_time)
        self.remaining_time_label.config(text=f"Оставшееся время: {remaining_time:.2f} сек")
        if remaining_time <= 0:
            self.game_over = True
            self.canvas.create_text(FIELD_WIDTH * CELL_SIZE / 2, FIELD_HEIGHT * CELL_SIZE / 2, text="Time's up!",
                                    fill="red", font=("Helvetica", 40))
        else:
            self.remaining_time_label.config(
                text=f"Оставшееся время: {remaining_time:.2f} сек")
            self.remaining_time_id = self.master.after(100, self.update_remaining_time)

    def start_game(self, event=None):
        self.start_game_button.pack_forget()
        self.background_canvas.pack_forget()
        self.master.unbind('<Key>')
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        self.bottom_frame = tk.Frame(self.frame)
        self.bottom_frame.pack(side=tk.BOTTOM, pady=10)
        self.game_frame = tk.Frame(self.frame, width=FIELD_WIDTH * CELL_SIZE, height=FIELD_HEIGHT * CELL_SIZE)
        self.game_frame.pack(side=tk.LEFT)
        self.game_frame.config(bg="black")
        self.canvas = tk.Canvas(self.game_frame, width=FIELD_WIDTH * CELL_SIZE, height=FIELD_HEIGHT * CELL_SIZE, bg="white")
        self.canvas.pack()

        self.preview_frame = tk.Frame(self.frame)
        self.preview_frame.place(x=FIELD_WIDTH * CELL_SIZE + 20, y=200, width=PREVIEW_SIZE * PREVIEW_CELL_SIZE, height=PREVIEW_SIZE * PREVIEW_CELL_SIZE)
        self.preview_label = tk.Label(self.preview_frame, text="Следующая фигура:", font=("Helvetica", 11))
        self.preview_label.pack(side=tk.TOP, pady=5, padx=5)
        self.preview_canvas = tk.Canvas(self.preview_frame, width=PREVIEW_SIZE * PREVIEW_CELL_SIZE, height=PREVIEW_SIZE * PREVIEW_CELL_SIZE, bg="white")
        self.preview_canvas.pack(padx=5, pady=5)

        self.game_over = False
        self.game_paused = False
        self.next_shape = None
        self.field = [[WHITE_CELL for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
        self.score = 0
        self.start_time = time.time()

        self.restart_button = tk.Button(self.bottom_frame, text="Рестарт", command=self.restart_game, width=20)
        self.restart_button.pack(side=tk.LEFT, padx=10)
        self.pause_button = tk.Button(self.bottom_frame, text="Пауза", command=self.pause_game)
        self.pause_button.pack(side=tk.RIGHT, padx=10)
        self.time_label = tk.Label(self.frame, text="Итого времени: 0",font=("Helvetica", 20))
        self.time_label.pack(side=tk.TOP, padx=10, pady=10)
        self.score_label = tk.Label(self.bottom_frame, text="Счёт: 0",font=("Helvetica", 15))
        self.score_label.pack(side=tk.BOTTOM, padx=10, pady=10)


        self.init_game()
        self.load_high_scores()
        self.show_hints()

        self.master.bind("<Left>", self.move_left)
        self.master.bind("<Right>", self.move_right)
        self.master.bind("<Down>", self.move_down)
        self.master.bind("<Up>", self.rotate)
        self.master.bind("<space>", self.drop_shape)
        self.master.bind("<KeyPress-p>", self.pause_game)

    def save_high_score(self):
        current_score = self.score
        current_date = datetime.now().strftime("Y-m-d H:M:S")
        high_scores_path = "high_scores.txt"
        try:
            with open(high_scores_path, "r") as file:
                existing_records = file.readlines()
        except FileNotFoundError:
            existing_records = []

        with open(high_scores_path, "w") as file:
            new_records = []
            new_high_score = True

            for record in existing_records:
                score = int(record.split(", ")[0].split(": ")[1])
                if current_score > score:
                    new_records.append(f"рекорд: {current_score}, Date: {current_date}\n")
                    new_high_score = False
                else:
                    new_records.append(record)

            if new_high_score:
                new_records.append(f"рекорд: {current_score}, Date: {current_date}\n")

            file.writelines(new_records)

    def load_high_scores(self):
        try:
            with open("high_scores.txt", "r") as file:
                high_scores = file.readlines()

            if high_scores:
                valid_scores = []
                for line in high_scores:
                    try:
                        parts = line.strip().split(", ")
                        score_part = parts[0].split(": ")
                        score = int(score_part[1])
                        valid_scores.append((score, line.strip()))
                    except (IndexError, ValueError):
                        print(f"Пропускаем некорректную запись: {line.strip()}")

                if valid_scores:
                    max_score_record = max(valid_scores, key=lambda x: x[0])
                    self.max_score_label = tk.Label(self.frame, text=f"Максимальный {max_score_record[1]}")
                    self.max_score_label.pack(side=tk.TOP, pady=10)
                else:
                    self.max_score_label = tk.Label(self.frame, text="Допустимые записи отсутствуют")
                    self.max_score_label.pack(side=tk.TOP, pady=10)

            else:
                self.max_score_label = tk.Label(self.frame, text="Записи в файле рекордов отсутствуют")
                self.max_score_label.pack(side=tk.TOP, pady=10)

        except FileNotFoundError:
            self.max_score_label = tk.Label(self.frame, text="Файл рекордов не найден")
            self.max_score_label.pack(side=tk.TOP, pady=10)

    def restart_game(self):
        self.canvas.delete("all")
        self.score = 0
        self.score_label.config(text="Счёт: 0")
        self.time_label.config(text="Время: 0")
        self.field = [[WHITE_CELL for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
        self.start_time = time.time()
        self.game_over = False
        self.canvas.after_cancel(self.move_down_id)
        self.init_game()

    def pause_game(self, event=None):
        if self.game_paused:
            self.game_paused = False
            self.move_down_auto()
        else:
            self.game_paused = True
            self.master.bind("<KeyPress-p>", self.pause_game)

    def new_shape(self):
        self.shape = self.next_shape or random.choice(SHAPES)
        self.next_shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.shape_position = (0, FIELD_WIDTH // 2 - len(self.shape[0]) // 2)
        if self.check_collision(self.shape_position, self.shape):
            self.game_over = True
            print("Игра окончена! Твой счёт:", self.score)
            self.canvas.create_text(FIELD_WIDTH * CELL_SIZE / 2, FIELD_HEIGHT * CELL_SIZE / 2, text="Game Over!",
                                    fill="red", font=("Helvetica", 40))
        else:
            self.update()
            self.update_preview()

    def draw_grid(self):
        for i in range(FIELD_HEIGHT):
            for j in range(FIELD_WIDTH):
                if self.field[i][j] != WHITE_CELL:
                    self.draw_cell(i, j, self.field[i][j])
                else:
                    self.draw_cell(i, j, self.field[i][j])

    def draw_shape(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.draw_cell(i + self.shape_position[0], j + self.shape_position[1], self.color)

    def draw_cell(self, row, col, color, canvas=None, size=CELL_SIZE):
        if canvas is None:
            canvas = self.canvas
        x1 = col * size
        y1 = row * size
        x2 = x1 + size
        y2 = y1 + size
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def move_left(self, event):
        if not self.game_paused:
            new_pos = (self.shape_position[0], self.shape_position[1] - 1)
            if not self.check_collision(new_pos, self.shape):
                self.shape_position = new_pos
                self.update()

    def move_right(self, event):
        if not self.game_paused:
            new_pos = (self.shape_position[0], self.shape_position[1] + 1)
            if not self.check_collision(new_pos, self.shape):
                self.shape_position = new_pos
                self.update()

    def move_down(self, event=None):
        if not self.game_paused:
            new_pos = (self.shape_position[0] + 1, self.shape_position[1])
            if self.check_collision(new_pos, self.shape):
                self.lock_shape()
                self.new_shape()
            else:
                self.shape_position = new_pos
                self.update()

    def rotate(self, event):
        if not self.game_paused:
            rotated_shape = list(zip(*self.shape[::-1]))
            if not self.check_collision(self.shape_position, rotated_shape):
                self.shape = rotated_shape
                self.update()

    def drop_shape(self, event):
        if not self.game_paused:
            while not self.check_collision((self.shape_position[0] + 1, self.shape_position[1]), self.shape):
                self.shape_position = (self.shape_position[0] + 1, self.shape_position[1])
                self.update()
            self.lock_shape()
            self.new_shape()

    def check_collision(self, pos, shape):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    r, c = pos[0] + i, pos[1] + j
                    if r >= FIELD_HEIGHT or c < 0 or c >= FIELD_WIDTH or (r >= 0 and self.field[r][c] != WHITE_CELL):
                        return True
        return False

    def lock_shape(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.field[self.shape_position[0] + i][self.shape_position[1] + j] = self.color
        self.clear_lines()
        if self.game_over:
            self.game_over_sound.play()

    def clear_lines(self):
        cleared_lines = 0
        lines_deleted = True
        while lines_deleted:
            lines_deleted = False
            for i in range(len(self.field) - 1, -1, -1):
                if WHITE_CELL not in self.field[i]:
                    del self.field[i]
                    self.field.insert(0, [WHITE_CELL for _ in range(FIELD_WIDTH)])
                    cleared_lines += 1
                    lines_deleted = True
                    break
        self.score += cleared_lines * cleared_lines
        self.score_label.config(text=f"Счёт: {self.score}")
        self.line_clear_sound.play()

    def increase_speed(self):
        self.speed -= 50
        if self.speed < 100:
            self.speed = 100

    def decrease_speed(self):
        self.speed += 50

    def change_difficulty(self, level):
        if level == "easy":
            self.speed = 500
        elif level == "medium":
            self.speed = 300
        elif level == "hard":
            self.speed = 150

    def show_hints(self):
        self.hint_label = tk.Label(self.frame, text="Подсказка:")
        self.hint_label.pack(side=tk.BOTTOM, pady=10)
        self.update_hint()

    def play_background_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load("background_music.wav")
        pygame.mixer.music.play(-1)  #Цикл

    def play_sound_effect(self, sound):
        pygame.mixer.init()
        if sound == "line_clear":
            sound_effect = pygame.mixer.Sound("sound/line_clear.wav")
        elif sound == "game_over":
            sound_effect = pygame.mixer.Sound("sound/game_over.wav")
        sound_effect.play()

    def update_hint(self):
        hints = [
            "Используйте стрелки для перемещения фигуры",
            "Нажмите Пробел для ускоренного падения фигуры",
            "Нажмите P для паузы/возобновления игры",
            "Чем выше счёт, тем быстрее падают фигуры",
            "Очистите ряды для получения очков"
        ]
        self.hint_label.config(text=f"Подсказка: {random.choice(hints)}")
        self.hint_id = self.master.after(5000, self.update_hint)

    def move_down_auto(self):
        if not self.game_over and not self.game_paused:
            self.move_down()
            self.move_down_id = self.master.after(500, self.move_down_auto)

    def update_preview(self):
        self.preview_canvas.delete("all")
        next_shape = self.next_shape
        offset_x = (PREVIEW_SIZE - len(next_shape[0])) // 1.1
        offset_y = (PREVIEW_SIZE - len(next_shape)) // 3
        for i, row in enumerate(next_shape):
            for j, cell in enumerate(row):
                if cell:
                    color = self.color
                    self.draw_cell(i + offset_y, j + offset_x, color, self.preview_canvas, PREVIEW_CELL_SIZE)

    def update_time(self):
        elapsed_time = round(time.time() - self.start_time)
        self.time_label.config(text=f"Итого времени: {elapsed_time} сек")

    def update(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_shape()
        self.update_preview()
        self.update_time()

if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
    
