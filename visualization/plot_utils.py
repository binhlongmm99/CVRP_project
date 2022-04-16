import glob
import pandas as pd

def loadResultPaths(dataset, instance):
    all_instance_path = glob.glob("./results/" + dataset + "/" + instance[:-4] + "/*.csv")
    all_instance_path = [i.replace("\\","/") for i in all_instance_path]
    # print(all_instance_path)
    csv_files = [eachpath.split("/")[-1] for eachpath in all_instance_path]
    # print(csv_files)
    return all_instance_path, csv_files


def loadCsv(csv_file_path):
    instance = pd.read_csv(csv_file_path)
    return instance