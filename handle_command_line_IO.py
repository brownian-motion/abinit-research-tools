from __future__ import print_function # https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
import sys # for reading command line args

def errprint(*args, **kwargs):
    """
    prints to stderr using print()
    see https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    """
    print(*args, file=sys.stderr, **kwargs)

def get_input_file_and_args(function_that_displays_help_message):
    """
    Gets a file handle to the input, and remaining unused arguments, as a tuple
    If a file name was passed as the first command line argument, returns a handle to that.
    If a help flag [-h | --help | /h | /?] was passed instead, prints a help message and exits.
    Otherwise, returns a handle to stdin, to read input from there.
    """
    if len(sys.argv) < 2:
        errprint("No input file specified. Reading from stdin")
        return sys.stdin, [] #no excess arguments
    elif is_help_flag(sys.argv[1]):
        function_that_displays_help_message()
        exit()
    else:
        return open(sys.argv[1], "r"), sys.argv[2:]

def get_input_file(function_that_displays_help_message):
    """
    Gets a file handle to the input, ignoring extra command line arguments.
    If a file name was passed as the first command line argument, returns a handle to that.
    If a help flag [-h | --help | /h | /?] was passed instead, prints a help message and exits.
    Otherwise, returns a handle to stdin, to read input from there.

    See get_input_file_and_args
    """
    input_file, _ = get_input_file_and_args(function_that_displays_help_message)
    return input_file

def is_help_flag(flag):
    """
    determines whether the given string is a flag indicating the user wants help.
    Returns true if flag is -h, --help, /?, or /h
    """
    return (flag == "-h") or (flag == "/h") or (flag == "--help") or (flag ==  "/?")
