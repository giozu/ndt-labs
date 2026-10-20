# Launcher

`ndt_setup.py` prepares the environment for the Project Lab notebooks. You never open or
run it yourself: the first cells of every session notebook import it and call `setup()`.

| | on Colab | on your own machine |
|---|---|---|
| what `setup()` does | installs FEniCSx, z3st and gmsh, at pinned versions, and downloads the course material | installs nothing: it only checks your environment and finds the course material |
| where things are | `/content/z3st_src`, `/content/ndt-labs` | wherever you cloned z3st and `ndt-labs` |

Both end with the same environment check, so a Colab run and a local run print the same
report.

## Running locally

The environment is the one of z3st, built with its own instructions,
<https://github.com/giozu/z3st#quick-installation>:

```bash
git clone https://github.com/giozu/z3st.git
cd z3st
conda env create -f z3st_env.yml
conda activate z3st
pip install -e .
```

Then:

1. clone `ndt-labs` as well, anywhere: the two clones need not sit side by side;
2. run `conda activate z3st` **before** `jupyter lab`, and open the session notebook from
   inside your `ndt-labs` clone.

A Jupyter started outside the environment runs a different Python, and the check reports
`z3st not importable`. That is the first thing to look at when the check fails.

## Keeping your case between sessions

On Colab the disk of the virtual machine is deleted when the runtime ends. The notebook
survives, the case you built does not. At the end of a session,
`ndt_setup.save_work(case_dir)` downloads it as a zip: keep it. At the start of the next
one, `ndt_setup.restore_work(dest)` asks you to upload it. On your own machine the case
stays in `ndt-work/`, inside your clone, and nothing is downloaded.
