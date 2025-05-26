
VECT_SIG := ./vector_sigma
ABS_PATH := $(realpath $(VECT_SIG))

build:
	docker build . -t vector_sig

start:
	echo $(ABS_PATH)
	docker run -v signal-cli-data:/root/.local/share/signal-cli/data  --mount type=bind,source=$(ABS_PATH),target=/src/vector_sigma --gpus all -it vector_sig bash

