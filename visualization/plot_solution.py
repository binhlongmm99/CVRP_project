import matplotlib.pyplot as plt
import pandas as pd
from src.CVRP import CVRP, routeToSubroute
import json
import os
from visualization import plot_utils

VISUALIZATION_PATH = "./visualization_config_test.json"


# Loading locations and customers to dataframe
def getCoordinatesDframe(instance):
    num_of_cust = instance.number_of_customers
    # Getting all customer coordinates
    customer_list = [i for i in range(1, num_of_cust + 1)]
    x_coord_cust = [instance.customers[f'customer_{i}']['coordinates']['x'] for i in customer_list]
    y_coord_cust = [instance.customers[f'customer_{i}']['coordinates']['y'] for i in customer_list]
    # Getting depot x,y coordinates
    depot_x = [instance.customers['depart']['coordinates']['x']]
    depot_y = [instance.customers['depart']['coordinates']['y']]
    # Adding depot details
    customer_list = [0] + customer_list
    x_coord_cust = depot_x + x_coord_cust
    y_coord_cust = depot_y + y_coord_cust
    df = pd.DataFrame({"X": x_coord_cust,
                       "Y": y_coord_cust,
                       "customer_list": customer_list
                       })
    return df

def plotSubroute(subroute, dfhere, color):
    totalSubroute = [0]+subroute+[0]
    subroutelen = len(subroute)
    for i in range(subroutelen+1):
        firstcust = totalSubroute[0]
        secondcust = totalSubroute[1]
        plt.plot([dfhere.X[firstcust], dfhere.X[secondcust]],
                 [dfhere.Y[firstcust], dfhere.Y[secondcust]], c=color)
        totalSubroute.pop(0)


def plotRoute(route, csv_file_path, data_instance, optimal = False):
    subroutes = routeToSubroute(route, data_instance)
    colorslist = ["blue","green","red","cyan","magenta","yellow","black","#eeefff"]
    colorindex = 0

    # getting df
    dfhere = getCoordinatesDframe(data_instance)


    # Plotting scatter
    fig = plt.figure(figsize=(10, 10))

    for i in range(dfhere.shape[0]):
        if i == 0:
            plt.scatter(dfhere.X[i], dfhere.Y[i], c='green', s=200)
            plt.text(dfhere.X[i], dfhere.Y[i], "depot", fontsize=12)
        else:
            plt.scatter(dfhere.X[i], dfhere.Y[i], c='orange', s=200)
            plt.text(dfhere.X[i], dfhere.Y[i], f'{i}', fontsize=12)

    # Plotting routes
    for route in subroutes:
        plotSubroute(route, dfhere, color=colorslist[colorindex])
        colorindex += 1

    # Plotting is done, adding labels, Title
    plt.xlabel("X - Coordinate")
    plt.ylabel("Y - Coordinate")

    csv_title = csv_file_path.split("/")[-1][:-4]
    dataset = csv_file_path.split("/")[-3]
    instance =  csv_file_path.split("/")[-2]
    if optimal == False:
        print("Plotting: ", csv_title)
        filename = "./figures/solution/" + dataset + "/" + instance + "/" + csv_title + ".png"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.title(csv_title)
        
    else:
        print("Plotting: ", csv_title.split("_")[0] + "_optimal")
        filename = "./figures/solution/" + dataset + "/" + instance + "/" + csv_title.split("_")[0] + "_optimal.png"
        # print(filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.title(csv_title.split("_")[0] + "_optimal")

    plt.savefig(filename)
        
    # plt.show()
    plt.close(fig)


def createAllSolutionPlots(config):
    allpaths = []
    for dataset in config["input_result"]["set"]:
        for instance in config["instance"][dataset]:
            instance_path, csv_files = plot_utils.loadResultPaths(dataset, instance)
            allpaths.extend(instance_path)
    # print(allpaths)

    # Plotting all
    for eachpath in allpaths:
        csv_instance = plot_utils.loadCsv(eachpath)
        
        dataset = eachpath.split("/")[-3]
        instance_name = eachpath.split("/")[-2]
        data_instance = CVRP.init_from_file("./data/" + dataset + "/" + instance_name + ".vrp")

        best_route_column = csv_instance['best_one']
        # get the last row
        best_last_one = best_route_column.iloc[-1]
        best_last_one = json.loads(best_last_one)
        plotRoute(best_last_one, eachpath, data_instance)


# if __name__ == "__main__":
#     with open(VISUALIZATION_PATH, 'r') as f:
#         visualize_config = json.load(f)

#     for type in visualize_config["output_result"]["type"]:
#         os.makedirs(visualize_config["output_result"]["output_path"] + type, exist_ok=True)

#     # plot all instances
#     createAllSolutionPlots(visualize_config)

#     # # plot 1 instance
#     # sample_route = [1, 2, 4, 25, 24, 22, 23, 17, 13, 10, 15, 19, 18, 12, 14, 16, 11, 9, 6, 8, 7, 3, 5, 21, 20]
#     # data_instance = CVRP.init_from_file("./data/A/A-n33-k5.vrp")
#     # plotRoute(sample_route, 
#     #             "./results/A/A-n33-k5/A-n33-k5_pop200_crossProb0.8_mutProb0.1_numGen5000_seed0.csv",
#     #             data_instance)
