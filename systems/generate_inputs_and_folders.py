import numpy as np
import json
import argparse
import itertools
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

parser = argparse.ArgumentParser(description="Generate folders and inputs")

parser.add_argument(
    "metadata_path", 
    help="Path to the folder to metadata"
)

parser.add_argument(
    "-d", "--dry_run", 
    help="Dry run",
    action="store_true", required=False
)

parser.add_argument(
    "-o", "--output",
    help="File to write input script to",
    default=None, required=False,
)


def safe_format(inp: str, d: dict) -> str:
    """Safely format a string with placeholders, leaving all other braces intact."""
    # Step 1: Escape all braces
    safe_inp = inp.replace('{', '{{').replace('}', '}}')
    
    # Step 2: Re-enable valid placeholders
    for key in d:
        safe_inp = safe_inp.replace('{{' + key + '}}', '{' + key + '}')
    
    # Step 3: Apply format_map with SafeDict
    class SafeDict(dict):
        def __missing__(self, key):
            return '{' + key + '}'
    
    return safe_inp.format_map(SafeDict(d))

def read_metadata(metadata_path: str) -> dict:
    """
    Reads metadata from a file.
    """
    with open(metadata_path, 'r') as f:
        return json.load(f)

def write_input(template_file, kwargs, inp=None):
    with open(template_file, 'r') as tinp:
        template = tinp.read()
    input_script = safe_format(template, kwargs)
    if inp is None:
        print(input_script)
    else:
        with open(inp, 'w') as out:
            
            out.write(input_script)



def format_value(value, fmt_spec=None):
    """Apply format string like '06.3f' if specified."""
    if fmt_spec:
        try:
            return format(value, fmt_spec)
        except Exception:
            # fallback in case of bad format or non-numeric value
            return str(value)
    return str(value)

def generate_items(iterables):

    keys = list(iterables.keys())
    value_lists = [v["values"] for v in iterables.values()]

    for combo in itertools.product(*value_lists):
        params = dict(zip(keys, combo))
        yield params

def generate_file_paths(args, meta):
    """Yield (file_path, folder_path, kwargs) tuples for each parameter combination."""
    iterables = {k: v for k, v in meta.items() if isinstance(v, dict) and v.get("iterable")}
    working_folder = os.path.dirname(args.metadata_path)
    template_file = os.path.join(working_folder, meta['template'])

    for params in generate_items(iterables):
        path_parts = [working_folder]
        file_prefix = meta["file_prefix"]

        kwargs = {}
        for key, value in params.items():
            conf = iterables[key]
            fmt_value = format_value(value, conf.get("format"))
            prefix = conf.get("prefix", "{value}").format(value=fmt_value)

            if conf.get("subfolder"):
                path_parts.append(prefix)
            else:
                file_prefix += prefix + "_"

            kwargs[key] = fmt_value

        folder_path = os.path.join(*path_parts)
        filename = file_prefix.rstrip("_") + ".inp"
        kwargs["full_file_prefix"] = file_prefix.rstrip("_")
        file_path = os.path.join(folder_path, filename)

        yield file_path, folder_path, template_file, kwargs


def write_generated_files(args, meta):
    """Write input files based on generated file paths."""
    non_iterables = {k: v for k, v in meta.items() if not (isinstance(v, dict) and v.get("iterable"))}
    for file_path, folder_path, template_file, kwargs in generate_file_paths(args, meta):
        kwargs.update(non_iterables)
        if args.dry_run:
            print(f"Dry-run, would write to {file_path}:")
            write_input(template_file, kwargs)
        else:
            os.makedirs(folder_path, exist_ok=True)
            if args.output is not None:
                inpfile = os.path.join(os.path.dirname(file_path), args.output)
            else:
                inpfile = file_path
            write_input(template_file, kwargs, inp=inpfile)


def generate_files(args, meta):
    """Backward-compatible entry point."""
    write_generated_files(args, meta)

if __name__ == "__main__":
    args = parser.parse_args()
    metadata = read_metadata(args.metadata_path)
    generate_files(args, metadata)
    
        
