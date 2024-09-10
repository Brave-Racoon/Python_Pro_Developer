# Define the settings variable
ifneq ($(OS),Windows_NT)
    # Linux/MacOS
    SETTINGS_DIR=settings
    PYTHON=python3
    OS_TYPE=Lin
else
    # Windows
    SETTINGS_DIR=./mysite
    PYTHON=python
    OS_TYPE=Win
endif

# Define default server to run
# DEV_SETTINGS=$(SETTINGS_DIR)/settings_dev.py
DEV_SETTINGS=settings_dev.py
PROD_SETTINGS=$(SETTINGS_DIR)/settings_prod.py

# Update project name
PROJECT_NAME=./mysite

# Define Django commands
dev:
	$(PROJECT_NAME) $(PYTHON) manage.py runserver --settings=$(DEV_SETTINGS)
  
prod:
	$(PYTHON) manage.py runserver --settings=$(PROD_SETTINGS)

migrate-dev:
	$(PROJECT_NAME) $(PYTHON) manage.py migrate --settings=$(DEV_SETTINGS)

migrate-prod:
	$(PYTHON) manage.py migrate --settings=$(PROD_SETTINGS)

# Clean unnecessary files
clean:
	@echo "Cleaning cache and unnecessary files..."
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf build/
	rm -rf dist/
ifeq ($(OS), Windows_NT)
	del /S *.pyc
	del /S "__pycache__" /Q
	del /S *.egg-info /Q
	del /S build /Q
	del /S dist /Q
endif
	@echo "Clean up complete."

# Help command to display available options
help:
	@echo "Django Makefile Commands:"
	@echo " dev:             Run the server with development settings"
	@echo " prod:            Run the server with production settings"
	@echo " migrate-dev:     Run migrations with development settings"
	@echo " migrate-prod:    Run migrations with production settings"
	@echo " clean:           Clean up unnecessary files"
	@echo " help:            Display this help message"
	@echo " print-%:         Print makefile var (replace % to var)"

print-%:
	@echo $*=$($*)

.PHONY: dev prod migrate-dev migrate-prod clean help print-%
