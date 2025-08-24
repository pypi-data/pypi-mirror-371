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
    name='snapkit',
    version='0.0.1',
    description="SnapKit: Handy image-related utilities for daily AI/CV use.",
    long_description="""\
*****************************************************
Message : This snapkit library has been developed by Tamal Mallick (github/mallickboy)

Modules included:
1. jpg_to_png (jpg/jpeg to png converter)

*****************************************************
""",
    long_description_content_type="text/plain",
    author="Tamal Mallick",
    author_email="contact@mallickboy.com",
    packages=find_packages(),
    url="https://github.com/mallickboy",
    license="MIT",
    install_requires=[
        "Pillow",
        "tqdm"
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
    entry_points={
        "console_scripts": [
            "snapkit = snapkit.utils.cli.cli_handler:main",
        ],
    },
)
