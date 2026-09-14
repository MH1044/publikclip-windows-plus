"""Width-aware caption chunking — chunks must stay inside the 1080px frame.

CHUNK_MAX_WIDTH_PX (900) leaves ~30px slack inside the 960px usable width
(1080 PlayResX minus 60px margins on each side)."""

from publikclip_pipeline.captions import ass as ass_mod
from publikclip_pipeline.captions.ass import PRESETS, CHUNK_MAX_WIDTH_PX, Word, chunk_words


def _words(texts: list[str], gap: float = 0.3, dur: float = 0.25) -> list[Word]:
    return [Word(t, i * gap, i * gap + dur) for i, t in enumerate(texts)]


def test_long_words_split_below_word_budget():
    """A 4-word chunk of long words in the wide 'hormozi' preset (Archivo
    Black 80, uppercase) must be split into more than one chunk."""
    preset = PRESETS["hormozi"]
    words = _words(["insane", "crazy", "literally", "unbelievable"])
    chunks = chunk_words(words, preset)
    assert len(chunks) >= 2

    for chunk in chunks:
        text = " ".join(w.text for w in chunk.words)
        assert ass_mod._rendered_width(text, preset) <= CHUNK_MAX_WIDTH_PX


def test_short_words_stay_in_one_chunk():
    """Short words well under the width budget still respect the existing
    4-word budget rule and aren't split early."""
    preset = PRESETS["classic"]
    words = _words(["hey", "so", "go", "now"])
    chunks = chunk_words(words, preset)
    assert len(chunks) == 1
    assert len(chunks[0].words) == 4


def test_all_presets_stay_within_width_budget():
    """For every preset, chunks built from a sample of long words never
    measure over CHUNK_MAX_WIDTH_PX."""
    long_words = [
        "insane", "unbelievable", "million", "billion", "literally",
        "shocked", "actually", "exposed", "hormozi", "gasoline",
    ]
    for preset in PRESETS.values():
        words = _words(long_words)
        chunks = chunk_words(words, preset)
        assert chunks, f"no chunks produced for preset {preset.name!r}"
        for chunk in chunks:
            text = " ".join(w.text for w in chunk.words)
            width = ass_mod._rendered_width(text, preset)
            assert width <= CHUNK_MAX_WIDTH_PX, (
                f"preset {preset.name!r} chunk {text!r} measured {width}px"
            )


def test_single_overlong_word_gets_its_own_chunk():
    """A single word wider than the budget still must not be merged with a
    neighbor — WrapStyle 0 handles wrapping it if libass still can't fit
    it, but chunk_words must not try to split a chunk to zero words."""
    preset = PRESETS["hormozi"]
    words = _words(["pneumonoultramicroscopicsilicovolcanoconiosis", "ok"])
    chunks = chunk_words(words, preset)
    assert len(chunks[0].words) == 1
    assert chunks[0].words[0].text == "pneumonoultramicroscopicsilicovolcanoconiosis"
