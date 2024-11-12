PYTHON := python

SCRIPT := log_interpreter.py

IMAGE_NAME := hw01

# Define Docker Compose file
COMPOSE_FILE := docker-compose.yml

# Define requirements file
REQUIREMENTS := requirements.txt

# Define default target
all: help

# Define help target
help:
	@echo "Usage:"
	@echo "  make run-local    Run the script locally"
	@echo "  make run-docker   Run the script in a Docker container"
	@echo "  make build        Build the Docker image"
	@echo "  make up           Start the Docker Compose application"
	@echo "  make clean        Remove build artifacts"
	@echo "  make lint         Run pylint"
	@echo "  make format       Run black"
	@echo "  make test         Run pytest"

# Define run-local target
run-local:
	$(PYTHON) $(SCRIPT)

# Define the run-docker target
run-docker: build
	docker run -v $(PWD)/logs:/app/logs -v $(PWD)/reports:/app/reports $(IMAGE_NAME)

# Define build target
build:
	docker build -t $(IMAGE_NAME) .

# Define the up target
up:
	docker-compose -f $(COMPOSE_FILE) up --build

# Define the clean target
clean:
	docker rmi $(IMAGE_NAME)
	docker-compose -f $(COMPOSE_FILE) down -v
	rm -rf __pycache__

# Define the install requirements target
pip-install:
	$(PYTHON) -m pip install -r $(REQUIREMENTS)

# Define the lint target
lint:
	pylint $(SCRIPT)

# Define the format target
format:
	black $(SCRIPT)

# Define the test target
test:
	pytest ./tests/test_log_parser.py

.PHONY: all help run-local run-docker build up clean pip-install lint format test
