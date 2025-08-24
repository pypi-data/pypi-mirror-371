from setuptools import setup, find_packages
from setuptools.command.install import install
import sys

class CustomInstallCommand(install):
    def run(self):
        print("*****************************************************")
        print("Message : This snapkit library has been developed by Tamal Mallick (github/mallickboy)")
        print("""Libraries: 
              1. jpg_to_png (jpg/jpeg to png converter) 
              """)
        print("Installing my custom library...")
        print("*****************************************************")
        sys.stdout.flush()
        install.run(self)

setup(
    name="snapkit",
    version="0.0.2",
    description="SnapKit: Handy image utilities for AI/CV workflows",
    long_description="""\
        SnapKit is a lightweight toolkit for everyday image-related tasks
        in AI, Computer Vision, and ML workflows. 

        Current Modules:
        - jpg_to_png: Convert JPEG/JPG images to PNG (multi-threaded for speed)

        Roadmap:
        - More conversion utilities
        - Visualization helpers
        - Stitching & plotting tools
        - CLI-first design for productivity

        Author: Tamal Mallick (github.com/mallickboy)
        License: MIT
        """,
    long_description_content_type="text/plain",
    author="Tamal Mallick",
    author_email="contact@mallickboy.com",
    url="https://github.com/mallickboy/snapkit",
    license="MIT",
    install_requires=[
        "Pillow",
        "tqdm",
    ],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
    ],
    entry_points={
        "console_scripts": [
            "snapkit = snapkit.utils.cli.cli_handler:main",
        ],
    },
)
