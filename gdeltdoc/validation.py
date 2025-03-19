from typing import List, Union

Filter = Union[List[str], str]


def validate_tone(tone: Filter) -> None:
    if not ("<" in tone or ">" in tone):
        raise ValueError("Tone must contain either greater than or less than")

    if "=" in tone:
        raise ValueError("Tone cannot contain '='")

    if type(tone) == list:
        raise NotImplementedError("Multiple tones are not supported yet")
