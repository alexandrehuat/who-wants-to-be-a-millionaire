import re
import tkinter as tk

from millionaire import Stage, Joker
from millionaire.display import ColorTheme
from millionaire.display.animator import AnimationTerminal


def hlconf(color):
    return {key: color for key in ["bg", "highlightbackground"]}


STYLE = dict(background=ColorTheme["bg"])
LABEL_STYLE = STYLE | dict(anchor=tk.W)
BTN_STYLE = STYLE | hlconf(ColorTheme["bg"]) | dict(highlightthickness=2)
WIN_BTN_STYLE = BTN_STYLE | dict(anchor=tk.E)
QUEST_BTN_STYLE = BTN_STYLE | dict(anchor=tk.CENTER)
ANSW_BTN_STYLE = BTN_STYLE | dict(anchor=tk.W)
UNPUBLISHED_STYLE = hlconf(ColorTheme["disabled"])
PUBLISHED_STYLE = hlconf(ColorTheme["base"])
VALID_STYLE = hlconf(ColorTheme["valid"])
WARNING_STYLE = hlconf(ColorTheme["warning"])
ERROR_STYLE = hlconf(ColorTheme["error"])
AT_STAKE_STYLE = hlconf(ColorTheme["base"])
WALK_AWAY_STYLE = hlconf(ColorTheme["altbase"])

GRID_STYLE = dict(sticky=tk.NSEW)


class MillionaireTk(tk.Tk):
    def clear(self):
        for child in self.winfo_children():
            child.destroy()


class TkAnimationTerminal(AnimationTerminal, MillionaireTk):
    PAD = 6

    def __init__(self, game, *args, **kwargs):
        AnimationTerminal.__init__(self, game)
        MillionaireTk.__init__(self, *args, **kwargs)
        self.config(**STYLE)
        self._init_size()
        self._set_title()

    def _init_size(self):
        height = 720
        width = int(4 * height / 3)
        self.minsize(width, height)

    def _set_title(self, widget: tk.Widget = None, ts_key: str = "app_title"):
        prefix = "".join(map(self._ts, ["millionaire_short", ":"]))
        if widget is None:
            widget = self
        widget.title(f'{prefix} {self._ts(ts_key)}')

    def _create_label_frame(self, master: tk.Widget, ts_key: str) -> tk.LabelFrame:
        return tk.LabelFrame(master, text=self._ts(ts_key), **STYLE)

    def _create_button(self, master: tk.Widget, command: str, prefix: str = "", suffix: str = "") -> tk.Button:
        text = prefix + self._ts(command) + suffix
        return tk.Button(master, text=text, command=getattr(self.game, command), **BTN_STYLE)

    def _new_page(self, goto_menu: bool = True) -> tk.Frame | tuple[tk.Frame, tk.Button]:
        self.clear()
        frame = tk.Frame(self, **STYLE)
        frame.pack(expand=True)
        if goto_menu:
            button = self._create_button(frame, "main_menu")
            return frame, button
        return frame

    def _create_label(self, master: tk.Widget, ts_key: str, colon: bool = False, **kwargs) -> tk.Label:
        text = self._ts(ts_key)
        if colon:
            text += self._ts(":")
        return tk.Label(master, text=text)

    def main_menu(self):
        frame = self._new_page(False)
        cmds = ["opening", "closing", "toggle_lang", "start_qualif", "start_round", "start_free_game"]
        for i, cmd in enumerate(cmds):
            column, row = divmod(i, 3)
            button = self._create_button(frame, cmd)
            button.grid(column=column, row=row, **GRID_STYLE)

    def start_qualif(self):
        frame, goto_menu = self._new_page(True)
        quest_frame = self._create_quest_frame(frame)

        for i, widget in enumerate([goto_menu, quest_frame]):
            widget.grid(column=0, row=i, **GRID_STYLE)

    def _create_winnings_button(self, master: tk.Widget, index: int) -> tk.Button:
        win_str = self.format_num(self.game.winnings_pyramid[index], self.game.winnings_unit)
        text = f" {index + 1}. {win_str}"
        cmd = lambda: self.game.set_question_num(index)
        return tk.Button(master, text=text, command=cmd, **WIN_BTN_STYLE)

    def _create_winnings_frame(self, master: tk.Widget) -> tk.LabelFrame:
        frame = self._create_label_frame(master, "winnings")
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
            button.grid(column=column, row=row, **GRID_STYLE)
            self._win_btns.append(button)
        return frame

    def _create_joker_button(self, master: tk.Widget, joker: Joker) -> tk.Button:
        return tk.Button(master, text=self._ts(joker, "icon") + " " + self._ts(joker),
                         command=lambda: self.game.play_joker(joker))

    def _create_jokers_frame(self, master: tk.Widget) -> tk.LabelFrame:
        frame = self._create_label_frame(master, "jokers")
        self._joker_btns = {}
        for i, joker in enumerate(Joker):
            button = self._create_joker_button(frame, joker)
            column, row = divmod(i, 3)
            button.grid(column=column, row=row, **GRID_STYLE)
            self._joker_btns[joker] = button
        return frame

    def update_winnings(self):
        n = self.game.question_num
        for style, start, stop in [(VALID_STYLE, None, n), (AT_STAKE_STYLE, n, n + 1), (BTN_STYLE, n + 1, None)]:
            for button in self._win_btns[start:stop]:
                button.config(**style)

    def update_jokers(self):
        for j, btn in self._joker_btns.items():
            btn.config(command=lambda j=j: self.game.restore_jokers(j), **BTN_STYLE)
        for j in self.game.available_jokers:
            btn = self._joker_btns[j]
            btn.config(command=lambda j=j: self.game.play_joker(j), **AT_STAKE_STYLE)

    def _create_quest_widgets(self, master: tk.Widget):
        self._quest = tk.StringVar(master)
        cmd = lambda: self.game.publish_question(0)
        self._quest_btn = tk.Button(master, textvariable=self._quest, command=cmd, **QUEST_BTN_STYLE)

        self._answs, self._answ_btns = [], []
        for i in range(4):
            textvar = tk.StringVar(master)
            cmd = lambda i=i: self.game.publish_question(i + 1)
            button = tk.Button(master, textvariable=textvar, command=cmd, **ANSW_BTN_STYLE)
            self._answs.append(textvar)
            self._answ_btns.append(button)

    def _create_quest_actions(self, master: tk.Widget) -> list[tk.Button]:
        buttons = []
        game = self.game
        qualif = game.in_qualif
        for text, style, cmd, disable in [
            ("switch_action", BTN_STYLE, game.load_question, qualif),
            ("publish", BTN_STYLE, game.publish_question, False),
            ("walk_away", WALK_AWAY_STYLE, game.walk_away, qualif),
            ("next", AT_STAKE_STYLE, game.next_question, False)
        ]:
            state = tk.DISABLED if disable else tk.NORMAL
            button = tk.Button(master, text=self._ts(text), command=cmd, state=state, **style)
            buttons.append(button)
        return buttons

    def _create_quest_frame(self, master: tk.Widget) -> tk.LabelFrame:
        frame = self._create_label_frame(master, "question")
        author, level, pub_date, note = self._create_quest_metadata(frame)
        self._create_quest_widgets(frame)
        action_btns = self._create_quest_actions(frame)

        kws = GRID_STYLE | dict(columnspan=2)
        for row, widget in enumerate([author, level, pub_date]):
            widget.grid(column=0, row=row, **kws)

        row += 1
        kws["pady"] = (self.PAD, 0)
        self._quest_btn.grid(column=0, row=row, **kws)

        row += 1
        for i, button in enumerate(self._answ_btns):
            r, c = divmod(i, 2)
            button.grid(column=c, row=row + r, **GRID_STYLE)

        row += 1
        kws["pady"] = kws["pady"][::-1]
        note.grid(column=0, row=row, **kws)

        row += 1
        for i, button in enumerate(action_btns):
            r, c = divmod(i, 2)
            button.grid(column=c, row=row + r, **GRID_STYLE)

        return frame

    def _create_quest_metadata(self, master: tk.Widget) -> tuple[tk.Label, ...]:
        labels = []
        for attr in ["_auth", "_lvl", "_pub_date", "_note"]:
            textvar = tk.StringVar(master)
            label = tk.Label(master, textvariable=textvar, **LABEL_STYLE)
            setattr(self, attr, textvar)
            labels.append(label)
        return tuple(labels)

    def start_round(self):
        frame, self._main_menu_btn = self._new_page()
        win_frame = self._create_winnings_frame(frame)
        self.update_winnings()
        quest_frame = self._create_quest_frame(frame)
        joker_frame = self._create_jokers_frame(frame)
        self.update_jokers()

        self._main_menu_btn.grid(column=0, row=0, **GRID_STYLE)
        kws = GRID_STYLE | dict(columnspan=self._colspan, pady=(self.PAD, 0))
        win_frame.grid(column=0, row=1, **kws)
        quest_frame.grid(column=0, row=2, **kws)
        joker_frame.grid(column=0, row=3, **kws)

    def load_question(self):
        if not self.game.in_qualif:
            self.update_winnings()
            self.update_jokers()
        self._load_quest_metadata()
        self._load_quest_data()

    def _load_quest_data(self):
        game = self.game
        quest = game.question

        def getkws(index):
            return dict(command=lambda: self.game.publish_question(index + 1),
                        state=tk.NORMAL, **UNPUBLISHED_STYLE)

        self._quest.set(quest)
        self._quest_btn.config(**getkws(-1))
        for i, answ in enumerate(quest.mixed_answers):
            self._answs[i].set(f" ◆ {chr(65 + i)}{self._ts(":")} {answ} ")
            self._answ_btns[i].config(**getkws(i))

    def _load_quest_metadata(self):
        quest = self.game.question
        metadata = [
            ("_auth", "author", quest.author),
            ("_lvl", "level", self._ts(quest.level.name.lower())),
            ("_pub_date", "publishing_date", quest.publishing_date),
            ("_note", "note", quest.note),
        ]
        for attr, title, value in metadata:
            title = "".join(map(self._ts, [title, ":"]))
            if not value:
                value = self._ts("no_data")
            textvar = getattr(self, attr)
            textvar.set(f"{title} {value}")

    def publish_question(self, n_answers: int = -1):
        def getkws(index):
            style = PUBLISHED_STYLE if n_answers > index else UNPUBLISHED_STYLE
            if index >= 0 and n_answers >= 4:
                cmd = lambda: self.game.ask_final_answer(index)
            else:
                cmd = lambda: self.game.publish_question(index + 1)
            return dict(command=cmd, state=tk.NORMAL, **style)

        quest = self.game.question
        self._quest.set(quest)
        self._quest_btn.config(**getkws(-1))
        for i in range(len(quest.mixed_answers)):
            self._answ_btns[i].config(**getkws(i))

    def ask_final_answer(self):
        for i, button in enumerate(self._answ_btns):
            if i == self.game.final_answer_index:
                cmd = self.game.confirm_answer
                style = WARNING_STYLE
            else:
                cmd = lambda i=i: self.game.ask_final_answer(i)
                style = PUBLISHED_STYLE
            button.config(command=cmd, state=tk.NORMAL, **style)

    def reveal_answer(self):
        styles = {self.game.final_answer_index: ERROR_STYLE,
                  self.game.question.right_index: VALID_STYLE}
        for i, style in styles.items():
            self._answ_btns[i].config(**style)

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
        self._set_title(top, metatype)

        subtype = re.sub("Error|Warning$", "", type_name)
        text = self._ts(subtype)
        if msg := str(exc):
            text += f"\n\n{msg}"

        pad = 2 * self.PAD
        label = tk.Label(top, text=text, padx=pad, pady=pad)
        label.pack()
