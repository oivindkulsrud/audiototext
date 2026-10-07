"""Install the current checkout's recorder shortcut for the current GNOME user."""

import os
from pathlib import Path
import shlex
import shutil

from gi.repository import Gio, GLib


def main():
    ptyxis = shutil.which("ptyxis")
    uv = shutil.which("uv")
    if not ptyxis or not uv:
        raise SystemExit("Install Ptyxis (sudo dnf install ptyxis) and uv first.")

    project = Path(__file__).resolve().parent.parent
    binding = os.environ.get("SHORTCUT", "<Control><Alt><Shift><Super>less")
    if not binding.strip():
        raise SystemExit("SHORTCUT must not be empty.")

    schema = "org.gnome.settings-daemon.plugins.media-keys"
    path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/audiototext/"
    settings = Gio.Settings.new(schema)
    shortcut = Gio.Settings.new_with_path(schema + ".custom-keybinding", path)
    command = shlex.join([
        ptyxis, "--new-window", "--title", "Audio Recorder",
        "--working-directory", str(project), "--", "/usr/bin/env", f"UV_BIN={uv}",
        "/bin/bash", str(project / "app_runner_fedora"),
    ])
    paths = settings.get_strv("custom-keybindings")
    values = {"name": "Audio Recorder", "command": command, "binding": binding}
    if not settings.is_writable("custom-keybindings") or not all(
        shortcut.is_writable(key) for key in values
    ):
        raise SystemExit("GNOME shortcut settings are not writable for this user.")

    for key, value in values.items():
        if not shortcut.set_string(key, value):
            raise SystemExit(f"Could not set shortcut {key}.")
    if path not in paths:
        if not settings.set_strv("custom-keybindings", [*paths, path]):
            raise SystemExit("Could not register shortcut.")
    Gio.Settings.sync()
    print(f"Installed Audio Recorder shortcut: {binding}")


if __name__ == "__main__":
    try:
        main()
    except GLib.Error as error:
        raise SystemExit(str(error)) from error
