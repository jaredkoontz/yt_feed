from typing import Any
from typing import TypeAlias
from typing import cast

import yt_dlp

InfoDict: TypeAlias = dict[str, Any]


def _data(url: str, ydl_opts: dict[str, list[dict[str, str]] | str]) -> InfoDict:
    # pyrefly: ignore [bad-argument-type]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return cast(InfoDict, ydl.extract_info(url, download=False))


def extract_audio(url: str) -> InfoDict:
    ydl_audio_opts = {
        "format": "m4a/bestaudio/best",
        "postprocessors": [
            {
                # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
    }
    return _data(url, ydl_audio_opts)
