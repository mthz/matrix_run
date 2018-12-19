#!/usr/bin/env python
import logging
import timeit
import time
import datetime
import os
from subprocess import call
import shutil
import argparse
import json
import pprint
import itertools

def main():
    logging.basicConfig(level=logging.WARNING)

    parser = argparse.ArgumentParser(
        description='run executable with a test matrix. replaces %axis% with value of the arguments and %result_dir%')

    parser.add_argument('--matrix', required=True,
                        help='json test matrix defintion: e.g. {"axes":["name","sequence"],"name":"test1","sequence":["seq1","seq2"]}')

    parser.add_argument('--binary', default='', help="target binary to execute")
    parser.add_argument('--arguments', help="arguments for binary")
    parser.add_argument('--result_dir', default='results', help="top level result directorz")
    parser.add_argument('--log', action='store_true', help="redirect binary output to result_dir/stdout")
    parser.add_argument('--stdout', default=None, help="redirect binary output to this file")
    parser.add_argument('--aggregate', default=None)
    parser.add_argument('--aggregate_file', default="")
    parser.add_argument(
        '-v', '--verbose',
        help="verbose output",
        action="store_const", dest="loglevel", const=logging.INFO, default=logging.WARNING,
    )


    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    #---------------------------------------
    # build experiments

    matrix = json.loads(args.matrix)

    axes_names_values = []
    axes_names = matrix["axes"]

    aggregate_down_axis = []
    if args.aggregate:
        logging.info("aggregating till axis %s", args.aggregate)
        agg_idx = axes_names.index(args.aggregate)
        axes_names = axes_names[0:agg_idx + 1]
        aggregate_down_axis = axes_names[agg_idx + 1:]

    # create values for each axis
    for axis in axes_names:
        if isinstance(matrix[axis], str):
            axes_names_values.append([matrix[axis]])
        elif isinstance(matrix[axis], int):
            axes_names_values.append(range(0, matrix[axis]))
        else:
            axes_names_values.append(matrix[axis])

    # create permutation
    experiments = tuple(list(zip(axes_names, v)) for v in itertools.product(*axes_names_values))

    logging.info("running %d experiments", (len(experiments)))

    global_result_dir = args.result_dir

    #----------------------------------------------
    # run experiments

    for experiment in experiments:
        experiment_name = "-".join(str(v) for k, v in experiment)

        result_dir = os.path.join(global_result_dir, experiment_name)

        logging.info("=======================\n"
                     "running experiment %s\n"
                     "  result_dir: %s", experiment_name, result_dir)

        # generate dir if no exist
        if not os.path.isdir(result_dir):
            os.makedirs(result_dir)
        else:
            logging.warning("%s already exists", result_dir)

        # create debug log file
        debug_log_file = os.path.join(result_dir, "matrix_run.log")
        logging.info("debug_log_file: %s" % debug_log_file)

        # replace variables in argument
        mapping = [
            ('%experiment_name%', experiment_name),
            ('%result_dir%', result_dir)
        ]
        for k, v in experiment:
            mapping.append(("%" + k + "%", str(v)))

        logging.info("provide following mappings: \n" + "\n   ".join(k + " : " + v for k, v in mapping))

        arguments = args.arguments.split(" ")
        parsed_arguments = []
        for arg in arguments:
            for var in mapping:
                arg = arg.replace(var[0], var[1])
            parsed_arguments.append(arg)

        logger = logging.getLogger("matrix_run")
        logger.setLevel(args.loglevel)

        if args.log:
            logger.setLevel(logging.INFO)
            hflogger = logging.FileHandler(debug_log_file, 'w')
            logger.addHandler(hflogger)

        # write time
        today = datetime.datetime.utcnow()
        logger.info(str(today))

        cmd = [args.binary]
        cmd.extend(parsed_arguments)

        logger.info("")
        logger.info("===============\n  matrix:\n----------------\n  " + pprint.pformat(matrix))
        logger.info("===============\n  experiment:\n----------------\n  " + experiment_name)
        logger.info("===============\n  variables:\n----------------\n  " + pprint.pformat(mapping))
        logger.info("===============\n  cmd:\n----------------\n  " + " ".join(cmd))
        logger.info("===============\n  arguments:\n----------------\n  " + pprint.pformat(parsed_arguments))

        # handle stdout redirection
        stdout = None
        if args.stdout:
            stdout = open(args.stdout, "w")
        elif args.log:
            stdoutfile = os.path.join(result_dir, 'stdout.txt')
            logger.info("logging stdout to: " + stdoutfile)
            stdout = open(stdoutfile, "w")

        call(cmd, stdout=stdout)

        today = datetime.datetime.utcnow()
        logger.info("finished: " + str(today))

        if args.log:
            logger.removeHandler(hflogger)


if __name__ == '__main__':
    main()
