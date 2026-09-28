# Local CAD runtime extension inside Hermes

Use when a functional prototyping task needs real CAD export but the runtime does not already have system CAD packages.

## Goal
Keep the solution local-first and self-contained inside the workspace instead of requiring global package installation.

## Pattern
1. Create a project-local tool directory, e.g. `cad-tools/`.
2. Create a Python venv there.
3. Install `cadquery` into the venv.
4. Download `OpenSCAD` as an `AppImage` into the same directory.
5. If the AppImage or CadQuery import fails because of missing shared libraries, download the needed Debian runtime packages with `apt download`, extract them with `dpkg-deb -x` into a local directory such as `local-libs/`, and run both tools with `LD_LIBRARY_PATH` pointing to that directory.
6. Verify with:
   - `cadquery` import and version output;
   - `OpenSCAD --version`;
   - one real STL export from the target `.scad`.

## Why this matters
This keeps delivery possible even when:
- there is no root access;
- the base system lacks GUI/runtime libraries;
- the user wants artifacts now rather than a setup discussion.

## Reporting rules
Always report separately:
- what was installed locally;
- what command path runs the tool;
- whether STL export actually succeeded;
- whether the exported mesh raised non-manifold warnings.

## Prototype-envelope rule
For this class of task, once export works, also report:
- maximum assembled envelope dimensions;
- dimensions of the main removable modules;
- any installation-dependent parameters that still need user measurement.
