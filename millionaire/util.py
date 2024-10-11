DECIMAL_SEP = {"fr": ",", "en": "."}
THOUSAND_SEPS = {"fr": ["\u202F", "\u00A0", " "], "en": ","}


def str_is_int(string: str, lang: str) -> bool:
    if lang is None:
        return any(str_is_num(string, l) for l in DECIMAL_SEP.keys())

    parts = string.strip().split(THOUSAND_SEPS[lang][0])
    if len(parts) > 1 \
            and len(parts[0]) > 3 \
            or any(len(part) != 3 for part in parts[1:]):
        return False


def str_is_num(string: str, lang: str = None) -> bool:
    if lang is None:
        return any(str_is_num(string, l) for l in DECIMAL_SEP.keys())

    _string = string.strip().lower()
    if _string[0] in "+-":
        _string = _string[1:]
    if _string.lower() in ["nan", "inf"]:
        return True

    try:
        parts = _string.split(DECIMAL_SEP[lang])
        if len(parts) > 2 \
                or not str_is_int(parts[0], lang) \
                or len(parts) > 1 and not str_is_int(parts[1][::-1], lang):
            return False
    except KeyError:
        raise NotImplementedError(f"unsupported language {lang!r}")
    return True


def to_num(string: str, lang: str = None, raise_: bool = False) -> int | float | None:
    """
    Converts a string to a number if `:py:func:`str_is_num(string, lang).
    :raises ValueError: If cannot be converted and `raise_` is false
    """
    _string = string.strip()
    if not str_is_num(string, lang):
        if raise_:
            raise ValueError(f"{string} cannot be converted to a number in the supported languages")
        return None
    for olds, new in [(DECIMAL_SEP, "."), (THOUSAND_SEPS, "")]:
        for old in olds[lang]:
            _string = _string.replace(old, new)
    try:
        return int(_string)
    except ValueError:
        return float(_string)


def format_int(num: int, lang: str) -> str:
    string = str(num)
    n = len(string)
    if n <= 3:
        return string
    m = n % 3
    parts = [string[:m]]
    for i in range(m, n, 3):
        parts.append(string[i:i + 3])
    return THOUSAND_SEPS[lang][0].join(filter(None, parts))


def format_num(num: int | float, unit: str, lang: str) -> str:
    try:
        parts = list(map(int, str(num).split(".")))
        parts[0] = format_int(parts[0], lang)
        if len(parts) > 1:
            parts[1] = format_int(parts[1][::-1], lang)
    except KeyError:
        raise NotImplementedError(f"unsupported language {lang!r}")
    numstr = DECIMAL_SEP[lang].join(parts)
    if lang == "fr":
        return f"{numstr} {unit}"
    elif lang == "en":
        return f"{unit}{numstr}"
