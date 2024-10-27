"""
The public display.
"""
import tkinter as tk
from tkinter import font as tf

from millionaire import Joker, Question
from millionaire.display import MillionaireView, ColorTheme
from millionaire.question import DUMMY_QUESTION


class PublicScreen(MillionaireView, tk.Tk):
    FONT_FAMILY = "Luciole"
    FONT_SIZE_NORMAL = 24
    FONT_SIZE_JOKERS = 20
    FONT_SIZE_WINNINGS = 16
    QUEST_WRAP_LEN = 76
    DFT_FRAME_KWS = dict(font=(FONT_FAMILY, FONT_SIZE_NORMAL, tf.ITALIC), bg=ColorTheme["bg"])
    DFT_WIDGET_KWS = (DFT_FRAME_KWS |
                      dict(font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                           justify=tk.LEFT))
    PAD = 8
    DFT_GRID_KWS = dict(sticky="nsew", padx=PAD, pady=PAD)

    def __init__(self, game, *args, **kwargs):
        MillionaireView.__init__(self, game)
        tk.Tk.__init__(self, *args, **kwargs)
        self.title(self._ts("public_screen_title"))
        self.config(bg=self.DFT_WIDGET_KWS["bg"])
        self.minsize(1280, 720)
        self._init_frames()

    @staticmethod
    def _create_expand_frame(master: tk.Widget):
        return tk.Frame(master, bg=ColorTheme["bg"])

    def _init_frames(self):
        self._main_frame = self._create_expand_frame(self)
        quest = self._create_quest_frame()
        self.show_question()
        jokers = self._create_jokers_frame()
        wins = self._create_winnings_frame()
        quest.grid(column=0, row=0, **self.DFT_GRID_KWS)
        jokers.grid(column=0, row=1, **self.DFT_GRID_KWS)
        wins.grid(column=1, row=0, rowspan=2, **self.DFT_GRID_KWS)
        self._main_frame.pack(expand=True)

    def _create_label_frame(self, text, master: tk.Widget = None, **kwargs) -> tk.LabelFrame:
        mast = self._main_frame if master is None else master
        return tk.LabelFrame(mast, text=self._ts(text), **(self.DFT_FRAME_KWS | kwargs))

    def _create_quest_frame(self):
        frame = self._create_label_frame("question")

        expf = self._create_expand_frame(frame)
        self._quest = tk.StringVar(expf)
        kws = self.DFT_WIDGET_KWS | dict(anchor="c")
        quest_label = tk.Label(expf, textvariable=self._quest, **kws)
        quest_label.grid(column=0, columnspan=2, **self.DFT_GRID_KWS)

        self._answs, self._answ_btns = [], []
        kws["anchor"] = "w"
        for i in range(4):
            self._answs.append(tk.StringVar(expf))
            kws["highlightbackground"] = ColorTheme["base"]
            button = tk.Button(expf, textvariable=self._answs[i], **kws)
            r, c = divmod(i, 2)
            button.grid(column=c, row=1 + r, **self.DFT_GRID_KWS)
            self._answ_btns.append(button)

        self._qtimecv, self._qtimerect = self._create_timebar(expf)
        self._qtimecv.grid(column=3, row=1, rowspan=2, **self.DFT_GRID_KWS)

        expf.pack(expand=True)
        return frame

    def _create_timebar(self, master: tk.Widget, vertical: bool = True):
        width, height = 240, 2 * self.PAD
        if vertical:
            width, height = height, width
        canvas = tk.Canvas(master, width=width, height=height, bg=ColorTheme["bg"])
        fill = 2 ** 16  # Safely large value for filling
        rectangle = canvas.create_rectangle(0, fill, fill, fill)
        return canvas, rectangle

    def _update_timebar(self, canvas: tk.Canvas, rectangle, progress):
        color = "altbase" if progress < 2 / 3 else "warning" if progress < 1 else "error"
        coords = canvas.coords(rectangle)
        coords[1] = (1 - progress) * canvas.winfo_reqheight()
        canvas.itemconfig(rectangle, fill=ColorTheme[color])
        canvas.coords(rectangle, *coords)

    def update_question_timer(self):
        progress = self.game.question_time_progress
        self._update_timebar(self._qtimecv, self._qtimerect, progress)

    def update_joker_timer(self):
        progress = self.game.joker_time_progress
        self._update_timebar(self._joktimecv, self._joktimerect, progress)

    def _create_jokers_frame(self):
        frame = self._create_label_frame("jokers")
        expf = self._create_expand_frame(frame)
        subwids = [self._create_label_frame("classical", expf),
                   self._create_label_frame("additional", expf)]

        self._joker_btns = {}
        kws = self.DFT_WIDGET_KWS.copy()
        kws.update(anchor="w", highlightbackground=ColorTheme["base"], font=(self.FONT_FAMILY, self.FONT_SIZE_JOKERS))
        for i, joker in enumerate(Joker):
            column, row = divmod(i, 3)
            text = " ".join(["", self._ts(joker, "icon"), self._ts(joker)])
            button = tk.Button(subwids[column], text=text, **kws)
            button.grid(column=0, row=row, **self.DFT_GRID_KWS)
            self._joker_btns[joker] = button

        self._joktimecv, self._joktimerect = self._create_timebar(expf)

        subwids.insert(1, self._joktimecv)
        for column, subframe in enumerate(subwids):
            subframe.grid(column=column, row=0, **self.DFT_GRID_KWS)

        expf.pack(expand=True)
        return frame

    def _create_winnings_frame(self):
        frame = self._create_label_frame("winnings")
        expf = self._create_expand_frame(frame)

        self._win_btns = []
        ind_kws = self.DFT_WIDGET_KWS | dict(anchor="c", width=1)
        win_kws = self.DFT_WIDGET_KWS | dict(anchor="w")
        ind_kws["font"] = win_kws["font"] = (self.FONT_FAMILY, self.FONT_SIZE_WINNINGS)

        game = self.game
        unit = game.winnings_unit
        pyramid = game.winnings_pyramid
        row = len(pyramid)
        for i, win in enumerate(pyramid):
            row -= 1
            ind_kws["highlightbackground"] = win_kws["fg"] = self._win_btn_color(i)

            ind_btn = tk.Button(expf, text=str(i + 1).rjust(2), **ind_kws)
            ind_btn.grid(column=0, row=row, **self.DFT_GRID_KWS)
            self._win_btns.append(ind_btn)

            win_btn = tk.Label(expf, text=self.format_num(win, unit), **win_kws)
            win_btn.grid(column=1, row=row, **self.DFT_GRID_KWS)

        expf.pack(expand=True)
        return frame

    def _win_btn_color(self, index):
        mstones = self.game.milestones
        if index in mstones.safe_nets:
            stage = "safe_net"
        else:
            stage = mstones.stage(index).name.lower()
        return ColorTheme["winnings"][stage]

    @staticmethod
    def wrap_text(text: str, length: int):
        lines = []
        line = ""
        split = []
        for word in text.split():
            if word in ".,:;?!":
                split[-1] += " " + word
            else:
                split.append(word)
        for word in split:
            if len(line) + len(word) > length:
                lines.append(line)
                line = ""
            line += " " + word
        lines.append(line)
        return "\n".join(lines)

    def show_question(self, n_answers: int = 4):
        quest = self.game.question
        if quest is None:
            n_answers = 4
            quest = DUMMY_QUESTION[self.lang]

        text = self.wrap_text(quest, self.QUEST_WRAP_LEN) if n_answers >= 0 else ""
        self._quest.set(text)
        self._show_answers(quest, n_answers)

        for i in self.game.joker_indices:
            self._answ_btns[i].config(state=tk.DISABLED)

        self.update_question_timer()

    def _show_answers(self, quest: Question, n_answers: int):
        kws = self.DFT_WIDGET_KWS.copy()
        for i, answ in enumerate(quest.mixed_answers):
            if n_answers > i:
                state = tk.NORMAL
            else:
                answ, state = " " * len(answ), tk.ACTIVE
            text = f" ◆ {chr(65 + i)}{self._ts(":")} {answ} "
            text = self.wrap_text(text, self.QUEST_WRAP_LEN // 2)
            self._answs[i].set(text)
            kws["highlightbackground"] = ColorTheme["base"]
            self._answ_btns[i].config(state=state, **kws)

    def ask_final_answer(self):
        for button in self._answ_btns:
            button.config(highlightbackground=ColorTheme["base"])
        button = self._answ_btns[self.game.final_answer_index]
        button.config(highlightbackground=ColorTheme["warning"])
        self.show_winnings(True)

    def reveal_answer(self):
        game = self.game
        colors = {game.final_answer_index: "error", game.question.right_index: "valid"}
        for i, color in colors.items():
            self._answ_btns[i].config(highlightbackground=ColorTheme[color])

    def show_jokers(self):
        for button in self._joker_btns.values():
            button.config(state=tk.DISABLED, highlightbackground=ColorTheme["base"])
        for joker in self.game.available_jokers:
            self._joker_btns[joker].config(state=tk.NORMAL)
        for joker in self.game.played_jokers:
            self._joker_btns[joker].config(state=tk.DISABLED, highlightbackground=ColorTheme["altbase"])

        self.update_joker_timer()

    def show_winnings(self, final_answer: bool = False):
        n = self.game.question_num
        config = [(self._win_btns[:n], tk.NORMAL, "valid"),
                  (self._win_btns[n:n + 1], tk.ACTIVE, "warning" if final_answer else "base"),
                  (self._win_btns[n + 1:], tk.DISABLED, "disabled")]
        for buttons, state, color in config:
            for button in buttons:
                button.config(state=state, highlightbackground=ColorTheme[color])

    def show(self, n_answers: int = 4):
        self.show_question(n_answers)
        self.show_jokers()
        self.show_winnings()

    def loss(self):
        current = self.game.question_num
        safe = self.game.safe_net
        if safe is None:
            safe = -1
        for i, button in enumerate(self._win_btns[:current + 1]):
            if i <= safe:
                color = "valid"
            elif i == current:
                color = "error"
            else:
                color = "base"
            self._win_btns[i].config(highlightbackground=ColorTheme[color])

    def walk_away(self):
        colors = ["altbase"]
        for button in self._answ_btns:
            button.config(highlightbackground=ColorTheme[colors[0]])
        if (n := self.game.question_num) > 0:
            colors.append("valid")
        for i, color in enumerate(colors):
            self._win_btns[n - i].config(highlightbackground=ColorTheme[color])
