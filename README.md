# Matrix Run

Utility script to run a test matrix with all permutations on an executable

## Usage

1) define test matrix json

Example: `{"axes":["name","sequence"],"name":"test1","sequence":["seq1","seq2"]}`

`axes`: defines the order of the axes, followed by the value definition for each axis which can be a list of strings or a number

2) build command line and use `%axis%` as placeholder within `--arguments`

`entry_matrix_run.py --binary awesome_application --arguments "--sequence %sequence%"`

the script offers some special variables:

* `%experiment_name%`: concatanation of axes e.g. test1-sequence
* `%result_dir%`: --result_dir/%experiment_name%

## Additional Features

### Logging 

* `-v` verbose script output
* `--log` redirect output of binary into %result_dir%/stdout.txt and script output to matrix_run.log
* `--stdout filename.txt` redirect output of binary into filename.txt



