import json
from GA import GA

DATA_PATH = ".\data_config_test.json"
GA_PATH = ".\GA_config.json"

def main():
    with open(DATA_PATH, 'r') as f:
        data_config = json.load(f)
    with open(GA_PATH, 'r') as f:
        GA_config = json.load(f)
    GA(data_config, GA_config).runMain()


if __name__ == '__main__':
    main()