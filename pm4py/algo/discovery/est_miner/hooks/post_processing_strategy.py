import abc
from collections import defaultdict

from gurobipy import *

from progress.bar import ShadyBar

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
                    logger.info('Removing redundant place ' + p_test.name)
                pruned_set.discard(p_test)
        return pruned_set
    
    def is_redundant(self, p_test, transitions, pre, post, pruned_set):
        redundant = False
        model = Model('Redundant Place Test')
        y = {}

        for p in pruned_set.difference({p_test}):
            y[p] = model.addVar(
                vtype=GRB.BINARY
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

class RemoveImplicitPlacesLPPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places, transitions, logger=None):
        """
        Removes implicit places as in [1].

        Parameters:
        -----------
        candidate_places: Set of fitting places, discovered in the search phase
        transitions: Set of transitions occurring in the log
        logger: Possible logger instance

        Returns:
        -----------
        A set of places that do not contain any implicit places.

        References
        -----------
        J.M. Colom and M. Silva, "Improving the Linearly Based Characterization
        of P/T Nets"
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
        bar = ShadyBar('Removing Structural Implicit Places', max=len(candidate_places))
        for p_test in candidate_places:
            if self.is_implicit(p_test, transitions, pre, post, pruned_set):
                if (logger is not None):
                    logger.info('Removing implicit place ' + p_test.name)
                pruned_set.discard(p_test)
            bar.next()
        bar.finish()
        
        return pruned_set
        
    def is_implicit(self, p_test, transitions, pre, post, pruned_set):
        implicit = False
        model = Model('Implicit Place Test')
        model.setParam('OutputFlag', 0)
        y = {}

        for p in pruned_set.difference({p_test}):
            y[p] = model.addVar(
                vtype=GRB.BINARY
            )

        mu = model.addVar(
            vtype=GRB.INTEGER
        )

        model.update()
        model.setObjective(
            mu,
            GRB.MINIMIZE
        )

        # Constraints
        for t in transitions:
            model.addConstr(quicksum(y[p] * (post[p, t] - pre[p, t]) for p in pruned_set.difference({p_test})) <= post[p_test, t] - pre[p_test, t])
        
        for t in p_test.output_trans:
            model.addConstr(quicksum(y[p] * pre[p, t] + mu for p in pruned_set.difference({p_test})) >= pre[p_test, t])

        model.optimize()
        if model.status == GRB.OPTIMAL:
            if model.objVal <= 0:
                implicit = True
            
        return implicit

class RemoveConcurrentImplicitPlacesPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places, transitions, logger=None):
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
        bar = ShadyBar('Removing Concurrent Implicit Places', max=len(candidate_places))
        for p_test in candidate_places:
            if self.is_concurrent_implicit(p_test, transitions, pre, post, pruned_set):
                if (logger is not None):
                    logger.info('Removing implicit place ' + p_test.name)
                pruned_set.discard(p_test)
            bar.next()
        bar.finish()
        
        return pruned_set
    
    def is_concurrent_implicit(self, p_test, transitions, pre, post, pruned_set):
        concurrent_implicit = False
        model = Model('Concurrent Implicit Place Test')
        model.setParam('OutputFlag', 0)
        y = {}
        z = {}

        for p in pruned_set.difference({p_test}):
            y[p] = model.addVar(
                vtype=GRB.BINARY
            )

            z[p] = model.addVar(
                vtype=GRB.BINARY
            )

        mu = model.addVar(
            vtype=GRB.INTEGER
        )

        model.update()
        model.setObjective(
            mu,
            GRB.MAXIMIZE
        )

        # Constraints
        for t in transitions:
            model.addConstr(quicksum(y[p] * (post[p, t] - pre[p, t]) for p in pruned_set.difference({p_test})) <= post[p_test, t] - pre[p_test, t])
        
        for t in p_test.output_trans:
            model.addConstr(quicksum(z[p] * pre[p, t] + mu for p in pruned_set.difference({p_test})) >= pre[p_test, t])
        
        model.addConstr(mu <= 0)

        model.optimize()
        if model.status == GRB.OPTIMAL:
            if model.objVal <= 0:
                concurrent_implicit = True
            
        return concurrent_implicit 

class RemoveConcurrentAndStructuralImplicitPlacesPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places, transitions, logger=None):
        structural_impl_places_remover = RemoveImplicitPlacesLPPostProcessingStrategy()
        concurrent_impl_places_remover = RemoveConcurrentImplicitPlacesPostProcessingStrategy()

        without_structural_impl_places = structural_impl_places_remover.execute(
            candidate_places,
            transitions,
            logger=logger
        )

        without_concurrent_impl_places = concurrent_impl_places_remover.execute(
            without_structural_impl_places,
            transitions,
            logger=logger
        )
        return without_concurrent_impl_places

class RemoveRedundantAndImplicitPlacesPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places, transitions, logger=None):
        redundant_places_remover = RemoveRedundantPlacesLPPostProcessingStrategy()
        implicit_places_remover = RemoveImplicitPlacesLPPostProcessingStrategy()

        without_redundant_places = redundant_places_remover.execute(
            candidate_places,
            transitions,
            logger=logger
        )

        without_implicit_places = implicit_places_remover.execute(
            without_redundant_places,
            transitions,
            logger=logger
        )
        return without_implicit_places

class DeleteDuplicatePlacesPostProcessingStrategy(PostProcessingStrategy):

    def execute(self, candidate_places, transitions):
        return set(candidate_places)
