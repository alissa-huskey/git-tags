PREFIX ?= ~/.local
MANDIR ?= $(PREFIX)/share/man
PIP ?= ~/.asdf/shims/pip

## these lines are included in help
## nodoc
NAME = git-tags
MAKEFILE = $(word 1, $(MAKEFILE_LIST))  ## default: Makefile
MSG =
## end-nodoc

install:  clean build   ## help: install package locally
	@install share/man/man1/$(NAME).1 $(MANDIR)/man1/$(NAME).1
	@$(PIP) install dist/*.whl --disable-pip-version-check

uninstall:   ## help: uninstall package
	@rm -f $(MANDIR)/man1/$(NAME).1
	@$(PIP) uninstall --yes $(NAME) -qq

reinstall: | uninstall install ## help: reinstall package

build:       ## help: build package
	@tools/mkman
	@poetry build

clean:       ## help: remove build files
	@rm -rf dist

test:        ## help: run tests
	@xdoctest -m tools
	@xdoctest -m gittags

bump:        ## help: bump version
	poetry version patch
	sed -i'' -Ee "s/^__version__ = .*$$/__version__ = '$$(poetry version -s)'/" gittags/__init__.py

tag:                    ## help: [MSG=""] create tag at HEAD
	message="$(MSG)" ; git tag -f "v$$(poetry version -s)" $${message:+-m "$$message"}

help:        ## help: show this help screen
	@echo $(NAME) Makefile
	@echo
	@echo  "  usage: make [ <target> ] [ <OPTION>=<VALUE> ]"
	@echo
	@echo "Targets:"
	@echo 
	@sed -nEe '/^[a-z]+:.*## help:/ { s/^([a-z]+):.+ ## help:/\x1b[36m\1\x1b[0m\t/ p ; }' $(MAKEFILE) \
		| sort | column -ts $$'\t'
	@echo
	@echo
	@echo "Options:"
	@echo
	@sed -nEe '/^## nodoc/,/^## end-nodoc/ { /^##/ !{ s,^([A-Z]+),\x1b[36m\1\x1b[0m, ; /##/ { s/=.+## default:/=/ ; } ; p ; } ; } ;' \
		$(MAKEFILE) | sort | column -ts $$'\t'
	@echo
	@echo


.PHONY: build bump clean help install reinstall tag test uninstall cmd
.DEFAULT_GOAL := help
