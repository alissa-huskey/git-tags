NAME = git-tags
PREFIX ?= ~/.local
MANDIR ?= $(PREFIX)/share/man
PIP ?= ~/.pyenv/shims/pip
MAKEFILE = $(word 1, $(MAKEFILE_LIST))

install:  build   ## install package
	@install share/man/man1/$(NAME).1 $(MANDIR)/man1/$(NAME).1
	@$(PIP) install . --disable-pip-version-check

uninstall:   ## uninstall package
	@rm -f $(MANDIR)/man1/$(NAME).1
	@$(PIP) uninstall --yes $(NAME) -qq

reinstall: | uninstall install ## reinstall package

build:       ## build package
	@tools/mkman
	@poetry build

help:        ## show this help screen
	@echo $(NAME) Makefile
	@echo
	@echo  "  usage: make [ <target> ] [ <OPTION>=<VALUE> ]"
	@echo
	@echo "Targets:"
	@echo
	@awk -F'[ ]*(##|:|[|])[ ]*' '/^\w.+:\s*[|].+##/ { printf "  \033[36m%s\033[0m\t%s\n", $$1, $$4 } ; /^\w.+:[^|]+##/ { printf "  \033[36m%s\033[0m\t%s\n", $$1, $$3 }' $(MAKEFILE) | column -ts $$'\t'
	@echo
	@echo "Options:"
	@echo
	@awk -F'[ ]*(=|?=|:=)[ ]*' '/^[A-Z_]+ .+## nodoc/ {next} ; /^[A-Z_]+ .+/ { printf "  \033[36m%s\033[0m\t%s\n", $$1, $$2 }' $(MAKEFILE) | column -ts $$'\t'
	@echo

.PHONY: build help install uninstall vars var
.DEFAULT_GOAL := help
