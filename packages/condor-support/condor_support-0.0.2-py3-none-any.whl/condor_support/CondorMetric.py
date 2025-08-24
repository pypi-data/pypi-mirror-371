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

"""Class representing a DAG metric file"""

import datetime
import json

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'
__myname__ = 'CondorMetric'


class CondorMetric():

    def __init__(self, logger, event_name):
        self.logger = logger
        self.event = event_name
        self.start = -1.
        self.date = 'None'
        self.duration = -1
        self.exitcode = -1
        self.jobs = -1
        self.jfailed = -1
        self.jsucceeded = -1
        self.total_jobs = -1
        self.total_job_time = -1
        self.dag_status = -1

    @staticmethod
    def get_csv_labels():
        ret = 'Event, Date, Start, Duration, Job status, Jobs, Fail, ' \
              'Succeed, DAG status'
        return ret

    def parse(self, fname):
        with open(fname, 'r') as jfd:
            metric = json.load(jfd)

        self.start = metric['start_time']
        start = datetime.datetime.fromtimestamp(self.start)
        self.date = start.strftime('%Y-%m-%d %H:%M:%S')
        self.duration = metric['duration']
        self.exitcode = metric['exitcode']
        self.jobs = metric['jobs']
        self.jfailed = metric['jobs_failed']
        self.jsucceeded = metric['jobs_succeeded']
        self.dag_status = metric['dag_status'] if 'dag_status' in metric.keys() else 0
        self.total_jobs = metric['total_jobs']
        self.total_job_time = metric['total_job_time'] if 'total_job_time' in metric.keys() else 0

    def get_csv(self):
        ret = '{}, {}, {:.3f}, {:.1f}, ' \
              '{:d}, {:d}, {:d}, {:d}, ' \
              '{:d}'.\
            format(self.event, self.date, self.start, self.duration,
                   self.exitcode, self.jobs, self.jfailed, self.jsucceeded,
                   self.dag_status)
        return ret
