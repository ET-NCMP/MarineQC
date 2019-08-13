import numpy as np
import qc


class YMCounter:

    def __init__(self, y1, m1, y2, m2):

        self.n = 12*(y2-y1) + m2 - m1 + 1

        self.years = np.zeros(self.n)
        self.months = np.zeros(self.n)
        self.counter = np.zeros(self.n)

        ct = 0
        for year, month in qc.year_month_gen(y1, m1, y2, m2):
            self.years[ct] = year
            self.months[ct] = month
            ct += 1

    def setym(self, y, m, flag):
        self.counter[(self.years == y) & (self.months == m)] = flag

    def get_chunks(self, gap):

        starts = []
        ends = []
        zeros = 10
        lastdata = -1

        for i in range(0, self.n):

            if self.counter[i] == 0:
                zeros += 1

            if self.counter[i] == 1 and zeros >= gap:
                starts.append(i)
                zeros = 0
                if lastdata != -1:
                    ends.append(lastdata)
                    lastdata = -1

            if self.counter[i] == 1 and zeros < gap:
                lastdata = i
                zeros = 0

        if len(ends) < len(starts):
            ends.append(lastdata)

        return starts, ends

    def index(self, y, m):
        """
        Get the index of year and month in the array

        :param y: year of index
        :param m: month of index
        :return: index in array
        """

        indices = np.arange(0, self.n)
        outindex = indices[(self.years == y) & (self.months == m)]
        return outindex

    def yield_start_and_end_dates(self, gap):
        """
        Provide an iterable thingy to provide start and end dates for chunks of data separated by "gap" months with
        no observations
        :param gap: number of months by which chunks of data must be separated.
        :return: year and month of start of chunk, year and month of end of chunk and classification of that chunk
        """
        starts, ends = self.get_chunks(gap)

        for i, val in enumerate(starts):

            y1 = int(self.years[val])
            m1 = int(self.months[val])

            y2 = int(self.years[ends[i]])
            m2 = int(self.months[ends[i]])

            classification = []

            if self.index(y1, m1) < gap:
                classification.append('start_edge_case')
            if self.index(y2, m2) > self.n - gap - 1:
                classification.append('end_edge_case')
            if self.index(y2, m2) == self.n - gap - 1:
                classification.append('new')

            if not('start_edge_case' in classification or 'end_edge_case' in classification):
                classification.append('regular')

            yield y1, m1, y2, m2, classification
