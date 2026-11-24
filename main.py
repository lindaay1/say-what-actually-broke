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
    """Refuse anything the gate would refuse, with a plain reason.

    Returns the exact UTF-8 payload to write, so the bytes that were
    checked are the bytes that ship — nothing re-encoded in between.
    """
    problems = []
    if not isinstance(line, str):
        problems.append("line is not text")
    elif not line.strip():
        problems.append("line is blank")
    elif len(line) > LIMIT:
        problems.append("line is %d chars, over the %d limit" % (len(line), LIMIT))
    elif "\n" in line or "\r" in line:
        problems.append("line must stay one line")
    if problems:
        raise ValueError("; ".join(problems))
    try:
        return line.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("line is not valid UTF-8")


def resolve_outdir():
    """Where the harness wants the entry: env override, else /output."""
    wanted = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    folder = Path(wanted)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def main():
    payload = guard(LINE)
    target = resolve_outdir() / "entry.txt"
    target.write_bytes(payload)
    written = target.read_bytes()
    if written != payload or len(written) != len(payload):
        raise AssertionError("entry.txt did not round-trip")
    print("wrote %d chars (%d bytes) to %s" % (len(LINE), len(payload), target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
