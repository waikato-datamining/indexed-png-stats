# indexed-png-stats
Python library that inspects indexed PNG files and outputs the pixel counts
per palette entry.
Can inspect multiple directories and work recursively as well.
Output can be as summary or per file, in plain-text or JSON.  
It is also possible to remap palette indices, e.g., replacing 5 with 1.

## Installation

```
pip install indexed-png-stats
```

## Command-line

### Statistics

```
usage: indexed-png-stats [-h] -d DIR [DIR ...] [-r] [-t {summary,per-file}]
                         [-f {plain-text,json}] [-o FILE] [-v]

Generates statistics from indexed PNG files.

optional arguments:
  -h, --help            show this help message and exit
  -d DIR [DIR ...], --image_dir DIR [DIR ...]
                        the directory with the PNG files (default: None)
  -r, --recursive       whether to scan the directory recursively (default:
                        False)
  -t {summary,per-file}, --stats_type {summary,per-file}
                        the type of statistics to generate (default: summary)
  -f {plain-text,json}, --output_format {plain-text,json}
                        how to present the statistics (default: plain-text)
  -o FILE, --output_file FILE
                        the file to store the generated statistics in
                        (default: None)
  -v, --verbose         whether to be more verbose with the processing
                        (default: False)
```

### Remapping

```
usage: indexed-png-remap [-h] -d DIR [DIR ...] [-r] -m MAPPING [MAPPING ...]
                         [-b] [-v]

Remaps color palette entries in indexed PNGs. E.g., swapping 5 with 1.

optional arguments:
  -h, --help            show this help message and exit
  -d DIR [DIR ...], --image_dir DIR [DIR ...]
                        the directory with the PNG files (default: None)
  -r, --recursive       whether to scan the directory recursively (default:
                        False)
  -m MAPPING [MAPPING ...], --mapping MAPPING [MAPPING ...]
                        the mapping of 0-based palette indices to apply
                        (format: old:new) (default: None)
  -b, --backup          whether to create a backup of the original images
                        (default: False)
  -v, --verbose         whether to be more verbose with the processing
                        (default: False)
```