import sys

def print_progress(current, total):
    _format = 'processing {0} of {1}'
    if current > 1:
        _format = '\r' + _format

    sys.stdout.write(_format.format(current, total))
    sys.stdout.flush()
