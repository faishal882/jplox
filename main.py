import sys
import pathlib
from libs import tokenizer, parser, interpreter 

def remove_trailing_zeros(number_str):
    try:
        number = float(number_str)
        result = ('{:.10f}'.format(number)).rstrip('0').rstrip('.')
        return result
    except:
        return number_str


def main():
    command = sys.argv[1]
    filename = sys.argv[2]
        
    file_contents = pathlib.Path(filename).read_text()

    scanner = tokenizer.Scanner(file_contents)
    tokens, errors = scanner.scan_tokens()
    if command == "tokenize":
        for token in tokens:
            print(token)

        for error in errors:
            print(error, file=sys.stderr)

        if errors:
            exit(65)
        else:
            exit(0)

    elif command == "parse":
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            exit(65)

        parse = parser.Parser(tokens)
        ast = parse.parse()
        if ast is not None:
            printer = parser.AstPrinter()
            print(printer.print(ast))
    
    elif command == "evaluate":
        parse = parser.Parser(tokens)
        ast = parse.parse()

        if ast is not None:
            _interpreter = interpreter.Interpreter()
            try:
                eval = _interpreter.evaluate(ast)
            except Exception as e:
                print(e, file=sys.stderr)
                exit(70)
            print("EVAL: ", remove_trailing_zeros(eval))

    else:
        print("Wrong command")
    
if __name__ == "__main__":
    main()
