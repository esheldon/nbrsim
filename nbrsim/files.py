from __future__ import print_function
import os, sys

#
# data directory structure
#

INDEX_FMT='%06d'

BASE_DIR_KEY='NBRSIM_DIR'
CONFIG_DIR_KEY='NBRSIM_CONFIG_DIR'
FILE_FRONT='nbrsim'

def get_basedir():
    """
    The base directory

    Runs are held under bad/run
    """
    if BASE_DIR_KEY not in os.environ:
        raise ValueError("$%s environment variable is not set" % BASE_DIR_KEY)

    return os.environ[BASE_DIR_KEY]

def get_generic_basename(run, index=None, type=None, ext='fits'):
    """
    basic file names are
        {front}-{run}.{ext}
        or
        {front}-{run}-{index}.{ext}
        or
        {front}-{run}-{index}-{type}.{ext}
    """
    fname = [FILE_FRONT,run]
    
    if index is not None:
        fname += [INDEX_FMT % index]

    if type is not None:
        fname += [type]

    fname = '-'.join(fname)

    if ext is not None:
        fname += '.' + ext

    return fname


def get_rundir(run):
    """
    The run directory BASE_DIR/run
    """
    bdir=get_basedir()
    return os.path.join(bdir, run)

def get_script_dir(run, index):
    """
    currently same as output dir
    """
    return get_output_dir(run, index)

def get_output_dir(run, index):
    """
    The script directory BASE_DIR/{run}/output
    """
    bdir=get_basedir()

    rdir = INDEX_FMT % index
    return os.path.join(bdir, run, 'output', rdir)


def get_galsim_script_file(run, index):
    """
    get the script file path
    """

    dir=get_script_dir(run, index)
    basename = get_generic_basename(run, index=index, type='galsim', ext='sh')
    return os.path.join(dir, basename)

def get_reduce_script_file(run, index):
    """
    get the script file path
    """

    dir=get_script_dir(run, index)
    basename = get_generic_basename(run, index=index, type='reduce', ext='sh')
    return os.path.join(dir, basename)

def get_meds_script_file(run, index):
    """
    get the script file path
    """

    dir=get_script_dir(run, index)
    basename = get_generic_basename(run, index=index, type='meds', ext='sh')
    return os.path.join(dir, basename)


def get_wq_dir(run):
    """
    We don't want wq stuff on gpfs
    """
    bdir = os.environ['TMPDIR']
    return os.path.join(bdir, 'nbrsim', run, 'scripts')

def get_lsf_dir(run):
    """
    We don't want wq stuff on gpfs
    """
    return get_wq_dir(run)


def get_galsim_wq_file(run, index):
    """
    get the script file path
    """
    dir=get_wq_dir(run)
    basename = get_generic_basename(run, index=index, type='galsim', ext='yaml')
    return os.path.join(dir, basename)

def get_reduce_wq_file(run, index):
    """
    get the script file path
    """
    dir=get_wq_dir(run)
    basename = get_generic_basename(run, index=index, type='reduce', ext='yaml')
    return os.path.join(dir, basename)

def get_meds_wq_file(run, index):
    """
    get the script file path
    """
    dir=get_wq_dir(run)
    basename = get_generic_basename(run, index=index, type='meds', ext='yaml')
    return os.path.join(dir, basename)

def get_galsim_lsf_file(run, index):
    """
    get the script file path
    """
    dir=get_lsf_dir(run)
    basename = get_generic_basename(run, index=index, type='galsim', ext='lsf')
    return os.path.join(dir, basename)

def get_reduce_lsf_file(run, index):
    """
    get the script file path
    """
    dir=get_lsf_dir(run)
    basename = get_generic_basename(run, index=index, type='reduce', ext='lsf')
    return os.path.join(dir, basename)

def get_meds_lsf_file(run, index):
    """
    get the script file path
    """
    dir=get_lsf_dir(run)
    basename = get_generic_basename(run, index=index, type='meds', ext='lsf')
    return os.path.join(dir, basename)




def get_image_file(run, index, ext='fits.fz'):
    """
    get the path to a image file
    """
    dir=get_output_dir(run, index)
    basename = get_generic_basename(
        run,
        index=index,
        type='image',
        ext=ext,
    )

    return os.path.join(dir, basename)

def get_seg_file(run, index, ext='fits.fz'):
    """
    get the path to a image file
    """
    dir=get_output_dir(run, index)
    basename = get_generic_basename(
        run,
        index=index,
        type='seg',
        ext=ext,
    )

    return os.path.join(dir, basename)

def get_sxcat_file(run, index):
    """
    get the path to a image file
    """
    dir=get_output_dir(run, index)
    basename = get_generic_basename(
        run,
        index=index,
        type='sxcat',
        ext='fits',
    )

    return os.path.join(dir, basename)

def get_meds_file(run, index, ext='fits.fz'):
    """
    get the path to a image file
    """
    dir=get_output_dir(run, index)
    basename = get_generic_basename(
        run,
        index=index,
        type='meds',
        ext=ext,
    )

    return os.path.join(dir, basename)



def get_psfex_file(run, index):
    """
    get the path to a image file
    """
    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, type='psfcat', ext='psf')

    return os.path.join(dir, basename)


def get_truth_file(run, index):
    """
    get the path to a stars file
    """
    dir=get_output_dir(run, index)
    basename = get_generic_basename(
        run,
        index=index,
        type='truth',
        ext='fits',
    )

    return os.path.join(dir, basename)

def get_galsim_log_file(run, index):
    """
    location of the log file
    """

    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, type='galsim', ext='log')

    return os.path.join(dir, basename)

def get_reduce_log_file(run, index):
    """
    location of the log file
    """

    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, type='reduce', ext='log')

    return os.path.join(dir, basename)

def get_meds_log_file(run, index):
    """
    location of the log file
    """

    dir=get_output_dir(run, index)
    basename = get_generic_basename(run, index=index, type='meds', ext='log')

    return os.path.join(dir, basename)


#
# configuration files
#

def get_config_dir():
    """
    get the value of the BASE_CONFIG_DIR environement variable
    """
    if CONFIG_DIR_KEY not in os.environ:
        raise ValueError("$%s environment variable is not set" % CONFIG_DIR_KEY)

    return os.environ[CONFIG_DIR_KEY]

def get_config_file(run):
    """
    the path to the config file
    """

    cdir=get_config_dir()
    basename = get_generic_basename(run, ext='yaml')
    return os.path.join(cdir, basename)


def read_config(run):
    """
    read the yaml config file
    """
    fname = get_config_file(run)
    return read_yaml(fname)

def read_yaml(fname):
    """
    wrapper to read yaml files
    """
    import yaml
    print("reading:",fname)
    with open(fname) as fobj:
        data=yaml.load( fobj )

    return data




#
# sx, psfex, findstars
#

# executables
def get_sx_exe():
    return os.environ['SX_EXE']
    #return '/astro/u/rarmst/soft/bin/sex'

def get_psfex_exe():
    return os.environ['PSFEX_EXE']
    #return '/astro/u/rarmst/soft/bin/psfex'

def get_findstars_exe():
    return 'findstars'

def get_piff_exe():
    return '/astro/u/mjarvis/bin/piffify'

def get_share_dir():
    d=sys.exec_prefix
    return os.path.join(d,'share','nbrsim-config')

# config files
def get_sx_config():
    d=get_share_dir()
    return os.path.join(d, 'sx.conf')

def get_sx_params():
    d=get_share_dir()
    return os.path.join(d, 'sx.param')

def get_sx_filter():
    d=get_share_dir()
    return os.path.join(d, 'sx.conv')

def get_sx_nnw():
    d=get_share_dir()
    return os.path.join(d, 'sx.nnw')



def get_psfex_config():
    d=get_share_dir()
    return os.path.join(d, 'psfex.conf')

def get_wl_config():
    d=get_share_dir()
    return os.path.join(d, 'wl.config')

def get_findstars_config():
    d=get_share_dir()
    return os.path.join(d, 'findstars.config')

def get_piff_config():
    d=get_share_dir()
    return os.path.join(d, 'piff.yaml')


def get_meds_config():
    d=get_share_dir()
    return os.path.join(d, 'meds.yaml')
