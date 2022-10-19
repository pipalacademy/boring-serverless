import os
import sys


def get_log_file(logdir, logtype):
    subdomain = host.split(".", maxsplit=1)[0]
    return os.path.join(logdir, f"{logtype}.log")

def get_log_dir(hamr_dir, host):
    subdomain = host.split(".", maxsplit=1)[0]
    return os.path.join(hamr_dir, "apps", subdomain, "logs")

if len(sys.argv) < 3:
    raise Exception("log_type and hamr_dir args are required")

hamr_dir, log_type= sys.argv[1:3]

for line in sys.stdin:
    host, rest = line.split(maxsplit=1)
    log_dir = get_log_dir(hamr_dir, host)
    if not os.path.exists(log_dir):
        # graceful exit, maybe app doesn't exist
        print(f"logdir ('{log_dir}') does not exist.", file=sys.stderr)
        continue

    with open(get_log_file(log_dir, log_type), "a") as f:
        f.write(rest)
