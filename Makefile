PYTHON ?= python3
BACKEND ?= docker
.PHONY: all setup build example assets catalogue preview package test validate-release release cheatsheet covers docs-check repo-check clean
all: build
setup:
	$(PYTHON) scripts/build.py --setup --backend $(BACKEND)
build:
	$(PYTHON) scripts/build.py --backend $(BACKEND)
example:
	$(PYTHON) scripts/build.py examples/assets-example.tex --backend $(BACKEND)
assets:
	$(PYTHON) scripts/prepare-assets.py
catalogue:
	$(PYTHON) scripts/build-asset-catalogue.py
	$(PYTHON) scripts/build.py examples/asset-catalogue.tex --backend $(BACKEND)
preview:
	$(PYTHON) scripts/build.py --backend $(BACKEND) --open
cheatsheet:
	$(PYTHON) scripts/build.py examples/icon-cheatsheet.tex --backend $(BACKEND)
covers:
	$(PYTHON) scripts/build.py examples/cover-layouts.tex --backend $(BACKEND)
docs-check:
	$(PYTHON) scripts/check-docs.py
	$(PYTHON) scripts/build-asset-catalogue.py --check
repo-check:
	$(PYTHON) scripts/check-repo.py
package:
	$(PYTHON) scripts/package.py
test:
	$(PYTHON) -m unittest discover -s tests -v
validate-release: package
	$(PYTHON) scripts/validate-release.py --backend $(BACKEND)
release:
	$(PYTHON) scripts/release.py --backend $(BACKEND)
clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('build', ignore_errors=True); shutil.rmtree('dist', ignore_errors=True)"
