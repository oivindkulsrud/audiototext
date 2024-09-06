# intro
Script to do audio to text from the terminal. Developed and tested on the mac but probably works fine on linux as well.


# Install ffmpeg and portaudio

brew install ffmpeg
brew install portaudio

or

sudo apt-get install ffmpeg
maybe portaudio? not sure

# install python packages
poetry install

# run the app
poetry run python app.py

# make the runner executable
chmod +x app_runner_macos
you can then drag the app_runner_macos file to your dock and run it from there

(you also need to make the terminal app you use close automatically on exit, or at least you should consider it)