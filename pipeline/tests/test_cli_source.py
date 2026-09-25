from pathlib import Path

from publikclip_pipeline.cli import normalize_source


def test_url_passthrough():
    assert normalize_source("https://youtu.be/abc") == ("url", "https://youtu.be/abc")


def test_quoted_url_is_unwrapped():
    assert normalize_source('"https://youtu.be/abc"') == ("url", "https://youtu.be/abc")


def test_copy_as_path_quotes_are_stripped(tmp_path):
    video = tmp_path / "talk 01.01 - guest speaker.MP4"
    video.write_bytes(b"")
    source_type, source = normalize_source(f'"{video}"')
    assert source_type == "file"
    assert Path(source) == video.resolve()


def test_single_quotes_and_whitespace(tmp_path):
    video = tmp_path / "a.mp4"
    video.write_bytes(b"")
    assert normalize_source(f"  '{video}'  ") == ("file", str(video.resolve()))


def test_relative_file_is_pinned_to_absolute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "rel.mp4").write_bytes(b"")
    source_type, source = normalize_source("rel.mp4")
    assert source_type == "file"
    assert Path(source).is_absolute()
    assert Path(source) == (tmp_path / "rel.mp4").resolve()


def test_lone_quote_is_not_stripped():
    # only a *matching pair* is unwrapped; a stray quote stays part of the path
    _, source = normalize_source('"C:/weird')
    assert '"' in source
