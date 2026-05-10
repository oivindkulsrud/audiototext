.PHONY: run debug local microphones

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
