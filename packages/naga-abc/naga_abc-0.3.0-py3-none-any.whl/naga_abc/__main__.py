from pathlib import Path
from .speakers import Justin
# from naga_abc.speakers import Justin


def main():
    Justin().print_name()
    with (Path(__file__).parent / "names.txt").open("r") as file:
        print(file.read())

if __name__ == "__main__":
    main()
