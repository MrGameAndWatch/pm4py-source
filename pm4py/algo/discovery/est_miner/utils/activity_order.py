class ActivityOrderBuilder:

    def __init__(self, activities):
        self.__is_larger_relations = {a:list() for a in activities}
    
    def add_relation(self, larger=None, smaller=None):
        self.__is_larger_relations[smaller].append(larger)
    
    def get_ordering(self):
        return ActivityOrder(self.__is_larger_relations)

class ActivityOrder:

    def __init__(self, relations):
        self.__is_larger_relations = relations
    
    @property
    def is_larger_relations(self):
        return self.__is_larger_relations
