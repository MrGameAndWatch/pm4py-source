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
