#!/usr/bin/python
import argparse
import os.path
import glob
import difflib, sys

def _cli_parse(args):
    odir_path = args.original_directory[0]
    mdir_path = args.modified_directory[0]
    try:
        assert(os.path.isdir(odir_path))
    except AssertionError:
        print("Error!", odir_path, "is not a valid directory.")
    try:
        assert(os.path.isdir(mdir_path))
    except AssertionError:
        print("Error!", mdir_path, "is not a valid directory.")
    try:
        assert(odir_path != mdir_path)
    except AssertionError:
        print("These directories are the same directory.")

    o = set()
    for path in glob.iglob(os.path.join(odir_path, '**'), recursive=True):
        if os.path.isdir(path):
            continue
        o.add(path[len(odir_path):])
    m = set()
    for path in glob.iglob(os.path.join(mdir_path, '**'), recursive=True):
        if os.path.isdir(path):
            continue
        m.add(path[len(mdir_path):])

    if (o - m):
        print("\nDeleted files:")
        for path in (o - m):
            print(' ---', path)
    if (m - o):
        print("\nNew files:")
        for path in (m - o):
            print(' +++', path)
    if o.intersection(m):
        print("\nLooking for changed files...")
        for filepath in o.intersection(m):
            with open(odir_path + filepath, 'r') as ofile_obj:
                ofile = ofile_obj.readlines()
            with open(mdir_path + filepath, 'r') as mfile_obj:
                mfile = mfile_obj.readlines()
            sys.stdout.writelines(difflib.context_diff(ofile, mfile, fromfile=odir_path+filepath, tofile=mdir_path+filepath))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('original_directory', nargs=1,
                        help="Directory path containing the original files.")
    parser.add_argument('modified_directory', nargs=1,
                        help="Directory path containing the modified files.")
    args = parser.parse_args()
    _cli_parse(args)
