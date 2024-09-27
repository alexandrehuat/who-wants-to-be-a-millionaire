import random
from enum import IntEnum

from millionaire import util


class QLevel(IntEnum):
    TRIVIAL = 0
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXTREME = 4

    @classmethod
    def from_str(cls, value: str):
        return cls(int(value))


class Question(str):
    def __new__(cls, level: QLevel | int | str,
                question: str,
                right_answer: str,
                *wrong_answers: str,
                author: str = None,
                note: str = None,
                lang: str = "en"):
        return super().__new__(cls, question)

    def __init__(self, level: QLevel | int | str,
                 question: str,
                 right_answer: str,
                 *wrong_answers: str,
                 author: str = None,
                 note: str = None,
                 lang: str = "en"):
        self._lvl = QLevel(level)
        self._right_answ = str(right_answer)
        self._wrong_answs = tuple(map(str, wrong_answers))
        self._auth = str(author) if author else ""
        self._note = str(note) if note else ""
        self._lang = lang
        self.shuffle()

    @property
    def level(self) -> QLevel:
        return self._lvl

    @property
    def right_answer(self) -> str:
        return self._right_answ

    @property
    def wrong_answers(self) -> tuple[str]:
        return self._wrong_answs

    @property
    def author(self) -> str:
        return self._auth

    @property
    def note(self) -> str:
        return self._note

    def shuffle(self, seed: int = None):
        answers = [self._right_answ, *self._wrong_answs]
        num_answs = [util.to_num(answ, self._lang, raise_=False) for answ in answers]
        if all(answ is not None for answ in num_answs):
            answers = map(str, sorted(num_answs))
        else:
            random.seed(seed)
            random.shuffle(answers)
        self._mixed_answs = tuple(answers)

    @property
    def mixed_answers(self) -> tuple[str]:
        return self._mixed_answs

    @property
    def right_index(self) -> int:
        for i, answ in enumerate(self._mixed_answs):
            if answ == self._right_answ:
                return i

    def wrong_indices(self) -> tuple[int]:
        inds = []
        for i, answ in enumerate(self._mixed_answs):
            if answ != self._right_answ:
                inds.append(i)
        return inds

    def check_answer(self, index: int) -> bool:
        """
        Returns true if the index is that of the right answer.
        """
        return self._mixed_answs[index] == self._right_answ
