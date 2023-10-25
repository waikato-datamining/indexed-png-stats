import argparse
import numpy as np
import os
import traceback

from PIL import Image
from shutil import copyfile


def generate_backup(path, verbose=False):
    """
    Generates a backup of the specified file.

    :param path: the file to create a backup for
    :type path: str
    :param verbose: whether to output some logging information
    :type verbose: bool
    :return: the backup file that was generated
    :rtype: str
    """
    i = 0
    while True:
        if i == 0:
            path_bak = path + ".bak"
        else:
            path_bak = path + ".bak" + str(i)
        if not os.path.exists(path_bak):
            if verbose:
                print("  creating backup: %s" % os.path.basename(path_bak))
            copyfile(path, path_bak)
            return path_bak


def remap(image_dirs, mapping, recursive=False, backup=False, verbose=False):
    """
    Applies the supplied mapping of palette entries to indexed PNG files.

    :param image_dirs: the directory to look for PNG files
    :type image_dirs: list
    :param mapping: the dictionary mapping the 0-based int indices (old -> new)
    :type mapping: dict
    :param recursive: whether to search recursively for PNG files
    :type recursive: bool
    :param backup: whether to create a backup of the original PNG
    :type backup: bool
    :param verbose: whether to output some logging information
    :type verbose: bool
    """
    for image_dir in image_dirs:
        if verbose:
            print("Entering: %s" % image_dir)
        for f in os.listdir(image_dir):
            if f == "." or f == "..":
                continue

            full = os.path.join(image_dir, f)

            # recurse?
            if recursive and os.path.isdir(full):
                remap([full], mapping, recursive=True, verbose=verbose)
                print("Back in: %s" % image_dir)

            # png?
            if f.lower().endswith(".png"):
                if verbose:
                    print("%s" % f)

                # indexed?
                try:
                    img = Image.open(full)
                    p = img.getpalette()
                except:
                    img = None
                    p = None
                if p is None:
                    if verbose:
                        print("  no palette information")
                    continue

                # apply mapping
                arr = np.array(img)
                arr_updated = np.zeros(arr.shape, dtype=arr.dtype)
                modified = False
                for old in mapping:
                    new = mapping[old]
                    arr_old = np.where(arr == old, arr, 0)
                    unique = np.unique(arr_old)
                    update = old in unique
                    if update:
                        modified = True
                        arr_new = np.where(arr_old == old, new, 0).astype(np.uint8)
                        arr_updated = np.add(arr_updated, arr_new)

                # update image
                if modified:
                    if backup:
                        generate_backup(full, verbose=verbose)
                    if verbose:
                        print("  got modified, saving")
                    img_new = Image.fromarray(arr_updated, mode='P')
                    img_new.putpalette(p)
                    img_new.save(full)
                else:
                    if verbose:
                        print("  nothing remapped")


def main(args=None):
    """
    The main method for parsing command-line arguments and labeling.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    parser = argparse.ArgumentParser(
        description="Remaps color palette entries in indexed PNGs. E.g., swapping 5 with 1.",
        prog="indexed-png-remap",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--image_dir", metavar="DIR", nargs="+", help="the directory with the PNG files", required=True)
    parser.add_argument("-r", "--recursive", action="store_true", help="whether to scan the directory recursively", required=False)
    parser.add_argument("-m", "--mapping", help="the mapping of 0-based palette indices to apply (format: old:new)", required=True, nargs="+", type=str)
    parser.add_argument("-b", "--backup", action="store_true", help="whether to create a backup of the original images", required=False)
    parser.add_argument("-v", "--verbose", action="store_true", help="whether to be more verbose with the processing", required=False)
    parsed = parser.parse_args(args=args)
    mapping = dict()
    for m in parsed.mapping:
        parts = m.split(":")
        if len(parts) != 2:
            raise Exception("Invalid mapping, expected 'old:new' but found: %s" % m)
        mapping[int(parts[0])] = int(parts[1])

    if parsed.verbose:
        print("Mapping: %s" % str(mapping))
    remap(parsed.image_dir, mapping, recursive=parsed.recursive, backup=parsed.backup, verbose=parsed.verbose)


def sys_main() -> int:
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    """
    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == '__main__':
    main()
