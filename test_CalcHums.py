import unittest
import numpy as np
import CalcHums as ch


class Test_humidity_functions(unittest.TestCase):
   
    def test_vap_from_example(self):
        '''
        This is from Kate's example in the file
        '''
        self.assertEqual(ch.vap(10., 15., 1013), 12.3)

    def test_vap_from_sh(self):
        '''
        This is from Kate's example in the file
        '''
        self.assertEqual(ch.vap_from_sh(7.6,1013.), 12.3)

    def test_sh(self):
        '''
        This is from Kate's example in the file
        '''
        self.assertEqual(ch.sh(10.,15.,1013.), 7.6)

    def test_sh_from_vap(self):
        '''
        This is from Kate's example in the file
        '''
        #self.assertEqual(ch.sh_from_vap(10.,15.,1013.), 7.6)

    def test_rh(self):
        '''
        This is from Kate's example in the file
        '''
        self.assertEqual(ch.rh(10.,15.,1013.), 72.0)

    def test_wb(self):
        '''
        This is from Kate's example in the file
        '''       
        self.assertEqual(ch.wb(10.,15.,1013), 12.2)

    def test_dpd(self):
        '''
        This is from Kate's example in the file
        '''       
        self.assertEqual(ch.dpd(10.,15.), 5.0)

    def test_td_from_vap(self):
        '''
        They're all from Kate's examples in the file
        '''       
        self.assertEqual(ch.td_from_vap(12.3,1013.,15.), 10.0)
        
        
        

if __name__ == '__main__':
    unittest.main()
