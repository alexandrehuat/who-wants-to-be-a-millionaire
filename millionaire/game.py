"""
The game's logic.
Mixes the model with the controller in the MVC design pattern.
"""

import csv
import sys
import time

from env import QUESTION_FILE, WINNINGS_FILE
from millionaire import *
from millionaire import QLevel
from millionaire.display.animator.tk import TkAnimationTerminal
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
    def __init__(self, lang: str = "fr",
                 milestones: Milestones = Milestones.fifteen(),
                 question_timeout: int = 180):
        self._lang = lang
        self.milestones = milestones
        self.question_timeout = question_timeout

        self.init_question_data()
        self._init_winnings()
        self._soundp = SoundPlayer(self)
        self._init_display()
        self.main_menu()

    @property
    def lang(self) -> str:
        return self._lang

    def toggle_lang(self):
        for i, lang in enumerate(LANGS):
            if lang == self.lang:
                self._lang = LANGS[(i + 1) % len(LANGS)]
                break
        self._init_display()

    def _parse_qdata(self, encoding: str = "utf-8"):
        with open(QUESTION_FILE, newline='', encoding=encoding) as f:
            reader = csv.reader(f, dialect=csv.excel_tab)
            for row in reader:
                level = row[5]
                kws = {}
                for i, name in enumerate(["author", "note", "publishing_date"]):
                    try:
                        value = row[6 + i]
                    except IndexError:
                        value = None
                    kws[name] = value
                quest = Question(level, row[0], row[1], *row[2:5], lang=self.lang, **kws)
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
        data = data[self.lang]
        self._wins = data["pyramid"][str(self.milestones.end)]
        self._win_unit = data["unit"]

    @property
    def winnings_pyramid(self):
        return self._wins

    @property
    def winnings_unit(self):
        return self._win_unit

    def _init_display(self):
        for attr, cls in [("_anim_term", TkAnimationTerminal), ("_pub_screen", PublicScreen)]:
            try:
                getattr(self, attr).destroy()
            except AttributeError:
                pass
            setattr(self, attr, cls(self))
        self.main_menu()
        self._anim_term.mainloop()

    @property
    def animation_terminal(self) -> TkAnimationTerminal:
        return self._anim_term

    @property
    def public_screen(self) -> PublicScreen:
        return self._pub_screen

    def opening(self):
        self.sound_player.credits(True)

    def closing(self):
        self.sound_player.credits(False)

    def restart(self):
        self.sound_player.stop()
        self.__init__(self.lang, self.milestones, self._qtimeout)

    def quit(self):
        sys.exit()

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
    def question_timeout(self) -> int | float:
        if self.in_qualif:
            return self.sound_player.get_length(Question)
        return self._qtimeout

    @question_timeout.setter
    def question_timeout(self, value: int):
        self._qtimeout = int(value)

    @property
    def question_num(self) -> int:
        return self._qnum

    def set_question_num(self, num: int, force: bool = False):
        if force or num != self._qnum:
            self._qnum = num
            self.sound_player.stop()
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

    def display_reveal_answer(self):
        self.animation_terminal.reveal_answer()
        self.public_screen.reveal_answer()

    def start_round(self):
        self._qnum = 0
        self._played_jokers = set()
        self.animation_terminal.start_round()
        self.set_question_num(0, force=True)

    def start_free_game(self):
        self.animation_terminal.raise_exc(NotImplementedError)

    @property
    def question(self) -> Question | None:
        try:
            return self._qdata[self._qpicked[-1]]
        except IndexError:
            return None

    def _qpick(self):
        self._qpicked.append(self._qtoask.pop())

    def _restack_qtoask(self):
        self._qtoask.extend(self._qpicked)
        random.shuffle(self._qtoask)
        self._qpicked = []

    def load_question(self):
        self._run_qtimer = False
        self._pub_answs = -1
        try:
            self._qpick()
            while not self.milestones.allows_question(self.question, self._qnum):
                self._qpick()
        except IndexError:  # No more questions to pick
            self.animation_terminal.raise_exc(QuestionUnderflowWarning)
            self._restack_qtoask()
        self._joker_fifty_ind = None
        self.question.shuffle()
        self.animation_terminal.load_question()

    def publish_question(self, n_answers: int = None):
        if n_answers is None:
            n_answers = self._pub_answs + 1
        if self.in_qualif and n_answers > 0:
            n_answers = 4
        self._pub_answs = max(-1, min(n_answers, 4))

        self._reset_joker_timer()
        if n_answers > 0 and not self._run_qtimer:
            self._start_quest_timer()
        else:
            self._qcountup = 0

        self.animation_terminal.publish_question(self._pub_answs)
        self.public_screen.show(self._pub_answs)
        if not self.sound_player.is_playing_question_stage(self.stage):
            self.sound_player.question()

    REFRESH_RATE = int(1000 / 30)

    def _start_quest_timer(self, restart: bool = True):
        if restart:
            self._run_qtimer = True
            self._qtimestart = time.time()
        if self._run_qtimer:
            self._qcountup = time.time() - self._qtimestart
            self.public_screen.update_question_timer()
            if self._qcountup >= self.question_timeout:
                if not self.in_qualif:
                    self.sound_player.reveal_qualif()
                self.public_screen.update_question_timer()
                self._run_qtimer = False
            else:
                repeat = lambda: self._start_quest_timer(False)
                self.animation_terminal.after(self.REFRESH_RATE, repeat)

    @property
    def question_time_progress(self) -> float:
        try:
            return self._qcountup / self.question_timeout
        except AttributeError:
            return 0

    def ask_final_answer(self, index: int):
        self._final_answ_ind = index
        self.animation_terminal.ask_final_answer()
        self.public_screen.ask_final_answer()
        if self.in_qualif:
            self.sound_player.reveal_answers()
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
        self._run_qtimer = False
        self.display_reveal_answer()
        if self.question.level != QLevel.TRIVIAL:
            right = self.question.check_answer(self.final_answer_index)
            next_ends = self.milestones.is_ended(self.question_num + 1)
            if self.in_qualif or right or next_ends:
                self.sound_player.win()
            else:
                self._stop_round(right)

    def next_question(self):
        if self.in_qualif:
            self.load_question()
        else:
            num = self._qnum + (self.question.level != QLevel.TRIVIAL)
            self.set_question_num(num)

    def restore_jokers(self, joker: Joker):
        self._played_jokers.remove(joker)
        if joker == Joker.FIFTY:
            self._joker_fifty_ind = None
        self.animation_terminal.update_jokers()
        self.public_screen.show()

    def _play_joker_fifty(self):
        wrong_inds = self.question.wrong_indices()
        half = (len(wrong_inds) + 1) // 2
        self._joker_fifty_ind = random.sample(wrong_inds, half)
        self.animation_terminal.play_joker_fifty()
        self.public_screen.show_question()

    @property
    def joker_indices(self) -> tuple[int]:
        try:
            return tuple(self._joker_fifty_ind)
        except (AttributeError, TypeError):
            return tuple()

    def play_joker(self, joker: Joker):
        if self.question.level == QLevel.TRIVIAL:
            self.animation_terminal.raise_exc(JokersDisabledForQLevelError)
        else:
            try:
                self._played_jokers.add(joker)
                self._reset_joker_timer()
                match joker:
                    case Joker.FIFTY:
                        self._play_joker_fifty()
                    case Joker.FRIEND:
                        self._start_joker_timer()
                    case Joker.SWITCH:
                        self.load_question()
                self.animation_terminal.update_jokers()
                self.public_screen.show_jokers()
                self.sound_player.joker(joker)
            except KeyError:
                raise DisabledJokerError(joker)

    @property
    def joker_timeout(self):
        return 30

    def _start_joker_timer(self, restart: bool = True):
        if restart:
            self._run_qtimer = False
            self._run_joktimer = True
            self._joktimestart = time.time()
        if self._run_joktimer:
            self._jokcountup = time.time() - self._joktimestart
            self.public_screen.update_joker_timer()
            if self._jokcountup >= self.joker_timeout:
                self._run_joktimer = False
                self.public_screen.update_joker_timer()
                try:
                    self._qtimestart += self._jokcountup
                except AttributeError:
                    self._qtimestart = time.time()
                self._jokcountup = 0
                self._run_qtimer = True
                self._start_quest_timer(False)
            else:
                repeat = lambda: self._start_joker_timer(False)
                self.animation_terminal.after(self.REFRESH_RATE, repeat)

    def _reset_joker_timer(self):
        self._run_joktimer = False
        self._jokcountup = 0
        self.public_screen.update_joker_timer()

    @property
    def joker_time_progress(self) -> float:
        try:
            return self._jokcountup / self.joker_timeout
        except AttributeError:
            return 0

    @property
    def played_jokers(self) -> tuple:
        try:
            return tuple(self._played_jokers)
        except AttributeError:
            return tuple()

    @property
    def available_jokers(self) -> tuple[Joker, ...]:
        jokers = self.milestones.allowed_jokers(self.question_num)
        return tuple(jokers.difference(self.played_jokers))

    def walk_away(self):
        self.sound_player.stop()
        self.public_screen.walk_away()
