#!/usr/bin/env python3
"""Plan the unchanged full CPU/GPU matrix; actual execution needs separate authorization."""
import argparse
from pathlib import Path
import sys
from run_cpu_gpu_pilot import run

def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--executable',type=Path,required=True)
    parser.add_argument('--input-tool',type=Path,required=True)
    parser.add_argument('--prerequisites',type=Path)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--framework-compatibility-policy',
                        help='Explicit pinned framework compatibility; requires complete identity-matched full prerequisites')
    parser.add_argument('--execute-study',action='store_true',
                        help='Execution latch; use only after separate study authorization and fresh prerequisites')
    args=parser.parse_args()
    if not args.dry_run and not args.execute_study:
        parser.error('planning only: specify --dry-run; execution requires separate authorization and --execute-study')
    args.executable=args.executable.absolute();args.input_tool=args.input_tool.absolute()
    try:return run(args,part='study')
    except (OSError,ValueError,KeyError) as error:print(error,file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
