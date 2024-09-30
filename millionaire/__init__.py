import json
import random
from enum import IntEnum, StrEnum

from env import RSC_DIR
from millionaire.question import Question, QLevel

with open(RSC_DIR / "translations.json") as f:
    TRANSLATIONS = json.load(f)

LANGS = tuple(TRANSLATIONS["toggle_lang"].keys())


class Stage(IntEnum):
    QUALIF = -1
    FIRST = 0
    SECOND = 1
    LAST = 2
    END = 3


class Joker(StrEnum):
    FIFTY = "fifty"
    FRIEND = "friend"
    AUDIENCE = "audience"
    SWITCH = "switch"
    ANIMATOR = "animator"
    EXPERT = "expert"


CLASSICAL_JOKERS = (Joker.FIFTY, Joker.FRIEND, Joker.AUDIENCE)
ADDITIONAL_JOKERS = tuple(set(Joker).difference(CLASSICAL_JOKERS))


class Milestones:
    """Handles milestones relatively to the question number."""

    def __init__(self, end: int = 15, first: int = None, second: int = None):
        _end = int(end)
        if first is None and second is None:
            first = _end / 3
            second = 2 * first
        elif first is None or second is None:
            raise ValueError("'first' and 'second' must be both none or both integers")
        self._data = int(first), int(second), _end
        self._add_jokers = random.sample(range(3), 2)

    @property
    def safe_nets(self) -> tuple[int, int, int]:
        return tuple(i - 1 for i in self._data)

    def safe_net(self, num: int) -> int | None:
        for i, net in enumerate(self.safe_nets[::-1]):
            if num > net:
                return net
        return None

    @classmethod
    def fifteen(cls):
        return cls(15)

    @classmethod
    def twelve_classic(cls):
        return cls(12, 7, 2)

    @classmethod
    def twelve_balanced(cls):
        return cls(12)

    @property
    def first_milestone(self):
        return self._data[0]

    @property
    def second_milestone(self):
        return self._data[1]

    @property
    def end(self):
        return self._data[2]

    def in_qualif(self, num: int) -> bool:
        return num < 0

    def in_first_stage(self, num: int) -> bool:
        return 0 <= num < self.first_milestone

    def in_second_stage(self, num: int) -> bool:
        return self.first_milestone <= num < self.second_milestone

    def in_last_stage(self, num: int) -> bool:
        return self.second_milestone <= num < self.end

    def is_ended(self, num: int) -> bool:
        return num >= self.end

    def stage(self, num: int) -> Stage:
        stages = list(Stage)
        for i, stone in enumerate((0,) + self._data):
            if num < stone:
                return stages[i]
        return stages[-1]

    def allows_question(self, question: Question, num: int) -> bool:
        if self.is_ended(num):
            raise NotImplementedError(f"{num=} is not supposed to be greater than {self.end}")
        lvl = question.level
        qualif = self.in_qualif(num)
        return (lvl == QLevel.EXTREME and qualif
                or lvl == QLevel.TRIVIAL and not qualif
                or lvl == QLevel.EASY and self.in_first_stage(num)
                or lvl == QLevel.MEDIUM and self.in_second_stage(num)
                or lvl == QLevel.HARD and self.in_last_stage(num))

    def allowed_jokers(self, num: int) -> set[Joker]:
        jokers = set(CLASSICAL_JOKERS)
        for stone, joker in zip(self._data, self._add_jokers):
            if num > stone:
                jokers.add(ADDITIONAL_JOKERS[joker])
        return jokers


def translate(key, lang="fr"):
    try:
        opt = TRANSLATIONS[key]
        for _lang in [lang, "*"]:
            try:
                return opt[_lang]
            except KeyError:
                pass
        raise KeyError(f"{key}.{_lang}")
    except KeyError as e:
        return repr(e)
