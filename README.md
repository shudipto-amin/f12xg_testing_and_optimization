# README

This repo is for developing test routines for [F12-XG implementation](https://github.com/ak-ustutt/molpro/issues/1) in Molpro

## SETUP

run 
`$> bash setup.sh`

## Scripts

### Input generators

`gen_test_input.py` : Generates molpro input files for Neon for standard (different ansatzes), default, and xg. (writes to `outputs/`)

`dimers/gen_input.py` : Generates molpro input files based on provided template, for 'xg', 'standard', and 'default'.

`optimize_gamma_by_element/gen_input.py` : Generates input file content based on atom name, gammas, etc

`optimize_gamma_by_element/multi_inputs.sh` : Generates (using `gen_input.py` in same folder) many input files based on atom, basis, into the `outputs/` folder

`f12xg_inputs/generate_gauss_from_gamma.ipynb` : Write Expfile.

### Output parsing

`analyze_outs.ipynb` : For experimenting with and further developing `xml_output_parser.py`

`xml_output_parser.py` : For parsing to get energy from xml outputs. Works only on:
- standard and default xml files
- **single point energy output files**, not ones containing multiple jobs, such as those with different gamma
- **MP2-F12** method only for now

`tabulate_outs.py` : For tabulating energies. Depends on `xml_output_parser.py`

DEPERACTED `analyze_outputs.py` : Analyzes outputs generated from generated input files above.

### Plotting

`optimize_gamma_by_element/plot.ipynb` : Plots E vs gamma



## Reference files (!!Need to add!!)

`neon_df-hf_df-mp2-f12_aug-cc-pVDZ.*.{xml, out}`

These files are from older dates (before F12-devel was implemented) and can be used for reference.

## ITF files read by different ansatzes
| Ansatz         | ITF                       |
|----------------|---------------------------|
| 3C-FIX-HY1-NOZ | `DfMp2-f12.itfca`           |
|                | `DfMp2-f12_cfixhy1ca.itfca` |
| 3-C-FIX-NOZ    | `DfMp2-f12.itfca`           |
|                | `DfMp2-f12_scfixca.itfca`   |
| 3C-FIX-NOZ     | `DfMp2-f12.itfca`           |
|                | `DfMp2-f12_cfixca.itfca`    |
