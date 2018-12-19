#!/usr/bin/env bash

test_matrix='{"axes":["name","sequence","repeat"],"name":"test1","sequence":["seq1","seq2"],"repeat":4}'

./entry_matrix_run.py --log --matrix $test_matrix --binary echo --arguments "example run %name% %sequence% %repeat%"