install:
	pip install . --user

uninstall:
	pip uninstall pymadx

develop:
	pip install --editable . --user

# bumpversion is a python utility available via pip.  Make sure to add
# your pip user install location's bin directory to your PATH.
bump-major:
	bumpversion major setup.py setup.cfg

bump-minor:
	bumpversion minor setup.py setup.cfg

bump-patch:
	bumpversion patch setup.py setup.cfg

pypi-upload:
	python setup.py sdist bdist_wheel; \
	twine upload --repository pypi dist/*
