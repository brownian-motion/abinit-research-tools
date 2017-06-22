from __future__ import print_function # https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
import sys # for reading command line args

def errprint(*args, **kwargs):
    """
    prints to stderr using print()
    see https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    """
    print(*args, file=sys.stderr, **kwargs)

def get_input_file(function_that_displays_help_message):
    """
    Gets a handle to the file passed as input.
    If a file name was passed as the first command line argument, returns that.
    If a help flag [-h | --help | /h | /?] was passed instead, prints a help message and exits.
    Otherwise, returns a handle to stdin, to read a file from there.
    """
    if len(sys.argv) < 2:
        errprint("No input file specified. Reading from stdin")
        return sys.stdin
    elif is_help_flag(sys.argv[1]):
        function_that_displays_help_message()
        exit()
    else:
        return open(sys.argv[1], "r")

def is_help_flag(flag):
    """
    determines whether the given string is a flag indicating the user wants help.
    Returns true if flag is -h, --help, /?, or /h
    """
    return (flag == "-h") or (flag == "/h") or (flag == "--help") or (flag ==  "/?")
