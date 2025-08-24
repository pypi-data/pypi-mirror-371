#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2024 Joseph Areeda <joseph.areeda@ligo.org>
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
Class representing a single log file
"""

import datetime
import logging

import htcondor

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__version__ = '0.0.1'


class CondorLog:

    def __init__(self, logger=None, job_name='Unknown'):
        self.start = None
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger('CondorLog')

        self.job_name = job_name
        self.sub_time = -1      # timestamp: job submission
        self.exe_time = -1      # timestamp: execution start
        self.end_time = -1      # timestamp: DAG termination

        self.qtime = -1         # time spent in queue
        self.rtime = -1

        self.norm = None
        self.retcode = ''
        self.memused = ''
        self.memreq = ''
        self.cpureq = ''
        self.cpuused = ''
        self.diskreq = ''
        self.diskuse = ''

    @staticmethod
    def get_csv_labels():
        cols = 'job, date, que time, run time, norm, status, mem req, mem used, cpu req,' \
               ' cpu used, disk req, disk used'
        return cols

    def get_csv(self):
        """summarize log in one line per job"""
        try:
            q = self.qtime if self.qtime is not None else ''
            r = self.rtime if self.rtime is not None else ''
            if isinstance(self.sub_time, datetime.datetime):
                dstr = self.sub_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                dstr = '?'

            ret = f'{self.job_name}, {dstr}, {q}, {r}, {self.norm}, {self.retcode}, {self.memreq},' \
                  f' {self.memused}, {self.cpureq}, {self.cpuused}, {self.diskreq}, {self.diskuse}'
        except TypeError:
            ret = ''
        return ret

    def parse_date(self, date_time_str):
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
        return date_time_obj

    def parse(self, infile):
        my_types = {'sub': 'SubmitEvent', 'exe': 'ExecuteEvent', 'term': 'JobTerminatedEvent'}
        info = {'usage': 'TotalRemoteUsage',
                'norm': 'TerminatedNormally', 'retcode': 'ReturnValue', 'memused': 'MemoryUsage', 'memreq': 'Memory',
                'cpureq': 'Cpus', 'cpuuse': 'CpusUsage', 'diskreq': 'RequestDisk', 'diskuse': 'DiskUsage'}
        jel = htcondor.JobEventLog(infile)
        self.logger.debug(f'------ {infile}')

        for je in jel.events(stop_after=0):

            self.logger.debug(' Job event: {}'.format(je))
            for k in je.keys():
                val = je[k]
                typ = type(val)
                self.logger.debug(' key:{} val:{} ({})'.format(k, val, typ))

            myt = 'MyType'
            if myt in je.keys():
                jetyp = je[myt]

                if jetyp == 'JobDisconnectedEvent' and self.exe_time == -1 and self.sub_time != -1:
                    self.logger.critical('{} - disconnect with no execute'.format(infile))

                if jetyp == my_types['sub'] and self.sub_time == -1:
                    # job submitted
                    self.sub_time = self.parse_date(je['EventTime'])
                elif jetyp == my_types['exe'] and self.exe_time == -1:
                    self.exe_time = self.parse_date(je['EventTime'])
                elif jetyp == my_types['term']:
                    self.end_time = self.parse_date(je['EventTime'])
                    self.norm = je[info['norm']]
                    self.retcode = self.get_num(je, info['retcode'])
                    self.memused = self.get_num(je, info['memused'])
                    self.memreq = self.get_num(je, info['memreq'])
                    self.cpureq = self.get_num(je, info['cpureq'])
                    self.cpuused = self.get_num(je, info['cpuuse'])
                    self.diskreq = self.get_num(je, info['diskreq'])
                    self.diskuse = self.get_num(je, info['diskuse'])
        # some calculations
        if isinstance(self.sub_time, datetime.datetime) and isinstance(self.exe_time, datetime.datetime):
            self.qtime = (self.exe_time - self.sub_time).total_seconds()
        if isinstance(self.exe_time, datetime.datetime) and isinstance(self.end_time, datetime.datetime):
            self.rtime = (self.end_time - self.exe_time).total_seconds()

    def get_num(self, je, key):
        try:
            ret = je[key]
        except KeyError:
            ret = float('NaN')
        return ret
