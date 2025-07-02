import yt_dlp


def _data(url: str, ydl_opts: dict[str, str]) -> dict:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def extract_video(url: str) -> dict:
    ydl_audio_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio"
    }
    return _data(url, ydl_audio_opts)


def extract_audio(url: str) -> dict:
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
