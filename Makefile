# Makefile for building and testing generics and pipeline

.PHONY: all setup clean test lint test-generics test-pipeline build-generics build-pipeline clean-generics clean-pipeline clean

# Default target
all: clean lint test build install

dev: clean lint test build

setup:
	@echo "Setting up linters..."
	pip install flake8 pytest

install: install-generics install-pipeline
	@echo "All packages installed."

# Install generics
install-generics:
	@echo "Installing generics package..."
	pip install $(wildcard generics/dist/*.whl)

# Install pipeline
install-pipeline:
	@echo "Installing pipeline package..."
	pip install $(wildcard pipeline/dist/*.whl)

lint:
	flake8 generics pipeline
	@echo "Lint complete."

test: test-generics test-pipeline
	@echo "All tests passed."

# Test generics
test-generics:
	@echo "Testing generics package..."
	cd generics && pytest -v tests & cd ..

# Test pipeline
test-pipeline:
	@echo "Testing pipeline package..."
	cd pipeline && pytest -v tests & cd ..

# Build all packages
build: build-generics build-pipeline

# Build generics
build-generics:
	@echo "Building generics package..."
	cd generics && python -m build & cd ..

# Build pipeline
build-pipeline:
	@echo "Building pipeline package..."
	cd pipeline && python -m build & cd ..

# Clean build artifacts for generics
clean-generics:
	@echo "Cleaning build artifacts for generics..."
	python -c "import shutil; shutil.rmtree('generics/dist', ignore_errors=True); shutil.rmtree('generics/build', ignore_errors=True); shutil.rmtree('generics/*.egg-info', ignore_errors=True)"
	python -c "import shutil, glob; [shutil.rmtree(d, ignore_errors=True) for d in glob.glob('generics/*.egg-info')]"

# Clean build artifacts for pipeline
clean-pipeline:
	@echo "Cleaning build artifacts for pipeline..."
	python -c "import shutil; shutil.rmtree('pipeline/dist', ignore_errors=True); shutil.rmtree('pipeline/build', ignore_errors=True); shutil.rmtree('pipeline/*.egg-info', ignore_errors=True)"
	python -c "import shutil, glob; [shutil.rmtree(d, ignore_errors=True) for d in glob.glob('pipeline/*.egg-info')]"

# Clean build artifacts for both packages
clean: clean-generics clean-pipeline
	@echo "All build artifacts cleaned."


release: release-patch

release-patch: clean lint test build
	bump2version patch  --commit --tag
	git push && git push --tags

release-minor: clean lint test build
	bump2version minor  --commit --tag
	git push && git push --tags

release-major: clean lint test build
	bump2version major  --commit --tag
	git push && git push --tags