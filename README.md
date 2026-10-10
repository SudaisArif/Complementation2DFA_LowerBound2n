# Complementation2DFA_LowerBound2n

**A Factor-Two Lower Bound for Complementing Two-Way Deterministic Finite Automata**  
Sudais Arif · Carnegie Mellon University in Qatar  
Preprint · 8 October 2026 · Editorial revision, 10 October 2026

**[Read the paper (PDF)](complementation_exact_2n.pdf)** · [LaTeX source](complementation_exact_2n.tex) · [Source ZIP](complementation_exact_2n_arxiv.zip) · [Verification instructions](VERIFICATION.md)

## Main result

For every $n\ge22$, there is a language $K_n$ over the fixed alphabet $\{A,B,C\}$ such that

$$
\operatorname{sc}(K_n)=n,
\qquad
\operatorname{sc}(\overline{K_n})=2n.
$$

The result is unconditional. Both state minima allow arbitrary two-way deterministic finite automata, including automata that reject by an infinite computation. The lower bound is proved in the paper; the included programs provide finite checks of the explicit constructions.

The convention is part of the exact statement:

| Acceptance convention | Exact source complexity | Exact complement complexity | Range |
| --- | --- | --- | --- |
| Paper's left-endmarker model | $n$ | $2n$ | Every $n\ge22$ |
| Geffert–Mereghetti–Pighizzini (GMP), acceptance anywhere | $N$ | $2N-1$ | Every $N\ge23$ |

In the first row, the automaton starts on the left endmarker and accepts exactly when it reaches its designated final state **at that marker**. Moves are left or right, endmarker moves are inward, and undefined transitions and infinite runs reject. Every state, including the initial and final states, is counted. The final state may perform ordinary work away from the accepting marker.

In GMP's convention, reaching a final state anywhere accepts. Section 8 proves the exact transfer for the same language, with $N=n+1$, including the fixed accepting channel that sharpens the lower bound to $2N-1$. The explicit matching complement shows that this particular family does not require $2N$ states under GMP's convention. The leading factor is two in both conventions.

## What is proved

- A complete ternary source five-tuple, with exact source minimality and complement lower bound against unrestricted deterministic targets.
- A matching halting complement using $2n$ states for sources whose incoming transition direction is determined by the destination state.
- A halting complement with at most $2n+2b$ states for arbitrary sources, where $b$ counts states entered in both directions, after deleting the effective outgoing row at the accepting configuration.
- The exact acceptance-convention comparison above.

The lower-bound proof uses two independent transformation systems, interval diagrams, a product of alternating groups, and a permutation-query obstruction. The manuscript contains the proofs and transition prescriptions, 17 references, and a source-flow diagram.

This does **not** establish a general $2n$ upper bound for unrestricted sources. The bounds proved here for the general ternary problem are $2n\le C_3(n)\le4n$ for $n\ge22$.

## Connection to the 2007 open problem

Geffert, Mereghetti, and Pighizzini ask for a complementation gap in the fifth concluding problem of *Complementing two-way finite automata*, Section 6(e), printed page 1186. The manuscript cites that question and their Lemma 3.1, and proves the gap in their own convention in Theorem 8.2.

V. Geffert, C. Mereghetti, and G. Pighizzini. *Information and Computation* 205(8):1173–1187, 2007. [DOI: 10.1016/j.ic.2007.01.008](https://doi.org/10.1016/j.ic.2007.01.008).

## Repository contents

| Path | Contents |
| --- | --- |
| [`complementation_exact_2n.pdf`](complementation_exact_2n.pdf) | Compiled 18-page preprint |
| [`complementation_exact_2n.tex`](complementation_exact_2n.tex) | Complete LaTeX source; bibliography and BBL are alongside it |
| [`complementation_exact_2n_arxiv.zip`](complementation_exact_2n_arxiv.zip) | TeX, BibTeX, and BBL source archive |
| [`VERIFICATION.md`](VERIFICATION.md) | Instructions for the three Python programs and their recorded `expected_*` reports |
| [`CORRECTNESS_REVIEW.txt`](CORRECTNESS_REVIEW.txt) | Scope and outcome of the mathematical and computational review |
| [`CITATION.cff`](CITATION.cff) | Citation metadata |
| [`SHA256SUMS`](SHA256SUMS) | Checksums of the published files |

## Build the paper

The committed PDF can be read directly. To rebuild, use a TeX installation with the standard `article`, AMS, `newtx`, `geometry`, `microtype`, `titlesec`, TikZ, and `hyperref` packages. The diagram is drawn in LaTeX; no external images or custom style files are required.

With Tectonic (the released PDF was built with version 0.17.0):

```sh
mkdir -p build
tectonic --keep-logs --keep-intermediates --outdir build complementation_exact_2n.tex
```

Or, with a standard TeX distribution and `latexmk`:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error complementation_exact_2n.tex
```

The source ZIP was independently extracted and compiled; its resulting PDF has the same extracted text as the published PDF. During any later submission, check the PDF generated by the submission service.

## Reproduce the finite checks

Python 3.10 or later is sufficient; no third-party Python packages are needed.

```sh
python3 witness_verification.py
python3 audit_generation_check.py
python3 audit_direction_upper.py --full
```

See [`VERIFICATION.md`](VERIFICATION.md) for expected outputs and scope. The original verification includes 26,240 witness/formula/complement comparisons and 4,960,600 upper-construction checks across 850,552 machine presentations. These checks corroborate the constructions; they do not replace the mathematical proof of the lower bound.

To check the downloaded artifacts on macOS or Linux:

```sh
shasum -a 256 -c SHA256SUMS
```

## Cite this preprint

```bibtex
@misc{arif2026exactfactor,
  author = {Sudais Arif},
  title = {A Factor-Two Lower Bound for Complementing Two-Way Deterministic Finite Automata},
  year = {2026},
  note = {Preprint, editorial revision of 10 October 2026},
  url = {https://github.com/SudaisArif/Complementation2DFA_LowerBound2n}
}
```

The PDF and sources on the main branch include the editorial revision of 10 October 2026: the revised title, introduction, notation, acknowledgments, and reference links. The original `v1.0.0` release remains available as a historical snapshot.

Use a release tag or commit identifier when citing a specific version. Corrections and mathematical questions can be reported through the repository's Issues tab. Review details and the acknowledgments, including research assistance, appear in the paper and review summary.
