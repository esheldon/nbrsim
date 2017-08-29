# nbrsim
sim to test deblending and shear

Framework to run simulations for testing the effect of neighbors on deblending
and shear. Most people will use this library to access the files.

Any galsim config files with the proper naming scheme can be used, but we are
co-developing a set of scripts in the https://github.com/esheldon/nbrsim-config
repository

Examples accessing output files.
--------------------------------

```python
# make sure the NBRSIM_DIR environment variable is set to the base directory
# e.g. at BNL we use
# NBRSIM_DIR=/gpfs/mnt/gpfs01/astro/workarea/esheldon/lensing/des-lensing/nbrsim

import nbrsim
from nbrsim import files

# location of a star field image
run='v006'
index=8842
files.get_stars_file(run, index)
'/gpfs/mnt/gpfs01/astro/workarea/esheldon/lensing/des-lensing/nbrsim/v006/output/nbrsim-v006-008842.fits'

# location of the truth catalog for the star field
files.get_stars_truth_file(run, index)
'/gpfs/mnt/gpfs01/astro/workarea/esheldon/lensing/des-lensing/nbrsim/v006/output/nbrsim-truth-v006-008842.fits'
```

Examples running the sims
---------------------------

```bash
# write scripts for a run named v001
# - the config file must live in $NBRSIM_CONFIG_DIR/nbrsim-stars-${run}.yaml
# - currently we write stars only images
# - use the wq batch system to run jobs

run=v001
system=wq
nbrsim-make-scripts --system=$system $run

# You can also have some additional commands run.  For
# example, this sets up an anaconda environment

nbrsim-make-scripts $run $system --extra-commands="source activate nbrsim"

# the above write scripts into $NBRSIM_DIR/$run/scripts

cd $NBRSIM_DIR/v001/scripts

# run a script
bash nbrsim-stars-v001-0019.sh

# submit to the queue
wq sub -b nbrsim-stars-v001-0019.yaml

# outputs are in $NBRSIM_DIR/$run/output

# the output file
ls $NBRSIM_DIR/v001/output/nbrsim-stars-v001-0017.fits

# the log file
ls $NBRSIM_DIR/v001/output/nbrsim-stars-v001-0017.log
```

Setup
-----

To find file paths, you need the NBRSIM_DIR environment variable set

To run the sims, you also need the NBRSIM_CONFIG_DIR environment variable set

Dependencies for running sims
-----------------------------

- galsim and all its dependencies
- galsim_extra https://github.com/esheldon/galsim_extra

Optional Dependencies
---------------------

- nbrsim_config - this repo holds our official configuration files
