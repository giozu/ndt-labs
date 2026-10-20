# SPDX-License-Identifier: Apache-2.0
"""
Shared bootstrap for all NDT sessions, on Colab AND on a local machine.
Author: Giovanni Zullo

Every session notebook starts with ONE cell that puts this file on sys.path and
calls setup(), so the install logic lives in exactly one place and cannot drift
between the sessions. Safe to re-run: each step detects what is already there.

Two modes, chosen automatically by platform():

  colab  -- install everything into the runtime: FEniCSx from the FEM-on-Colab
            wheels (pinned), then z3st (pinned tag), then gmsh, then a clone of
            the course material. This is the default path for the class.
  local  -- INSTALL NOTHING AND CLONE NOTHING. The student has already built the
            environment following z3st's own "Quick installation" (conda env
            create -f z3st_env.yml; conda activate z3st; pip install -e .) and
            started Jupyter from inside it. setup() only verifies what is loaded
            and locates the course material; on failure it says what is missing
            and points at that recipe rather than trying to repair the machine.

Maintained pins are at the top. See launcher/README.md for the history of what
each guard here is protecting against -- none of them are decorative.
"""

# --- pins -------------------------------------------------------------------
# FEM-on-Colab publishes a new release WEEKLY. Pinning freezes the class
# environment for the semester. This commit = release fenicsx-20260926-022552 (DOLFINx
# v0.11.0.post0, the same as the July pin), for the Ubuntu 24.04 Colab image of September
# 2026. The July pin (e376d3b2, fenicsx-20260725) was built for the previous image: on the
# new one its gcc step finds a different libstdc++ and kills itself (exit -9), seen 2026-09-30.
# A Colab image change breaks any pin: when the install dies like that, move to the newest
# gh-pages commit of fem-on-colab.github.io and check its DOLFINx version first.
FEM_ON_COLAB_COMMIT = 'aa3560b7'
FEM_ON_COLAB_SCRIPT = 'fenicsx-install-release-real.sh'   # note: "-release-"
# A tag, a branch, or a full commit SHA of giozu/z3st -- install_z3st() handles all
# three. It is NOT enough for this to be "a released version": it must be a revision
# that RUNS THE COURSE'S OWN CASES.
#
# 2026-09-25: the pin is `course-2627.1` (d58f938), the first mid-course change, made the
# way the paragraph below prescribes. What it adds over `.0`: set_power() no longer
# doubles the heat source on nodes shared by two heated materials, plus the verification
# case two_heated_materials_2D that guards it. None of the five cases here has two heated
# materials in contact, and all five were re-run cold on `.1` the same day: five PASS.
#
# 2026-09-12: the pin became the ANNOTATED TAG `course-2627.0` on the `course` branch
# of giozu/z3st, cut from develop at 5b20855. Why a tag and not the branch: a branch
# moves, so two students installing a week apart would get different code and a bug
# report would stop being reproducible; the branch is where course work lands, the tag
# is what the room installs. When something must change mid-course, commit on `course`,
# cut the next tag (`course-2627.2`, ...), re-run the five cases, and change the line below -- deliberately,
# not as a side effect of a push.
#
# All five cases in ndt-labs/cases (G5_vessel_non_adiabatic, G6_asme_gamma_cylinder,
# G6_primary_only, G7_shield, G7_vessel_shielded) were re-run on this revision on
# 2026-09-12 -- gmsh -> `python -m z3st` -> non-regression.py -- and all five report
# `[SUMMARY] PASS`, with relative errors of order 1e-2 on the stresses and 1e-5 on the
# temperatures.
#
# What the tag adds over the previous pin (0.3.2 = main = 5c6d01e): five commits of
# develop, mostly plot style (`plotstyle.py`, `utils_plot.py`, `plot_convergence.py`),
# updated non-regression baselines, and `bump.py` with a version-consistency check.
# Content-wise develop is a superset of 0.3.2 -- nothing from the release is lost.
# Beware: those five commits do NOT bump the version string, so `z3st.__version__`
# still reads 0.3.2 on this revision. A version is not a revision; trust the tag.
#
# 2026-08-12 (superseded): release 0.3.2 = main = commit 5c6d01e, five PASS at 0.3.1
# (0d51b3a) plus G6_primary_only re-run on 0.3.2, which changed no code. Superseded
# b5a1bab.
#
# History of why the bar is "runs the course's cases", not "is released": tag `0.2.0`
# installed perfectly and then died on the first output write, because every case here
# uses `order: 2` (P2 displacement) and 0.2.0's VTU writer reshaped u.x.array assuming
# vertex resolution. Fixed by writer._u_out(); the fix is in 0.3.x.
Z3ST_REF = 'course-2627.1'   # annotated tag on the `course` branch == d58f938
NDT_LABS_URL = 'https://github.com/giozu/ndt-labs.git'
# ----------------------------------------------------------------------------

import importlib
import os
import shutil
import subprocess
import sys
import tempfile

Z3ST_INSTALL_DOC = 'https://github.com/giozu/z3st#quick-installation'

# Where the Colab runtime keeps the two clones. These paths exist ONLY on Colab:
# everything that uses them is guarded by platform() == 'colab'.
#
# The z3st clone is deliberately NOT called "z3st". Colab keeps /content on sys.path, so
# a directory /content/z3st -- the repository ROOT, which has no __init__.py -- is
# importable as a NAMESPACE PACKAGE and shadows the real package inside it. `import z3st`
# then yields an empty module whose __file__ is None, and anything reading __file__ dies
# with "expected str, bytes or os.PathLike object, not NoneType". Renaming the clone
# removes the whole class of problem; z3st_root() also survives it, defensively.
COLAB_Z3ST_DIR = '/content/z3st_src'
COLAB_LABS_DIR = '/content/ndt-labs'


def platform():
    """'colab' or 'local'. The one switch the whole file branches on."""
    try:
        import google.colab  # noqa: F401
        return 'colab'
    except ImportError:
        return 'local'


IS_COLAB = platform() == 'colab'

# A teaching plot is not a paper plot. From z3st 0.3.3 on the develop line,
# `import z3st` installs a publication house style that makes `set_title`,
# `suptitle` and `plt.title` no-ops, because publishers want the title in the
# caption and not on the artwork. In these notebooks the title carries the
# lesson -- "The 0.2 % offset is a construction, not a measurement" is the point
# of that figure -- so it has to be drawn. z3st provides the switch; we set it
# here, before z3st is imported, so the course does not depend on which revision
# of z3st happens to be installed. `setdefault`, so an explicit choice wins.
os.environ.setdefault('Z3ST_PLOT_TITLES', '1')



def labs_root(start=None):
    """Absolute path of the ndt-labs checkout, or None if it cannot be found.

    On Colab that is the clone get_course_material() makes. Locally it is found by
    walking up from the notebook's directory: the course repository is the first
    parent holding both cases/ and sessions/. Notebooks must use this instead of
    guessing with '../..', which is wrong as soon as one is opened from elsewhere.
    """
    if IS_COLAB and os.path.isdir(COLAB_LABS_DIR):
        return COLAB_LABS_DIR
    d = os.path.abspath(start or os.getcwd())
    while True:
        if (os.path.isdir(os.path.join(d, 'cases'))
                and os.path.isdir(os.path.join(d, 'sessions'))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def z3st_root():
    """Absolute path of the z3st source tree, or None if z3st is not importable.

    Locally z3st is wherever the student cloned it and pip-installed it from; the installed package knows, so nothing has to be assumed about the layout.
    """
    try:
        import z3st
    except ImportError:
        return None
    f = getattr(z3st, '__file__', None)
    if f: # regular package: <root>/z3st/__init__.py
        return os.path.dirname(os.path.dirname(os.path.abspath(f)))

    paths = list(getattr(z3st, '__path__', None) or [])
    return os.path.abspath(paths[0]) if paths else None


def z3st_revision():
    """`git describe` of the z3st checkout, or None if it is not a git tree.

    Answers the question the version string cannot: *which code is this?* Output
    looks like `0.2.0` on the tag, `0.2.0-60-gb5a1bab` sixty commits past it.
    """
    root = z3st_root()
    if root is None or not os.path.isdir(os.path.join(root, '.git')):
        return None
    r = subprocess.run(['git', '-C', root, 'describe', '--tags', '--always', '--dirty'],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def z3st_pin_state():
    """Is the local z3st checkout the revision the course pins?

    Returns (state, detail) with state in {'pinned', 'other', 'unknown'}. The
    revision, not the version string: on 2026-09-10 two of the eight session
    notebooks turned out to carry outputs produced on `5b20855`, a commit that is
    not even an ancestor of the pin, while every one of them printed "0.3.2".
    """
    root = z3st_root()
    if root is None or not os.path.isdir(os.path.join(root, '.git')):
        return 'unknown', 'not a git checkout'

    def _rev(ref):
        r = subprocess.run(['git', '-C', root, 'rev-parse', ref + '^{commit}'],
                           capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None

    head, pin = _rev('HEAD'), _rev(Z3ST_REF)
    if head is None or pin is None:
        return 'unknown', f'cannot resolve {Z3ST_REF}'
    if head == pin:
        return 'pinned', Z3ST_REF
    return 'other', head[:7]


def z3st_cases(*parts):
    """A path inside z3st's own bundled cases, e.g. z3st_cases('verification')."""
    root = z3st_root()
    if root is None:
        raise SystemExit('z3st is not importable -- run the bootstrap cell first.')
    return os.path.join(root, 'z3st', 'cases', *parts)


def save_work(case_dir, quiet=False):
    """Pack a group's own case into a zip they KEEP, and hand it to them.

    The reason this exists: on Colab a group's case lives in /content, which is the
    scratch disk of a virtual machine that is destroyed when the runtime ends. The
    notebook survives (it is a file), the case does not -- so a group would arrive at
    the next session, days after building its vessel, and find nothing. Downloading a zip
    works on every track (Colab from GitHub, Colab from Drive, a local machine),
    unlike anything that relies on Drive being mounted.

    Locally nothing is downloaded: the case is already on a real disk.
    """
    case_dir = os.path.abspath(case_dir)
    if not os.path.isdir(case_dir):
        # Not an error: until the group uncomments the template and builds its own
        # vessel there is genuinely nothing to save, and a notebook must still run
        # end to end from a clean checkout.
        print(f'nothing to save yet: {case_dir} does not exist.\n'
              'Build your own case first (the template cell above), then re-run this.')
        return None
    archive = shutil.make_archive(
        os.path.join(tempfile.gettempdir(), os.path.basename(case_dir)), 'zip',
        root_dir=os.path.dirname(case_dir), base_dir=os.path.basename(case_dir))
    if not quiet:
        print(f'{archive}  ({os.path.getsize(archive) / 1e6:.1f} MB)')
    if IS_COLAB:
        from google.colab import files
        files.download(archive)
        print('Downloading. KEEP THIS FILE -- it is your work.\n'
              'Everything in /content is deleted when this runtime ends; the next\n'
              'session starts by uploading this zip back.')
    else:
        print('local run: your case is already on disk, nothing to download')
    return archive


def restore_work(dest):
    """Put back a case saved with save_work(). On Colab, prompts for the upload.

    Idempotent: if `dest` is already there, it is left alone and nothing is asked.
    """
    dest = os.path.abspath(dest)
    if os.path.isdir(dest):
        print(f'already here, nothing to restore: {dest}')
        return dest
    if not IS_COLAB:
        # Local: nothing is ever lost when a session ends, so an absent case means the
        # group has not built one yet. Say so and continue -- do not stop the notebook.
        print(f'not found: {dest}\n'
              'On your own machine nothing is lost when a session ends, so this simply '
              'has not been built yet: build it first.')
        return None

    from google.colab import files
    print('Choose the .zip you downloaded at the end of the previous session.')
    up = files.upload()
    if not up:
        print('nothing uploaded -- rebuild your case, or continue on the '
              'neutral one and say so in your report.')
        return None
    name = next(iter(up))
    tmp = os.path.join(tempfile.gettempdir(), name)
    with open(tmp, 'wb') as fh:
        fh.write(up[name])

    parent = os.path.dirname(dest)
    os.makedirs(parent, exist_ok=True)
    before = set(os.listdir(parent))
    shutil.unpack_archive(tmp, parent)
    new = [d for d in set(os.listdir(parent)) - before
           if os.path.isdir(os.path.join(parent, d))]
    # The zip carries the folder name it was saved under, which need not be the name
    # being restored to. Rename rather than fail: the group renamed nothing, we did.
    if not os.path.isdir(dest):
        if len(new) != 1:
            raise SystemExit(f'unexpected archive contents: {sorted(new)}')
        os.rename(os.path.join(parent, new[0]), dest)
    print('restored:', dest)
    return dest


def workdir(name):
    """Where a group's OWN case should go. Returns a path; does NOT create it.

    Only the parent is created. `<name>` itself is left absent on purpose, because
    the caller is `shutil.copytree(CASE, MY_CASE)` and copytree requires the
    destination NOT to exist -- creating it here would make every session's first
    real step fail with FileExistsError.

    On Colab that is /content/<name>, which dies with the runtime -- which is what
    save_work() exists for. Locally it is <clone>/ndt-work/<name>: INSIDE the course
    clone, so a group has one directory tree to think about rather than two. That
    folder is git-ignored (except its own README), so the work in it never appears
    in `git status` and `git pull` stays clean.

    The trade-off is deliberate and stated in ndt-work/README.md: work kept inside
    the clone does not survive `git clean -fdx`, a re-clone, or replacing the folder
    with a fresh download. Hence the DO NOT DELETE notice that ships in it.

    Falls back to ~/ndt-work/<name> when the clone cannot be located -- a notebook
    opened from outside it still has somewhere to write.
    """
    if IS_COLAB:
        d = os.path.join('/content', name)
    else:
        root = labs_root() or os.path.expanduser('~')
        d = os.path.join(root, 'ndt-work', name)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    return d


# PETSc prints this at initialization on the FEM-on-Colab image. It is WRONG:
# diagnosed on 2026-07-31 on a clean runtime, there is no MPICH on the machine at
# all -- only OpenMPI exists on disk, only OpenMPI is mapped into the process, and
# no loaded library defines an MPICH symbol. Inside libpetsc the string sits next
# to "Open MPI library version %s does not match what PETSc was compiled with",
# i.e. it is the same version-check routine drawing the wrong conclusion. It is a
# printf, not an abort: lame_gps_2D (3321 nodes) matches the closed-form Lame
# solution to 1e-5 with it printed. Hidden here so it does not send students
# chasing a non-existent problem; check_environment() does the real test.
PETSC_FALSE_ALARM = 'linked against both OpenMPI and MPICH'


def _quiet_petsc(text):
    """Drop the known-false PETSc MPI line, keeping everything else verbatim."""
    kept = [l for l in text.splitlines() if PETSC_FALSE_ALARM not in l]
    if len(kept) != len(text.splitlines()):
        kept.append('[ndt] (PETSc\'s "both OpenMPI and MPICH" line hidden: it is a '
                    'known false alarm on this image, not a problem with your run)')
    return '\n'.join(kept)


def _sh(cmd, label, quiet=False):
    """Run a shell command and SHOW its output.

    os.system() sends output to the kernel log, not the notebook cell, which
    once hid a failing install for two debugging rounds.
    """
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout.strip() and not quiet:
        print(r.stdout[-3000:])
    if r.returncode != 0:
        print(f'--- {label} FAILED (exit {r.returncode}) ---')
        print(_quiet_petsc(r.stderr[-3000:]))
    return r.returncode


def install_fenicsx():
    try:
        import dolfinx
        print(f'dolfinx {dolfinx.__version__} already present')
        return
    except ImportError:
        pass

    base = ('https://github.com/fem-on-colab/fem-on-colab.github.io'
            f'/raw/{FEM_ON_COLAB_COMMIT}/releases') if FEM_ON_COLAB_COMMIT else \
           'https://fem-on-colab.github.io/releases'
    url = f'{base}/{FEM_ON_COLAB_SCRIPT}'
    dest = '/tmp/fenicsx-install.sh'
    print(f'installing FEniCSx (a few minutes)\n  {url}')

    rc = _sh(f'wget "{url}" -O {dest}', 'download', quiet=True)
    size = os.path.getsize(dest) if os.path.exists(dest) else 0
    # An HTTP error leaves a 0-byte file, and `bash` on an empty file exits 0,
    # so the install would silently "succeed" having done nothing.
    if rc != 0 or size < 1000:
        raise SystemExit(f'installer download failed (exit {rc}, {size} bytes)\n'
                         f'URL: {url}\n'
                         'Check the name at https://fem-on-colab.github.io/packages.html')

    if _sh(f'bash {dest}', 'FEniCSx install', quiet=True) != 0:
        raise SystemExit('the FEniCSx installer reported an error. If it died with exit -9 '
                         'after a libstdc++ message, the Colab image has changed under the '
                         'pinned FEM-on-Colab release: tell the teaching assistant.')

    importlib.invalidate_caches()          # files appeared during this process
    import dolfinx
    print(f'dolfinx {dolfinx.__version__} installed')


def install_z3st():
    if not os.path.isdir(COLAB_Z3ST_DIR):
        # A full clone, then checkout: `clone --branch` accepts a tag or a branch but
        # NOT a commit SHA, and being able to pin a SHA matters when the revision the
        # course needs has not been tagged yet. z3st is small; the extra cost is seconds.
        _sh(f'git clone https://github.com/giozu/z3st.git {COLAB_Z3ST_DIR}',
            'clone z3st', quiet=True)
    if _sh(f'git -C {COLAB_Z3ST_DIR} checkout --quiet {Z3ST_REF}',
           f'checkout z3st {Z3ST_REF}') != 0:
        raise SystemExit(f'z3st has no revision {Z3ST_REF!r} -- check Z3ST_REF')

    # --no-deps protects the image's numpy: re-resolving z3st's dependencies can
    # replace it and break dolfinx.
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '--no-deps',
                    '-e', COLAB_Z3ST_DIR], check=True)
    # ...but --no-deps also skips what the image does NOT ship. gmsh is the one
    # that matters: it provides the command-line mesher every case needs.
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',
                    'gmsh', 'pyyaml', 'meshio', 'pyvista'], check=True)

    # Make `import z3st` reach the package we just installed even on a runtime that is
    # already dirty -- e.g. a leftover /content/z3st from before the clone was renamed,
    # which Colab would import as an empty namespace package because /content is on
    # sys.path. Putting the clone first, and dropping any z3st imported so far, is enough;
    # nothing is deleted from the runtime.
    while COLAB_Z3ST_DIR in sys.path:
        sys.path.remove(COLAB_Z3ST_DIR)
    sys.path.insert(0, COLAB_Z3ST_DIR)
    if getattr(sys.modules.get('z3st'), '__file__', 'ok') is None:
        del sys.modules['z3st']
    importlib.invalidate_caches()
    print(f'z3st {Z3ST_REF} installed')


def gmsh_status():
    """(runnable?, message). Presence on disk is not readiness."""
    exe = shutil.which('gmsh')
    if exe is None:
        for cand in ('/usr/local/bin', os.path.join(sys.prefix, 'bin'),
                     os.path.expanduser('~/.local/bin')):
            if os.path.exists(os.path.join(cand, 'gmsh')):
                os.environ['PATH'] = cand + os.pathsep + os.environ['PATH']
                exe = shutil.which('gmsh')
                break
    if exe is None:
        return False, 'not found on PATH'
    r = subprocess.run([exe, '--version'], capture_output=True, text=True)
    return r.returncode == 0, ((r.stdout + r.stderr).strip() or 'no output')


def fix_gmsh():
    ok, msg = gmsh_status()
    if ok:
        return ok, msg
    # The pip gmsh wheel is the GUI build and dlopen()s OpenGL/GLU, which the
    # minimal Colab image lacks: it installs cleanly and then refuses to start.
    print(f'gmsh installed but not runnable ({msg[-120:]}); adding system libraries')
    _sh('apt-get -qq update', 'apt update', quiet=True)
    _sh('apt-get -qq install -y libglu1-mesa libxcursor1 libxinerama1 '
        'libxft2 libxrender1', 'apt install', quiet=True)
    return gmsh_status()


def get_course_material():
    """Clone/refresh ndt-labs. Harmless if it is not public yet."""
    if os.path.isdir(COLAB_LABS_DIR):
        subprocess.run(['git', '-C', COLAB_LABS_DIR, 'pull', '--ff-only'],
                       capture_output=True, text=True)
        return True
    r = subprocess.run(['git', 'clone', '--depth', '1', NDT_LABS_URL, COLAB_LABS_DIR],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print('  (course repository not reachable - continuing; the session case '
              'may live in the z3st clone instead)')
        return False
    return True


def check_environment():
    problems = []
    try:
        importlib.invalidate_caches()
        import dolfinx
        print(f'  dolfinx  {dolfinx.__version__}')
    except Exception as e:
        problems.append(f'dolfinx not importable: {e!r}')

    try:
        import numpy as np
        print(f'  numpy    {np.__version__}')
        if int(np.__version__.split('.')[0]) < 2:
            problems.append(f'numpy {np.__version__} too old (z3st needs >= 2)')
    except Exception as e:
        problems.append(f'numpy missing: {e!r}')

    ok, msg = gmsh_status()
    if ok:
        print(f'  gmsh     {msg.splitlines()[0]}')
    else:
        problems.append(f'gmsh not runnable: {msg}')

    try:
        import z3st
        # `import z3st` must reach the real package, not a directory that merely has its
        # name. A namespace package has __file__ = None and no code in it at all: the
        # solver still runs (it is launched as a subprocess from the case folder) so the
        # symptom surfaces far away, in whatever first reads z3st.__file__.
        if getattr(z3st, '__file__', None) is None:
            where = ', '.join(getattr(z3st, '__path__', None) or ['?'])
            problems.append(
                f'`import z3st` resolves to an EMPTY namespace package at {where} -- a '
                'directory named z3st with no __init__.py is on sys.path and is hiding '
                'the installed one. Remove it from sys.path or rename it.')
        ver = getattr(z3st, '__version__', None)
        if ver is None:
            from importlib import metadata
            ver = metadata.version('z3st')
        # The version STRING does not identify the code. It is set in pyproject and
        # stays the same across every commit until the next release: on 2026-08-01 a
        # working tree 60 commits past `0.2.0` reported "0.2.0", identical to the
        # pinned tag -- which is why a Colab-only crash looked like a Colab problem
        # for an hour. Report what git actually has checked out.
        print(f'  z3st     {ver}   [{z3st_revision() or "not a git checkout"}]')
        state, detail = z3st_pin_state()
        if state == 'other':
            print(f'           NOTE: this is {detail}, not the course revision '
                  f'{Z3ST_REF}. Results may differ from the reference ones. '
                  f'To match them: git -C {z3st_root()} checkout {Z3ST_REF}')
    except Exception as e:
        problems.append(f'z3st not importable: {e!r}')

    # Two MPI implementations in ONE process would give wrong answers on larger runs
    # while small serial cases still pass. What matters is not which libraries exist
    # on disk (the image ships several) but which one is mapped into this process.
    try:
        from mpi4py import MPI
        print(f'  MPI      {MPI.Get_library_version().strip().splitlines()[0][:55]}')
        families = {'MPICH' if 'mpich' in line.split()[-1] else 'OpenMPI'
                    for line in open('/proc/self/maps')
                    if 'libmpi' in line.split()[-1]}
        if len(families) > 1:
            problems.append(f'two MPI implementations loaded at once: {sorted(families)}')
    except Exception:
        pass

    print()
    if problems:
        print('ENVIRONMENT NOT OK')
        for p in problems:
            print('  -', p)
        print('\nSend this whole output to the teaching assistant.')
        return False
    print('ENVIRONMENT OK')
    return True


def run_case(case_dir, mesh_dim='-2'):
    """gmsh -> solve -> non-regression, showing output. 
    Returns True on PASS."""
    if not os.path.isdir(case_dir):
        raise SystemExit(f'no such case: {case_dir}')
    steps = [(['gmsh', 'mesh.geo', mesh_dim, '-o', 'mesh.msh'], 'mesh'),
             ([sys.executable, '-m', 'z3st'], 'solve'),
             ([sys.executable, 'non-regression.py'], 'self-check')]
    for cmd, label in steps:
        print(f'\n$ {" ".join(cmd)}')
        r = subprocess.run(cmd, cwd=case_dir, capture_output=True, text=True)
        print(_quiet_petsc(r.stdout[-4000:]))
        if r.returncode != 0:
            print(_quiet_petsc(r.stderr[-3000:]))
            raise SystemExit(f'{label} failed in {case_dir}')
    return True


LOCAL_HELP = f"""
Nothing was installed: on a local machine this notebook does not touch your system.
Build the environment once, following z3st's own instructions:

    {Z3ST_INSTALL_DOC}

    git clone https://github.com/giozu/z3st.git
    cd z3st
    conda env create -f z3st_env.yml
    conda activate z3st
    pip install -e .

then start Jupyter FROM THAT ACTIVATED ENVIRONMENT (`conda activate z3st` first --
a Jupyter started elsewhere runs a different Python and will fail this check again),
and open this notebook from inside your own clone of the course repository.
"""


def setup(course_material=True):
    """Prepare and verify the environment. Returns True if it is usable.

    On Colab this installs the class environment; locally it only checks it. The
    two branches share check_environment(), so a student who compares a local run
    with a Colab run is reading the same report.
    """
    if IS_COLAB:
        print('[ndt] Colab detected -- installing the class environment')
        install_fenicsx()
        install_z3st()
        fix_gmsh()

        if course_material and labs_root() is None:
            get_course_material()
        print(f'  labs at  {labs_root() or "NOT FOUND"}')
    else:
        root = labs_root()
        print('[ndt] local environment detected -- nothing will be installed')
        print(f'  python   {sys.executable}')
        print(f'  z3st at  {z3st_root() or "NOT INSTALLED"}')
        print('  labs at  ' + (root or 'NOT FOUND (open this notebook from inside '
                               'your ndt-labs clone)'))

    print('\n--- environment check ---')
    ok = check_environment()
    if not ok and not IS_COLAB:
        print(LOCAL_HELP)
    return ok


if __name__ == '__main__':
    setup()
