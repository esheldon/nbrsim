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
            if self['system'] == 'wq':
                self._write_wq(i)

            elif self['system'] == 'lsf':
                self._write_lsf(i)

            else:
                raise RuntimeError("bad system: '%s'" % self['system'])

            self._write_galsim_script(i)
            self._write_reduce_script(i)
            self._write_meds_script(i)

    def _write_galsim_script(self, index):
        """
        write the basic bash script
        """
        self['jobnum'] = index + 1
        # temporary


        self['output_dir'] = files.get_output_dir(
            self['run'],
            index,
        )

        self['image'] = files.get_image_file(
            self['run'],
            index,
        )
        self['image_nocompress'] = os.path.basename(
            files.get_image_file(
                self['run'],
                index,
                ext='fits',
            )
        )
        text=_galsim_script_template % self

        script_fname=files.get_galsim_script_file(self['run'], index)
        #print("writing:",script_fname)
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
        #print("writing:",script_fname)
        with open(script_fname, 'w') as fobj:
            fobj.write(text)

    def _write_meds_script(self, index):
        """
        write the basic bash script
        """

        self['index'] = index
        text=_meds_script_template % self

        script_fname=files.get_meds_script_file(self['run'], index)
        #print("writing:",script_fname)
        with open(script_fname, 'w') as fobj:
            fobj.write(text)


    def _write_wq(self, index):
        self._write_galsim_wq(index)
        self._write_reduce_wq(index)
        self._write_meds_wq(index)

    def _write_lsf(self, index):
        self._write_galsim_lsf(index)
        self._write_reduce_lsf(index)
        self._write_meds_lsf(index)


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
        text = _wq_template  % self

        print("writing:",wq_fname)
        with open(wq_fname,'w') as fobj:
            fobj.write(text)


    def _write_galsim_lsf(self, index):
        """
        write the lsf submission script
        """

        lsf_dir = files.get_lsf_dir(self['run'])
        if not os.path.exists(lsf_dir):
            os.makedirs(lsf_dir)

        lsf_fname=files.get_galsim_lsf_file(self['run'], index)

        if self.missing:
            lsf_fname = lsf_fname.replace('.lsf','-missing.lsf')

            imfile = files.get_image_file(self['run'], index)
            if os.path.exists(imfile):
                if os.path.exists(lsf_fname):
                    os.remove(lsf_fname)
                return

        job_name = os.path.basename(lsf_fname)
        job_name = job_name.replace('.lsf','')

        self['job_name'] = job_name
        self['logfile'] = files.get_galsim_log_file(self['run'], index)
        self['script']=files.get_galsim_script_file(self['run'], index)
        self['ncores']=2
        self['extra_requirements'] = '#BSUB -R "span[hosts=1]"'

        text = _lsf_template  % self

        print("writing:",lsf_fname)
        with open(lsf_fname,'w') as fobj:
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
        text = _wq_template  % self

        print("writing:",wq_fname)
        with open(wq_fname,'w') as fobj:
            fobj.write(text)

    def _write_reduce_lsf(self, index):
        """
        write the lsf submission script
        """

        lsf_dir = files.get_lsf_dir(self['run'])
        if not os.path.exists(lsf_dir):
            os.makedirs(lsf_dir)

        lsf_fname=files.get_reduce_lsf_file(self['run'], index)

        if self.missing:
            lsf_fname = lsf_fname.replace('.lsf','-missing.lsf')

            psfex_file = files.get_psfex_file(self['run'], index)
            #seg_file = files.get_seg_file(self['run'], index)

            if os.path.exists(psfex_file):
                if os.path.exists(lsf_fname):
                    os.remove(lsf_fname)
                return

        job_name = os.path.basename(lsf_fname)
        job_name = job_name.replace('.lsf','')

        self['job_name'] = job_name
        self['logfile'] = files.get_reduce_log_file(self['run'], index)
        self['script']=files.get_reduce_script_file(self['run'], index)
        self['ncores']=1
        self['extra_requirements'] = ''


        text = _lsf_template  % self

        print("writing:",lsf_fname)
        with open(lsf_fname,'w') as fobj:
            fobj.write(text)


    def _write_meds_wq(self, index):
        """
        write the wq submission script
        """

        wq_dir = files.get_wq_dir(self['run'])
        if not os.path.exists(wq_dir):
            os.makedirs(wq_dir)

        wq_fname=files.get_meds_wq_file(self['run'], index)

        if self.missing:
            wq_fname = wq_fname.replace('.yaml','-missing.yaml')

            meds_file = files.get_meds_file(self['run'], index)
            if os.path.exists(meds_file):
                if os.path.exists(wq_fname):
                    os.remove(wq_fname)
                return

        job_name = os.path.basename(wq_fname)
        job_name = job_name.replace('.yaml','')

        self['job_name'] = job_name
        self['logfile']  = files.get_meds_log_file(self['run'], index)
        self['script']   =files.get_meds_script_file(self['run'], index)
        text = _wq_template  % self

        print("writing:",wq_fname)
        with open(wq_fname,'w') as fobj:
            fobj.write(text)


    def _write_meds_lsf(self, index):
        """
        write the lsf submission script
        """

        lsf_dir = files.get_lsf_dir(self['run'])
        if not os.path.exists(lsf_dir):
            os.makedirs(lsf_dir)

        lsf_fname=files.get_meds_lsf_file(self['run'], index)

        if self.missing:
            lsf_fname = lsf_fname.replace('.lsf','-missing.lsf')

            meds_file = files.get_meds_file(self['run'], index)
            if os.path.exists(meds_file):
                if os.path.exists(lsf_fname):
                    os.remove(lsf_fname)
                return

        job_name = os.path.basename(lsf_fname)
        job_name = job_name.replace('.lsf','')

        self['job_name'] = job_name
        self['logfile']  = files.get_meds_log_file(self['run'], index)
        self['script']   =files.get_meds_script_file(self['run'], index)
        self['ncores']=1
        self['extra_requirements'] = ''

        text = _lsf_template  % self

        print("writing:",lsf_fname)
        with open(lsf_fname,'w') as fobj:
            fobj.write(text)


    def _makedirs(self):
        """
        make all the directories needed
        """

        dirs=[]

        for i in xrange(self['njobs']):
            output_dir = files.get_output_dir(self['run'],i)
            script_dir = files.get_script_dir(self['run'],i)

            dirs += [output_dir]

            if script_dir != output_dir:
                dirs += [script_dir]

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


# image creation
#
_galsim_script_template = r"""#!/bin/bash
# set up environment before running this script

export OMP_NUM_THREADS=1

# final output directory
odir="%(output_dir)s"

# final image location
image="%(image)s"

# the uncompressed file written by galsim
image_nocompress="%(image_nocompress)s"

# the galsim configuration file
config="%(config_file)s"

# this identifies which file galsim is writing
njobs=%(njobs)d
jobnum=%(jobnum)d

# on SLAC worker nodes, this will be something like
# /scratch/esheldon/${LSB_JOBID}
# when running from the .lsf file, this directory
# gets cleaned up

pushd "$TMPDIR"

# over-ride to use local path. Note over-ride of
# config variables must come after the config
# file argument
galsim                                   \
    -n $njobs                            \
    -j $jobnum                           \
    "$config"                            \
    output.dir="./"                      \
    output.file_name="$image_nocompress"

fpack -qz 4.0 -t 10240,1 "$image_nocompress"

bname=$(basename $image)
mv -fv "$bname" "$odir/"
mv -fv *truth.fits "$odir/"

rm -v "$image_nocompress"

popd
"""


#
# running sx, findstars, and psfex
#

_reduce_script_template = """#!/bin/bash
# set up environment before running this script

nbrsim-reduce %(image)s
"""


#
# MEDS making
#

_meds_script_template = """#!/bin/bash
# set up environment before running this script

nbrsim-make-meds %(run)s %(index)d
"""


#
# templates for job submission files
#

_wq_template = """#!/bin/bash
command: |
    %(extra_commands)s

    export tmpdir=$TMPDIR

    logfile="%(logfile)s"
    tmp_logfile="$(basename $logfile)"
    tmp_logfile="$tmpdir/$tmp_logfile"
    /usr/bin/time bash %(script)s &> "$tmp_logfile"

    mv -vf "$tmp_logfile" "$logfile"

job_name: "%(job_name)s"
"""

_lsf_template = """#!/bin/bash
#BSUB -J %(job_name)s
#BSUB -n %(ncores)d
#BSUB -oo ./%(job_name)s.oe
#BSUB -W 12:00
#BSUB -R "linux64 && rhel60 && scratch > 2"
%(extra_requirements)s

echo "working on host: $(hostname)"
uptime

export tmpdir="/scratch/esheldon/${LSB_JOBID}"
export TMPDIR="$tmpdir"

mkdir -p ${tmpdir}
echo "cd $tmpdir"
cd $tmpdir

logfile="%(logfile)s"
tmp_logfile="$(basename $logfile)"
tmp_logfile="$tmpdir/$tmp_logfile"

/usr/bin/time bash %(script)s &> "$tmp_logfile"

mv -vf "$tmp_logfile" "$logfile"

rm -r $tmpdir
"""



