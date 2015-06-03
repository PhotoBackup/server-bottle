all:
	[ -e venv/bin/pip ] || pyvenv venv
	./venv/bin/pip install bottle logbook
