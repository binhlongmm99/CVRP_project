import os
import io
import csv
import json
from CVRP import CVRP


def calculate_distance(customer1, customer2):
    # Calculate distance between customer1 and customer 2 given their
    # Euclidean coordinates
    # Returns euclidean distance
    """
    Inputs: customer1 from json object, customer2 from json object
    Outputs: Returns Euclidian distance between these customer locations.
    """
    return ((customer1['coordinates']['x'] - customer2['coordinates']['x']) ** 2 + \
            (customer1['coordinates']['y'] - customer2['coordinates']['y']) ** 2) ** 0.5

# Load the given problem, which can be a json file
def load_instance(json_file):
    """
    Inputs: path to json file
    Outputs: json file object if it exists, or else returns NoneType
    """
    if os.path.exists(path=json_file):
        with io.open(json_file, 'rt', newline='') as file_object:
            return json.load(file_object)
    return None

def read_input(file_name):
    with open(file_name, "r") as f:
        name = f.readline().split(":")[1].strip()
        comment = f.readline().split(":")[1].strip()
        type = f.readline().split(":")[1].strip()
        dimensions = int(f.readline().split(":")[1].strip())
        f.readline()
        capacity = int(f.readline().split(":")[1].strip())

        # read NODE_COORD_SECTION

        # read DEMAND_SECTION 
    
        # read DEPOT_SECTION

        instance = CVRP()
        return instance


def exportCsv(csv_file_name, csv_path, logbook):
    # Exporting CSV files
    csv_columns = logbook[0].keys()

    filename = os.path.join(csv_path, csv_file_name)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in logbook:
                writer.writerow(data)
    except IOError:
        print("I/O error")


if __name__ == "__main__":
    # Test parts
    cvpr = CVRP.init_from_file("data/A/A-n32-k5.vrp")

    # can install `rich` library for pretty print
    print(cvpr.__dict__)
    