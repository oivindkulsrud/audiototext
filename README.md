
# Intro

Script to do audio to text from the terminal. Developed and tested on Mac, but likely works fine on Linux as well.

# OpenAI API Key Setup

This application requires an OpenAI API key for the audio transcription. You can set it up in one of two ways:

**macOS/Linux:**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Windows PowerShell:**

```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

OR create a `.env` file in the project root:

**macOS/Linux:**

```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

**Windows PowerShell:**

```powershell
Set-Content .env "OPENAI_API_KEY=your-api-key-here"
```

*Note: Make sure not to commit your `.env` file to version control. Add it to your `.gitignore` file.*

# Install ffmpeg and portaudio

**macOS:**

```sh
brew install ffmpeg
brew install portaudio
```

**Linux (Debian/Ubuntu):**

```sh
sudo apt-get install ffmpeg portaudio19-dev
```

**Linux (Fedora):**

```sh
sudo dnf install ffmpeg portaudio-devel
```

*Note: On Linux, you may need the PortAudio development package for Python bindings to build correctly. On Debian/Ubuntu this is `portaudio19-dev`; on Fedora this is `portaudio-devel`.*

**Windows10:**

```powershell
choco install ffmpeg-full
```

Or with winget:

```powershell
winget install Gyan.FFmpeg
```

After installing ffmpeg on Windows, open a new PowerShell window so the updated `PATH` is loaded.

# Install uv

**Windows PowerShell:**

```powershell
winget install astral-sh.uv
```

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# Install Python packages

```bash
uv sync
```

# Run the app

```bash
uv run python app.py
```

*Follow the prompts to record audio and get the transcription.*

# GNOME keyboard shortcut

On Fedora GNOME, install **Hyper+<** for the current user with:

```bash
make install-shortcut-fedora
```

Run this from your desktop session, without `sudo`. Requires Ptyxis (`sudo dnf install ptyxis`), uv, and Fedora's system Python with PyGObject (`sudo dnf install python3-gobject`). It launches this checkout, preserves existing shortcuts, and updates the same entry when rerun.

The default binding is `<Control><Alt><Shift><Super>less`, matching a Hyper key that sends Ctrl+Alt+Shift+Super. If your keyboard uses GNOME's separate Hyper modifier, use:

```bash
make install-shortcut-fedora SHORTCUT='<Hyper>less'
```

The target registers the shortcut; your Hyper key must already be configured. You can override `SHORTCUT` with any other [GTK accelerator](https://docs.gtk.org/gtk4/func.accelerator_parse.html).

To launch the recorder from GNOME keyboard shortcuts with Ptyxis, paste this command into the keyboard manager:

```bash
ptyxis --new-window \
  --title 'Audio Recorder' \
  --working-directory /home/klsrd/cb/software/audiototext \
  -- /usr/bin/env UV_BIN=/home/linuxbrew/.linuxbrew/bin/uv \
  /bin/bash /home/klsrd/cb/software/audiototext/app_runner_fedora
```

Adjust `UV_BIN` to your uv executable (`command -v uv`). Rerun
`make install-shortcut-fedora` to update an existing installed shortcut, or replace
its command with the launcher command above.

The global `DEBUG_MODE` variable in `app_runner_fedora` defaults to `false`, so
the terminal closes automatically. Set `DEBUG_MODE=true` to enable debugging.
In debug mode, after the recorder exits, it opens an interactive shell in the same terminal so
logs and tracebacks remain visible, including failures in uv or Python startup.
Type `exit` to close the terminal.
Python output is unbuffered so logs appear as they are written.

If `OPENAI_API_KEY` is missing from the shortcut's environment, the Fedora launcher
sources `~/.config/personal-pc-secrets-filen/main_machine.sh` when readable and
exports the key to Python. An existing environment key takes precedence. The app
also supports a project `.env` file as described above.

# Run with local Whisper

```bash
uv run python app.py --local --language en
```

# Make the runner executable

```sh
chmod +x app_runner_macos
```

You can then drag the `app_runner_macos` file to your dock and run it from there.

*You may want your terminal app to close automatically on exit for convenience.*

# Compile AppleScript (macOS only)

```sh
osacompile -o TalkPaste.app dictation_with_paste.applescript
fileicon set TalkPaste.app /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarMicrophone.icns
```

---

Let me know if you want to clarify or expand any of these steps!
