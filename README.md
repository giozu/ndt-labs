# NDT Labs — 057922 Nuclear Design and Technology

Computational material for **Nuclear Design and Technology** (057922), Politecnico di Milano, Teaching Assistant (TA): G. Zullo.

What is published here is the **tutoring track**: the mechanics, thermal-analysis and lattice-scale background the course assumes but does not teach. The material of the project block is distributed separately, when the block starts.

## Where to start

Open [`tutoring/`](tutoring/) and read its README first: it says what the module covers, what it assumes, and how long it takes.

The modules are **plain Python**. No install, no environment to build, no Google account: they run on a Colab runtime or on any local Python, unchanged. Each one is published shortly before the lectures it prepares, so check back rather than expecting the whole track at once.

## Layout

| Folder | Contents |
|---|---|
| `tutoring/` | the optional tutoring track, published module by module |

## Getting help

Issues and pull requests are disabled on this repository. Bring problems to the session, or email the TA, and always include the **full output of the cell that failed**, not a screenshot of the last line.

## Note

This repository contains teaching material only. Reference solutions and anything
related to grading are not here and will not be published.

## Licence

Copyright 2026 Giovanni Zullo, Politecnico di Milano. All rights reserved except as granted below.

Two kinds of work, two licences, and nothing here is unlicensed:

| | |
|---|---|
| **software** — every `.py` file | [Apache-2.0](LICENSES/Apache-2.0.txt), the same licence as [z3st](https://github.com/giozu/z3st) |
| **teaching material** — the notebooks and all the prose | [CC BY-NC 4.0](LICENSES/CC-BY-NC-4.0.txt): credit the author, say what you changed, do not sell it |

A notebook is teaching material that contains code, so to remove the doubt: the **code cells inside the notebooks may also be used under Apache-2.0**. 
Teaching a course from this material is the use it was written for. Details in [`LICENSE`](LICENSE).

## Convention: notebooks are committed as they are, outputs included

Every notebook here is verified by executing it end to end with zero errors, that is the bar for "done", and its README records the numbers it produced. Whatever outputs that run left in the file are **kept**: a notebook you can read before running it is more useful than a blank one.

To refresh them:

```bash
jupyter nbconvert --to notebook --execute --inplace <nb>.ipynb
```
