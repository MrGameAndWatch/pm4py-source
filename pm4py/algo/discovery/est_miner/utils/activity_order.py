class LargerActivityStack:

    def __init__(self):
        self.__larger_activities = list()
    
    def push(self, activity):
        self.__larger_activities.append(activity)
    
    def pop(self):
        return self.__larger_activities.pop()
    
    def peek(self):
        return self.__larger_activities[self.size - 1]
    
    def size(self):
        return len(self.__larger_activities)
    
    def to_set(self):
        return set(self.__larger_activities)

class ActivityOrderBuilder:

    def __init__(self):
        self.__is_larger_relations = dict()
    
    def add_relation(self, larger=None, smaller=None):
        if smaller not in self.__is_larger_relations:
            self.__is_larger_relations[smaller] = LargerActivityStack()
        self.__is_larger_relations[smaller].push(larger)
    
    def get_ordering(self):
        return ActivityOrder(self.__is_larger_relations)

class ActivityOrder:

    def __init__(self, relations):
        self.__is_larger_relations = relations
    
    @property
    def is_larger_relations(self):
        return self.__is_larger_relations
