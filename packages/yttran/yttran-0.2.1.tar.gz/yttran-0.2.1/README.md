# yttran

`yttran` (“YouTube Transcript”) is a lightweight CLI tool that allows you to quickly fetch the **plain transcript text** from YouTube videos without downloading the video itself. It leverages the official `youtube-transcript-api` and can be run via [uvx](https://github.com/astral-sh/uvx) for easy, one-step usage.

---

## Problem

YouTube videos often have captions or auto-generated transcripts.

There are websites like https://transcribefromyoutube.com/ that one can use to get a transcript but they require you to leave the terminal and copy paste the text for further processing.

A CLI lternative is to use the cli that comes with `youtube-transcript-api` but I can never remember all the switches nor do I want to type all of those long commands.

```bash
uvx run youtube_transcript_api <first_video_id> <second_video_id> ... --languages en --format text > transcripts.txt
```

I need to be able to run a short command and specify only the youtube video so that I can pipe transcript into AI analysis and summarization tools.  I also what to save the transacript into a local cache to I don't need to fetch it again.

Further processing to extract summaries and wisdonm can be done with tools like Claude AI, ChatGPT or [Fabric](https://github.com/danielmiessler/fabric).

Insummary, in order to maximize learning from Youtube videos...

- Downloading full videos just to get transcription text is cumbersome.
- Subtitles come in `.srt` or `.vtt` formats, which include timestamps, numbering, and formatting tags.
- Cleaning and deduplicating these files is tedious, especially when automating workflows.

`yttran` solves this by providing **a single command to get clean, readable transcript text**, ready for passing on to AI pipelines, research, or note-taking.

---

## Dependency

uv manages project dependencies and environments for python packages.

See https://docs.astral.sh/uv/#installation

## Code repository

https://github.com/rnwolf/yttran


## Install package during development for testing

```bash
uv pip install .
```

Now you can run the cli tool binary.

Example run on MS-Windows:

```bash
.\.venv\Scripts\yttran.exe https://www.youtube.com/watch?v=4b0iet22VIk > test-tran.txt
```

## Publish Packge to PyPi for world to use

Make sure verions number of package is incremented as required in pyproject.toml

```bash
uv build
uv publish
```
You’ll need your PyPI credentials (username and password).

After publishing, verify your package is live on PyPI by visiting:

`https://test.pypi.org/project/yttran/`


## Installation Published Public Package for use on local PC

If you have [`uvx`](https://github.com/astral-sh/uvx) installed, you can run `yttan` directly from PyPI without manual dependency management:

```bash
uvx yttran <youtube-video-url-or-id> > transcript.txt
```
