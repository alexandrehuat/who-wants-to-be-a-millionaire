"""
Sound management
"""

__all__ = ["SoundPlayer"]

from pygame import mixer

mixer.init()

from millionaire import Joker, Stage
from env import SOUND_DIR


class SoundPlayer:
    LONG_FADE_MS = 5000
    SHORT_FADE_MS = 700

    def __init__(self, game):
        self.game = game

    def _play(self, *path, **kwargs):
        self._qplay_stage = self.game.stage if "question" in path else None
        path = SOUND_DIR.joinpath("/".join(path)).with_suffix(".mp3")
        self.stop()
        try:
            self._sound = mixer.Sound(str(path))
            if self._sound.get_length() > 90:  # 90 seconds
                kwargs["fade_ms"] = kwargs.get("fade_ms", self.LONG_FADE_MS)
            self._sound.play(**kwargs)
        except FileNotFoundError:
            self._qplay_stage = None

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

    def _qsound(self, name: str) -> tuple[str, ...]:
        return "stage", self.game.stage.name.lower(), name

    def question(self):
        self._play(*self._qsound("question"))

    def is_playing_question_stage(self, stage: Stage) -> bool:
        try:
            return mixer.get_busy() and self._qplay_stage == stage
        except AttributeError:
            return False

    def reveal_qualif_answers(self):
        self._play(*self._qsound("reveal"))

    def win(self):
        self._play(*self._qsound("win"))

    def loss(self):
        self._play(*self._qsound("loss"))

    def walk_away(self):
        self._play(*self._qsound("walk_away"))

    def final_answer(self):
        self._play(*self._qsound("final_answer"))

    JOKER_REPL = {Joker.SWITCH: Joker.FIFTY,
                  Joker.EXPERT: Joker.FRIEND}

    def joker(self, name: Joker):
        if name in [Joker.ANIMATOR, Joker.EXPERT]:
            self.stop()
        else:
            name = self.JOKER_REPL.get(name, name)
            self._play("joker", name.value.lower())
