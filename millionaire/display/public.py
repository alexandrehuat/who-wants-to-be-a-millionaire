"""
The public display.
"""
import tkinter as tk
from tkinter import font as tf

from millionaire import Joker, Question, QLevel
from millionaire.display import MillionaireWidget, Theme

DUMMY_QUESTION = Question(
    QLevel.EXTREME,
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum eleifend tortor vitae enim aliquet, at mollis dui ultricies. Proin ullamcorper risus ligula, non finibus erat tincidunt nec.",
    "Integer molestie ullamcorper neque sit amet fringilla.",
    "Aliquam ut arcu posuere, tempus magna sit amet, ullamcorper justo. Morbi purus lacus, luctus sit amet dictum tincidunt, fermentum in diam.",
    "Sed lacinia tortor rutrum, dictum sapien nec, maximus lorem.",
    "Cras vulputate nunc metus, vel porta nisi scelerisque at. Mauris quis quam vitae tortor feugiat finibus nec at sem. Nunc at convallis purus.",
    author="Julius Caesar",
)


class PublicScreen(MillionaireWidget, tk.Tk):
    FONT_FAMILY = "Luciole"
    FONT_SIZE = 24
    QUEST_WRAP_LEN = 76
    DFT_FRAME_KWS = dict(font=(FONT_FAMILY, FONT_SIZE, tf.ITALIC),
                         bg=Theme["color"]["bg"])
    DFT_WIDGET_KWS = (DFT_FRAME_KWS |
                      dict(font=(FONT_FAMILY, FONT_SIZE, tf.NORMAL),
                           anchor="w",
                           justify=tk.LEFT))
    PAD = 8
    DFT_GRID_KWS = dict(sticky="nsew", padx=PAD, pady=PAD)

    def __init__(self, game, *args, **kwargs):
        MillionaireWidget.__init__(self, game)
        tk.Tk.__init__(self, *args, **kwargs)
        self.title(self._ts("public_screen_title"))
        self.config(bg=self.DFT_WIDGET_KWS["bg"])
        self.minsize(1280, 720)
        self._init_frames()

    @staticmethod
    def _create_expand_frame(master: tk.Widget):
        return tk.Frame(master, bg=Theme["color"]["bg"])

    def _init_frames(self):
        self._main_frame = self._create_expand_frame(self)
        quest = self._create_quest_frame()
        self.show_question(_q=DUMMY_QUESTION)
        jokers = self._create_jokers_frame()
        wins = self._create_winnings_frame()
        quest.grid(column=0, row=0, **self.DFT_GRID_KWS)
        jokers.grid(column=0, row=1, **self.DFT_GRID_KWS)
        wins.grid(column=1, row=0, rowspan=2, **self.DFT_GRID_KWS)
        self._main_frame.pack(expand=True)

    def _create_top_label_frame(self, text, **kwargs) -> tk.LabelFrame:
        return tk.LabelFrame(self._main_frame, text=self._ts(text), **(self.DFT_FRAME_KWS | kwargs))

    def _create_quest_frame(self):
        frame = self._create_top_label_frame("question")

        expf = self._create_expand_frame(frame)
        self._quest = tk.StringVar(expf)
        kws = self.DFT_WIDGET_KWS.copy()
        quest_label = tk.Label(expf, textvariable=self._quest, **kws)
        quest_label.grid(column=0, columnspan=2, **self.DFT_GRID_KWS)

        self._answs, self._answ_btns = [], []
        for i in range(4):
            self._answs.append(tk.StringVar(expf))
            kws["highlightbackground"] = Theme["color"]["aql"][i]
            button = tk.Button(expf, textvariable=self._answs[i], **kws)
            r, c = divmod(i, 2)
            button.grid(column=c, row=1 + r, **self.DFT_GRID_KWS)
            self._answ_btns.append(button)
        expf.pack(expand=True)

        return frame

    def _create_jokers_frame(self):
        frame = self._create_top_label_frame("jokers")
        expf = self._create_expand_frame(frame)
        self._joker_btns = {}
        kws = self.DFT_WIDGET_KWS | dict(highlightbackground=Theme["color"]["altbase"])
        for i, joker in enumerate(Joker):
            text = " ".join(["", self._ts(joker, "icon"), self._ts(joker)])
            button = tk.Button(expf, text=text, **kws)
            c, r = divmod(i, 3)
            button.grid(column=c, row=r, **self.DFT_GRID_KWS)
            self._joker_btns[joker] = button
        expf.pack(expand=True)
        return frame

    def _create_winnings_frame(self):
        frame = self._create_top_label_frame("winnings")
        expf = self._create_expand_frame(frame)

        self._win_btns = []
        ind_kws = self.DFT_WIDGET_KWS | dict(anchor="e", width=1)
        win_kws = self.DFT_WIDGET_KWS | dict(anchor="w")

        game = self.game
        unit = game.winnings_unit
        pyramid = game.winnings_pyramid
        row = len(pyramid)
        bg_key = "highlightbackground"
        for i, win in enumerate(pyramid):
            row -= 1
            ind_kws[bg_key] = win_kws[bg_key] = self._win_btn_bg(i)

            ind_btn = tk.Button(expf, text=f"{i + 1} ", **ind_kws)
            ind_btn.grid(column=0, row=row, **self.DFT_GRID_KWS)
            self._win_btns.append(ind_btn)

            win_btn = tk.Button(expf, text=" " + self.format_num(win, unit), **win_kws)
            win_btn.grid(column=1, row=row, **self.DFT_GRID_KWS)

        expf.pack(expand=True)
        return frame

    def _win_btn_bg(self, index):
        mstones = self.game.milestones
        if index in mstones.safe_nets:
            bg = Theme["color"]["base"]
        else:
            stage = mstones.stage(index).name.lower()
            bg = Theme["color"]["winnings"][stage]
        return bg

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

    def show_question(self, *, _q: Question = None):
        quest = _q if _q is not None else self.game.question
        text = self.wrap_text(quest, self.QUEST_WRAP_LEN)
        self._quest.set(text)
        for i, answ in enumerate(quest.mixed_answers):
            text = f" ◆ {chr(65 + i)}. {answ} "
            text = self.wrap_text(text, self.QUEST_WRAP_LEN // 2)
            self._answs[i].set(text)
            self._answ_btns[i].config(**self.DFT_WIDGET_KWS, state=tk.NORMAL)
        for i in self.game.joker_indices:
            self._answ_btns[i].config(state=tk.DISABLED)

    def ask_final_answer(self):
        for button in self._answ_btns:
            button.config(highlightbackground=Theme["color"]["altbase"])
        button = self._answ_btns[self.game.final_answer_index]
        button.config(highlightbackground=Theme["color"]["warning"])

    def reveal_answer(self):
        game = self.game
        colors = {game.final_answer_index: "error", game.question.right_index: "valid"}
        for i, color in colors.items():
            self._answ_btns[i].config(highlightbackground=Theme["color"][color])

    def show_jokers(self):
        for button in self._joker_btns.values():
            button.config(state=tk.DISABLED)
        for joker in self.game.jokers:
            self._joker_btns[joker].config(state=tk.NORMAL)

    def show_winnings(self):
        n = self.game.question_num
        config = [(self._win_btns[:n], tk.NORMAL, Theme["color"]["valid"]),
                  (self._win_btns[n:n + 1], tk.ACTIVE, Theme["color"]["altbase"]),
                  (self._win_btns[n + 1:], tk.DISABLED, Theme["color"]["disabled"])]
        for buttons, state, bg in config:
            for button in buttons:
                button.config(state=state, highlightbackground=bg)

    def loss(self):
        try:
            button = self._win_btns[self.game.safe_net]
            button.config(highlightbackground=Theme["color"]["valid"])
        except TypeError:  # Safe net is none
            pass

    def walk_away(self):
        button = self._win_btns[self.game.question_num - 1]
        button.config(highlightbackground=Theme["color"]["valid"])
