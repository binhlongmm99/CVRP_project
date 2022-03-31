import io
import os
import re
from json import load

class CVRP():

    def __init__(self, 
        instance_name: str, 
        number_of_customers: int, 
        vehicle_capacity: int, 
        distance_matrix: list, 
        customers: list
    ):
        self.instance_name = instance_name
        self.number_of_customers = number_of_customers
        self.vehicle_capacity = vehicle_capacity
        self.distance_matrix = distance_matrix
        self.customers = customers
        
    @classmethod
    def init_from_file(cls, file_name):
        """
            Parse the input text file and return a new CVPR instance initialized with the parsed values
            
            Input:
            -----
            file_name: the input file path
            
            Output:
            ------
            cvpr: new CVPR instance
            
            Content Format for the input file:
            ---------------------------------
            NAME : A-n32-k5
            COMMENT : (Augerat et al, No of trucks: 5, Optimal value: 784)
            TYPE : CVRP
            DIMENSION : 32
            EDGE_WEIGHT_TYPE : EUC_2D 
            CAPACITY : 100
            NODE_COORD_SECTION
             1 82 76
             2 96 44
            ...
            DEMAND_SECTION
             1 0 
             2 19 
            ...
            DEPOT_SECTION
            ...
            EOF
        """
        content = open(file_name).read().replace("\n", "|")
        # comment   = re.search("COMMENT\s*:\s+(.*?)\|", content).group(1)
        # type_     = re.search("TYPE\s*:\s+(.*?)\|", content).group(1)
        # dimension = re.search("DIMENSION\s+:\s+(.*?)\|", content).group(1)
        # ew_type   = re.search("EDGE_WEIGHT_TYPE\s+:\s+(.*?)\|", content).group(1)
        name      = re.search("NAME\s*:\s+(.*?)\|", content).group(1)
        capacity  = re.search("CAPACITY\s+:\s+(.*?)\|", content).group(1)
        coords    = re.search("NODE_COORD_SECTION(.*)DEMAND_SECTION", content).group(1)
        coords    = [x.strip().split() for x in coords.split("|") if x.strip()]
        demands   = re.search("DEMAND_SECTION(.*)DEPOT_SECTION", content).group(1)
        demands   = [x.strip().split() for x in demands.split("|") if x.strip()]
        customers = {}
        customers["depart"] = {
            "coordinates": {
                "x": float(coords[0][1]),
                "y": float(coords[0][2])
            },
            "demand": float(demands[0][1])
        }
        for coord, demand in zip(coords[1:], demands[1:]):
            # assert the coordinate and the demand have the same id
            assert int(coord[0]) == int(demand[0])
            customers[f"customer_{int(coord[0])-1}"] = {
                "coordinates": {
                    "x": float(coord[1]),
                    "y": float(coord[2])
                },
                "demand": float(demand[1])
            }
        distance_matrix = [
            calculate_distance(customers[c1], customers[c2]) for c1 in customers.keys() for c2 in customers.keys()
        ]
        return cls(
            instance_name=name,
            number_of_customers=len(customers)-1,
            vehicle_capacity=capacity,
            distance_matrix=distance_matrix,
            customers=customers
        )
            

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
            return load(file_object)
    return None


# Take a route of given length, divide it into subroute 
# where each subroute is assigned to vehicle
def routeToSubroute(individual, instance):
    """
    Inputs: Sequence of customers that a route has
            Loaded instance problem
    Outputs: Route that is divided in to subroutes
             which is assigned to each vechicle.
    """
    route = []
    sub_route = []
    vehicle_load = 0
    last_customer_id = 0
    vehicle_capacity = instance['vehicle_capacity']
    
    for customer_id in individual:
        # print(customer_id)
        demand = instance[f"customer_{customer_id}"]["demand"]
        # print(f"The demand for customer_{customer_id}  is {demand}")
        updated_vehicle_load = vehicle_load + demand

        if(updated_vehicle_load <= vehicle_capacity):
            sub_route.append(customer_id)
            vehicle_load = updated_vehicle_load
        else:
            route.append(sub_route)
            sub_route = [customer_id]
            vehicle_load = demand
        
        last_customer_id = customer_id

    if sub_route != []:
        route.append(sub_route)

    # Returning the final route with each list inside for a vehicle
    return route


def printRoute(route, merge=False):
    route_str = '0'
    sub_route_count = 0
    for sub_route in route:
        sub_route_count += 1
        sub_route_str = '0'
        for customer_id in sub_route:
            sub_route_str = f'{sub_route_str} - {customer_id}'
            route_str = f'{route_str} - {customer_id}'
        sub_route_str = f'{sub_route_str} - 0'
        if not merge:
            print(f'  Vehicle {sub_route_count}\'s route: {sub_route_str}')
        route_str = f'{route_str} - 0'
    if merge:
        print(route_str)


# Calculate the number of vehicles required, given a route
def getNumVehiclesRequired(individual, instance):
    """
    Inputs: Individual route
            Json file object loaded instance
    Outputs: Number of vechiles according to the given problem and the route
    """
    # Get the route with subroutes divided according to demand
    updated_route = routeToSubroute(individual, instance)
    num_of_vehicles = len(updated_route)
    return num_of_vehicles


# Given a route, give its total cost
def getRouteCost(individual, instance, unit_cost=1):
    """
    Inputs : 
        - Individual route
        - Problem instance, json file that is loaded
        - Unit cost for the route (can be petrol etc)
    Outputs:
        - Total cost for the route taken by all the vehicles
    """
    total_cost = 0
    updated_route = routeToSubroute(individual, instance)

    for sub_route in updated_route:
        # Initializing the subroute distance to 0
        sub_route_distance = 0
        # Initializing customer id for depot as 0
        last_customer_id = 0

        for customer_id in sub_route:
            # Distance from the last customer id to next one in the given subroute
            distance = instance["distance_matrix"][last_customer_id][customer_id]
            sub_route_distance += distance
            # Update last_customer_id to the new one
            last_customer_id = customer_id
        
        # After adding distances in subroute, adding the route cost from last customer to depot
        # that is 0
        sub_route_distance = sub_route_distance + instance["distance_matrix"][last_customer_id][0]

        # Cost for this particular sub route
        sub_route_transport_cost = unit_cost*sub_route_distance

        # Adding this to total cost
        total_cost = total_cost + sub_route_transport_cost
    
    return total_cost


# Get the fitness of a given route
def eval_indvidual_fitness(individual, instance, unit_cost):
    """
    Inputs: individual route as a sequence
            Json object that is loaded as file object
            unit_cost for the distance 
    Outputs: Returns a tuple of (Number of vechicles, Route cost from all the vechicles)
    """

    # we have to minimize number of vehicles
    # TO calculate req vechicles for given route
    vehicles = getNumVehiclesRequired(individual, instance)

    # we also have to minimize route cost for all the vehicles
    route_cost = getRouteCost(individual, instance, unit_cost)

    return (vehicles, route_cost)


if __name__ == "__main__":
    # Test parts
    cvpr = CVRP.init_from_file("data/A/A-n32-k5.vrp")

    # can install `rich` library for pretty print
    print(cvpr.__dict__)
