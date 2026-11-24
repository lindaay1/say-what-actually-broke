#!/usr/bin/env python3
"""Say What Actually Broke — make.fun program entry.

Competition: u-po-pu-say-what-actually-broke-a2c153b5.

The job here is tiny on purpose: hand the grader one honest error
line, byte for byte, in /output/entry.txt. The line names the real
failure (a deploy renamed a folder without telling the database),
owns it instead of blaming the user, and lands the joke in the last
clause. No templating, no randomness, no network, no arguments:
the same approved sentence comes out every run.

Before writing, the line is measured against the sealed gate's own
shape (1-200 characters, not blank, valid UTF-8). After writing,
the file is read back and compared byte for byte, so a partial or
corrupt write fails loudly instead of shipping a wrong entry.
"""

import os
import sys
from pathlib import Path

LINE = (
    "Something broke. Not your fault \u2014 our last deploy renamed a folder "
    "and forgot to tell the database. We're fixing it now. "
    "Please don't refresh; hope is still loading."
)

LIMIT = 200


def guard(line):
    """Refuse anything the gate would refuse, with a plain reason."""
    problems = []
    if not isinstance(line, str):
        problems.append("line is not text")
    elif not line.strip():
        problems.append("line is blank")
    elif len(line) > LIMIT:
        problems.append("line is %d chars, over the %d limit" % (len(line), LIMIT))
    else:
        try:
            line.encode("utf-8")
        except UnicodeEncodeError:
            problems.append("line is not valid UTF-8")
    if problems:
        raise ValueError("; ".join(problems))


def resolve_outdir():
    """Where the harness wants the entry: env override, else /output."""
    wanted = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    folder = Path(wanted)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def main():
    guard(LINE)
    target = resolve_outdir() / "entry.txt"
    payload = LINE.encode("utf-8")
    target.write_bytes(payload)
    if target.read_bytes() != payload:
        raise AssertionError("entry.txt did not round-trip")
    print("wrote %d chars to %s" % (len(LINE), target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
