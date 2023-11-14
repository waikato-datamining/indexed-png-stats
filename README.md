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
usage: indexed-png-stats [-h] -d DIR [DIR ...] [-r] [-b COUNT] [-a COUNT]
                         [-i [INDEX [INDEX ...]]]
                         [-t {summary,per-file,file-name-only}]
                         [-f {plain-text,json}] [-o FILE] [-v]

Generates statistics from indexed PNG files.

optional arguments:
  -h, --help            show this help message and exit
  -d DIR [DIR ...], --image_dir DIR [DIR ...]
                        the directory with the PNG files (default: None)
  -r, --recursive       whether to scan the directory recursively (default:
                        False)
  -b COUNT, --below COUNT
                        only output files if there are less annotation pixels
                        than this threshold (default: None)
  -a COUNT, --above COUNT
                        only output files if there are more annotation pixels
                        than this threshold (default: None)
  -i [INDEX [INDEX ...]], --index [INDEX [INDEX ...]]
                        the palette indices to apply the above/below
                        thresholds to (default: None)
  -t {summary,per-file,file-name-only}, --stats_type {summary,per-file,file-name-only}
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

## Examples

### Inspect multiple directories

Output statistics for each image in the specified directories:

```bash
indexed-png-stats \
    --image_dir /some/where/train/ /some/where/val/ /some/where/test/ \
    --stats_type per-file \
    --output_format plain-text \
    --verbose
```

### Inspect recursively

Output a summary for all images below the specified directory:

```bash
indexed-png-stats \
    --image_dir /some/where/ \
    --recursive \
    --stats_type summary \
    --output_format plain-text \
    --verbose
```

### Output files with too few annotations

The following lists images that have less than 20 pixel annotations for
any of its palette entries:

```bash
indexed-png-stats \
    --image_dir /some/where/ \
    --recursive \
    --stats_type file-name-only \
    --below 20 \
    --output_format plain-text \
    --verbose
```

This command only lists images that have fewer than 20 pixel annotations
for palette entries 2 or 5:

```bash
indexed-png-stats \
    --image_dir /some/where/ \
    --recursive \
    --stats_type file-name-only \
    --below 20 \
    --index 2 5 \
    --output_format plain-text \
    --verbose
```

### Remap palette entries

The following fixes images, mapping palette entry 5 to 1 for all images 
recursively, whilst creating backup files of the original images:

```bash
indexed-png-remap \
    --image_dir /some/where/ \
    --recursive \
    --mapping 5:1 \
    --verbose \
    --backup
```
