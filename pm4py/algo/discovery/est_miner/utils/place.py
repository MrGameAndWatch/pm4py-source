class Place:

    def __init__(self, input_trans, output_trans):
        self.__input_trans = input_trans
        self.__output_trans = output_trans
    
    def __eq__(self, other):
        return (self.input_trans, self.output_trans) == (other.input_trans, other.output_trans)
    
    def __hash__(self):
        return hash((self.input_trans, self.output_trans))
    
    @property
    def input_trans(self):
        return self.__input_trans
    
    @property
    def output_trans(self):
        return self.__output_trans
    
    @property
    def name(self):
        return str(self.input_trans) + ', ' + str(self.output_trans)
