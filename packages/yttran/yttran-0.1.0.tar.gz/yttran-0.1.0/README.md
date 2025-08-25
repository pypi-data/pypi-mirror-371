# yttan

`yttran` (“YouTube Transcript”) is a lightweight CLI tool that allows you to quickly fetch the **plain transcript text** from YouTube videos without downloading the video itself. It leverages the official `youtube-transcript-api` and can be run via [uvx](https://github.com/astral-sh/uvx) for easy, one-step usage.

---

## Problem

YouTube videos often have captions or auto-generated transcripts.

There are websites like https://transcribefromyoutube.com/ that one can use to get a transcript but they require you to leave the terminal and copy paste the text for further processing.
Further processing to extract summaries and wisdonm can be done with tools like Claude AI, ChatGPT or [Fabric](https://github.com/danielmiessler/fabric).

- Downloading full videos just to get text is cumbersome.
- Subtitles come in `.srt` or `.vtt` formats, which include timestamps, numbering, and formatting tags.
- Cleaning and deduplicating these files is tedious, especially when automating workflows.

`yttran` solves this by providing **a single command to get clean, readable transcript text**, ready for pipelines, research, or note-taking.

---

## Dependency

uv manages project dependencies and environments for python packages.

See https://docs.astral.sh/uv/#installation

## Installation

If you have [`uvx`](https://github.com/astral-sh/uvx) installed, you can run `yttan` directly from PyPI without manual dependency management:

```bash
uvx yttran <youtube-video-url-or-id> > transcript.txt
```
