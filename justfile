default:
    just --list

build:
    uv version $(grep '^__version__' behatrix/version.py | awk -F'"' '{print $2}')

    git commit -am "new wheel" || true
    git push

    rm -rf *.egg-info build dist
    uv build

publish:
    uvx twine upload --verbose --repository pypi dist/*


publish_test:
    uvx twine upload --verbose --repository testpypi dist/*









