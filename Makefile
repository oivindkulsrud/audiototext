.PHONY: run debug local microphones inst install-deps-ubuntu install-deps-fedora install-deps-macos

PYTHON ?= uv run python
ARGS ?=
MIC ?=
GAIN ?=
MIC_ARG = $(if $(MIC),--input-device-index $(MIC),)
GAIN_ARG = $(if $(GAIN),--gain-db $(GAIN),)

run:
	$(PYTHON) app.py $(MIC_ARG) $(GAIN_ARG) $(ARGS)

debug:
	$(PYTHON) app.py --debug-save-recording $(MIC_ARG) $(GAIN_ARG) $(ARGS)

local:
	$(PYTHON) app.py --local --language en $(MIC_ARG) $(GAIN_ARG) $(ARGS)

microphones:
	$(PYTHON) app.py --list-devices

inst:
	@echo "Use one of: make install-deps-ubuntu, make install-deps-fedora, make install-deps-macos"

install-deps-ubuntu:
	sudo apt-get update
	sudo apt-get install -y ffmpeg portaudio19-dev

install-deps-fedora:
	sudo dnf install -y ffmpeg portaudio-devel

install-deps-macos:
	brew install ffmpeg portaudio
