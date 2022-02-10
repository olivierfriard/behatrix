create_wheel:
	rm -rf *.egg-info build dist; python3 setup.py sdist bdist_wheel


upload_pip_test:
	python3 -m twine upload --config-file /home/olivier/.pypirc --repository testpypi dist/*


upload_pip:
	python3 -m twine upload --config-file /home/olivier/.pypirc --repository pypi dist/*









