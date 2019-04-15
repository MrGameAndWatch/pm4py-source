import abc
from collections import defaultdict

from gurobipy import *

from pm4py.algo.discovery.est_miner.utils.place import Place
from pm4py.algo.discovery.est_miner.utils import constants as const

class PostProcessingStrategy(abc.ABC):

    @abc.abstractmethod
    def execute(self, candidate_places, transitions, logger=None):
        """
        Remove redundant places from the found candidate places
        to make the resulting network better interpretable by 
        human readers.
        """
        pass

class NoPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places, transitions):
        print('Executed Post Processing')
        return candidate_places

class RemoveRedundantPlacesLPPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places, transitions, logger=None):
        """
        Removes redundant places [1].

        Parameters:
        -----------
        candidate_places: Set of fitting places, discovered in the search phase
        transitions: Set of transitions occurring in the log
        logger: Possible logger instance

        Returns:
        -----------
        A set of places that do not contain any redundant places.
        But still have implicit places.

        References
        -----------
        Wil M. P. van der Aalst, "Discovering the "Glue" Connecting Activities
        - Exploiting Monotonicity to Learn Places Faster"
        """
        if (logger is not None):
            logger.info('Starting Post Processing')
        pre  = {}
        post = {}
        for p in candidate_places:
            for t in transitions:
                if t in p.input_trans:
                    pre[p, t] = 1
                else:
                    pre[p, t] = 0
                
                if t in p.output_trans:
                    post[p, t] = 1
                else:
                    post[p, t] = 0

        pruned_set = set(candidate_places)
        for p_test in candidate_places:
            if self.is_redundant(p_test, transitions, pre, post, pruned_set):
                if (logger is not None):
                    logger.info('Removing ' + p_test.name)
                pruned_set.discard(p_test)
        return pruned_set
    
    def is_redundant(self, p_test, transitions, pre, post, pruned_set):
        redundant = False
        model = Model('Test Place')
        y = {}

        for p in pruned_set.difference({p_test}):
            y[p] = model.addVar(
                vtype=GRB.BINARY, 
                name='y_({name})'.format(name=p.name)
            )
        model.update()
        model.setObjective(
            quicksum(y[p] for p in pruned_set.difference({p_test})),
            GRB.MINIMIZE
        )

        # Constraints
        for t in transitions:
            model.addConstr(quicksum(y[p] * pre[p, t] for p in pruned_set.difference({p_test})) == pre[p_test, t])
            model.addConstr(quicksum(y[p] * post[p, t] for p in pruned_set.difference({p_test})) == post[p_test, t])
            model.addConstr(quicksum(y[p] * pre[p, t] for p in pruned_set.difference({p_test})) <= 1)
            model.addConstr(quicksum(y[p] * post[p, t] for p in pruned_set.difference({p_test})) <= 1)
            
        model.optimize()
        if model.status == GRB.OPTIMAL:
            redundant = True
        
        return redundant

class DeleteDuplicatePlacesPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places, transitions):
        return set(candidate_places)
