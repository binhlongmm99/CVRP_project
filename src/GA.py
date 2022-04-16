import random
import numpy as np
import utils
import CVRP
from deap import base, creator, tools

class GA():
    def __init__(self, data_config, GA_config):
        self.data_config = data_config
        self.GA_config = GA_config
        # self.json_instance = CVRP.CVRP()

        self.pop_size = self.GA_config["pop_size"]
        self.cx_prob = self.GA_config["cx_prob"]
        self.mu_prob = self.GA_config["mu_prob"]
        self.n_generation = self.GA_config["n_generation"]


    def runMain(self):
        for input_set in self.GA_config["input_data"]["set"]:
            input_path = self.GA_config["input_data"]["input_path"] + input_set + "/"
            for i in range(len(self.data_config[input_set])):
                fileName = self.data_config[input_set][i] 
                self.instance = CVRP.CVRP.init_from_file(input_path + fileName)
                # print(self.json_instance.__dict__)
                self.ind_size = self.instance.number_of_customers

                for j in range(self.GA_config["n_runs"]):
                    print("------------------------------------------------------------------");
                    random.seed(j)
                    np.random.seed(j)

                    self.toolbox = base.Toolbox()
                    self.logbook, self.stats = createStatsObjs()
                    self.createCreators()
                    self.generatingPopFitness()
                    self.runGenerations()
                    self.getBestInd()
                    self.doExport(j, input_set)
                    del creator.FitnessMin
                    del creator.Individual

    def createCreators(self):
        creator.create('FitnessMin', base.Fitness, weights=(-1.0, ))
        creator.create('Individual', list, fitness=creator.FitnessMin)

        # Registering toolbox
        self.toolbox.register('indexes', random.sample, range(1, self.ind_size + 1), self.ind_size)

        # Creating individual and population from that each individual
        self.toolbox.register('individual', tools.initIterate, creator.Individual, self.toolbox.indexes)
        self.toolbox.register('population', tools.initRepeat, list, self.toolbox.individual)

        # Creating evaluate function using custom fitness
        self.toolbox.register('evaluate', CVRP.eval_indvidual_fitness, instance=self.instance, unit_cost=1)

        # Selection method
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        # Crossover method
        # self.toolbox.register("mate", cxOrderedCVRP)
        self.toolbox.register("mate", cxPartialyMatched)

        # Mutation method
        self.toolbox.register("mutate", mutationCVRP, indpb=self.mu_prob)


    def generatingPopFitness(self):
        self.pop = self.toolbox.population(n=self.pop_size)
        self.invalid_ind = [ind for ind in self.pop if not ind.fitness.valid]
        self.fitnesses = list(map(self.toolbox.evaluate, self.invalid_ind))
        for ind, fit in zip(self.invalid_ind, self.fitnesses):
            ind.fitness.values = fit
        self.pop = self.toolbox.select(self.pop, len(self.pop))
        recordStat(self.invalid_ind, self.logbook, self.pop, self.stats, gen = 0)


    def runGenerations(self):
        count = 0
        best_cost = tools.selBest(self.pop, 1)[0].fitness.values[0]

        # Running algorithm for given number of generations
        for gen in range(self.n_generation):
            # if gen % 50 == 0:
            #     print(f"{20*'#'} Currently Evaluating {gen} Generation {20*'#'}")

            # Selecting individuals
            # Selecting offsprings from the population
            self.offspring = self.toolbox.select(self.pop, len(self.pop))

            self.offspring = [self.toolbox.clone(ind) for ind in self.offspring]

            # Performing crossover and mutation operations according to their probabilities
            for ind1, ind2 in zip(self.offspring[::2], self.offspring[1::2]):
                if random.random() <= self.cx_prob:
                    self.toolbox.mate(ind1, ind2)

                    # If cross over happened to the individuals then we are deleting those individual
                    # fitness values, This operations are being done on the offspring population.
                    del ind1.fitness.values, ind2.fitness.values
                self.toolbox.mutate(ind1)
                self.toolbox.mutate(ind2)

            # Calculating fitness for all the invalid individuals in offspring
            self.invalid_ind = [ind for ind in self.offspring if not ind.fitness.valid]
            self.fitnesses = self.toolbox.map(self.toolbox.evaluate, self.invalid_ind)
            for ind, fit in zip(self.invalid_ind, self.fitnesses):
                ind.fitness.values = fit

            # Recalcuate the population with newly added offsprings and parents
            # We have to select same population size
            self.pop = self.toolbox.select(self.pop + self.offspring, self.pop_size)

            # Recording stats in this generation
            recordStat(self.invalid_ind, self.logbook, self.pop, self.stats, gen + 1)
            
            if (tools.selBest(self.pop, 1)[0].fitness.values[0] == best_cost):
                count += 1
            else: 
                best_cost = tools.selBest(self.pop, 1)[0].fitness.values[0]
                count = 0
            if count == 500:
                break

        print(f"{20 * '#'} End of Generations {20 * '#'} ")


    def getBestInd(self):
        self.best_individual = tools.selBest(self.pop, 1)[0]

        # Printing the best after all generations
        print(f"Best individual is {self.best_individual}")

        # Printing the route from the best individual
        CVRP.printRoute(CVRP.routeToSubroute(self.best_individual, self.instance))
        print(f"Cost "f"{self.best_individual.fitness.values[0]}")

    def doExport(self, seed, input_set):
        csv_file_name = f"{self.instance.instance_name}_" \
                        f"pop{self.pop_size}_crossProb{self.cx_prob}" \
                        f"_mutProb{self.mu_prob}_numGen{self.n_generation}" \
                        f"_seed{seed}.csv"
        csv_path = self.GA_config["output_data"] + input_set + "/" + self.instance.instance_name + "/"
        utils.exportCsv(csv_file_name, csv_path, self.logbook)


# Order Crossover
def cxOrderedCVRP(input_ind1, input_ind2):
    ind1 = [x-1 for x in input_ind1]
    ind2 = [x-1 for x in input_ind2]
    size = min(len(ind1), len(ind2))
    a, b = random.sample(range(size), 2)
    if a > b:
        a, b = b, a

    # print(f"The cutting points are {a} and {b}")
    holes1, holes2 = [True] * size, [True] * size
    for i in range(size):
        if i < a or i > b:
            holes1[ind2[i]] = False
            holes2[ind1[i]] = False

    # We must keep the original values somewhere before scrambling everything
    temp1, temp2 = ind1, ind2
    k1, k2 = b + 1, b + 1
    for i in range(size):
        if not holes1[temp1[(i + b + 1) % size]]:
            ind1[k1 % size] = temp1[(i + b + 1) % size]
            k1 += 1

        if not holes2[temp2[(i + b + 1) % size]]:
            ind2[k2 % size] = temp2[(i + b + 1) % size]
            k2 += 1

    # Swap the content between a and b (included)
    for i in range(a, b + 1):
        ind1[i], ind2[i] = ind2[i], ind1[i]

    # Finally adding 1 again to reclaim original input
    ind1 = [x+1 for x in ind1]
    ind2 = [x+1 for x in ind2]
    return ind1, ind2

# Partially Mapped Crossover
def cxPartialyMatched(input_ind1, input_ind2):
    ind1 = [x-1 for x in input_ind1]
    ind2 = [x-1 for x in input_ind2]
    size = min(len(ind1), len(ind2))
    p1, p2 = [0] * size, [0] * size

    # Initialize the position of each indices in the individuals
    for i in range(size):
        p1[ind1[i]] = i
        p2[ind2[i]] = i
    # Choose crossover points
    cxpoint1 = random.randint(0, size)
    cxpoint2 = random.randint(0, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:  # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    # Apply crossover between cx points
    for i in range(cxpoint1, cxpoint2):
        # Keep track of the selected values
        temp1 = ind1[i]
        temp2 = ind2[i]
        # Swap the matched value
        ind1[i], ind1[p1[temp2]] = temp2, temp1
        ind2[i], ind2[p2[temp1]] = temp1, temp2
        # Position bookkeeping
        p1[temp1], p1[temp2] = p1[temp2], p1[temp1]
        p2[temp1], p2[temp2] = p2[temp2], p2[temp1]
    
    # Finally adding 1 again to reclaim original input
    ind1 = [x+1 for x in ind1]
    ind2 = [x+1 for x in ind2]
    return ind1, ind2

def mutationCVRP(individual, indpb):
    """
    Inputs : Individual route
             Probability of mutation betwen (0,1)
    Outputs : Mutated individual according to the probability
    """
    size = len(individual)
    if random.random() < indpb:
        indx_1 = random.randint(0, size - 1)
        indx_2 = random.randint(0, size - 1)
        while indx_1 == indx_2:
            indx_2 = random.randint(0, size - 1)
        if random.random() <= 0.5:
            individual[indx_1], individual[indx_2] = \
                individual[indx_2], individual[indx_1]
        else: 
            min_indx = min(indx_1, indx_2)
            max_indx = max(indx_1, indx_2)
            individual[min_indx:max_indx] = individual[min_indx:max_indx][::-1]
    return individual


## Statistics and Logging
def createStatsObjs():
    # Method to create stats and logbook objects
    """
    Inputs : None
    Outputs : tuple of logbook and stats objects.
    """
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    # Methods for logging
    logbook = tools.Logbook()
    logbook.header = "Generation", "avg", "std", "min", "max", "best_one", "fitness_best_one"

    return logbook, stats


def recordStat(invalid_ind, logbook, pop, stats, gen):
    """
    Inputs : invalid_ind - Number of children for which fitness is calculated
             logbook - Logbook object that logs data
             pop - population
             stats - stats object that compiles statistics
    Outputs: None, prints the logs
    """
    record = stats.compile(pop)
    best_individual = tools.selBest(pop, 1)[0]
    record["best_one"] = best_individual
    record["fitness_best_one"] = best_individual.fitness
    logbook.record(Generation=gen, **record)
    print(logbook.stream)
