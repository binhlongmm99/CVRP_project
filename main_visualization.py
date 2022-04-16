from sqlalchemy import true
from visualization.plot_convergence import *
from visualization.plot_solution import *
from src import CVRP
import json


# VISUALIZATION_PATH = "./visualization/visualization_config_test.json"
VISUALIZATION_PATH = "./visualization/visualization_config.json"


if __name__ == "__main__":
    with open(VISUALIZATION_PATH, 'r') as f:
        visualize_config = json.load(f)

    for type in visualize_config["output_result"]["type"]:
        os.makedirs(visualize_config["output_result"]["output_path"] + type, exist_ok=True)
        
    # Plotting all instances
    # convergence
    print("Plotting convergence")
    createAllFitnessPlots(visualize_config)
    print()

    # solution
    print("Plotting solution")
    createAllSolutionPlots(visualize_config)


    # Plotting 1 instance
    # convergence
    # plotFitnessFromCSV("./results/A/A-n33-k5/A-n33-k5_pop200_crossProb0.8_mutProb0.1_numGen5000_seed0.csv")
    
    # solution
    # sample_route = [15, 17, 9, 3, 16, 29, 12, 5, 26, 7, 8, 13, 32, 
    #                 2, 20, 4, 27, 25, 30, 10, 23, 28, 18, 22, 24, 
    #                 6, 19, 14, 21, 1, 31, 11]
    # data_instance = CVRP.CVRP.init_from_file("./data/A/A-n33-k5.vrp")
    # plotRoute(sample_route, 
    #             "./results/A/A-n33-k5/A-n33-k5_pop200_crossProb0.8_mutProb0.1_numGen5000_seed0.csv",
    #             data_instance,
    #             optimal= true)
