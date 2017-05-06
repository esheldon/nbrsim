from __future__ import print_function
import numpy
import yaml

import esutil as eu
import meds
import desmeds
import fitsio

from . import files


class NbrSimMEDSMaker(desmeds.DESMEDSMakerDESDM):
    def __init__(self, run, index):
        """
        load the config, catalog, and image info
        """

        self['run'] = run
        self['index'] = index

        self._load_config()
        self._set_extra_config()
        self._load_file_config()
        self._load_cat()
        self._set_psfs()

    def _build_meta_data(self):
        """
        create the mdata data structure and copy in some information
        """
        print('building meta data')
        cfg = {}
        cfg.update(self)
        cfg = yaml.dump(cfg)
        dt = self._get_meta_data_dtype(cfg)
        meta_data = numpy.zeros(1,dtype=dt)
        meta_data['medsconf'] = self['medsconf']
        meta_data['config'] = cfg
        self.meta_data = meta_data


    def _get_scale(self, *args, **kw):
        return 1.0

    def _get_coadd_objects_ids(self):
        """
        fake this for the sim
        """

        dt=[
            ('coadd_objects_id','i8'),
            ('object_number','i4'),
        ]
        res=numpy.zeros(self.coadd_cat.size, dtype=dt)

        res['object_number'] = 1+numpy.arange(res.size)
        res['coadd_objects_id'] = res['object_number']

        return res

    def _read_coadd_cat(self):
        """
        we already read the catalog
        """
        self.coadd_cat = self.sxcat

    def _load_cat(self):
        """
        read the "coadd" catalog, sorting by the number field (which
        should already be the case)
        """

        fname = files.get_sxcat_file(self['run'],self['index'])

        print('reading coadd cat:',fname)
        cat = fitsio.read(
            fname,
            ext=self['sxcat_ext'],
            lower=True,
        )

        add_dt=[
            ('ra','f8'),
            ('dec','f8'),
        ]
        cat = eu.numpy_util.add_fields(cat, add_dt)
        cat['ra'] = cat[self['ra_name']]
        cat['dec'] = cat[self['dec_name']]

        self.sxcat = cat


    def _set_extra_config(self):
        """
        set extra configuration parameters that are not user-controlled
        """


        self['extra_obj_data_fields'] = [
            ('number','i8'),
            ('input_row','f8'),
            ('input_col','f8'),
        ]

    def _load_config(self):
        """
        load the config and the galsim config
        """

        fname = files.get_meds_config()
        super(NbrSimMEDSMaker,self)._load_config(fname)

        # also pull in the galsim config to get the psf
        self.galsim_conf = files.read_config(self['run'])

    def _set_psfs(self):
        """
        set the list of psfs as galsim objects
        """
        import galsim
        pconf = self.galsim_conf['psf']
        wcsconf = self.galsim_conf['image']['wcs']

        type=pconf['type']
        if type == 'Moffat':
            psf = galsim.Moffat(
                beta=pconf['beta'],
                fwhm=pconf['fwhm'],
            )
        elif type == 'Gaussian':
            psf = galsim.Moffat(
                fwhm=pconf['fwhm'],
            )
        else:
            raise ValueError("bad psf type: '%s'" % type)

        if 'ellip' in pconf:
            psf = psf.shear(
                g1=pconf['ellip']['g1'],
                g2=pconf['ellip']['g2'],
            )

        print("psf:",psf)

        wcs = galsim.JacobianWCS(
            dudx = wcsconf['dudx'],
            dudy = wcsconf['dudy'],
            dvdx = wcsconf['dvdx'],
            dvdy = wcsconf['dvdy'],
        )
        self.psf_data = [PSFMaker(psf, wcs)]

        
    def _load_srclist(self):
        """
        there are currently no single epoch images
        """
        return []

    def _load_file_config(self):
        """
        fake up the file config
        """

        fd={}
        fd['coadd_image_url'] = files.get_image_file(
            self['run'],
            self['index'],
        )
        fd['coadd_seg_url'] = files.get_seg_file(
            self['run'],
            self['index'],
        )
        fd['coadd_cat_url'] = files.get_sxcat_file(
            self['run'],
            self['index'],
        )
        # we need this here, but it is not used.  Scale
        # will always be 1
        fd['coadd_magzp'] = 32.2


        fd['meds_url'] = files.get_meds_file(
            self['run'],
            self['index'],
        )

        self.file_dict=fd

    def _write_meds_file(self):
        """
        write the data using the MEDSMaker
        """
        from desmeds.files import StagedOutFile

        maker=meds.MEDSMaker(
            self.obj_data,
            self.image_info,
            config=self,
            psf_data=self.psf_data,
            meta_data=self.meta_data,
        )

        fname=self.file_dict['meds_url']

        print("writing MEDS file:",fname)

        tmpdir = desmeds.files.get_temp_dir()

        #maker.write(fname)
        with StagedOutFile(fname,tmpdir=tmpdir) as sf:
            maker.write(sf.path)

class PSFMaker(object):
    def __init__(self, psfobj, wcs):
        self.psfobj = psfobj
        self.wcs = wcs

        # assume constant for now
        self.psfim = psfobj.drawImage(
            wcs = wcs,
        ).array

        self.moms = moments(self.psfim)

        self.sigma = numpy.sqrt(self.moms['T']/2.0)

    def get_cen(self, *args, **kw):
        return self.moms['cen'].copy()

    def get_sigma(self, *args, **kw):
        return self.sigma

    def get_shape(self, *args, **kw):
        return self.psfim.shape

    def get_rec(self, *args, **kw):
        return self.psfim.copy()

def moments(image):
    """
    Measure the unweighted centroid and second moments of an image.
    """

    # ogrid is so useful
    row,col=numpy.ogrid[0:image.shape[0], 0:image.shape[1]]

    Isum = image.sum()

    rowcen = (image*row).sum()/Isum
    colcen = (image*col).sum()/Isum
    cen = numpy.array( [rowcen,colcen] )

    rm = row - cen[0]
    cm = col - cen[1]

    Irr = (image*rm**2).sum()/Isum
    Irc = (image*rm*cm).sum()/Isum
    Icc = (image*cm**2).sum()/Isum

    T=Irr+Icc
    e1=(Icc-Irr)/T
    e2=2.*Irc/T

    return {
        'cen':cen,
        'T':Irr + Icc,
        'e1':e1,
        'e2':e2,
    }

