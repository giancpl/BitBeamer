PYTHON ?= python3
BACKEND ?= docker
.PHONY: all setup build example assets catalogue preview package test validate-release release cheatsheet covers docs-check repo-check clean academic studio studio-catalogue
all: build
setup:
	$(PYTHON) scripts/build.py --setup --backend $(BACKEND)
build:
	$(PYTHON) scripts/build.py --backend $(BACKEND)
academic:
	$(PYTHON) scripts/build.py main-academic.tex --backend $(BACKEND)
studio:
	$(PYTHON) scripts/build.py main-studio.tex --backend $(BACKEND)
studio-catalogue:
	$(PYTHON) scripts/review.py all --backend $(BACKEND)
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
	$(PYTHON) scripts/build-studio-catalogue.py --check
	$(PYTHON) scripts/build-asset-catalogue.py --check
repo-check:
	$(PYTHON) scripts/check-repo.py
package:
	$(PYTHON) scripts/package.py
test:
	$(PYTHON) -m unittest discover -s tests -v
validate-release:
	$(PYTHON) scripts/package.py --style all
	$(PYTHON) scripts/validate-release.py --style all --backend $(BACKEND)
release:
	$(PYTHON) scripts/release.py --backend $(BACKEND)
clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('build', ignore_errors=True)"

.PHONY: studio-review studio-review-package
studio-review:
	$(PYTHON) scripts/review.py selection --backend $(BACKEND)
studio-review-package:
	$(PYTHON) scripts/package-studio-review.py

.PHONY: studio-selection
studio-selection:
	$(PYTHON) scripts/review.py selection --backend $(BACKEND)

.PHONY: studio-slide studio-sync review-check release-review
studio-slide:
	$(PYTHON) scripts/review.py slide $(ID) --backend $(BACKEND)
studio-sync:
	$(PYTHON) scripts/review.py sync
review-check:
	$(PYTHON) scripts/review.py check
release-review:
	$(PYTHON) scripts/release.py --review --backend $(BACKEND)

.PHONY: start-academic start-studio
start-academic:
	$(PYTHON) scripts/build.py start-academic.tex --backend $(BACKEND)
start-studio:
	$(PYTHON) scripts/build.py start-studio.tex --backend $(BACKEND)

.PHONY: studio-customization studio-content-check
studio-customization:
	$(PYTHON) scripts/build.py examples/studio-customization.tex --backend $(BACKEND)
studio-content-check:
	$(PYTHON) scripts/check-studio-content.py --backend $(BACKEND)

.PHONY: studio-models studio-palettes
studio-models:
	$(PYTHON) scripts/review.py models --backend $(BACKEND)
studio-palettes:
	$(PYTHON) scripts/review.py palettes --backend $(BACKEND)

.PHONY: studio-overview
studio-overview:
	$(PYTHON) scripts/build-studio-overview.py --backend $(BACKEND)

# Personal decks: make deck-new DECK=my-talk; use BACKEND=native when installed.
DECK ?= my-talk
STYLE ?= studio
.PHONY: deck-new deck-build deck-check deck-layouts
deck-new:
	$(PYTHON) scripts/deck.py new $(DECK) --style $(STYLE)
deck-build:
	$(PYTHON) scripts/deck.py build $(DECK) --backend $(BACKEND)
deck-check:
	$(PYTHON) scripts/deck.py check $(DECK) --backend $(BACKEND) --preview
deck-layouts:
	$(PYTHON) scripts/deck.py layouts
