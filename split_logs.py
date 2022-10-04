import os
import sys


def get_log_file(hamr_dir, host, log_type):
    subdomain = host.split(".", maxsplit=1)[0]
    return os.path.join(hamr_dir, f"apps/{subdomain}/logs/{log_type}.log")

if len(sys.argv) < 3:
    raise Exception("log_type and hamr_dir args are required")

hamr_dir, log_type= sys.argv[1:3]

for line in sys.stdin:
    host, rest = line.split(maxsplit=1)
    with open(get_log_file(hamr_dir, host, log_type), "a") as f:
        f.write(rest)
