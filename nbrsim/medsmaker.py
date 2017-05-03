import numpy
import esutil as eu
import desmeds
import yaml
from . import files


class NbrSimMEDSMaker(desmeds.DESMEDSMakerDESDM):
    def __init__(self, run, index):
        """
        load the config, catalog, and image info
        """

        self._load_config()
        self._set_extra_config(run, index)
        self._load_file_config()
        self._load_catalog()
        self._load_image_info()
        self._load_meta_data()

    def _build_meta_data(self):
        """
        create the mdata data structure and copy in some information
        """
        print('building meta data')
        cfg = {}
        cfg.update(self)
        cfg = yaml.dump(cfg)
        dt = self._get_meta_data_dtype(cfg)
        meta_data = zeros(1,dtype=dt)
        meta_data['medsconf'] = self['medsconf']
        meta_data['config'] = cfg
        self.meta_data = meta_data


    def _get_scale(self, *args, **kw):
        return 1.0

    def _get_coadd_objects_ids(self):
        """
        fake this for the sim
        """
        # do queries to get coadd object ids        
        qwry = """
        select
            coadd_objects_id,
            object_number
        from
            coadd_objects
        where
            COADD_OBJECTS.imageid_{band} = {id}
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

        self.coadd_cat = cat


    def _set_extra_config(self, run, index):
        """
        set extra configuration parameters that are not user-controlled
        """

        self['run'] = run
        self['index'] = index

        self['extra_obj_data_fields'] = [
            ('number','i8'),
            ('input_row','f8'),
            ('input_col','f8'),
        ]

    def _load_config(self):
        fname = files.get_meds_config()
        super(NbrSimMEDSMaker,self)._load_config(fname)


    def _load_srclist(self):
        """
        there are currently no single epoch images
        """
        return []

    def _load_file_config(self):
        """
        band: band in string form
        coadd_image_url: string
        coadd_seg_url: string
        coadd_magzp: float
        ngwint_flist: string
            path to the ngwint file list
        seg_flist: string
            path to the seg file list
        bkg_flist: string
            path to the bkg file list
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

    def _write_meds_file(self):
        """
        write the data using the MEDSMaker
        """
        from desmeds.files import StagedOutFile

        maker=meds.MEDSMaker(
            self.obj_data,
            self.image_info,
            config=self,
            meta_data=self.meta_data,
        )

        fname=self.file_dict['meds_url']

        print("writing MEDS file:",fname)

        tmpdir = desmeds.files.get_temp_dir()

        with StagedOutFile(fname,tmpdir=tmpdir) as sf:
            maker.write(sf.path)
