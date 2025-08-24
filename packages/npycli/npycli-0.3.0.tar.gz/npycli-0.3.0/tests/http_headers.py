from sys import argv
from typing import Annotated
from npycli import Command
from npycli.parameters import Alias


def http_headers(
    *,
    headers: Annotated[tuple[str], Alias("header", private=True)]
):
    for header in headers:
        print(f"{header}\\r\\n")
    print("\\r\\n")


if __name__ == "__main__":
    cmd: Command = Command(http_headers, ("http-headers",))
    cmd(argv[1:])
