import matplotlib.pyplot as plt
import os
from visualization import plot_utils

VISUALIZATION_PATH = "./visualization_config_test.json"

def cleanResult(csv_file_path):
    loaded_result = plot_utils.loadCsv(csv_file_path)
    min_column = loaded_result['min']
    gen_column = loaded_result['Generation']

    def clean_row(inp):
        out = inp.replace("[","").replace("]","").strip().split(" ")
        return out

    min_dist = [float(clean_row(i)[-1]) for i in min_column]
    min_vehicles = [float(clean_row(i)[0]) for i in min_column]
    return min_dist, gen_column


def plotFitnessFromCSV(csv_file_path):
    distances, generations = cleanResult(csv_file_path)
    csv_title = csv_file_path.split("/")[-1][:-4]
    print("Plotting: ", csv_title)

    fig = plt.figure(figsize=(10, 8))
    plt.plot(generations, distances)
    plt.xlabel("Generations")
    plt.ylabel("Distance")
    plt.title(csv_title)

    dataset = csv_file_path.split("/")[-3]
    instance =  csv_file_path.split("/")[-2]
    filename = "./figures/convergence/" + dataset + "/" + instance + "/" + csv_title + ".png"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)

    # plt.show()
    plt.close(fig)


def createAllFitnessPlots(config):
    allpaths = []
    for dataset in config["input_result"]["set"]:
        for instance in config["instance"][dataset]:
            instance_path, csv_files = plot_utils.loadResultPaths(dataset, instance)
            allpaths.extend(instance_path)
    # print(allpaths)

    # Plotting all
    for eachpath in allpaths:
        plotFitnessFromCSV(eachpath)



# if __name__ == "__main__":
#     with open(VISUALIZATION_PATH, 'r') as f:
#         visualize_config = json.load(f)

#     for type in visualize_config["output_result"]["type"]:
#         os.makedirs(visualize_config["output_result"]["output_path"] + type, exist_ok=True)

#     # plot all instances
#     createAllFitnessPlots(visualize_config)

#     # # plot 1 instance
#     # plotFitnessFromCSV("../results/A/A-n33-k5/A-n33-k5_pop200_crossProb0.8_mutProb0.1_numGen5000_seed0.csv")