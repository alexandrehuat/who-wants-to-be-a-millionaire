"""
The game's logic.
Mixes the model with the controller in the MVC design pattern.
"""

import csv
import random

from env import QUESTION_FILE, WINNINGS_FILE
from millionaire import *
from millionaire import QLevel
from millionaire.display.animator import AnimationTerminal
from millionaire.display.public import PublicScreen
from millionaire.exceptions import (
    PerformanceError,
    QuestionUnderflowWarning,
    DisabledJokerError,
    JokersDisabledForQLevelError
)
from millionaire.question import Question
from millionaire.sound import SoundPlayer


class Game:
    def __init__(self, lang: str = "fr", milestones: Milestones = Milestones.twelve_balanced()):
        self._lang = lang
        self.milestones = milestones
        self.init_question_data()
        self._init_winnings()
        self._soundp = SoundPlayer()
        self._init_display()
        self.start_round()

    @property
    def lang(self) -> str:
        return self._lang

    def toggle_lang(self):
        for i, lang in enumerate(LANGS):
            if lang == self.lang:
                self._lang = LANGS[(i + 1) % len(LANGS)]
                break
        self.animation_terminal.update_lang()

    def _parse_qdata(self, encoding: str = "utf-8"):
        with open(QUESTION_FILE, newline='', encoding=encoding) as f:
            reader = csv.reader(f, dialect=csv.excel_tab)
            for row in reader:
                lvl = QLevel.from_str(row[5])
                auth = note = None
                try:
                    auth = row[6]
                    note = row[7]
                except IndexError:
                    pass
                quest = Question(lvl, row[0], row[1], *row[2:5],
                                 author=auth, note=note, lang=self.lang)
                self._qdata.append(quest)

    def init_question_data(self):
        self._qdata = []
        for encoding in ["utf-8", "utf-16", "latin1"]:
            try:
                self._parse_qdata(encoding)
            except UnicodeError:
                pass
        n = len(self._qdata)
        if n > (thres := 65536):  # 2 ** 16 questions; empirically set
            raise PerformanceError(f"too many questions (> {thres})")
        self._qtoask = random.sample(range(n), n)
        self._qpicked = []
        self._qasked = []

    def _init_winnings(self):
        self._wins = []
        with open(WINNINGS_FILE) as f:
            data = json.load(f)
        self._wins = data["pyramid"][str(self.milestones.end)]
        self._win_unit = data["unit"]

    @property
    def winnings_pyramid(self):
        return self._wins

    @property
    def winnings_unit(self):
        return self._win_unit

    def _init_display(self):
        self._anim_term = AnimationTerminal(self)
        self._pub_screen = PublicScreen(self)
        self.main_menu()
        self._anim_term.mainloop()

    @property
    def animation_terminal(self) -> AnimationTerminal:
        return self._anim_term

    @property
    def public_screen(self) -> PublicScreen:
        return self._pub_screen

    def opening(self):
        self.sound_player.credits(True)

    def closing(self):
        self.sound_player.credits(False)

    def main_menu(self):
        self.animation_terminal.main_menu()
        self.sound_player.stop()

    @property
    def sound_player(self) -> SoundPlayer:
        return self._soundp

    @property
    def milestones(self) -> Milestones:
        return self._mstone

    @milestones.setter
    def milestones(self, value: Milestones):
        self._mstone = value

    @property
    def safe_net(self) -> int | None:
        return self.milestones.safe_net(self.question_num)

    @property
    def stage(self):
        return self.milestones.stage(self.question_num)

    @property
    def question_num(self) -> int:
        return self._qnum

    def set_question_num(self, num: int, force: bool = False):
        if force or num != self._qnum:
            self.sound_player.stop()
            self._qnum = num
            self.sound_player.stage = self.stage
            self._restack_qtoask()
            self.load_question()

    def start_qualif(self):
        self._qnum = -1
        self.sound_player.open_qualif()
        self.animation_terminal.start_qualif()
        self.load_question()

    @property
    def in_qualif(self) -> bool:
        return self.milestones.in_qualif(self.question_num)

    def reveal_qualif(self):
        self.sound_player.win()
        self.reveal_answer()

    def reveal_answer(self):
        self.animation_terminal.reveal_answer()
        self.public_screen.reveal_answer()

    def start_round(self):
        self._qnum = 0
        self._jokers = set(Joker)
        self.animation_terminal.start_round()
        self.set_question_num(0, force=True)

    def start_free_game(self):
        raise NotImplementedError("TODO")

    @property
    def question(self) -> Question:
        return self._qdata[self._qpicked[-1]]

    def _qpick(self):
        self._qpicked.append(self._qtoask.pop())

    def _restack_qtoask(self):
        self._qtoask.extend(self._qpicked)
        random.shuffle(self._qtoask)
        self._qpicked = []

    def load_question(self):
        try:
            self._qpick()
            while not self.milestones.allows_question(self.question, self._qnum):
                self._qpick()
        except IndexError:  # No more questions to pick
            self.animation_terminal.raise_exc(QuestionUnderflowWarning)
            self._restack_qtoask()
        self._joker_ind = []
        self.question.shuffle()
        self.animation_terminal.load_question()

    def publish_question(self):
        self.public_screen.show_question()
        self.public_screen.show_jokers()
        self.public_screen.show_winnings()
        self.sound_player.question()

    def ask_final_answer(self, index: int):
        self._final_answ_ind = index
        self.animation_terminal.ask_final_answer()
        self.public_screen.ask_final_answer()
        if self.in_qualif:
            self.sound_player.reveal_qualif()
        else:
            self.sound_player.final_answer()

    @property
    def final_answer_index(self):
        return self._final_answ_ind

    def _stop_round(self, million: bool):
        if million:
            self.sound_player.credits(True)
            self.public_screen.show_winnings()
        else:
            self.sound_player.loss()
            self.public_screen.loss()

    def confirm_answer(self):
        self.reveal_answer()
        if self.question.level != QLevel.TRIVIAL:
            right = self.question.check_answer(self.final_answer_index)
            if self.milestones.is_ended(self.question_num + 1) or not right:
                self._stop_round(right)
            else:
                self.sound_player.win()

    def next_question(self):
        if self.in_qualif:
            self.load_question()
        else:
            num = self._qnum + (self.question.level != QLevel.TRIVIAL)
            self.set_question_num(num)

    def restore_jokers(self, joker: Joker):
        self._jokers.add(joker)
        self.animation_terminal.update_jokers()

    def _play_joker_fifty(self):
        wrong_inds = self.question.wrong_indices()
        half = (len(wrong_inds) + 1) // 2
        self._joker_ind = random.sample(wrong_inds, half)
        self.animation_terminal.play_joker_fifty()
        self.public_screen.show_question()

    @property
    def joker_indices(self) -> tuple[int]:
        try:
            return tuple(self._joker_ind)
        except AttributeError:
            return tuple()

    def play_joker(self, joker: Joker):
        if self.question.level == QLevel.TRIVIAL:
            self.animation_terminal.raise_exc(JokersDisabledForQLevelError)
        else:
            try:
                self._jokers.remove(joker)
                match joker:
                    case Joker.FIFTY:
                        self._play_joker_fifty()
                    case Joker.SWITCH:
                        self.load_question()
                self.animation_terminal.update_jokers()
                self.public_screen.show_jokers()
                self.sound_player.joker(joker)
            except KeyError:
                raise DisabledJokerError(joker)

    @property
    def jokers(self) -> tuple[Joker]:
        try:
            return tuple(self._jokers)
        except AttributeError:
            return tuple()

    def walk_away(self):
        self.sound_player.stop()
        self.public_screen.walk_away()
