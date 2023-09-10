#!/usr/bin/python

import sys

#sampleDurationSecs=0.35
sampleDurationSecs=0.5

def convert(line):
    try:
        v = int(line)
    except ValueError:
        sys.stderr.write(f"can't convert '{line}'\n")
        return None

    return int(v/sampleDurationSecs)

def main():
    while True:
        l = sys.stdin.readline()
        if not l:
            return 0
        conv = convert(l)
        if conv is None:
            conv = l
        sys.stdout.write(f"{conv}Hz\n")
        sys.stdout.flush()
    
    
if __name__ == '__main__':
	sys.exit(main())
