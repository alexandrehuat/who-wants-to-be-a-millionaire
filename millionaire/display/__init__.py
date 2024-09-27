from millionaire import util, translate

Theme = {"color":
    {
        "aql": [
            "#ED8E5B",
            "#4088AF",
            "#1D4A8A",
            "#882E7A",
        ],
        "base": "purple",
        "altbase": "royal blue",
        "valid": "green",
        "error": "red",
        "warning": "orange",
        "disabled": "gray",
        "winnings": {
            "first": "light goldenrod",
            "second": "goldenrod",
            "last": "dark goldenrod",
        },
        "bg": "black",
    }
}


class MillionaireWidget:
    def __init__(self, game):
        self._game = game

    @property
    def game(self):
        return self._game

    @property
    def lang(self) -> str:
        obj = getattr(self, "master")
        if obj is None:
            obj = self.game
        return obj.lang

    def _ts(self, key: str, lang: str = None) -> str:
        """Provides the translation from the resource translation file given the key."""
        return translate(key, self.lang if lang is None else lang)

    def format_num(self, num: int | float, unit: str, lang: str = None):
        return util.format_num(num, unit, self.lang if lang is None else lang)

    def clear(self):
        for child in self.winfo_children():
            child.destroy()