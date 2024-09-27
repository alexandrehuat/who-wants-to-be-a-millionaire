"""
The animator's hidden terminal.
"""
import re
import tkinter as tk

from millionaire import QLevel, Stage, Joker
from millionaire.display import Theme, MillionaireWidget


class AnimationTerminal(MillionaireWidget, tk.Tk):
    PAD = 6

    DFT_WIDGET_KWS = dict(bg=Theme["color"].get("bg"), highlightbackground=Theme["color"].get("bg"))
    DFT_GRID_KWS = dict(sticky="nsew")

    def __init__(self, game, *args, **kwargs):
        MillionaireWidget.__init__(self, game)
        tk.Tk.__init__(self, *args, **kwargs)
        self.config(self.DFT_WIDGET_KWS)
        self.set_title()
        for name, height in [("min", 480), ("max", 720)]:
            width = int(16 / 9 * height)
            getattr(self, f"{name}size")(width, height)

    def set_title(self, widget: tk.Widget = None, ts_key: str = "app_title"):
        prefix = "".join(map(self._ts, ["millionaire_short", ":"]))
        if widget is None:
            widget = self
        widget.title(f'{prefix} {self._ts(ts_key)}')

    def _create_label_frame(self, master: tk.Widget, ts_key: str) -> tk.LabelFrame:
        return tk.LabelFrame(master, text=self._ts(ts_key), **self.DFT_WIDGET_KWS)

    def _create_button(self, master: tk.Widget, command: str,
                       prefix: str = "", suffix: str = "",
                       **kwargs) -> tk.Button:
        text = prefix + self._ts(command) + suffix
        kws = self.DFT_WIDGET_KWS | kwargs
        return tk.Button(master, text=text, command=getattr(self.game, command), **kws)

    def _new_page(self, goto_menu: bool = True) -> tk.Frame | tuple[tk.Frame, tk.Button]:
        self.clear()
        frame = tk.Frame(self, **self.DFT_WIDGET_KWS)
        frame.pack(expand=True)
        if goto_menu:
            button = self._create_button(frame, "main_menu")
            return frame, button
        return frame

    def _create_label(self, master: tk.Widget, ts_key: str, colon: bool = False, **kwargs) -> tk.Label:
        text = self._ts(ts_key)
        if colon:
            text += self._ts(":")
        return tk.Label(master, text=text, **(self.DFT_WIDGET_KWS | kwargs))

    def main_menu(self):
        frame = self._new_page(False)
        cmds = ["opening", "start_qualif", "start_round", "start_free_game", "closing", "toggle_lang"]
        for i, cmd in enumerate(cmds):
            button = self._create_button(frame, cmd)
            button.grid(column=0, row=i, **self.DFT_GRID_KWS)

    def update_lang(self):
        self.clear()
        self.main_menu()

    def start_qualif(self):
        frame, goto_menu = self._new_page(True)
        quest_frame = self._create_quest_frame(frame)

        for i, widget in enumerate([goto_menu, quest_frame]):
            widget.grid(column=0, row=i, **self.DFT_GRID_KWS)

    def _create_winnings_button(self, master: tk.Widget, index: int) -> tk.Button:
        win_str = self.format_num(self.game.winnings_pyramid[index], self.game.winnings_unit)
        text = f" {index + 1}. {win_str}"
        kws = self.DFT_WIDGET_KWS | dict(anchor="w")
        return tk.Button(master, text=text, command=lambda: self.game.set_question_num(index), **kws)

    def _create_winnings_frame(self, master: tk.Widget) -> tk.LabelFrame:
        frame = self._create_label_frame(master, "winnings_stake")
        self._win_btns = []
        mstones = self.game.milestones
        column, row = -1, 0
        old_stage = Stage.FIRST
        self._colspan = 0
        for i in range(mstones.end):
            button = self._create_winnings_button(frame, i)
            stage = mstones.stage(i)
            if stage != old_stage:
                old_stage = stage
                row += 1
                column = 0
            else:
                column += 1
                self._colspan = max(self._colspan, row)
            button.grid(column=column, row=row, **self.DFT_GRID_KWS)
            self._win_btns.append(button)
        return frame

    def _create_joker_button(self, master: tk.Widget, joker: Joker) -> tk.Button:
        text = self._ts(joker, "icon") + " " + self._ts(joker)
        return tk.Button(master, text=text, **self.DFT_WIDGET_KWS,
                         command=lambda: self.game.play_joker(joker))

    def _create_jokers_frame(self, master: tk.Widget) -> tk.LabelFrame:
        frame = self._create_label_frame(master, "jokers")
        self._joker_btns = {}
        factor = 3
        for i, joker in enumerate(Joker):
            button = self._create_joker_button(frame, joker)
            button.grid(column=i % factor, row=i // factor, **self.DFT_GRID_KWS)
            self._joker_btns[joker] = button
        return frame

    def update_winnings(self):
        n = self.game.question_num
        for i, button in enumerate(self._win_btns):
            button.config(highlightbackground=self.cget("bg"))
        self._win_btns[n].config(highlightbackground=Theme["color"]["base"])

    def update_jokers(self):
        for j, button in self._joker_btns.items():
            button.config(highlightbackground=Theme["color"]["bg"],
                          command=lambda j=j: self.game.restore_jokers(j))
        for j in self.game.jokers:
            button = self._joker_btns[j]
            button.config(highlightbackground=Theme["color"]["base"],
                          command=lambda j=j: self.game.play_joker(j))

    def _create_answer_button(self, master: tk.Widget, index: int):
        kws = self.DFT_WIDGET_KWS | dict(anchor="w", highlightbackground=Theme["color"]["base"])
        return tk.Button(master, textvariable=self._answs[index], **kws)

    def _create_quest_widgets(self, master: tk.Widget):
        self._quest = tk.StringVar(master)
        wraplen = 7 * self.winfo_width() // 8
        kws = self.DFT_WIDGET_KWS | dict(wraplength=wraplen, anchor="w", bg=Theme["color"]["base"])
        self._quest_label = tk.Label(master, textvariable=self._quest, **kws)
        self._answs, self._answ_btns = [], []
        for i in range(4):
            strvar = tk.StringVar(master)
            self._answs.append(strvar)
            button = self._create_answer_button(master, i)
            self._answ_btns.append(button)

    def _create_question_actions(self, master: tk.Widget) -> list[tk.Button]:
        buttons = []
        game = self.game
        qualif = game.in_qualif
        for text, color, cmd, disable in [
            ("switch_action", "bg", game.load_question, qualif),
            ("publish", "bg", game.publish_question, False),
            ("walk_away", "altbase", game.walk_away, qualif),
            ("next", "base", game.next_question, False)
        ]:
            kws = self.DFT_WIDGET_KWS | dict(highlightbackground=Theme["color"][color])
            state = tk.DISABLED if disable else tk.NORMAL
            button = tk.Button(master, text=self._ts(text), command=cmd, state=state, **kws)
            buttons.append(button)
        return buttons

    def _create_quest_frame(self, master: tk.Widget) -> tk.LabelFrame:
        frame = self._create_label_frame(master, "question")
        self._auth = tk.StringVar(frame)
        author = tk.Label(frame, textvariable=self._auth, anchor="w", **self.DFT_WIDGET_KWS)
        self._lvl = tk.StringVar(frame)
        level = tk.Label(frame, textvariable=self._lvl, anchor="w", **self.DFT_WIDGET_KWS)
        self._create_quest_widgets(frame)
        self._note = tk.StringVar(frame)
        note = tk.Label(frame, textvariable=self._note, anchor="w", **self.DFT_WIDGET_KWS)
        action_btns = self._create_question_actions(frame)

        kws = self.DFT_GRID_KWS | dict(columnspan=2)
        author.grid(column=0, row=0, **kws)
        level.grid(column=0, row=1, **kws)

        kws["pady"] = (self.PAD, 0)
        self._quest_label.grid(column=0, row=2, **kws)
        for i, button in enumerate(self._answ_btns):
            r, c = divmod(i, 2)
            button.grid(column=c, row=3 + r, **self.DFT_GRID_KWS)
        kws["pady"] = kws["pady"][::-1]
        note.grid(column=0, row=5, **kws)

        for i, button in enumerate(action_btns):
            r, c = divmod(i, 2)
            button.grid(column=c, row=6 + r, **self.DFT_GRID_KWS)

        return frame

    def start_round(self):
        frame, self._main_menu_btn = self._new_page()
        win_frame = self._create_winnings_frame(frame)
        self.update_winnings()
        quest_frame = self._create_quest_frame(frame)
        joker_frame = self._create_jokers_frame(frame)
        self.update_jokers()

        self._main_menu_btn.grid(column=0, row=0, **self.DFT_GRID_KWS)
        kws = self.DFT_GRID_KWS | dict(columnspan=self._colspan, pady=(self.PAD, 0))
        win_frame.grid(column=0, row=1, **kws)
        quest_frame.grid(column=0, row=2, **kws)
        joker_frame.grid(column=0, row=3, **kws)

    def load_question(self):
        if not self.game.in_qualif:
            self.update_winnings()
        self._load_quest_auth_lvl()
        self._load_answers()
        self._load_quest_note()

    def _load_answers(self):
        game = self.game
        quest = game.question
        color = Theme["color"]["disabled" if quest.level == QLevel.TRIVIAL else "base"]
        self._quest.set(quest)
        self._quest_label.config(bg=color)
        for i, answ in enumerate(quest.mixed_answers):
            self._answs[i].set(f" ◆ {chr(65 + i)}. {answ} ")
            cmd = lambda i=i: game.ask_final_answer(i)
            self._answ_btns[i].config(command=cmd, state=tk.NORMAL, highlightbackground=color)

    def _load_quest_auth_lvl(self):
        quest = self.game.question
        self._auth.set(f'{self._ts("author")}{self._ts(":")} {quest.author}')
        x, y, z = tuple(map(self._ts, ["level", ":", quest.level.name.lower()]))
        self._lvl.set(f'{x}{y} {z}')

    def _load_quest_note(self):
        if not (note := self.game.question.note):
            note = self._ts("no_data")
        self._note.set(f'{self._ts("note")}{self._ts(":")} {note}')

    def ask_final_answer(self):
        self._load_answers()  # Resets colors and commands if the player switches the answer choice
        game = self.game
        index = game.final_answer_index
        button = self._answ_btns[index]
        cmd = game.reveal_qualif if game.in_qualif else game.confirm_answer
        button.config(command=cmd, highlightbackground=Theme["color"]["warning"])

    def reveal_answer(self):
        game = self.game
        colors = {game.final_answer_index: "error", game.question.right_index: "valid"}
        for i, color in colors.items():
            self._answ_btns[i].config(highlightbackground=Theme["color"][color])

    def play_joker_fifty(self):
        for btn in self._answ_btns:
            btn.config(state=tk.NORMAL)
        for i in self.game.joker_indices:
            self._answ_btns[i].config(state=tk.DISABLED)

    def raise_exc(self, exc: Exception | type):
        type_name = type(exc).__name__
        if isinstance(exc, type):
            return self.raise_exc(exc())
        elif not isinstance(exc, Exception):
            raise TypeError(type_name)

        top = tk.Toplevel()
        metatype = "warning" if isinstance(exc, Warning) else "error"
        self.set_title(top, metatype)

        subtype = re.sub("Error|Warning$", "", type_name)
        text = self._ts(subtype)
        if msg := str(exc):
            text += f"\n\n{msg}"

        pad = 2 * self.PAD
        kws = self.DFT_WIDGET_KWS | dict(bg=Theme["color"][metatype], padx=pad, pady=pad)
        label = tk.Label(top, text=text, **kws)
        label.pack()
