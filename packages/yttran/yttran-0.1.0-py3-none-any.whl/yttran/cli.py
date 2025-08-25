import sys
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter



def extract_video_id(url_or_id: str) -> str:
    if len(url_or_id) == 11 and "://" not in url_or_id:
        return url_or_id
    parsed = urlparse(url_or_id)
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query).get("v", [""])[0]
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")
    raise ValueError(f"Could not extract video id from {url_or_id}")


def main():
    if len(sys.argv) != 2:
        print("Usage: yttran <video-url-or-id>", file=sys.stderr)
        sys.exit(1)

    vid = extract_video_id(sys.argv[1])
    api = YouTubeTranscriptApi()
    transcript = api.fetch(vid, languages=["en"])

    formatter = TextFormatter()
    # .format_transcript(transcript) turns the transcript into a text string.
    text_formatted = formatter.format_transcript(transcript)
    print(text_formatted)

    # for entry in transcript:
    #     text = entry.text.strip()
    #     if text:
    #         print(text)
