"""Independent finite check of the paired-transformation generation claim.

This is an audit aid, not a proof of the lower bound.  Python standard library.
Unlike witness_verification.py, this enumerates transformation pairs rather
than source/target computations.  Append a letter using the two physically
opposite composition conventions specified in the manuscript.
"""

import argparse
from pathlib import Path
from collections import deque
from math import factorial


def compose(f, g):
    return tuple(f[v] for v in g)


def inverse(f):
    out = [0] * len(f)
    for i, j in enumerate(f):
        out[j] = i
    return tuple(out)


def generators(t):
    r = t if t % 2 else t - 1
    c = tuple((i + 1) % r if i < r else i for i in range(t))
    p = list(range(t))
    a, b = (0, 1) if t % 2 else (t - 2, t - 1)
    p[a], p[b] = p[b], p[a]
    e = (1,) + tuple(range(1, t))
    return c, tuple(p), e


def check(k, ell):
    ck, dk, ek = generators(k)
    cl, dl, el = generators(ell)
    letters = ((ck, dl), (dk, inverse(cl)), (ek, el))
    identity = (tuple(range(k)), tuple(range(ell)))
    seen = {identity}
    pending = deque([identity])
    while pending:
        f, g = pending.popleft()
        for fx, gx in letters:
            h = compose(fx, f), compose(g, gx)
            if h not in seen:
                seen.add(h)
                pending.append(h)
    expected = factorial(k) * factorial(ell) + (
        k**k - factorial(k)
    ) * (ell**ell - factorial(ell))
    assert len(seen) == expected
    assert all(
        (len(set(f)) == k) == (len(set(g)) == ell) for f, g in seen
    )
    message = (
        f"({k},{ell}): {len(seen):,} pairs; expected {expected:,}; "
        "all independent unit pairs and all paired singular maps present."
    )
    print(message)
    return message


def main():
    if not __debug__:
        raise SystemExit("Run without -O or PYTHONOPTIMIZE: verification requires assertions.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().parent / 'results' / 'audit_generation_check.txt',
                        help='Result text path (default: results/ beside this script)')
    args = parser.parse_args()
    report = [check(*dimensions) for dimensions in ((3, 3), (3, 4), (4, 4))]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(report)+'\n', encoding='utf-8')


if __name__ == "__main__":
    main()
