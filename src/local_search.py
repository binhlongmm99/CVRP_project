
import copy
import CVRP

def _2opt(route, i, k):
    new_route = copy.deepcopy(route)
    new_route[i:k+1] = new_route[i:k+1][::-1]
    return new_route


def local_search_best_improve(ind, instance):
    size = len(ind)
    best_ind = ind
    improved = True
    while improved:
        best_cost = CVRP.eval_indvidual_fitness(best_ind, instance, 1)[0]
        improved = False
        for i in range(size-1):
            for k in range(i+1, size):
                new_ind = _2opt(ind, i, k)
                new_cost = CVRP.eval_indvidual_fitness(new_ind, instance, 1)[0]
                if new_cost < best_cost:
                    best_ind = new_ind
                    best_cost = new_cost
                    improved = True
        ind = best_ind
    return ind


def local_search_first_improve(ind, instance):
    size = len(ind)
    best_cost = CVRP.eval_indvidual_fitness(ind, instance, 1)[0]
    for i in range(size-1):
        for k in range(i+1, size):
            new_ind = _2opt(ind, i, k)
            new_cost = CVRP.eval_indvidual_fitness(new_ind, instance, 1)[0]
            if new_cost < best_cost:
                return new_ind
    return ind
    

 
