import unittest
import numpy as np
import YMCounter as ym

class Test_chunks(unittest.TestCase):

    def test_simples(self):

        g = ym.YMCounter(1985,1,1985,12)
        g.counter = np.array([1,0,1,0,1,0,1,0,1,0,1,0])

        s, e = g.get_chunks(3)

        self.assertEqual(s[0],0)
        self.assertEqual(e[0],10)
        self.assertEqual(len(s), 1)
        self.assertEqual(len(e), 1)


    def test_simples2(self):

        g = ym.YMCounter(1985,1,1985,12)
        g.counter = np.array([0,1,0,1,0,1,0,1,0,1,0,1])

        s, e = g.get_chunks(3)

        self.assertEqual(s[0],1)
        self.assertEqual(e[0],11)
        self.assertEqual(len(s), 1)
        self.assertEqual(len(e), 1)

    def test_all_present(self):
        g = ym.YMCounter(1985,1,1985,12)
        g.counter = np.array([1,1,1,1,1,1,1,1,1,1,1,1])

        s, e = g.get_chunks(3)

        self.assertEqual(s[0],0)
        self.assertEqual(e[0],11)
        self.assertEqual(len(s), 1)
        self.assertEqual(len(e), 1)

    def test_none(self):

        g = ym.YMCounter(1985,1,1985,12)
        g.counter = np.array([0,0,0,0,0,0,0,0,0,0,0,0])

        s, e = g.get_chunks(3)

        self.assertEqual(len(s), 0)
        self.assertEqual(len(e), 0)

    def test_onegap(self):

        g = ym.YMCounter(1985,1,1985,12)
        g.counter = np.array([1,1,1,0,0,0,1,1,1,1,1,1])

        s, e = g.get_chunks(3)

        self.assertEqual(s[0], 0)
        self.assertEqual(e[0], 2)
        self.assertEqual(s[1], 6)
        self.assertEqual(e[1], 11)

class Test_yield(unittest.TestCase):

    def test_endcase(self):

        g = ym.YMCounter(1985, 1, 1985, 12)
        g.counter = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])

        for yy1, mm1, yy2, mm2, cl in g.yield_start_and_end_dates(3):
            pass

        self.assertEqual(yy1, 1985)
        self.assertEqual(yy2, 1985)
        self.assertEqual(mm1, 12)
        self.assertEqual(mm2, 12)
        self.assertEqual(cl[0], 'end_edge_case')

    def test_endcase(self):

        g = ym.YMCounter(1985, 1, 1985, 12)
        g.counter = np.array([1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0])

        for yy1, mm1, yy2, mm2, cl in g.yield_start_and_end_dates(3):
            pass

        self.assertEqual(yy1, 1985)
        self.assertEqual(yy2, 1985)
        self.assertEqual(mm1, 1)
        self.assertEqual(mm2, 6)
        self.assertEqual(cl[0], 'start_edge_case')

    def test_regular(self):

        g = ym.YMCounter(1985, 1, 1985, 12)
        g.counter = np.array([0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0])

        for yy1, mm1, yy2, mm2, cl in g.yield_start_and_end_dates(3):
            pass

        self.assertEqual(yy1, 1985)
        self.assertEqual(yy2, 1985)
        self.assertEqual(mm1, 4)
        self.assertEqual(mm2, 7)
        self.assertEqual(cl[0], 'regular')

    def test_new(self):

        g = ym.YMCounter(1985, 1, 1985, 12)
        g.counter = np.array([0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0])

        for yy1, mm1, yy2, mm2, cl in g.yield_start_and_end_dates(3):
            pass

        self.assertEqual(yy1, 1985)
        self.assertEqual(yy2, 1985)
        self.assertEqual(mm1, 4)
        self.assertEqual(mm2, 9)
        self.assertIn('regular', cl)
        self.assertIn('new', cl)


if __name__ == '__main__':
    unittest.main()
