import numpy as np
import os
import random
import copy


class Bee(object):
    """Assumes that dim is the same for all vars"""
    def __init__(self, MCN, SN, MR, SF, limit, func, dim, MFE):
        self.MCN = MCN
        self.SN = SN
        self.MR = MR
        self.limit = limit
        if SF == "ASF":
            self.autoscale = True
            self.SF = 1 #assumed to be the initialization here...
        else:
            self.autoscale = False
            self.SF = SF

        self.func_init_range = func.init_range
        self.func_search_range = func.init_range
        self.__func = func
        self.dim = dim

        #max function evalations, assumed to mean fitness function
        self.MFE = MFE
        self.number_of_function_evaluations = 0

        self.population = [self.initialize_site() for i in range(self.SN)]
        self.trials = np.array([0 for i in range(self.SN)])
        self.fitnesses = np.array([self.f_fitness(x) for x in self.population])
        self.cycle = 1

        self.successful_mutations = 0
        self.failed_mutations = 0

        self.best_fitness = -float('inf')
        self.best_cost = None
        self.best_site = None
        self.update_best()

    def f_fitness(self, site):
        self.number_of_function_evaluations += 1
        cost = self.__func(site)
        if cost >= 0:
            return 1.0/(1 + cost)
        else:
            return 1 + abs(cost)

    def initialize_site(self):
        """create one site, with each parameter within the functions bounds"""
        low,high = self.func_init_range
        f_init = lambda : low + random.random()*(high - low)
        L = [f_init() for i in range(self.dim)]
        return np.array(L)

    def sample(self, norm_weights, size=1):
        return np.random.choice(range(len(norm_weights)), size=size, p=norm_weights)

    def random_index_except_i(self, except_i):
        """Choose a random site except index.

           Idea: pick among range 1..SN-1, that way the last index is excluded.
                 Now if the chosen index turns out to be equal to except_i,
                 return the last index instead (the last index is never
                 directly chosen, so the distribution should remain uniform.
        """
        chosen_i = random.randint(0, self.SN-2)
        if chosen_i == except_i:
            chosen_i = (self.SN - 1)
        return chosen_i

    def neighbourhood(self, site, index):
        """Generate a new site in the neighbourhood of site"""
        low, high = self.func_search_range
        f_clamp = lambda x: min(max(x, low), high)

        new_site = []
        if self.MR == 0: #BASIC BEHAVIOUR, NOT ZERO PROBABILITY
            #pick a random index of site and perturb it using a second random site
            new_site.extend(site)

            k_index = self.random_index_except_i(index)
            j_index = random.randint(0, len(site)-1)
            old_param = site[j_index]
            other_param = self.population[k_index][j_index]
            perturb = random.random()*self.SF*2 - self.SF
            new_param = old_param + perturb*(old_param - other_param)

            new_site[j_index] = f_clamp(new_param)
        else:
            for j,old_param in enumerate(site):
                if random.random() < self.MR:
                    k_index = self.random_index_except_i(index)
                    other_param = self.population[k_index][j]
                    perturb = random.random()*self.SF*2 - self.SF
                    new_param = old_param + perturb*(old_param - other_param)

                    new_site.append(f_clamp(new_param))
                else:
                    new_site.append(old_param)
        return np.array(new_site)

    def generate_new_sources(self):
        new_sites = []
        new_fitnesses = []
        for i in range(self.SN):
            old_site = self.population[i]
            old_fitness = self.fitnesses[i]
            candidate_site = self.neighbourhood(old_site, i)
            candidate_fitness = self.f_fitness(candidate_site)
            if candidate_fitness > old_fitness:
                new_sites.append(candidate_site)
                new_fitnesses.append(candidate_fitness)
                self.trials[i] = 0
                self.successful_mutations += 1
            else:
                new_sites.append(old_site)
                new_fitnesses.append(old_fitness)
                self.trials[i] += 1
                self.failed_mutations += 1
        self.population = new_sites
        self.fitnesses = np.array(new_fitnesses)

    def probabilistic_exploit(self):
        probabilities = self.fitnesses/np.sum(self.fitnesses)

        #t = 0
        #while t < self.SN:
        """This part of the pseudocode does not make much sense; I here
           interpret the intended meaning to perform a roulette selection for
           each observer bee (SN observers in this case) among all sites,
           weighted by the fitness of that site.

           In an attempt to make it more efficient, sample all sites at once
           repeatedly (using numpy.random.choice)
        """

        #similar to generate_new_sources, except it is possible to have repeat
        #elements here. Note that due to the sampling all at once, even though
        #an exploited site might lead to an improvement, future (non)occurences
        #of that site are still sampled with the old distribution.
        #
        #This appears reasonable with respect to the pseudocode in the paper as
        #well
        choices = self.sample(probabilities, size=self.SN)
        for t in range(self.SN):
            old_site = self.population[choices[t]]
            old_fitness = self.fitnesses[choices[t]]
            candidate_site = self.neighbourhood(old_site, choices[t])
            candidate_fitness = self.f_fitness(candidate_site)
            if candidate_fitness > old_fitness:
                self.population[choices[t]] = candidate_site
                self.fitnesses[choices[t]] = candidate_fitness
                self.trials[choices[t]] = 0
                self.successful_mutations += 1
            else:
                self.trials[choices[t]] += 1
                self.failed_mutations += 1

    def check_maxtrials(self, max_renews=1):
        """by default max renewals per cycle is set to 1, as described in
           the paper (with respect to basic ABC; though no modification to this
           is mentioned later on, hence 1 appears to be the most reasonable
           assumption).
        """
        renewals = []
        for i,trial in enumerate(self.trials):
            if trial > self.limit:
                renewals.append((trial, i))
        renewals.sort(reverse=True)
        for renewal in range(max_renews):
            if not renewals:
                break
            _, index = renewals.pop()

            new_site = self.initialize_site()
            self.population[index] = new_site
            self.fitnesses[index] = self.f_fitness(new_site)
            self.trials[index] = 0

    def update_best(self):
        for i,fitness in enumerate(self.fitnesses):
            if fitness > self.best_fitness:
                self.best_fitness = fitness
                self.best_cost = self.__func(self.population[i])
                self.best_site = copy.deepcopy(self.population[i])

    # - - - - - - - - - -
    def step(self):
        # employed bees find food sources
        self.generate_new_sources()

        # each onlooker probabilistically selects a food source found by
        # the employed bees and attempts to improve it
        self.probabilistic_exploit()

        # check for maxtrials, scout for new
        self.check_maxtrials()

        #find best so far
        self.update_best()

        #ASF: adaptive scaling factor (SF) adjustment
        if self.autoscale:
            mutation_success_rate = self.successful_mutations \
                   / (self.successful_mutations + self.failed_mutations)
            if mutation_success_rate < 1.0/5.0:
                self.SF = self.SF*0.85
            elif mutation_success_rate > 1.0/5.0:
                self.SF = self.SF/0.85
            else:
                self.SF = self.SF

        self.cycle += 1

    def run(self):
        assert (not (self.MCN is None)) or (not (self.MFE is None))
        while (self.MCN is None) or (self.cycle <= self.MCN):
            #print('lowest cost: {:1.2E}'.format(self.best_cost), end='\r')
            self.step()
            if (not (self.MFE is None)) and (self.number_of_function_evaluations > self.MFE):
                #print("Max function evaluations ({}) exceeded with {} after {} cycles".format(
                #         self.MFE, self.number_of_function_evaluations, self.cycle))
                break
        else:
            #print("Max cycle number {} reached ({} evals}".format(
            #          self.MCN, self.number_of_function_evaluations))
            pass
        #print(' fit:', self.best_fitness)
        #print('cost:', self.best_cost)
        #print(self.best_site)
        return self.best_cost, self.best_site

def run_helper(tup):
    x,seed_offset = tup
    random.seed(64 + seed_offset)
    np.random.seed(64 + seed_offset)
    try:
        os.nice(20)
    except AttributeError:
        #print("OS does not support setting niceness")
        pass

    return x.run()
