from setuptools import setup
from setuptools import find_packages
import os

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def parse_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


requirements = parse_requirements(os.path.join(this_dir, "requirements.txt"))
dev_requirements = parse_requirements(os.path.join(this_dir, "requirements-dev.txt"))
setup(
    name="mongoshelve",
    version="{{VERSION_PLACEHOLDER}}",
    description="Scheduler for automation tasks that involve multiple stations/workers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rishi Kumar",
    author_email="rek010@eng.ucsd.edu",
    download_url="https://github.com/rekumar/roboflo",
    license="MIT",
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    packages=find_packages(),
    include_package_data=True,
    keywords=["research", "science", "machine", "automation"],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "Topic :: Office/Business :: Scheduling",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
