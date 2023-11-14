import argparse
import json
import numpy as np
import os
import traceback

from PIL import Image


STATS_TYPE_SUMMARY = "summary"
STATS_TYPE_PERFILE = "per-file"
STATS_TYPE_FILE_NAME_ONLY = "file-name-only"
STATS_TYPES = [
    STATS_TYPE_SUMMARY,
    STATS_TYPE_PERFILE,
    STATS_TYPE_FILE_NAME_ONLY,
]

OUTPUT_FORMAT_PLAINTEXT = "plain-text"
OUTPUT_FORMAT_JSON = "json"
OUTPUT_FORMATS = [
    OUTPUT_FORMAT_PLAINTEXT,
    OUTPUT_FORMAT_JSON,
]


SUMMARY_ENTRY = "all"


def collect(stats, image_dirs, recursive=False, stats_type=STATS_TYPE_SUMMARY,
            below=None, above=None, index=None, verbose=False):
    """
    Collects the statistics from the indexed PNG files.

    :param stats: the stats to append to
    :type stats: dict
    :param image_dirs: the directory to look for PNG files
    :type image_dirs: list
    :param recursive: whether to search recursively for PNG files
    :type recursive: bool
    :param stats_type: the type of stats to generate
    :type stats_type: str
    :param below: collect files in stats when less annotation pixels than this threshold, ignored when None
    :type below: int
    :param above: collect files in stats when more annotation pixels than this threshold, ignored when None
    :type above: int
    :param index: the palette indices to apply the below/above thresholds to, applied to all if None
    :type index: list
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
                collect(stats, [full], recursive=True, stats_type=stats_type, below=below, above=above, index=index, verbose=verbose)
                if verbose:
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

                # get stats
                img = np.array(img)
                unique, counts = np.unique(img, return_counts=True)

                if (below is not None) or (above is not None):
                    add = False

                    # below threshold?
                    if below is not None:
                        for idx, count in zip(unique, counts):
                            if count < below:
                                if index is None:
                                    add = True
                                    break
                                if (index is not None) and (idx in index):
                                    add = True
                                    break

                    # above threshold?
                    if above is not None:
                        for idx, count in zip(unique, counts):
                            if count > above:
                                if index is None:
                                    add = True
                                    break
                                if (index is not None) and (idx in index):
                                    add = True
                                    break
                else:
                    add = True

                # summary
                if add:
                    if stats_type == STATS_TYPE_SUMMARY:
                        for i in range(len(unique)):
                            v = unique[i]
                            c = counts[i]
                            l = str(v)
                            if len(stats) == 0:
                                stats[SUMMARY_ENTRY] = dict()
                            if l not in stats[SUMMARY_ENTRY]:
                                stats[SUMMARY_ENTRY][l] = 0
                            stats[SUMMARY_ENTRY][l] += int(c)
                        pass

                    # per file
                    elif stats_type == STATS_TYPE_PERFILE:
                        stats[full] = dict()
                        for i in range(len(unique)):
                            v = unique[i]
                            c = counts[i]
                            l = str(v)
                            stats[full][l] = int(c)

                    # file name only
                    elif stats_type == STATS_TYPE_FILE_NAME_ONLY:
                        stats[full] = dict()

                    # unsupported
                    else:
                        raise Exception("Unsupported stats type: %s" % stats_type)


def output_stats(stats, stats_type=STATS_TYPE_SUMMARY, output_format=OUTPUT_FORMAT_PLAINTEXT, output_file=None):
    # plain text
    if output_format == OUTPUT_FORMAT_PLAINTEXT:
        output = []
        for k in stats:
            skip = (k == SUMMARY_ENTRY)
            if not skip:
                output.append(k)
            for index in stats[k]:
                indent = ("" if skip else "  ")
                output.append("%s%s: %d" % (indent, index, stats[k][index]))
        if output_file is None:
            for line in output:
                print(line)
        else:
            with open(output_file, "w") as fp:
                for line in output:
                    fp.write(line)
                    fp.write("\n")

    # json
    elif output_format == OUTPUT_FORMAT_JSON:
        if (len(stats) > 0) and (SUMMARY_ENTRY in stats):
            stats = stats[SUMMARY_ENTRY]
        if stats_type == STATS_TYPE_FILE_NAME_ONLY:
            stats = list(stats.keys())
        if output_file is None:
            print(json.dumps(stats, indent=2))
        else:
            with open(output_file, "w") as fp:
                json.dump(stats, fp, indent=2)

    # unsupported
    else:
        raise Exception("Unsupported output format: %s" % output_format)


def main(args=None):
    """
    The main method for parsing command-line arguments and labeling.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    parser = argparse.ArgumentParser(
        description="Generates statistics from indexed PNG files.",
        prog="indexed-png-stats",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--image_dir", metavar="DIR", nargs="+", help="the directory with the PNG files", required=True)
    parser.add_argument("-r", "--recursive", action="store_true", help="whether to scan the directory recursively", required=False)
    parser.add_argument("-b", "--below", metavar="COUNT", default=None, type=int, help="only output files if there are less annotation pixels than this threshold", required=False)
    parser.add_argument("-a", "--above", metavar="COUNT", default=None, type=int, help="only output files if there are more annotation pixels than this threshold", required=False)
    parser.add_argument("-i", "--index", metavar="INDEX", default=None, type=int, help="the palette indices to apply the above/below thresholds to", required=False, nargs="*")
    parser.add_argument("-t", "--stats_type", choices=STATS_TYPES, default=STATS_TYPE_SUMMARY, help="the type of statistics to generate", required=False)
    parser.add_argument("-f", "--output_format", choices=OUTPUT_FORMATS, default=OUTPUT_FORMAT_PLAINTEXT, help="how to present the statistics", required=False)
    parser.add_argument("-o", "--output_file", metavar="FILE", default=None, help="the file to store the generated statistics in", required=False)
    parser.add_argument("-v", "--verbose", action="store_true", help="whether to be more verbose with the processing", required=False)
    parsed = parser.parse_args(args=args)
    stats = dict()
    collect(stats, parsed.image_dir, recursive=parsed.recursive, stats_type=parsed.stats_type,
            below=parsed.below, above=parsed.above, index=parsed.index, verbose=parsed.verbose)
    output_stats(stats, stats_type=parsed.stats_type, output_format=parsed.output_format, output_file=parsed.output_file)


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
