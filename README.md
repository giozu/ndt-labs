# NDT Labs - 057922 Nuclear Design and Technology

Computational material for **Nuclear Design and Technology** (057922), Politecnico di Milano, Teaching Assistant (TA): G. Zullo.

What is published here is the **tutoring track**, the background the course relies on, and the first sessions of the **Project Lab**.

## Where to start

Open [`tutoring/`](tutoring/) and read its README first: it lists the modules published so far and the hours of each.

The modules are **plain Python**. No install, no environment to build, no Google account: they run on a Colab runtime or on any local Python, unchanged. The modules are published one at a time, so check back rather than expecting the whole track at once.

For the **Project Lab**, open the session notebook in [`sessions/`](sessions/), [in Colab](https://colab.research.google.com/github/giozu/ndt-labs/blob/main/sessions/G03_heat_transfer/G03_heat_transfer.ipynb) or from your own clone: its Step 0 sets up the code. The sessions are published as the Project Lab reaches them.

## Layout

| Folder | Contents |
|---|---|
| `tutoring/` | the optional tutoring track, published module by module |
| `sessions/` | the Project Lab notebooks, published session by session |
| `cases/` | the z3st cases the sessions run, each checking itself against an analytical reference |
| `launcher/` | `ndt_setup.py`, which the session notebooks use to set up the environment |

## Getting help

Open an issue on this repository, bring the problem to the tutoring or to the Project Lab, or email the TA, and always include the **full output of the cell that failed**, not a screenshot of the last line.

## Note

This repository contains teaching material only. Reference solutions and anything
related to grading are not here and will not be published.

## Licence

Copyright 2026 Giovanni Zullo, Politecnico di Milano. All rights reserved except as granted below.

Two kinds of work, two licences, and nothing here is unlicensed:

| | |
|---|---|
| **software**: every `.py` file | [Apache-2.0](LICENSES/Apache-2.0.txt), the same licence as [z3st](https://github.com/giozu/z3st) |
| **teaching material**: the notebooks and all the prose | [CC BY-NC 4.0](LICENSES/CC-BY-NC-4.0.txt): credit the author, say what you changed, do not sell it |

A notebook is teaching material that contains code, so to remove the doubt: the **code cells inside the notebooks may also be used under Apache-2.0**. 
Teaching a course from this material is the use it was written for. Details in [`LICENSE`](LICENSE).

## Convention: notebooks are committed as they are, outputs included

Every notebook here is verified by executing it end to end with zero errors, that is the bar for "done". Whatever outputs that run left in the file are **kept**: a notebook you can read before running it is more useful than a blank one.

To refresh them:

```bash
jupyter nbconvert --to notebook --execute --inplace <nb>.ipynb
```
