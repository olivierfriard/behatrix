create_wheel:
	rm -rf *.egg-info build dist; python3 setup.py sdist bdist_wheel
	
upload_wheel_on_testpypi:
        python3 -m twine upload -r testpypi dist/*
	
upload_wheel_on_pypi:
	python3 -m twine upload -r pypi dist/*




