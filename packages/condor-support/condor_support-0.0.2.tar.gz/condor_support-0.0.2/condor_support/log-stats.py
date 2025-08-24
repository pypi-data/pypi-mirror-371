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

"""Summarize the output of dqr-log-scraper"""
import logging
import time

start_time = time.time()

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__process_name__ = 'dqr-log-stats'

import argparse

from astropy import table
import numpy as np

stat_cols = ['que time', 'run time', 'mem req', 'mem used', 'cpu req', 'cpu used', 'disk req', 'disk used']
col_hdr = 'job, count, success, fail, '
for c in stat_cols:
    col_hdr += '{0}-min, {0}-25, {0}-median, {0}-75, {0}-max,'.format(c)


def get_stats(tbl):
    ret = ''
    status = tbl['status'][np.logical_not(np.isnan(tbl['status']))]
    success = np.count_nonzero(status == 0)
    fail = np.count_nonzero(status != 0)
    ret += '{}, {}, '.format(success, fail)
    for col in stat_cols:
        ctbl = np.array(tbl[col][np.logical_not(np.isnan(tbl[col]))])
        if len(ctbl) < 5:
            for i in range(5):
                ret += ' n/a, '
        else:
            pcts = np.percentile(ctbl, [0, 25, 50, 75, 100])
            for p in pcts:
                ret += ' {},'.format(p)
    return ret


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger(__process_name__)
    logger.setLevel(logging.DEBUG)

    start_time = time.time()
    parser = argparse.ArgumentParser(description=__doc__, prog=__process_name__)
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='increase verbose output')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-q', '--quiet', default=False, action='store_true',
                        help='show only fatal errors')
    parser.add_argument('-i', '--intbl', help='outout from log scraper to summarize')
    parser.add_argument('-o', '--out', help='output base')
    args = parser.parse_args()

    verbosity = 0 if args.quiet else args.verbose

    if verbosity < 1:
        logger.setLevel(logging.CRITICAL)
    elif verbosity < 2:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    log_tbl = table.Table.read(args.intbl)
    tbl_by_job = log_tbl.group_by('job')
    out_csv = args.out + '-summary.csv'
    with open(out_csv, 'w') as csv:
        print(col_hdr, file=csv)
        for group in tbl_by_job.groups:
            line = '{}, {}, '.format(group[0]['job'], len(group))
            line += get_stats(group)
            print(line, file=csv)
    logger.info('Wrote: ' + out_csv)

    elap = time.time() - start_time
    logger.info('run time {:.1f} s'.format(elap))
