class Place: # make compareable based on configurable orders

    def __init__(self, input_trans, output_trans):
        self.__input_trans = input_trans
        self.__output_trans = output_trans
    
    @property
    def input_trans(self):
        return self.__input_trans
    
    @property
    def output_trans(self):
        return self.__output_trans
