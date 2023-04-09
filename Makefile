
clean:
	rm -rf dist build tsidpy.egg-info

build:
	python3 -m build

submit:
	python3 -m twine upload --repository pypi dist/* --verbose

submit-test:
	python3 -m twine upload --repository testpypi dist/* --verbose

install-test:
	python3 -m pip install --index-url https://test.pypi.org/simple/ tsidpy
