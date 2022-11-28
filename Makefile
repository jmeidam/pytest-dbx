#
# vim:ft=make
# Makefile
#
.DEFAULT_GOAL := help
.PHONY: test help


help:  # shows these help instructions
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

hidden: # example undocumented, for internal use only
	@true

install: # runs `poetry install`
	poetry install

showdeps: # runs poetry to show deps
	@echo "CURRENT:"
	poetry show --tree
	@echo
	@echo "LATEST:"
	poetry show --latest

lint: # runs black in check mode
	poetry run black --check .

format: # formats code with Black
	poetry run black .

test: hidden # runs pytest with coverage
	poetry run pytest tests -v --cov pytest_dbx

build: install lint test # runs `poetry build` to build source distribution and wheel
	poetry build
