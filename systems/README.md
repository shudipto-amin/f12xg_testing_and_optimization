# Setting up files and folders

* Create new folder, such as `cu_nh3` for each dimer. 

## Files to create in each folder with `cu_nh3` as example:
* Create a `cu_nh3/distances.txt`

## Subfolders to create:
   * `cu_nh3/standard/`
   * `cu_nh3/xg/`

### Within each subfolder (eg. standard/) create:
* template input file like `standard/standard_gamma_1.9.inp`
   * Make sure it has a `distance` variable somewhere in the geometry
* `metadata.json` file, with prefix matching that of template input file (current e.g.: `standard_gamma_1.9`)
    - "distances" array can be varied, this is for output parsing only.

# Generate input files
* In this directory, run `python gen_distance_inputs.py` with appropriate arguments (`-h` for help) to generate inputs.

# Generate outputs and analyze
* Run outputs manually for now, and if you run more than once for the same distance, choose only one to keep.
* If needed, change the "distances" key in `metadata.json` to include distances for which output exists.
* Run `get_table.py` to get a printout of energies for a given folder (use `-h, --help` for instructions)

# Misc

## Getting basis data

* First ensure that `gprint,basis` is enabled in input script, 
* Minimal calculation (hf) is sufficient
* Run and on output file use for example:

sed -n '/BASIS DATA/,/^ NUMBER OF VALENCE ORBITALS:/'p <outfile> > <datfile>

