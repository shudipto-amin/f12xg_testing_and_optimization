import numpy as np
import json
import argparse
import itertools
import os, sys
import warnings
import pandas as pd
from argparse import Namespace

# Add parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from systems import generate_inputs_and_folders as giaf
from systems import run_inputs_and_folders as riaf

import xml_output_parser as xo
import tabulate_outs as to
import glob

parser = argparse.ArgumentParser(
    description="Tabulates ouptputs using metadata"
)

parser.add_argument(
    "metadata_path",
    help="Path to metadata"
)
parser.add_argument(
    "--enertypes",
    nargs="+",
    help="List of energy types to extract (default: total energy, correlation energy)",
)
parser.add_argument(
    "--outtype",
    help="output type",
    default="*.out"
)

parser.add_argument(
    "--print_only",
    help="print output only",
    action='store_true'
)

parser.add_argument(
    "--outfile",
    help="output file to write data to, default is `data.csv` in same folder as metadata_path"
)
    
def _print_nested_dict(d, prefix=""):
    for key, val in d.items():
        if isinstance(val, dict):
            print(key)
            _print_nested_dict(val, prefix="   ")
            continue
        print(f"{prefix}{key:20s} {val}")

def get_outfile(infile, calctype='xg'):
    """
    Given an input file path (e.g. 'path/to/file.inp'),
    find all matching output files ('path/to/file.*.out').
    If multiple exist, issue a warning but return the latest one.
    """
    # Split path and base filename (without extension)
    base, _ = os.path.splitext(infile)
    if calctype == 'xg':
        pattern = f"{base}.*.out"
    else:
        pattern = f"{base}.*.xml"

    # Find matching files
    matches = glob.glob(pattern)

    if not matches:
        raise FileNotFoundError(f"No matching output files found for pattern: {pattern}")

    # Sort by modification time (latest last)
    matches.sort(key=os.path.getmtime)

    if len(matches) > 1:
        warnings.warn(
            f"Multiple output files found for {infile}:\n"
            + "\n".join(matches)
            + f"\nUsing latest: {matches[-1]}"
        )

    return matches[-1]
    
def update_dict(df_dict, kwargs):
    for key, val in kwargs.items():
        if key not in df_dict:
            df_dict[key] = []
        df_dict[key].append(val)

def df_from_csv(csvfile, energy_types):
    if csvfile.endswith('.csv'):
        sep = ','
    else:
        sep = r'\s+'
        
    df = pd.read_csv(
        csvfile, skipinitialspace=True, sep=sep, engine="python"
    )#, usecols=energy_types)
    return df

def dict_from_out(outfile, energy_types, kwargs, calctype):

    for enertype in energy_types:
        kwargs[enertype] = to.get_ener(
                outfile, enertype=enertype, 
                out_type=calctype
                )
    
    
def main(args):
    print ('| ARGUMENTS PROVIDED')
    _print_nested_dict(vars(args))
    meta = giaf.read_metadata(args.metadata_path)
    _print_nested_dict(meta)
    args_dict = {
        "metadata_path": args.metadata_path,
        "dry_run": False,
        "output": None,
    }
    args_ns = Namespace(**args_dict)

    data_frames = []
    
    for infile, folder_path, _, kwargs in giaf.generate_file_paths(args_ns, meta):

        if args.outtype == 'csv':
            csv_basename = kwargs['full_file_prefix'] + '.csv'
            csv_basename = csv_basename[:32] # Molpro allows only upto 32 chars :@
            csvfile = os.path.join(
                folder_path,
                csv_basename
            ) 
            energy_types = args.enertypes or ["TOT_ENER", "CORR_ENER"]
            df = df_from_csv(csvfile, energy_types)
            kwargs['outfile'] = csvfile
            data_frames.append(df.assign(**kwargs))
            
            #print(csvfile)
            #print(df.columns)
            
            
            
        else:     
            if meta['calc_type'] == 'xg':
                calctype = 'xg'
            else:
                calctype = 'std'
            outfile = get_outfile(infile, calctype=meta['calc_type'])
            energy_types = args.enertypes or ["total energy", "correlation energy"]
            kwargs['outfile'] = outfile
            dict_from_out(outfile, energy_types, kwargs, calctype)
            data_frames.append(pd.DataFrame([kwargs]))
            


    full_df = pd.concat(
        data_frames,
        ignore_index=True
    )
    columns = [key for key in kwargs if 'file' not in key]
    columns += [c for c in full_df.columns if c not in kwargs]
    columns += [key for key in kwargs if key == 'outfile']
    
    return full_df[columns]

def write_to_csv(df, args):
    if args.outfile:
        outfile = args.outfile
    else:
        outfile = os.path.join(
            os.path.dirname(args.metadata_path), 'data.csv'
        )
    df.to_csv(outfile ,index=False)
    
if __name__ == '__main__':
    args = parser.parse_args()
    df = main(args)
    if args.print_only:
        print(df.to_string())
    else:
        
        write_to_csv(df, args)
        