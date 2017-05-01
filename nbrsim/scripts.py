from __future__ import print_function
try:
    xrange
except:
    xrange=range
import os

from . import files

class ScriptWriter(dict):
    """
    class to write scripts and queue submission scripts

    parameters
    ----------
    run: string
        run identifier
    system: string
        Queue system.  Currently supports wq.
    extra_commands: string
        Extra shell commands to run, e.g. for setting up
        your environment
    """

    def __init__(self, run, system, missing=False, extra_commands=''):
        self['run'] = run
        self['extra_commands'] = extra_commands
        self['system'] = system
        
        self.missing=missing

        self._load_config()

        self['njobs']=self.conf['output']['nfiles']

        self._makedirs()

    def write_scripts(self):
        """
        write the basic bash scripts and queue submission scripts
        """
        for i in xrange(self['njobs']):
            if self['system']=='wq':
                self._write_wq(i)
            else:
                raise RuntimeError("bad system: '%s'" % self['system'])

            self._write_galsim_script(i)
            self._write_reduce_script(i)

    def _write_galsim_script(self, index):
        """
        write the basic bash script
        """
        self['jobnum'] = index + 1
        # temporary

        text=_script_template % self

        script_fname=files.get_galsim_script_file(self['run'], index)
        print("writing:",script_fname)
        with open(script_fname, 'w') as fobj:
            fobj.write(text)

    def _write_reduce_script(self, index):
        """
        write the basic bash script
        """
        self['jobnum'] = index + 1
        # temporary

        self['image'] = files.get_image_file(self['run'], index)
        text=_reduce_script_template % self

        script_fname=files.get_reduce_script_file(self['run'], index)
        print("writing:",script_fname)
        with open(script_fname, 'w') as fobj:
            fobj.write(text)


    def _write_wq(self, index):
        self._write_galsim_wq(index)
        self._write_reduce_wq(index)

    def _write_galsim_wq(self, index):
        """
        write the wq submission script
        """

        wq_dir = files.get_wq_dir(self['run'])
        if not os.path.exists(wq_dir):
            os.makedirs(wq_dir)

        wq_fname=files.get_galsim_wq_file(self['run'], index)

        if self.missing:
            wq_fname = wq_fname.replace('.yaml','-missing.yaml')

            imfile = files.get_image_file(self['run'], index)
            if os.path.exists(imfile):
                if os.path.exists(wq_fname):
                    os.remove(wq_fname)
                return

        job_name = os.path.basename(wq_fname)
        job_name = job_name.replace('.yaml','')

        self['job_name'] = job_name
        self['logfile'] = files.get_galsim_log_file(self['run'], index)
        self['script']=files.get_galsim_script_file(self['run'], index)
        text = _galsim_wq_template  % self

        print("writing:",wq_fname)
        with open(wq_fname,'w') as fobj:
            fobj.write(text)

    def _write_reduce_wq(self, index):
        """
        write the wq submission script
        """

        wq_dir = files.get_wq_dir(self['run'])
        if not os.path.exists(wq_dir):
            os.makedirs(wq_dir)

        wq_fname=files.get_reduce_wq_file(self['run'], index)

        if self.missing:
            wq_fname = wq_fname.replace('.yaml','-missing.yaml')

            psfex_file = files.get_psfex_file(self['run'], index)
            if os.path.exists(psfex_file):
                if os.path.exists(wq_fname):
                    os.remove(wq_fname)
                return

        job_name = os.path.basename(wq_fname)
        job_name = job_name.replace('.yaml','')

        self['job_name'] = job_name
        self['logfile'] = files.get_reduce_log_file(self['run'], index)
        self['script']=files.get_reduce_script_file(self['run'], index)
        text = _reduce_wq_template  % self

        print("writing:",wq_fname)
        with open(wq_fname,'w') as fobj:
            fobj.write(text)


    def _makedirs(self):
        """
        make all the directories needed
        """

        dirs=[]
        script_dir = files.get_script_dir(self['run'])

        dirs += [script_dir]

        for i in xrange(self['njobs']):
            output_dir = files.get_output_dir(self['run'],i)

            dirs += [output_dir]

        for d in dirs:
            if not os.path.exists(d):
                try:
                    print("making dir:",d)
                    os.makedirs(d)
                except:
                    pass

    def _load_config(self):
        """
        load the galsim config and do some checks
        """
        self['config_file']=files.get_config_file(self['run'])

        self.conf = files.read_config(self['run'])

#
# image creation
#
_script_template = """#!/bin/bash
# set up environment before running this script

galsim -n %(njobs)d -j %(jobnum)d %(config_file)s
"""


_galsim_wq_template = """#!/bin/bash
command: |
    %(extra_commands)s

    logfile="%(logfile)s"
    tmp_logfile="$(basename $logfile)"
    tmp_logfile="$TMPDIR/$tmp_logfile"
    bash %(script)s &> "$tmp_logfile"

    mv -vf "$tmp_logfile" "$logfile"

job_name: "%(job_name)s"
"""


#
# running sx, findstars, and psfex
#

_reduce_script_template = """#!/bin/bash
# set up environment before running this script

nbrsim-reduce %(image)s
"""

_reduce_wq_template = """#!/bin/bash
command: |
    %(extra_commands)s

    logfile="%(logfile)s"
    tmp_logfile="$(basename $logfile)"
    tmp_logfile="$TMPDIR/$tmp_logfile"
    bash %(script)s &> "$tmp_logfile"

    mv -vf "$tmp_logfile" "$logfile"

job_name: "%(job_name)s"
"""
