# TTS_ka
Lightweight CLI for text-to-speech using the `edge-tts` engine with caching, chunking and parallel generation.

## Languages supported
- Georgian (ka)
- English (en, en-US)
- Russian (ru)

## Requirements
- Python 3.8+ recommended
- Notable runtime extras:
    - `edge-tts` (required)
    - `pydub` (optional, used for faster/robust merging)
    - `ffmpeg` (required if `pydub` is available or when falling back to ffmpeg concat)
    - `tqdm` (optional, nicer progress bars)
    - `pyperclip` (optional, clipboard support)

Install locally for development:

```sh
pip install -r src/TTS_ka/requirements.txt
```

Or install the package (when published):

```sh
pip install TTS_ka
```

## CLI usage
Basic example:

```sh
python -m TTS_ka --lang en "Hello, how are you?"
```

Long text example with chunking and parallel generation:

```sh
python -m TTS_ka tests/test_reading.txt --lang en --chunk-seconds 45 --parallel 3
```

Key flags
- `--lang <code>` : language code (e.g., `ka`, `en`, `ru`).
- `--chunk-seconds N` : split long texts into chunks of approx N seconds (0 = disabled).
- `--parallel N` : number of concurrent workers when generating chunks.
- `--no-play` : do not auto-play the resulting MP3.
- `--no-cache` : do not use or write cache during this run.
- `--clear-cache` : delete all `.tts_cache_*.mp3` files before running (use with `--dry` to preview).
- `--dry` : with `--clear-cache` (or `--cache-age-days`) only report how much would be removed.
- `--cache-age-days N` : when used without a text argument, delete cache files older than N days and exit.
- `--clear-all-artifacts` : when clearing cache, also delete `.part_*.mp3` and `data*.mp3` files.
- `--keep-parts` : (future) keep generated part files after merging for inspection.

Cache behavior
- The tool caches generated MP3s as `.tts_cache_<sha>.mp3` to speed repeated conversions of the same text/voice.
- Use `--no-cache` to bypass cache for a one-off run.
- Use `--clear-cache` to remove all cached files; `--dry` shows how much space would be freed.
- Use `--cache-age-days N` to remove cache files older than N days (dry mode supported).

Notes & troubleshooting
- Merging parts requires `ffmpeg` on PATH; install it if you get merge errors.
- Increasing `--parallel` can speed up generation but may hit provider rate limits; try 2–4 and monitor for errors.
- If you want the CLI available as a system command, install the package or add a small launcher script that calls `python -m TTS_ka`.

Example: preview and clear cache

```sh
# show how much cache would be removed
python -m TTS_ka --clear-cache --dry

# actually clear cache
python -m TTS_ka --clear-cache
```

If you want more examples or to add a feature to the README (e.g., scheduled cleanup or custom cache dir), tell me which and I'll add it.


## AutoHotkey integration (`read.ahk`)

This repo includes an AutoHotkey v2 script `read.ahk` that integrates with the CLI for one-key reading of clipboard text and a few handy productivity hotkeys.

Where the script calls the CLI it uses `py -m TTS_ka` (so it runs the installed package or your local module when running from the repo).

Main actions
- Alt+E — read clipboard as English: runs the CLI with `--lang en` on the current clipboard text.
- Alt+R — read clipboard as Russian: runs with `--lang ru`.
- Alt+X — read clipboard as Georgian: runs with `--lang ka`.

The script launches the CLI inside `cmd /k` so the terminal remains open after the command completes. The `read.ahk` call looks like:

```
cmd := "cmd /k py -m TTS_ka --lang " . lang . " clipboard --chunk-seconds 45 --parallel 6 --no-cache"
Run(cmd)
```

Tips and customization
- If you want caching enabled when launched from AHK, remove the `--no-cache` flag in the `cmd` string.
- Lower `--parallel` to 2–3 if you see network or rate-limit errors.
- To read a file instead of clipboard, modify the `Run` command to pass a file path instead of `clipboard` (example in the script comments).

Extra hotkeys in the script
- Alt+L toggles an auto-clicker with configurable interval.
- Alt+M toggles holding the left mouse button down (useful for drag operations).
- Ctrl+R (when Ctrl pressed) reloads the script.
- Additional mappings open local dashboards and apps when used with Ctrl (see the script for URLs and paths).

How to use
1. Install AutoHotkey v2 (https://www.autohotkey.com/).
2. Double-click `read.ahk` to run it, or run it from your startup folder to enable the hotkeys on login.
3. Copy text, then press Alt+E / Alt+R / Alt+X to speak.

Advanced tips
- If you want the terminal window not to appear at all, change `Run(cmd)` to use `Run()` with the `Hide` option, but note debugging output will be hidden.
- You can replace `py -m TTS_ka` with a full python path (e.g., `C:\Python39\python.exe -m TTS_ka`) if you use a specific environment.
- For very long texts, prefer `--chunk-seconds 30` and `--parallel 3` as a balanced starting point.
- To debug problems (merge failures, missing ffmpeg), remove `--no-cache` temporarily and run the same CLI command manually in a command prompt to inspect output.

If you'd like, I can add a ready-to-run `read.ahk` installer snippet and an optional Windows scheduled task that starts it on login.
