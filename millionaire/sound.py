"""
Sound management
"""

__all__ = ["SoundPlayer"]

from pygame import mixer

mixer.init()

from millionaire import Stage, Joker
from env import SOUND_DIR


class SoundPlayer:
    LONG_FADE_MS = 5000
    SHORT_FADE_MS = 700

    def __init__(self, stage: Stage = Stage.QUALIF):
        self.stage = stage

    def _play(self, *path, **kwargs):
        path = SOUND_DIR.joinpath("/".join(path)).with_suffix(".mp3")
        self.stop()
        try:
            self._sound = mixer.Sound(str(path))
            if self._sound.get_length() > 90:  # 90 seconds
                kwargs["fade_ms"] = kwargs.get("fade_ms", self.LONG_FADE_MS)
            self._sound.play(**kwargs)
        except FileNotFoundError:
            pass

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, value: Stage):
        self._stage = Stage(value)

    def stop(self):
        try:
            self._sound.fadeout(self.SHORT_FADE_MS)
        except AttributeError:
            pass

    def credits(self, opening: bool = True):
        name = "opening" if opening else "closing"
        self._play("credits", name)

    def intro_players(self):
        self._play("players", "intro")

    def welcome_players(self):
        self._play("players", "welcome")

    def open_qualif(self):
        self._play("stage", "qualif", "opening")

    def reveal_qualif(self):
        self._play("stage", "qualif", "reveal")

    def win_qualif(self):
        self._play("stage", "qualif", "win")

    def _qrel_sound(self, name: str, stage: Stage = None) -> str:
        """
        Question related sounds
        """
        parts = ["stage", stage.name.lower(), name]
        return "/".join(parts)

    def question(self):
        self._play(self._qrel_sound("question", self.stage))

    def reveal_qualif_answers(self):
        self._play(self._qrel_sound("reveal", Stage.QUALIF))

    def win(self):
        self._play(self._qrel_sound("win", self.stage))

    def loss(self):
        self._play(self._qrel_sound("loss", self.stage))

    def walk_away(self):
        self._play(self._qrel_sound("walk_away", self.stage))

    def final_answer(self):
        self._play(self._qrel_sound("final_answer", self.stage))

    JOKER_REPL = {Joker.SWITCH: Joker.FIFTY,
                  Joker.EXPERT: Joker.FRIEND}

    def joker(self, name: Joker):
        if name in [Joker.ANIMATOR, Joker.EXPERT]:
            self.stop()
        else:
            name = self.JOKER_REPL.get(name, name)
            self._play("joker", name.value.lower())
