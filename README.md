**Summary:**
You want the step-by-step guide integrated into your provided format, including both macOS and Linux installation instructions.

---

# Intro

Script to do audio to text from the terminal. Developed and tested on Mac, but likely works fine on Linux as well.

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

*Note: On Linux, you may need to use `portaudio19-dev` for Python bindings to build correctly.*

# Install Python packages

```sh
poetry install
```

# Run the app

```sh
poetry run python app.py
```

*Follow the prompts to record audio and get the transcription.*

# Make the runner executable (macOS only)

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
