import sys
import pathlib
from libs import tokenizer, parser 

def inspect_object(obj):
    print("Class:", obj.__class__.__name__)
    print("Attributes and values:")
    for attr, value in vars(obj).items():
        print(f"  {attr}: {value}")

def main() -> None:
    command = sys.argv[1]
    filename = sys.argv[2]
        
    file_contents = pathlib.Path(filename).read_text()

    if(command == "tokenize"):
        scanner = tokenizer.Scanner(file_contents)
        tokens, errors = scanner.scan_tokens()

        for token in tokens:
            print(token)

        for error in errors:
            print(error, file=sys.stderr)

        if errors:
            exit(65)
        else:
            exit(0)

    elif(command == "parse"):
        tokens = tokenizer.Scanner(file_contents).scan_tokens()[0]
        parse = parser.Parser(tokens)
        ast = parse.expression()
        printer = parser.AstPrinter()
        print(printer.print(ast))
        # inspect_object(ast)

if __name__ == "__main__":

    main()
