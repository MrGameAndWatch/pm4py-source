class ActivityOrder:

    def __init__(self, smaller, larger):
        self.__smaller = smaller
        self.__larger  = larger
    
    def is_smaller(self, a1, a2):
        return a1 in self.__smaller[a2]
    
    def is_larger(self, a1, a2):
        return a1 in self.__larger[a2]

class ActivityOrderBuilder:

    def __init__(self, activities):
        self.__activities = activities
        self.__smaller = dict()
        self.__larger = dict()
    
    @property
    def activities(self):
        return self.__activities
    
    def smaller_than(self, a1, a2):
        """
        Stores that activity a1 is smaller than
        activity a2.

        Parameters:
        -----------
        a1 - the first activity
        a2 - the second activity

        Result:
        -----------
        a1 < a2 is stored
        """
        assert(a1 in self.activities)
        assert(a2 in self.activities)

        if (a2 not in self.__smaller):
            self.__smaller[a2] = set()
        self.__smaller[a2].append(a1)
        if (a1 not in self.__larger):
            self.__larger[a1] = a2
    
    def get_ordering(self):
        self.assert_consistent_ordering()
        return ActivityOrder(self.__smaller, self.__larger)
    
    def assert_consistent_ordering(self):
        """
        Asserts that the order is consistent.
        """
        for a in self.activities:
            for b in self.__smaller[a]:
                assert(a in self.__larger[b])
                assert(a not in self.__smaller[b])
                assert(b not in self.__larger[a])
