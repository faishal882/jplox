import sys
import pathlib
from libs import tokenizer, parser, interpreter 

def castNonetoNil(value):
    if value is None:
         return "nil"
    return str(value)

def remove_trailing_zeros(number_str):
    try:
        number = float(number_str)
        result = ('{:.10f}'.format(number)).rstrip('0').rstrip('.')
        return result
    except:
        return number_str

def flatten(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


def main():
    command = sys.argv[1]
    filename = sys.argv[2]
        
    file_contents = pathlib.Path(filename).read_text()

    scanner = tokenizer.Scanner(file_contents)
    tokens, errors = scanner.scan_tokens()
    parse = parser.Parser(tokens)
    _interpreter = interpreter.Interpreter()
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

        ast = parse.parse()
        if len(ast) == 0:
            exit(65);
        printer = parser.AstPrinter()
        for stmt in ast:
            print(printer.print(stmt))
    
    elif command == "evaluate":
        ast = parse.parse()
        print("EVAL: ", ast)
        if len(ast) == 0 or parse.has_errors:
            print("I AM FUCKED")
            exit(65)

        try:
            for stmt in ast:
                eval = _interpreter.evaluate(stmt)
                print("EVAL: ", remove_trailing_zeros(eval))
        except Exception as e:
            print(e, file=sys.stderr)
            exit(70)

    elif command == "run":
        ast = parse.parse()
        printer = parser.AstPrinter()
        if len(ast) == 0 or parse.has_errors:
            exit(65)

        # print("RUN: ", ast)
        try:
            for stmt in ast:
                result = _interpreter.run(stmt)
                if isinstance(result, list):
                    _result = flatten(result)
                    for r in _result:
                        print(remove_trailing_zeros(r))
                else:
                    if result is not None:
                        print(remove_trailing_zeros(result))
        except Exception as e:
            print(e, file=sys.stderr)
            exit(70)

    else:
        print("Wrong command")
    
if __name__ == "__main__":
    main()
