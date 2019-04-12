class Place:

    def __init__(self, input_trans, output_trans):
        self._input_trans = input_trans
        self._output_trans = output_trans

    @property
    def input_trans(self):
        return self._input_trans
    
    @property
    def output_trans(self):
        return self._output_trans
    
    def __eq__(self, other):
        return (self.input_trans, self.output_trans) == (other.input_trans, other.output_trans)
    
    def __hash__(self):
        return hash((self.input_trans, self.output_trans))
    
    @property
    def name(self):
        return '({input_trans} | {output_trans})'.format(
            input_trans=set(self.input_trans),
            output_trans=set(self.output_trans)
        )
