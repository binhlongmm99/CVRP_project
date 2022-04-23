import json
import sys
from GA import GA
from GA_LS import GA_LS


DATA_PATH = ".\data_config.json"
# DATA_PATH = ".\data_config_test.json"
GA_PATH = ".\GA_config.json"

def main():
    with open(DATA_PATH, 'r') as f:
        data_config = json.load(f)
    with open(GA_PATH, 'r') as f:
        GA_config = json.load(f)
        
    if int(sys.argv[1]) == 0:
        GA(data_config, GA_config).runMain()
    elif int(sys.argv[1]) == 1:
        GA_LS(data_config, GA_config).runMain()
    else:
        print("Invalid algorithm!")


if __name__ == '__main__':
    main()