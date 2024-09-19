.PHONY: build clean install test

# Build the package
build:
	python -m build

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info

# Install the package locally
install:
	pip install .

# Run tests
test:
	pytest tests/
