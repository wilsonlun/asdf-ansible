import sys

major = sys.version_info[0]
minor = sys.version_info[1]

if not (major > 3 or (major == 3 and minor >= 5)):
    exit(1)

