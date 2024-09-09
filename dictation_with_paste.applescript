-- Get the directory of the current script
-- set scriptDir to POSIX path of (path to me)
set scriptDir to "/Users/kuls/code/audiototext"
set scriptDir to do shell script "cd " & quoted form of scriptDir & " && pwd"

-- Change to the script's directory
do shell script "cd " & quoted form of scriptDir

-- Run the Python app using Poetry
do shell script "/usr/local/bin/poetry run python app.py"

-- Simulate keystroke for Command + Tab
tell application "System Events"
    keystroke tab using {command down}
end tell

delay 0.2

-- Simulate keystroke for Command + V
tell application "System Events"
    keystroke "v" using {command down}
end tell

-- Exit
do shell script "exit 0"
