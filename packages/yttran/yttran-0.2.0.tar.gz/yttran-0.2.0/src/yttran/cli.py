import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

CACHE_DIR = Path(os.path.expanduser("~/.cache/yttan"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def video_id_from_url(url_or_id: str) -> str:
    if len(url_or_id) == 11 and "://" not in url_or_id:
        return url_or_id
    parsed = urlparse(url_or_id)
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query).get("v", [""])[0]
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")
    raise ValueError(f"Could not extract video id from {url_or_id}")


def cache_path(video_id: str) -> Path:
    return CACHE_DIR / f"{video_id}.txt"


def fetch_transcript(video_id: str) -> str:
    vid = video_id_from_url(sys.argv[1])
    api = YouTubeTranscriptApi()
    transcript = api.fetch(vid, languages=["en"])
    formatter = TextFormatter()
    # .format_transcript(transcript) turns the transcript into a text string.
    text = formatter.format_transcript(transcript)
    # print(text)
    # text = "\n".join(entry['text'] for entry in transcript if entry['text'].strip())
    return text


def main():
    if len(sys.argv) < 2:
        print("Usage: yttran <youtube-url-or-id>", file=sys.stderr)
        sys.exit(1)

    vid = video_id_from_url(sys.argv[1])
    cache_file = cache_path(vid)

    if cache_file.exists():
        text = cache_file.read_text(encoding="utf-8")
    else:
        text = fetch_transcript(vid)
        cache_file.write_text(text, encoding="utf-8")

    sys.stdout.write(text)


if __name__ == "__main__":
    main()
