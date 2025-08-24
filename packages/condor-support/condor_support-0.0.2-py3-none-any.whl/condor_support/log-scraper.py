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

"""Scan directories for condor log files"""

import time

start_time = time.time()

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__process_name__ = 'condor-log-scraper'

import argparse
import glob
import logging
import os

from condor_support.CondorLog import CondorLog


def main():
    logging.basicConfig()
    logger = logging.getLogger(__process_name__)
    logger.setLevel(logging.DEBUG)

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
    parser.add_argument('-c', '--csvout', required=True, help='csv style summary')
    parser.add_argument('-i', '--indir', nargs='*',
                        help='Input directory/directories to scan for '
                             'condor log files')
    parser.add_argument('-f', '--infile', nargs='*',
                        help='Single file(s) to analyze')
    parser.add_argument('-F', '--flist',
                        help='Path to list of log files to process')

    args = parser.parse_args()

    verbosity = 0 if args.quiet else args.verbose

    if verbosity < 1:
        logger.setLevel(logging.CRITICAL)
    elif verbosity < 2:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    if args.logout:
        fh = logging.FileHandler(args.logout)
        logger.addHandler(fh)

    with open(args.csvout, 'a') as csvout:
        colname = False

        flist = []
        if args.infile:
            flist.extend(args.infile)
        if args.flist:
            with open(args.flist, 'r') as file:
                line = file.readline()
                while line:
                    line = line.strip()
                    flist.append(line)
                    line = file.readline()

        for infile in flist:
            if os.path.isfile(infile):
                p = os.path.abspath(infile)
                jobpath = os.path.dirname(p)
                job = os.path.basename(jobpath)

                job_name = os.path.basename(job)
                dlog = CondorLog(logger, job_name)
                dlog.parse(infile)
                if not colname:
                    print(CondorLog.get_csv_labels(), file=csvout)
                    colname = True
                csv = dlog.get_csv()
                print(csv, file=csvout)

        if args.indir:
            for indir in args.indir:
                events = glob.glob(os.path.join(indir, '[SGT]*'))
                logger.info('{} events found in {}'.format(len(events), indir))
                for event in events:
                    if os.path.isdir(event):
                        jobs = glob.glob(os.path.join(event, '*'))
                        for job in jobs:
                            if os.path.isdir(job):
                                logger.debug('Working on {} job'.format(job))
                                clogs = glob.glob(os.path.join(job, 'condor-*.log'))
                                if len(clogs) == 0:
                                    clogs = glob.glob(
                                        os.path.join(job, 'condor/*.log'))
                                for clogf in clogs:
                                    if os.path.isfile(clogf):
                                        job_name = os.path.basename(clogf).replace('.log', '')
                                        dlog = CondorLog(logger, job_name)
                                        dlog.parse(clogf)
                                        if not colname:
                                            print(CondorLog.get_csv_labels(), file=csvout)
                                            colname = True
                                        csv = dlog.get_csv()
                                        print(csv, file=csvout)
    logger.info(f'Wrote: {args.csvout}')

    elap = time.time() - start_time
    logger.info('run time {:.1f} s'.format(elap))


if __name__ == "__main__":
    main()
