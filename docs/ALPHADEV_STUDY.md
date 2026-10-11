# AlphaDev research review

AlphaDev treats program construction as a reinforcement-learning problem at the
assembly level. The agent appends instructions; the state includes the partial
program and machine state. Correctness and execution efficiency contribute to
reward. AlphaZero-style search and learned representations guide exploration.
This differs from choosing among complete sorting algorithms by dataset features.
See the [original Nature paper, Mankowitz et al. (2023)](https://www.nature.com/articles/s41586-023-06004-9).

The paper reports improvements to small fixed-length sorting routines and
variable-length routines, including instruction sequences that shorten an
existing sorting network. These routines can serve as building blocks in a
larger sorting implementation. That does not establish faster sorting for all
input sizes, processors, compilers or distributions. Published results belong
to the authors' experiments; they are not measurements from this repository.
The paper's DOI is 10.1038/s41586-023-06004-9, Nature 618, 257–263.

The [official implementation archive](https://github.com/google-deepmind/alphadev)
contains agent/environment pseudocode and discovered assembly programs with
correctness checks. Its README lists fixed routines for lengths3–8 and variable
routines up to lengths3–5. For example, it lists 17 instructions for Sort3 and
43 for Sort5. The pseudocode omits the assembly runner and is not a complete,
ready-to-run training system. Software is Apache2.0; other materials are CC-BY4.0.
No upstream code is copied into this project for this research section.

This project has **not reproduced AlphaDev training**, searched instruction
sequences, compiled its assembly tests, or attributed its own timing differences
to AlphaDev. PDQSort, Timsort, QuickSort, Merge Sort and Radix Sort retain their
documented identities. The optional learned sorter selector is not implemented;
the learned rank index is a different task.

# Learned-index relationship and limits

[Kraska et al., The Case for Learned Index Structures (SIGMOD2018)](https://arxiv.org/abs/1712.01208v3)
describes models predicting record positions and the need to correct prediction
errors. Our implementation is a deliberately simple single affine endpoint rank
model with certified correction and a binary-search fallback. It does not
reproduce that paper's recursive model index, neural training or reported speed
and memory improvements. Endpoint fitting uses the stored data; evaluation seeds
are held out from performance tuning and the correction radius is fixed before
study. Correctness tests may use those seeds; no performance tuning used them.
Owned vector capacity is distinct from constant-size model metadata and process
RSS. Highly repeated or skewed keys can produce substantial prediction errors;
fallback ensures correctness rather than promising constant-time lookup.

Sources were inspected on2026-10-11. Direct opening of the Nature page hit its
authentication redirect; the search-indexed primary-paper text and official
repository were accessible. The research-source record is retained in the
autonomous-completion audit. No paper's performance claim is used as our result.
