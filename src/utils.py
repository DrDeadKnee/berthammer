import os


def int_it(rawval):
    """
    Returns an integer with some basic
    string manipuilations and try/catch.
    """
    raw_result = str(rawval).replace("+", "")

    try:
        result = int(raw_result)
    except ValueError:
        result = raw_result

    return result


def prettify_text(string, prefix="\n\t"):
    """
    Returns version of text which fits terminal width,
    allowing for a prefix on each line.
    """
    out = ""
    depth, width = os.popen("stty size", "r").read().split()
    width = int(width)
    if "\t" in prefix:
        width -= 8
    width += len(prefix.replace("\t", "").replace("\n", ""))

    strs = [string[i: i + width] for i in range(0, len(string), width)]

    for i in strs:
        out += f"{prefix}{i}"

    return out
