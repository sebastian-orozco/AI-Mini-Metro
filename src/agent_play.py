import pygame

from config import framerate, screen_color, screen_height, screen_width
from event.convert import convert_pygame_event
from mediator import Mediator
from agents.dummy_agent import DummyAgent
from agents.rules_agent import RulesBasedAgent
import copy
import time
import random

# init
pygame.init()

# settings
flags = pygame.SCALED

# game constants initialization
screen = pygame.display.set_mode((screen_width, screen_height), flags, vsync=1)
clock = pygame.time.Clock()

mediator = Mediator()
station_idx = [0,1,2,3]

agent = RulesBasedAgent(mediator)

end_time = time.time()
start = True

# init table to store state-value pairings
solved_population = {}
elite_population = {} # stores max from every algo iteration

# create initial population
population_size = 5
count = 0
current_population = []
for _ in range(population_size):
    agent.generate_paths()
    current_population.append(copy.deepcopy(agent.planned_paths))
remaining_population = current_population
first = True
genetic_evaluation_step = False

# init scores
best_score = 0

# while not out of time, perform genetic algorithm
while True:
    # required
    dt_ms = clock.tick(framerate)
    mediator.increment_time(dt_ms)
    screen.fill(screen_color)
    mediator.render(screen)

    # step 1: evaluate each individual
    if first:
        # print("FIRST")
        first = False
        current_individual = remaining_population[0]
        mediator.assign_planned_paths(current_individual)
        remaining_population.remove(current_individual)
        end_time = time.time() + 5

        count += 1
    else:
        if not remaining_population and time.time() > end_time:
            # reset map
            for path in mediator.paths:
                mediator.remove_path(path)
            for station in mediator.stations:
                station.passengers.clear()
                station.reset_time_at_max_capacity()      

            # update table for last individual
            solved_population[tuple(tuple(line) for line in current_individual)] = best_score
            # print(f"BEST SCORE FOR INDIVIDUAL {count} = {best_score}")
            best_score = 0
            mediator.score = 0

            count = 0
            first = True
            genetic_evaluation_step = True

        elif time.time() >= end_time:
            # update table & reset score
            solved_population[tuple(tuple(line) for line in current_individual)] = best_score
            # print(f"BEST SCORE FOR INDIVIDUAL {count} = {best_score}")
            best_score = 0
            mediator.score = 0

            # reset map
            for path in mediator.paths:
                mediator.remove_path(path)
            for station in mediator.stations:
                station.passengers.clear()
                station.reset_time_at_max_capacity()

            # move on to next individual
            current_individual = remaining_population[0]
            mediator.assign_planned_paths(current_individual)
            remaining_population.remove(current_individual)
            end_time = time.time() + 5

            count += 1

    # steps 2-5
    if genetic_evaluation_step:
        # print("entering genetic eval step...")

        # select individuals for crossover
        parent_gen = []

        # # exploitation: pick 90% from the better performers
        sorted_population = sorted(solved_population.items(), key=lambda x: x[1], reverse=True)
        num_best = int(0.9 * (population_size // 2))

        best_individuals = [ind for ind, score in sorted_population[:num_best]]
        parent_gen.extend(best_individuals)        

        # # exploration: pick 10% from the others at random
        remaining_individuals = [ind for ind, score in sorted_population[num_best:]]
        num_random = (population_size // 2) - len(parent_gen)
        random_individuals = random.sample(remaining_individuals, min(num_random, len(remaining_individuals)))
        parent_gen.extend(random_individuals)

        # debug
        parent_gen_scores = [solved_population[ind] for ind in parent_gen]
        # print("parent gen best scores:", parent_gen_scores)
        print("avg score:", sum(parent_gen_scores) / len(parent_gen_scores))

        # # unpack tuples
        parent_gen = [ [list(line) for line in parent] for parent in parent_gen ]

        # for parent in parent_gen:
        #     print("parent = ", parent)

        # crossover
        children_gen = copy.deepcopy(parent_gen) # parents & children will compete in next iteration
        # print("SIZE OF PARENT GEN IS ", len(parent_gen))
        while len(children_gen) < population_size:
            # pick two parents at random
            p1, p2 = random.sample(parent_gen, 2)

            # combine random feature

            # child copies parent 1
            child = copy.deepcopy(p1)

            # pick random line from parent 1, and random line from parent 2
            l1 = random.choice(p1)
            l2 = random.choice(p2)

            # print(l1)

            # flip a coin:
            coin_flip = random.choice([0, 1])
            # heads -> end of line 1 is extended to random station along line 2
            if coin_flip:
                for line in child:
                    if line == l1:
                        station_to_add = random.choice(l2)  
                        if station_to_add not in line:  
                            line.append(station_to_add)
                        break

            # tails -> end of line 1 is removed and instead appended to different line
            else:
                orphan = None
                modified_line = None
                for line in child:
                    if line == l1 and len(line) > 1:  # ensure the line has at least two stations
                        orphan = line.pop(-1)  # remove the last station
                        modified_line = line
                        break

                if orphan:
                    # append orphaned station to a random other line
                    available_lines = [line for line in child if line != modified_line]
                    # if available_lines: 
                    new_line = random.choice(available_lines)
                    if orphan not in new_line:  # avoid duplicates
                        new_line.append(orphan)        
                
            children_gen.append(child)

        # print(children_gen)
        # print("NEXT GENERATION, SIZE = ", len(children_gen))
        genetic_evaluation_step = False
        remaining_population = current_population = children_gen

        # select for survival (this is done as the individuals in the next gen are evaluated)

        # mutate
        # # with 10% chance turn one of the lines in a random child into a loop 
        if random.random() < 0.1:
            # print("LOOP")
            child = random.choice(children_gen)
            line = random.choice(child)
            if line[0] != line[-1]:
                line.append(line[0])



    # update score
    if mediator.score > best_score:
        best_score = mediator.score

    # react to user interaction
    for pygame_event in pygame.event.get():
        if pygame_event.type == pygame.QUIT:
            best_path = max(solved_population.items(), key=lambda x: x[1])[0] 
            best_score = max(solved_population.values())  

            print("BEST SCORE =", best_score)
            print("BEST PATH =", best_path)
            raise SystemExit
        else:
            event = convert_pygame_event(pygame_event)
            mediator.react(event)

    pygame.display.flip()

