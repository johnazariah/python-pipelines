# Makefile for building and testing generics and pipeline

.PHONY: all build-generics build-pipeline clean-generics clean-pipeline clean

# Default target
all: build-generics build-pipeline

# Build generics
build-generics:
	@echo "Building generics package..."
	cd generics && python -m build

# Build pipeline
build-pipeline:
	@echo "Building pipeline package..."
	cd pipeline && python -m build

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