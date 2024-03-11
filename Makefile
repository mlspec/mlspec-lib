init:
# Detect if uv is installed
	@which uv || (echo "uv is not installed, please install it first" && exit 1)
# Install virtual env
	@uv venv
	source .venv/bin/activate
	export PATH=$(pwd)/.venv/bin:$PATH

install:
	poetry config warnings.export false
	@poetry export --without-hashes > requirements.txt && uv pip install -r requirements.txt

freeze:
	@poetry export --without-hashes > requirements.txt

test:
	@pytest tests

lint:
	@python3 -m ruff check . --fix