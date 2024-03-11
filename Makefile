init:
# Detect if uv is installed
	@which uv || (echo "uv is not installed, please install it first" && exit 1)
# Install virtual env
	@uv venv
	source .venv/bin/activate

install:
	@uv pip install -r requirements.txt

freeze:
	@uv pip freeze > requirements.txt

test:
	@pytest tests

lint:
	@python3 -m ruff check . --fix