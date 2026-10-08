#!/usr/bin/env python3
"""Independent audit of the incoming-direction 2n complement construction.

The transition-table compiler follows the manuscript. Correctness is checked
against both a direct source-run simulator and an independently built finite
configuration graph (backward reachability from the accepting configuration).
No pre-existing verifier is imported. All marker states and initial/final states
are counted. A repeated configuration is rejection, never a timeout heuristic.
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
import time
from collections import Counter, deque
from pathlib import Path

LEFT = '<'
RIGHT = '>'


def simulate(n, table, s, f, word):
    tape = (LEFT,) + tuple(word) + (RIGHT,)
    q, pos = s, 0
    seen = set()
    while True:
        if q == f and pos == 0:
            return 'accept', len(seen)
        if (q, pos) in seen:
            return 'loop', len(seen)
        seen.add((q, pos))
        row = table.get((q, tape[pos]))
        if row is None:
            return 'reject', len(seen)
        q, step = row
        pos += step
        assert 0 <= q < n
        assert 0 <= pos < len(tape), ('outside tape', row, tape)


def graph_accepts(n, table, s, f, word):
    """Explicit configuration graph; independent of any DFS compilation."""
    tape = (LEFT,) + tuple(word) + (RIGHT,)
    incoming = [[] for _ in range(n * len(tape))]
    for pos, symbol in enumerate(tape):
        for q in range(n):
            edge = table.get((q, symbol))
            if edge is not None:
                r, delta = edge
                target_pos = pos + delta
                assert 0 <= target_pos < len(tape)
                incoming[target_pos*n+r].append(pos*n+q)
    pending = [f]  # position zero
    reached = {f}
    for vertex in pending:
        for predecessor in incoming[vertex]:
            if predecessor not in reached:
                reached.add(predecessor)
                pending.append(predecessor)
    return s in reached, len(reached)


def complement_directional(n, alphabet, table, s, f, direction):
    """Return (state_count, transition_table, start, final)."""
    if s == f:
        return 2, {}, 0, 1
    if direction[f] == 1:
        return 1, {}, 0, 0
    effective = dict(table)
    effective.pop((f, LEFT), None)
    symbols = (LEFT,) + tuple(alphabet) + (RIGHT,)
    pred = {(q, a): [] for q in range(n) for a in symbols}
    for (p, a), (q, delta) in effective.items():
        assert delta == direction[q]
        pred[q, a].append(p)
    for values in pred.values():
        values.sort()
    result = {(f, LEFT): (f, 1)}
    # B_q is q; F_q is n+q.
    def choose(candidates, symbol, parent):
        for p in candidates:
            if symbol == LEFT and p == s:
                return None
            if ((symbol == LEFT and direction[p] == 1) or
                (symbol == RIGHT and direction[p] == -1)):
                continue
            return p, -direction[p]
        return n + parent, direction[parent]
    for q in range(n):
        for a in symbols:
            if q == f and a == LEFT:
                continue
            if ((a == LEFT and direction[q] == -1) or
                (a == RIGHT and direction[q] == 1)):
                continue
            edge = choose(pred[q, a], a, q)
            if edge is not None:
                result[q, a] = edge
    for p in range(n):
        for a in symbols:
            if (p, a) not in effective:
                continue
            q, _ = effective[p, a]
            edge = choose((r for r in pred[q, a] if r > p), a, q)
            if edge is not None:
                result[n+p, a] = edge
    return 2*n, result, f, n+f


def split_and_complement(n, alphabet, table, s, f):
    effective = dict(table)
    effective.pop((f, LEFT), None)
    incoming = [set() for _ in range(n)]
    for q, delta in effective.values():
        incoming[q].add(delta)
    mixed = sum(len(ds) == 2 for ds in incoming)
    if s == f:
        return (2, {}, 0, 1), mixed, None
    if -1 not in incoming[f]:
        return (1, {}, 0, 0), mixed, None
    clones = {}
    directions = []
    for q, ds in enumerate(incoming):
        for delta in sorted(ds or {-1}):
            clones[q, delta] = len(directions)
            directions.append(delta)
    copy_table = {}
    for (q, _), p in clones.items():
        for a in (LEFT,) + tuple(alphabet) + (RIGHT,):
            edge = effective.get((q, a))
            if edge is not None:
                r, delta = edge
                copy_table[p, a] = clones[r, delta], delta
    copy_s = next(p for (q, _), p in clones.items() if q == s)
    copy_f = clones[f, -1]
    nn = len(clones)
    assert nn == n + mixed
    return complement_directional(nn, alphabet, copy_table, copy_s, copy_f,
                                  directions), mixed, (nn, copy_table, copy_s, copy_f)


def words(alphabet, max_length):
    return [w for size in range(max_length+1)
            for w in itertools.product(alphabet, repeat=size)]


def tables(n, alphabet, direction=None):
    rows = [(q, a) for q in range(n)
            for a in (LEFT,) + tuple(alphabet) + (RIGHT,)]
    options = []
    for q, a in rows:
        allowed = [None]
        for target in range(n):
            for delta in (-1, 1):
                if a == LEFT and delta == -1:
                    continue
                if a == RIGHT and delta == 1:
                    continue
                if direction is not None and delta != direction[target]:
                    continue
                allowed.append((target, delta))
        options.append(allowed)
    for values in itertools.product(*options):
        yield {row: edge for row, edge in zip(rows, values) if edge is not None}


def legal_table(n, table):
    return all(0 <= q < n and 0 <= r < n and delta in (-1, 1)
               and (a != LEFT or delta == 1)
               and (a != RIGHT or delta == -1)
               for (q, a), (r, delta) in table.items())


def check_machine(n, alphabet, table, s, f, suite, stats, direction=None):
    assert legal_table(n, table)
    if direction is None:
        compiled, mixed, split = split_and_complement(n, alphabet, table, s, f)
        assert compiled[0] <= 2*n + 2*mixed
    else:
        compiled = complement_directional(n, alphabet, table, s, f, direction)
        assert compiled[0] <= 2*n
        split = None
    assert legal_table(compiled[0], compiled[1])
    stats['machines'] += 1
    for word in suite:
        original, steps = simulate(n, table, s, f, word)
        graph_answer, tree_size = graph_accepts(n, table, s, f, word)
        assert graph_answer == (original == 'accept'), ('oracle disagreement', n, table, s, f, word)
        opposite, csteps = simulate(*compiled, word)
        if split is not None:
            clone_answer, _ = simulate(*split, word)
            assert clone_answer == original
        assert opposite != 'loop', ('complement loops', n, table, s, f, direction, word, compiled)
        assert (opposite == 'accept') != graph_answer, ('incorrect', n, table, s, f, direction, word, compiled)
        stats['pairs'] += 1
        stats['source_'+original] += 1
        stats['empty_pairs'] += int(not word)
        stats['max_complement_steps'] = max(stats['max_complement_steps'], csteps)
        stats['max_acceptance_tree'] = max(stats['max_acceptance_tree'], tree_size)


def randomized(seed, number, stats):
    rng = random.Random(seed)
    for index in range(number):
        n = rng.randrange(2, 13)
        alphabet = ('a', 'b', 'c')
        direction = [rng.choice((-1, 1)) for _ in range(n)] if index % 2 else None
        table = {}
        for p in range(n):
            for a in (LEFT,) + alphabet + (RIGHT,):
                if rng.randrange(6) == 0:
                    continue
                candidates = [(q, delta) for q in range(n) for delta in (-1, 1)
                    if (a != LEFT or delta == 1) and (a != RIGHT or delta == -1)
                    and (direction is None or delta == direction[q])]
                if candidates:
                    table[p, a] = rng.choice(candidates)
        s, f = rng.randrange(n), rng.randrange(n)
        suite = words(alphabet, 3)
        suite += [tuple(rng.choice(alphabet) for _ in range(rng.randrange(4, 41)))
                  for _ in range(10)]
        check_machine(n, alphabet, table, s, f, suite, stats, direction)


def main():
    if not __debug__:
        raise SystemExit("Run without -O or PYTHONOPTIMIZE: verification requires assertions.")
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true', help='Also exhaust all directional three-state unary machines')
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().parent / 'results' / 'audit_direction_upper.json',
                        help='Result JSON path (default: results/ beside this script)')
    args = parser.parse_args()
    started = time.time()
    results = {'seed': 20261008, 'suites': {}, 'status': 'running'}
    for n in (1, 2):
        alphabet = ('a', 'b')
        stats = Counter()
        suite = words(alphabet, 4)
        for direction in itertools.product((-1, 1), repeat=n):
            for table in tables(n, alphabet, direction):
                for s, f in itertools.product(range(n), repeat=2):
                    check_machine(n, alphabet, table, s, f, suite, stats, direction)
        results['suites'][f'exhaustive_directional_binary_n{n}'] = dict(stats)
        print(f'directional binary n={n}: {dict(stats)}', flush=True)
    for n in (1, 2):
        alphabet = ('a',)
        stats = Counter()
        suite = words(alphabet, 6)
        for table in tables(n, alphabet):
            for s, f in itertools.product(range(n), repeat=2):
                check_machine(n, alphabet, table, s, f, suite, stats)
        results['suites'][f'exhaustive_arbitrary_unary_n{n}'] = dict(stats)
        print(f'arbitrary unary n={n}: {dict(stats)}', flush=True)
    if args.full:
        n, alphabet = 3, ('a',)
        stats = Counter()
        suite = words(alphabet, 4)
        for direction in itertools.product((-1, 1), repeat=n):
            for table in tables(n, alphabet, direction):
                for s, f in itertools.product(range(n), repeat=2):
                    check_machine(n, alphabet, table, s, f, suite, stats, direction)
        results['suites']['exhaustive_directional_unary_n3'] = dict(stats)
        print(f'directional unary n=3: {dict(stats)}', flush=True)
    stats = Counter()
    randomized(results['seed'], 6000, stats)
    results['suites']['random_ternary_n2_through_12'] = dict(stats)
    print(f'random ternary: {dict(stats)}', flush=True)
    results.update(status='passed', elapsed_seconds=round(time.time()-started, 3))
    results['total_machines'] = sum(s['machines'] for s in results['suites'].values())
    results['total_pairs'] = sum(s['pairs'] for s in results['suites'].values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in results.items() if key != 'suites'}, indent=2))

if __name__ == '__main__':
    main()
