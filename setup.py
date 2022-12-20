# https://stackoverflow.com/questions/44977227/how-to-configure-main-py-init-py-and-setup-py-for-a-basic-package

from setuptools import setup

setup(
    name="behatrix",
    version=[x for x in open("behatrix/version.py", "r").read().split("\n") if "__version__" in x][0]
    .split(" = ")[1]
    .replace('"', ""),
    description="Behatrix - Behavioral Sequences Analysis with permutation test",
    author="Olivier Friard - Marco Gamba",
    author_email="olivier.friard@unito.it",
    long_description=open("README_pip.rst", "r").read(),
    long_description_content_type="text/x-rst",
    url="http://www.boris.unito.it/pages/behatrix",
    python_requires=">=3.6",
    classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Operating System :: OS Independent",
    ],
    packages=["behatrix"],  # same as name
    install_requires=[
        "pyqt5",
        "numpy",
    ],
    # load in behatrix dir
    package_data={
        "behatrix": ["behatrix.qrc", "behatrix.ui", "icons/*"],
        "": ["README.TXT", "LICENSE.TXT"],
    },
    entry_points={
        "console_scripts": [
            "behatrix = behatrix:main",
        ],
    },
)
