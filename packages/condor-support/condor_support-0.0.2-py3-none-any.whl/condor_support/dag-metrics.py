#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2021 Joseph Areeda <joseph.areeda@ligo.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Scan dqr results to summarize metric files"""
import glob
import time
from pathlib import Path

start_time = time.time()

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__process_name__ = 'dqr-dag-metrics'

import argparse
import logging

from CondorMetric import CondorMetric


def proc_path(csvout, inpath):
    """
    Process a file or directory
    :param csvout:
    :param inpath:
    :return:
    """
    global colname, cnt
    if inpath.is_dir():
        metrics = glob.glob(str(inpath / '*'))
    elif str(inpath.name).endswith('.dag.metrics'):
        metrics = [inpath]
    else:
        metrics = []

    for metric_file in metrics:
        infile = Path(metric_file)
        if infile.is_dir():
            proc_path(csvout, infile)
        elif str(infile.name).endswith('.dag.metrics'):
            logger.debug(f'Metric file: {metric_file}')
            metric = CondorMetric(logger, infile.parent.name)
            metric.parse(metric_file)
            if not colname:
                lbls = CondorMetric.get_csv_labels()
                print(lbls, file=csvout)
                colname = True
            csv = metric.get_csv()
            print(csv, file=csvout)
            cnt += 1


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger(__process_name__)
    logger.setLevel(logging.DEBUG)

    start_time = time.time()
    parser = argparse.ArgumentParser(description=__doc__,
                                     prog=__process_name__)
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='increase verbose output')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-q', '--quiet', default=False, action='store_true',
                        help='show only fatal errors')
    parser.add_argument('-l', '--logout',
                        help='Optional path to logging output')
    parser.add_argument('-o', '--out', help='out file base')
    parser.add_argument('-i', '--indir', nargs='+',
                        help='Input directory to scan for condor metric files')
    args = parser.parse_args()

    verbosity = 0 if args.quiet else args.verbose

    if verbosity < 1:
        logger.setLevel(logging.CRITICAL)
    elif verbosity < 2:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    csv_name = args.out + '-metrics.csv'
    cnt = 0

    with open(csv_name, 'w') as csvout:
        colname = False
        for ind in args.indir:
            inpath = Path(ind)
            proc_path(csvout, inpath)

    logger.info('Wrote {:d} lines to {}'.format(cnt, csv_name))

    elap = time.time() - start_time
    logger.info('run time {:.1f} s'.format(elap))
