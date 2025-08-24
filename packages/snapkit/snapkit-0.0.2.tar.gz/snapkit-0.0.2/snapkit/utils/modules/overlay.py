import argparse
import sys

def overlay() -> None:
    print("Upcoming package")

def cli(argv=None):
    parser = argparse.ArgumentParser(description="Generates overlay using image and mask.")

    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)
    overlay()