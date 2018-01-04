#!/usr/bin/env python
import argparse, setlog

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Start from genbank file, find closest reference, add to pre-computed reference tree""")
    parser.add_argument("input", help="gbk file to start query")
    parser.add_argument("refdir", help="Directory of precomputed reference files")
    args = parser.parse_args()
