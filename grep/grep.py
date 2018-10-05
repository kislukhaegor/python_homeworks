"""
This is simple grep module
"""


import argparse
import sys
import re


def output(line):
    """
    Output lines from grep.
    """

    print(line)


def get_re_line(line):
    """
    Converts grep pattern to regular expression for re.
    """

    replacements = {"*": ".*", "?": "."}
    new_line = line
    for temp in replacements:
        new_line = new_line.replace(temp, replacements[temp])
    return new_line


def get_match_count(lines, params, regular):
    """
    Returns count of match in lines

    regular - compiled regular from re.compile
    """

    count = 0
    for line in lines:
        line = line.rstrip()
        if bool(regular.search(line)) ^ params.invert:
            count += 1
    return count


def make_output_line(line, index=0, is_main=True, show_number=False):
    """
    Converts line to grep output format

    is_main - True if line gets by matching pattern.
    If line gets by context it's must be False.
    """

    if not show_number:
        return line

    join_line = ':' if is_main else '-'
    return join_line.join([str(index), line])


def parse_lines(lines, params, regular):
    """
    Parse lines and output it.

    regular - compiled regular from re.compile
    """

    before_size = max(params.before_context, params.context)
    after_size = max(params.after_context, params.context)
    last_match_index = -after_size
    last_lines = []

    for index, line in enumerate(lines):
        index += 1  # because we count with 1 :(
        line = line.rstrip()
        if bool(regular.search(line)) ^ params.invert:
            last_match_index = index
            for last_index, last_line in last_lines:
                output(make_output_line(last_line,
                                        last_index,
                                        False,
                                        params.line_number))
            last_lines.clear()
            output(make_output_line(line,
                                    index,
                                    True,
                                    params.line_number))
        else:
            if (index - last_match_index) <= after_size:
                output(make_output_line(line,
                                        index,
                                        False,
                                        params.line_number))
            else:
                last_lines.append((index, line))
                if len(last_lines) > before_size:
                    del last_lines[0]


def grep(lines, params):
    """
    It's simple grep.

    lines - lines in which need to search matching lines

    params - parsed args from command line
    """

    flags = re.I if params.ignore_case else 0
    regular = re.compile(get_re_line(params.pattern), flags)
    if params.count:
        count = get_match_count(lines, params, regular)
        output(str(count))
    else:
        parse_lines(lines, params, regular)


def parse_args(args):
    """
    Parsing args from command line
    """

    parser = argparse.ArgumentParser(description='This is a simple grep \
                                                  on python')
    parser.add_argument(
        '-v',
        action="store_true",
        dest="invert",
        default=False,
        help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i',
        action="store_true",
        dest="ignore_case",
        default=False,
        help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, \
              starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context \
              surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern',
                        action="store",
                        help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    """
    Main function
    """

    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
