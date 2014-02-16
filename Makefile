
all: pep

pep:
	pep8 --first --show-source --show-pep8 --count models views controllers messages.py objects.py main.py

clean:
	rm *.pyc */*.pyc
