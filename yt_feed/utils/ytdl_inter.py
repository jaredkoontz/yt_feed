import yt_dlp


def _data(url: str, ydl_opts: dict[str, str]) -> dict:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # could download with
        # error_code = ydl.download(url)
        info = ydl.extract_info(url, download=False)
        return info


def extract_video(url: str) -> dict:
    # "format": "22/best" could be used?
    return _data(url, {})


def extract_audio(url: str) -> dict:
    ydl_audio_opts = {
        "format": "m4a/bestaudio/best",
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        "postprocessors": [
            {
                # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
    }
    return _data(url, ydl_audio_opts)
