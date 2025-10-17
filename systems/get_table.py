import os
import subprocess
import pandas as pd
import numpy as np
import re
from io import StringIO
import argparse
import json
import glob
import ast

parser = argparse.ArgumentParser(description="Get table of energies")
parser.add_argument(
    "outputs_path", 
    help="Path to the folder containing output files; e.g., dimers/xg_interation_outputs/"
)
parser.add_argument(
    "--metadata", 
    help="Optional path to metadata file (json). Defaults to 'metadata.json' in the outputs_path.", 
    default=None, required=False
)
parser.add_argument(
    "-o", "--outfile", 
    help="Optional path to write to (csv). By default generated from metadata and placed in outputs directory.",
    default=None, required=False
)
parser.add_argument(
    "-s", "--suffix", 
    help="Optional suffix for generated filename. Default is 'all'",
    default='all', required=False
)
parser.add_argument(
    "-p", "--print_only", 
    help="Dry run",
   action="store_true", required=False
)

def parse_output_to_df(output_str: str) -> pd.DataFrame:
    """
    Convert tabulated output string into a DataFrame with columns ['DISTANCES', 'E'].
    
    Parameters
    ----------
    output_str : str
        Multiline string containing a dataframe-like output with 'labels' and 'energies'.
    
    Returns
    -------
    pd.DataFrame
        Dataframe with 'DISTANCES' (float) and 'E' (np.float64).
    """
    # Step 1: Read the string into a DataFrame
    df = pd.read_csv(StringIO(output_str), sep=r'\s+')

    # Step 2: Extract distances from labels (float after second 'r_')
    distances = []
    for label in df['labels']:
        match = re.search(r"r_\d+\.\d+", label)
        if match:
            truncated = match.group(0)
            distances.append(float(truncated.split("_")[1]))
        else:
            raise ValueError(f"Could not parse distance from label: {label}")

    # Step 3: Build final DataFrame
    final_df = pd.DataFrame({
        "DISTANCES": distances,
        "Etot": df['total_energies'].astype(np.float64),
        "Ecorr": df['correlation_energies'].astype(np.float64)
    })

    return final_df

def read_metadata(metadata_path: str) -> dict:
    """
    Reads metadata from a file.
    """
    with open(metadata_path, 'r') as f:
        return json.load(f)


def get_cmd_from_metadata(metadata: dict, outputs_path: str):
    """
    Constructs the command string to run the appropriate tabulate script with the list of output files
    based on the metadata and outputs path.

    Args:
        metadata (dict): Metadata dictionary containing calc_type, distance_file, prefix, etc.
        outputs_path (str): Path to the directory containing output files.
        tabulate_script_path (str): Absolute path to tabulate_outs.py

    Returns:
        str: The command string to run, e.g.
             'python /abs/path/tabulate_outs.py --xgouts file1.out file2.out ...'
    """

    # Read distances
    distances_list = metadata['distances']

    file_ext = 'out' if metadata['calc_type'] == 'xg' else 'xml'
    cmd_arg = '--xgouts' if metadata['calc_type'] == 'xg' else '--outs'

    files = []
    for d in distances_list:
        formatted_d = format(d, metadata['distance_format'])
        filename = metadata['prefix'].format(distance=formatted_d)
        search_pattern = os.path.join(outputs_path, f"{filename}.*.{file_ext}")
        matched_files = glob.glob(search_pattern)
        if not matched_files:
            print("Empty array")
            print(matched_files)
            raise ValueError(f"No matches found for {search_pattern}")
        files.extend(matched_files)

    # Join all files as one space-separated string
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tabulate_script = os.path.join(script_dir, "..", "tabulate_outs.py")
    tabulate_script = os.path.abspath(tabulate_script)  # Get absolute path
    
    files_str = ' '.join(files)
    cmd = f"python {tabulate_script} {cmd_arg} {files_str}"
    return cmd

def get_default_output_fname(metadata, ext='csv', suffix='all'):
    fname = "{prefix}.{ext}".format(**metadata, ext=ext).format(distance = suffix)
    return fname

def main(args):
    # Save current working directory
    metadata_path = args.metadata or os.path.join(args.outputs_path, 'metadata.json')
    metadata = read_metadata(metadata_path)
    metadata_dir = os.path.dirname(os.path.abspath(metadata_path))
    
    cmd = get_cmd_from_metadata(metadata, args.outputs_path,)
    result = subprocess.run(
        cmd,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True,
        check=True
    )
   
    output_str = result.stdout
    df = parse_output_to_df(output_str)


    if not args.outfile:
        fname = os.path.join(
            args.outputs_path,get_default_output_fname(metadata, suffix=args.suffix)
        )
    else:
        fname = args.outfile

    if args.print_only:
        print(f"Dry-run, would write to `{fname}`:")
        print(df.to_string())
        return None
    df.to_csv(fname, index=False)
    #print(df.to_csv(fname, index=False))
    
if __name__ == "__main__":
    args = parser.parse_args()
    main(args)