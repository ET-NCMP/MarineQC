import unittest
import BackgroundField as bf


class TestBuildCompletions(unittest.TestCase):

    def test_simple(self):

        base = 'a'
        subs = ['b', 'c']

        completions = bf.build_completions(base, subs)

        self.assertEqual(completions[0], 'a/b')
        self.assertEqual(completions[1], 'a/b/c')

    def test_even_simpler(self):

        base = 'a'
        subs = ['b']

        completions = bf.build_completions(base, subs)

        self.assertEqual(completions[0], 'a/b')

    def test_too_many_slashes(self):

        base = 'a/'
        subs = ['b']

        completions = bf.build_completions(base, subs)

        self.assertEqual(completions[0], 'a/b')


class TestProcessString(unittest.TestCase):

    def test_simple(self):

        teststring = 'OnceUponAYYYYMMMMDDDD'
        correctstring = 'OnceUponA20190331'

        outstring = bf.process_string(teststring, 2019, 3, 31)

        self.assertEqual(outstring, correctstring)


class TestMakeFilename(unittest.TestCase):

    def test_basic(self):

        dirstub = '/project/data/coriolis/YYYY/MMMM/DDDD/'
        filenamestub = 'AwesomeData_YYYYMMMMDDDD.nc'

        year = 2002
        month = 2
        day = 17

        outstring = bf.make_filename(dirstub, filenamestub, year, month, day)

        correctstring = '/project/data/coriolis/2002/02/17/AwesomeData_20020217.nc'

        self.assertEqual(outstring, correctstring)

    def test_non_terminating_slash(self):

        dirstub = '/project/data/coriolis/YYYY/MMMM/DDDD'
        filenamestub = 'AwesomeData_YYYYMMMMDDDD.nc'

        year = 2002
        month = 2
        day = 17

        outstring = bf.make_filename(dirstub, filenamestub, year, month, day)

        correctstring = '/project/data/coriolis/2002/02/17/AwesomeData_20020217.nc'

        self.assertEqual(outstring, correctstring)


class TestGetBackgroundFilename(unittest.TestCase):

    def test_simple_cci(self):

        dirstubs = ['/project/earthobs/SST/ESACCI_SST/CDR2.1_release/Analysis/L4/YYYY/MMMM/DDDD/']
        filenamestubs = ['YYYYMMMMDDDD120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_CDR2.1-v02.0-fv01.0.nc']

        outfile = bf.get_background_filename(dirstubs, filenamestubs, 2002, 11, 30)

        correctfile = '/project/earthobs/SST/ESACCI_SST/CDR2.1_release/Analysis/L4/2002/11/30/' +\
                      '20021130120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_CDR2.1-v02.0-fv01.0.nc'

        self.assertEqual(outfile, correctfile)

    def test_missing_cci(self):

        dirstubs = ['/project/earthobs/SST/ESACCI_SST/CDR2.1_release/Analysis/L4/YYYY/MMMM/DDDD/']
        filenamestubs = ['YYYYMMMMDDDD120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_CDR2.1-v02.0-fv01.0.nc']

        outfile = bf.get_background_filename(dirstubs, filenamestubs, 1922, 11, 30)

        self.assertIsNone(outfile)

    def test_pre_2007_ostia(self):

        dirstubs = ['/project/ofrd/ostia/reanalysis/v1.0/YYYY/MMMM/',
                    '/project/ofrd/ostia/data/netcdf/YYYY/MMMM/']
        filenamestubs = ['YYYYMMMMDDDD-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIARAN.nc',
                         'YYYYMMMMDDDD-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc']

        outfile = bf.get_background_filename(dirstubs, filenamestubs, 2002, 11, 30)

        correctfile = '/scratch/hadjj/20021130-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIARAN.nc'

        self.assertEqual(outfile, correctfile)

    def test_post_2007_ostia(self):

        dirstubs = ['/project/ofrd/ostia/reanalysis/v1.0/YYYY/MMMM/',
                    '/project/ofrd/ostia/data/netcdf/YYYY/MMMM/']
        filenamestubs = ['YYYYMMMMDDDD-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIARAN.nc',
                         'YYYYMMMMDDDD-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc']

        outfile = bf.get_background_filename(dirstubs, filenamestubs, 2010, 8, 3)

        correctfile = '/scratch/hadjj/20100803-UKMO-L4HRfnd-GLOB-v01-fv02-OSTIA.nc'

        self.assertEqual(outfile, correctfile)


if __name__ == '__main__':
    unittest.main()
