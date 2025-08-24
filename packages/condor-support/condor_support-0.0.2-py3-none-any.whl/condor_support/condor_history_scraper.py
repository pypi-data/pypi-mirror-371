#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2025 Joseph Areeda <joseph.areeda@ligo.org>
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

"""
Queries  an htcondor schedd for job history and writes it to a CSV file,
 and creates hostogram plots for memory usage and runtime.
"""
import csv
import os
import socket
import time
from datetime import datetime

import matplotlib

start_time = time.time()

import argparse
import logging
from pathlib import Path
import re
import sys
import traceback

import htcondor

from astropy.io import ascii
import numpy as np
import matplotlib.pyplot as plt

try:
    from ._version import __version__
except ImportError:
    __version__ = '0.0.1'

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__process_name__ = Path(__file__).name

matplotlib.use('agg')
logger = None

epilog = """
Example usage:

With no arguments, the script will query the default schedd for all jobs
submitted by the detchar user.

Use the --schedd-name argument to specify a different schedd. This is a substring that must be
matched in the schedd name.

    condor_history_scraper --schedd-name omicron
May match detchar-omicron.ldas.ligo-la.caltech.edu. If multiple schedds match the name, the first one
will be used.

Use the --arg-str argument to group jobs by a particular string in the arguments. This is useful
for grouping jobs by a particular pipeline name.

    condor_history_scraper --arg-str " omicron "
Note the spaces in the string so that we match the omicron program not the onda environment name
or a path contained in the arguments.
"""


def parser_add_args(parser):
    """
    Set up the command parser
    :param argparse.ArgumentParser parser:
    :return: None but parser object is updated
    """
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='increase verbose output')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-q', '--quiet', default=False, action='store_true',
                        help='show only fatal errors')
    parser.add_argument('--schedd-name', help='partial string to match schedd name')
    parser.add_argument('-u', '--user', default='detchar', help='condor user to match')
    parser.add_argument('-m', '--match', type=int, default=0,
                        help='Maximum number of jobs to match ')

    default_out = Path(os.getenv('TMPDIR', '/tmp')) / 'condor_history_scraper'
    parser.add_argument('-o', '--out', type=Path, default=default_out, help='output directory')
    parser.add_argument('-a', '--arg-str', type=str, nargs='*',
                        help='Substring to match in the arguments, may be used multiple times')


def write_csv(outdir, job_name, data):
    """
    Writes the provided data to a CSV file located in a temporary directory.

    The function creates a CSV file named after the supplied job_name and stores
    it within the specified temporary directory. The data parameter is expected
    to provide the content that will populate the file. This function does not
    return any result but ensures the data is successfully written into the file.

    :param outdir: Directory path where the CSV file will be created
    :type outdir: str
    :param job_name: Name of the file to be created, without file extension
    :type job_name: str
    :param data: Data to be written to the CSV file. Should be in a format that can
                 be handled for writing as CSV content
    :type data: list or similar iterable
    :return: Table correasponding to the CSV file
    :type: astropy.table.Table
    """
    csv_path = Path(outdir) / f'{job_name}.csv'
    with open(csv_path, 'w', encoding='utf-8', newline='') as csvout:
        writer = csv.writer(csvout)
        for row in data:
            writer.writerow(row)
    logger.info(f'Wrote {len(data)} lines to {csv_path}')
    ret = ascii.read(csv_path, delimiter=',', guess=False)
    return ret


def make_histogram(outdir, job_name, data, col_name):
    """
    Generates and saves a histogram for a specific column within the provided data.

    :param outdir: The output directory where the resulting histogram image will be saved.
    :type outdir: Path|str
    :param job_name: A unique identifier or name for the job. Used for naming the output file.
    :type job_name: str
    :param data: The input data as a list of numbers
    :type data: plist
    :param col_name: The name of the column in the DataFrame for which the histogram is to be created.
    :type col_name: str
    :return: None
    """
    png_name = f'{job_name}-{col_name}-hist.png'
    png_name = re.sub('[^a-zA-Z0-9_\\-.\\s]', '_', png_name)
    png_path = Path(outdir) / png_name
    bins = np.linspace(0, max(data), 30)
    # Create the histogram
    fig = plt.figure(figsize=(10, 6))
    plt.hist(data, bins=bins, edgecolor='black', label=f'{job_name}-{col_name}')
    ax = plt.gca()
    ax.set_yscale('log')
    # ax.legend()

    # Add labels and title
    plt.xlabel(col_name, fontsize=14)
    plt.ylabel('Frequency (log)', fontsize=14)
    fig.tight_layout(h_pad=2.5)
    fig.subplots_adjust(top=0.9)
    fig.suptitle(f'Histogram of {col_name} from {job_name}', fontsize=16)
    percentile_txt = f"N={len(data)}. Percentiles:"
    for pctl in [5, 10, 25, 50, 75, 90, 95]:
        percentile_txt += f" {pctl}%: {np.percentile(data, pctl):.1f}"

    plt.title(percentile_txt, fontsize=12)

    plt.savefig(png_path)
    logger.info(f'Wrote histogram to {png_path}')
    pass


def get_default_ifo():
    # if at a site we have a default ifo
    host = socket.getfqdn()
    if 'ligo-la' in host:
        ifo = 'L1'
    elif 'ligo-wa' in host:
        ifo = 'H1'
    else:
        ifo = os.getenv('IFO')
    if ifo is None:
        ifo = 'UK'
    return ifo, host


def main():
    global logger

    log_file_format = "%(asctime)s - %(levelname)s - %(funcName)s %(lineno)d: %(message)s"
    log_file_date_format = '%m-%d %H:%M:%S'
    logging.basicConfig(format=log_file_format, datefmt=log_file_date_format)
    logger = logging.getLogger(__process_name__)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description=__doc__, prog=__process_name__, epilog=epilog,
                                     formatter_class=argparse.RawTextHelpFormatter,)
    parser_add_args(parser)
    args = parser.parse_args()
    verbosity = 0 if args.quiet else args.verbose

    if verbosity < 1:
        logger.setLevel(logging.CRITICAL)
    elif verbosity < 2:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    ifo, host = get_default_ifo()
    # debugging?
    logger.debug(f'{__process_name__} version: {__version__}  on {host}')

    out_dir = args.out or Path(os.getenv('TMPDIR', '/tmp')) / 'condor_history_scraper'
    out_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = out_dir / f'{__process_name__}.log'
    fh = logging.FileHandler(log_file_path, mode='w')
    fh.setFormatter(logging.Formatter(log_file_format, datefmt=log_file_date_format))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    logger.info(f'Output directory: {out_dir}, log file: {log_file_path}')
    for k, v in args.__dict__.items():
        logger.debug('    {} = {}'.format(k, v))

    if args.schedd_name:
        schedd_name = args.schedd_name
        collector = htcondor.Collector()
        schedd_ad = collector.locateAll(htcondor.DaemonTypes.Schedd)  # locate the requested schedd
        for ad in schedd_ad:
            if schedd_name in ad.get('Name'):
                schedd_ad = ad
                break
        logger.info(f'Found schedd {schedd_name} in {schedd_ad.get("Name")}')
        schedd = htcondor.Schedd(schedd_ad)
    else:
        logger.info('No schedd name provided, using default schedd')
        schedd = htcondor.Schedd()
        pass
    m = re.match('.*alias=([^&]+)', str(schedd.location))
    if m:
        logger.info(f'Using schedd {m.group(1)}')
    else:
        logger.info(f'Using schedd {schedd.location}')

    constraint = f'  OsUser=="{args.user}" && !regexp(".*dagman.*", Arguments)'
    if args.arg_str:
        group_all = True
        job_key = ''
        for arg_str in args.arg_str:
            constraint += f' && regexp("{arg_str}", Arguments)'
            job_key += '__' if job_key else ''
            job_key += re.sub('\\+?\\d+$', '', arg_str)
        job_key = re.sub('[^a-zA-Z0-9_\\-.]', '_', job_key)
        logger.info(f'Grouped jobs all jobss into [{job_key}]')
    else:
        group_all = False

    projection = ['OsUser', 'ResidentSetSize_RAW', 'RequestMemory', 'DiskUsage', 'RequestDisk', 'RequestCpus',
                  'JobCurrentStartDate', 'JobFinishedHookDone', 'RemoteWallClockTime', 'RemoteUserCpu', 'JobUniverse',
                  'JobBatchName', 'Err', 'Cmd', 'Arguments']
    column_names = ['user', 'mem_raw', 'mem_req', 'disk_raw', 'disk_req', 'cpu_req',
                    'start', 'finish', 'Clock_Time', 'CPU_Time', 'universe',
                    'batch_name', 'err', 'cmd', 'args']
    # column_dtypes = [str, int, int, int, int, int,
    #                  str, str, float, float, int,
    #                  str, str, str, str]
    match = args.match

    detchar_jobs = dict()  # we will have one table for each condor job name
    query_start = time.time()
    logger.debug(f'About to query history.\n    constraint: {constraint}\n    projection: {projection}\n    match: {match}')
    sched_history = list(schedd.history(constraint=constraint, projection=projection, match=match,))
    logger.debug(f'Got {len(sched_history)} jobs. Query time: {time.time() - query_start:.1f} s')
    ad_proc_start = time.time()
    for ad in sched_history:
        job_name = re.sub('\\+?\\d+$', '', ad['JobBatchName'])
        ad['JobBatchName'] = job_name
        job_key = job_key if group_all else job_name
        if job_key not in detchar_jobs:
            detchar_jobs[job_key] = list()
            detchar_jobs[job_key].append(column_names)
        row = list()
        for col in projection:
            it = ad.get(col)
            if col == 'JobCurrentStartDate':
                start_dt = datetime.fromtimestamp(it)
                it = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            elif col == 'JobFinishedHookDone':
                finish_dt = datetime.fromtimestamp(it)
                it = finish_dt.strftime('%Y-%m-%d %H:%M:%S')
            row.append(it)
        job_key = job_key if group_all else job_name
        detchar_jobs[job_key].append(row)
    logger.debug(f'Processed {len(sched_history)} jobs. Process time: {time.time() - ad_proc_start:.1f} s')
    data_tables = dict()
    for job_name, data in detchar_jobs.items():
        data_tables[job_name] = write_csv(out_dir, job_name, data)

    for job_name, table in data_tables.items():
        if len(table) > 100:
            mem_gbs = table['mem_raw'] / 1.0e6
            make_histogram(out_dir, f'{ifo}:{job_name}', mem_gbs, 'Memory GB')
            make_histogram(out_dir, f'{ifo}:{job_name}', table['Clock_Time'], 'Run time (s)')


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OSError, NameError, ArithmeticError, RuntimeError) as ex:
        print(ex, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    if logger is None:
        logging.basicConfig()
        logger = logging.getLogger(__process_name__)
        logger.setLevel(logging.DEBUG)
    # report our run time
    logger.info(f'Elapsed time: {time.time() - start_time:.1f}s')
