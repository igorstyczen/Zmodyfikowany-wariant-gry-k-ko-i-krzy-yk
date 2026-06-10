import tkinter as tk
from tkinter import messagebox
import math
import random

# =========================================================
# ZMODYFIKOWANY WARIANT GRY KOLKO I KRZYZYK
# Plansza: 4x4
# Warunek zwyciestwa: 3 znaki w jednej linii
# AI: Minimax + alfa-beta pruning + funkcja heurystyczna
# Dodatkowa zasada: wybrany rozpoczynajacy wykonuje 2 pierwsze ruchy
# =========================================================

BOARD_SIZE = 4
WIN_LENGTH = 3
HUMAN = "X"
AI = "O"
EMPTY = ""

DIFFICULTY_LEVELS = {
    "Latwy": 1,
    "Sredni": 3,
    "Trudny": 5
}

STARTERS = ["Gracz", "Komputer"]
OPENING_MOVES = 2


class ModifiedTicTacToeAI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zmodyfikowane kolko i krzyzyk 4x4 - AI")
        self.root.resizable(False, False)

        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.buttons = []
        self.game_over = False
        self.game_started = False

        self.current_difficulty = tk.StringVar(value="Trudny")
        self.current_starter = tk.StringVar(value="Gracz")

        self.turn = HUMAN
        self.opening_phase = False
        self.opening_player = None
        self.opening_moves_done = 0

        self.move_number = 0
        self.history_lines = []

        self.create_interface()
        self.disable_all_buttons()

    def create_interface(self):
        title = tk.Label(
            self.root,
            text="Zmodyfikowane kolko i krzyzyk 4x4",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        description = tk.Label(
            self.root,
            text="Plansza 4x4 | Wygrana: 3 znaki w linii | Startujacy wykonuje 2 pierwsze ruchy",
            font=("Arial", 10)
        )
        description.pack(pady=5)

        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=5)

        tk.Label(options_frame, text="Poziom:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        difficulty_menu = tk.OptionMenu(options_frame, self.current_difficulty, *DIFFICULTY_LEVELS.keys())
        difficulty_menu.config(font=("Arial", 10), width=8)
        difficulty_menu.grid(row=0, column=1, padx=5)

        tk.Label(options_frame, text="Zaczyna:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        starter_menu = tk.OptionMenu(options_frame, self.current_starter, *STARTERS)
        starter_menu.config(font=("Arial", 10), width=9)
        starter_menu.grid(row=0, column=3, padx=5)

        self.start_button = tk.Button(
            options_frame,
            text="Start gry",
            font=("Arial", 10, "bold"),
            command=self.start_game
        )
        self.start_button.grid(row=0, column=4, padx=8)

        board_frame = tk.Frame(self.root)
        board_frame.pack(pady=10)

        for row in range(BOARD_SIZE):
            button_row = []
            for col in range(BOARD_SIZE):
                button = tk.Button(
                    board_frame,
                    text="",
                    font=("Arial", 24, "bold"),
                    width=4,
                    height=2,
                    command=lambda r=row, c=col: self.human_move(r, c)
                )
                button.grid(row=row, column=col, padx=3, pady=3)
                button_row.append(button)
            self.buttons.append(button_row)

        self.status_label = tk.Label(
            self.root,
            text="Wybierz opcje i kliknij Start gry",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(pady=5)

        reset_button = tk.Button(
            self.root,
            text="Nowa gra",
            font=("Arial", 11),
            command=self.reset_game
        )
        reset_button.pack(pady=5)

        history_label = tk.Label(self.root, text="Historia ruchow:", font=("Arial", 10, "bold"))
        history_label.pack(pady=(8, 0))

        self.history_box = tk.Text(self.root, width=55, height=8, state="disabled", font=("Consolas", 9))
        self.history_box.pack(pady=(0, 10))

    def start_game(self):
        if self.game_started:
            return

        self.game_started = True
        self.game_over = False
        self.opening_phase = True
        self.opening_moves_done = 0
        self.start_button.config(state="disabled")

        starter = self.current_starter.get()

        if starter == "Gracz":
            self.opening_player = HUMAN
            self.turn = HUMAN
            self.enable_empty_buttons()
            self.status_label.config(text="Zaczyna gracz: wykonaj ruch 1/2")
            self.add_history("Start: gracz wykonuje 2 pierwsze ruchy.")
        else:
            self.opening_player = AI
            self.turn = AI
            self.disable_all_buttons()
            self.status_label.config(text="Zaczyna komputer: ruch 1/2")
            self.add_history("Start: komputer wykonuje 2 pierwsze ruchy.")
            self.root.after(400, self.ai_opening_move)

    def human_move(self, row, col):
        if self.game_over or not self.game_started:
            return

        if self.turn != HUMAN:
            return

        if self.board[row][col] != EMPTY:
            return

        self.place_move(row, col, HUMAN)

        if self.check_game_end():
            return

        if self.opening_phase and self.opening_player == HUMAN:
            self.opening_moves_done += 1

            if self.opening_moves_done < OPENING_MOVES:
                self.status_label.config(text=f"Zaczyna gracz: wykonaj ruch {self.opening_moves_done + 1}/2")
                return

            self.opening_phase = False
            self.turn = AI
            self.disable_all_buttons()
            self.status_label.config(text="Ruch komputera.")
            self.root.after(400, self.ai_move)
            return

        self.turn = AI
        self.disable_all_buttons()
        self.status_label.config(text="Ruch komputera.")
        self.root.after(400, self.ai_move)

    def ai_opening_move(self):
        if self.game_over or not self.game_started:
            return

        move = self.find_best_move(self.get_current_depth())

        if move is not None:
            row, col = move
            self.place_move(row, col, AI)

        if self.check_game_end():
            return

        self.opening_moves_done += 1

        if self.opening_moves_done < OPENING_MOVES:
            self.status_label.config(text=f"Zaczyna komputer: ruch {self.opening_moves_done + 1}/2")
            self.root.after(400, self.ai_opening_move)
            return

        self.opening_phase = False
        self.turn = HUMAN
        self.enable_empty_buttons()
        self.status_label.config(text="Twoj ruch")

    def ai_move(self):
        if self.game_over or not self.game_started:
            return

        difficulty = self.current_difficulty.get()

        if difficulty == "Latwy" and random.random() < 0.45:
            move = self.get_random_move()
        else:
            move = self.find_best_move(self.get_current_depth())

        if move is not None:
            row, col = move
            self.place_move(row, col, AI)

        if not self.check_game_end():
            self.turn = HUMAN
            self.enable_empty_buttons()
            self.status_label.config(text="Twoj ruch")

    def place_move(self, row, col, player):
        self.board[row][col] = player
        self.buttons[row][col].config(text=player, state="disabled")
        self.move_number += 1
        player_name = "Gracz" if player == HUMAN else "Komputer"
        self.add_history(f"{self.move_number}. {player_name} ({player}) -> wiersz {row + 1}, kolumna {col + 1}")

    def get_current_depth(self):
        return DIFFICULTY_LEVELS[self.current_difficulty.get()]

    def find_best_move(self, depth):
        best_score = -math.inf
        best_moves = []

        for row, col in self.get_candidate_moves():
            self.board[row][col] = AI
            score = self.minimax(depth - 1, False, -math.inf, math.inf)
            self.board[row][col] = EMPTY

            if score > best_score:
                best_score = score
                best_moves = [(row, col)]
            elif score == best_score:
                best_moves.append((row, col))

        if best_moves:
            return random.choice(best_moves)

        return self.get_random_move()

    def minimax(self, depth, is_maximizing, alpha, beta):
        winner = self.check_winner()

        if winner == AI:
            return 100000 + depth
        if winner == HUMAN:
            return -100000 - depth
        if self.is_draw():
            return 0
        if depth == 0:
            return self.evaluate_board()

        moves = self.get_candidate_moves()

        if is_maximizing:
            best_score = -math.inf

            for row, col in moves:
                self.board[row][col] = AI
                score = self.minimax(depth - 1, False, alpha, beta)
                self.board[row][col] = EMPTY

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)

                if beta <= alpha:
                    break

            return best_score

        best_score = math.inf

        for row, col in moves:
            self.board[row][col] = HUMAN
            score = self.minimax(depth - 1, True, alpha, beta)
            self.board[row][col] = EMPTY

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_score

    def evaluate_board(self):
        score = 0

        for line in self.get_all_possible_lines():
            score += self.evaluate_line(line)

        # W planszy 4x4 nie ma jednego srodka, dlatego premiowane sa 4 pola centralne.
        central_fields = [(1, 1), (1, 2), (2, 1), (2, 2)]
        for row, col in central_fields:
            if self.board[row][col] == AI:
                score += 8
            elif self.board[row][col] == HUMAN:
                score -= 8

        return score

    def evaluate_line(self, line):
        ai_count = line.count(AI)
        human_count = line.count(HUMAN)
        empty_count = line.count(EMPTY)

        if ai_count > 0 and human_count > 0:
            return 0

        if ai_count == 3:
            return 100000
        if ai_count == 2 and empty_count == 1:
            return 1000
        if ai_count == 1 and empty_count == 2:
            return 50

        if human_count == 3:
            return -100000
        if human_count == 2 and empty_count == 1:
            return -1200
        if human_count == 1 and empty_count == 2:
            return -50

        return 0

    def get_candidate_moves(self):
        occupied = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] != EMPTY:
                    occupied.append((row, col))

        if not occupied:
            return [(1, 1), (1, 2), (2, 1), (2, 2)]

        candidates = set()

        for row, col in occupied:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    new_row = row + dr
                    new_col = col + dc

                    if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                        if self.board[new_row][new_col] == EMPTY:
                            candidates.add((new_row, new_col))

        if not candidates:
            return self.get_all_empty_fields()

        return list(candidates)

    def get_random_move(self):
        empty_fields = self.get_all_empty_fields()
        if empty_fields:
            return random.choice(empty_fields)
        return None

    def get_all_empty_fields(self):
        empty_fields = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == EMPTY:
                    empty_fields.append((row, col))
        return empty_fields

    def get_all_possible_lines(self):
        lines = []

        # Poziomo
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE - WIN_LENGTH + 1):
                lines.append([self.board[row][col + i] for i in range(WIN_LENGTH)])

        # Pionowo
        for row in range(BOARD_SIZE - WIN_LENGTH + 1):
            for col in range(BOARD_SIZE):
                lines.append([self.board[row + i][col] for i in range(WIN_LENGTH)])

        # Przekatna: lewa gora -> prawy dol
        for row in range(BOARD_SIZE - WIN_LENGTH + 1):
            for col in range(BOARD_SIZE - WIN_LENGTH + 1):
                lines.append([self.board[row + i][col + i] for i in range(WIN_LENGTH)])

        # Przekatna: prawa gora -> lewy dol
        for row in range(BOARD_SIZE - WIN_LENGTH + 1):
            for col in range(WIN_LENGTH - 1, BOARD_SIZE):
                lines.append([self.board[row + i][col - i] for i in range(WIN_LENGTH)])

        return lines

    def check_winner(self):
        for line in self.get_all_possible_lines():
            if line.count(HUMAN) == WIN_LENGTH:
                return HUMAN
            if line.count(AI) == WIN_LENGTH:
                return AI
        return None

    def is_draw(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == EMPTY:
                    return False
        return True

    def check_game_end(self):
        winner = self.check_winner()

        if winner == HUMAN:
            self.game_over = True
            self.status_label.config(text="Wygral gracz!")
            messagebox.showinfo("Koniec gry", "Wygrales z komputerem!")
            self.disable_all_buttons()
            return True

        if winner == AI:
            self.game_over = True
            self.status_label.config(text="Wygral komputer!")
            messagebox.showinfo("Koniec gry", "Komputer wygral!")
            self.disable_all_buttons()
            return True

        if self.is_draw():
            self.game_over = True
            self.status_label.config(text="Remis!")
            messagebox.showinfo("Koniec gry", "Remis!")
            self.disable_all_buttons()
            return True

        return False

    def enable_empty_buttons(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == EMPTY:
                    self.buttons[row][col].config(state="normal")
                else:
                    self.buttons[row][col].config(state="disabled")

    def disable_all_buttons(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.buttons[row][col].config(state="disabled")

    def add_history(self, text):
        self.history_lines.append(text)
        self.history_box.config(state="normal")
        self.history_box.insert(tk.END, text + "\n")
        self.history_box.see(tk.END)
        self.history_box.config(state="disabled")

    def reset_game(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.game_over = False
        self.game_started = False
        self.opening_phase = False
        self.opening_player = None
        self.opening_moves_done = 0
        self.turn = HUMAN
        self.move_number = 0
        self.history_lines = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.buttons[row][col].config(text="", state="disabled")

        self.history_box.config(state="normal")
        self.history_box.delete("1.0", tk.END)
        self.history_box.config(state="disabled")

        self.start_button.config(state="normal")
        self.status_label.config(text="Wybierz opcje i kliknij Start gry")


if __name__ == "__main__":
    root = tk.Tk()
    app = ModifiedTicTacToeAI(root)
    root.mainloop()
