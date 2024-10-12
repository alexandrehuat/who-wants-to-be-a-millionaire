DECIMAL_SEP = {"fr": ",", "en": "."}
THOUSAND_SEPS = {"fr": ["\u202F", "\u00A0", " "], "en": ","}


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
