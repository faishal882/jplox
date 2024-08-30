import sys
import pathlib
from libs import tokenizer

def main() -> None:
    filename = sys.argv[1]
        
    file_contents = pathlib.Path(filename).read_text()

    scanner = tokenizer.Scanner(file_contents)

    tokens, errors = scanner.scan_tokens()

    for token in tokens:

        print(token)

    for error in errors:

        print(error, file=sys.stderr)

    if errors:

        exit(65)

if __name__ == "__main__":

    main()
