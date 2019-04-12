class ActivityOrderBuilder:

    def __init__(self, activities):
        self._is_larger_relations = {a:list() for a in activities}
    
    def add_relation(self, larger=None, smaller=None):
        self._is_larger_relations[smaller].append(larger)
    
    def get_ordering(self):
        return ActivityOrder(self._is_larger_relations)

class ActivityOrder:

    def __init__(self, relations):
        self._is_larger_relations = relations
    
    @property
    def is_larger_relations(self):
        return self._is_larger_relations

def max_element(activities, order):
    a_max = None
    for a in activities:
        if a_max == None:
            a_max = a
        elif a in set(order.is_larger_relations[a_max]):
            a_max = a
    return a_max
