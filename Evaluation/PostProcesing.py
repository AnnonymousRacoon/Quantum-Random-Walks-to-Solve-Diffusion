import pandas as pd
import re
import glob


def rebuild_counts_from_csv(path,n_dims, shots):
    df = pd.read_csv(path)
    return rebuild_counts_from_dataframe(dataframe=df, n_dims=n_dims, shots=shots)


def rebuild_counts_from_dataframe(dataframe,n_dims,shots):
    dimension_counts = {}
    for dimension in range(n_dims):
        dimension_counts[dimension] = []

    pde = list(dataframe.probability_density)


    for idx, density in enumerate(pde):
        n_counts = int(density*shots)
        for _ in range(n_counts):

            # print(dataframe["dimension_0"][idx])
            for dimension in range(n_dims):
                dimension_key = "dimension_{}".format(dimension)
                #
                dimension_counts[dimension]+=[dataframe[dimension_key][idx]]
                
    # print(dimension_counts)
    rebuilt_dict = {}
    for dimension in range(n_dims):
        rebuilt_dict[f"d{dimension}"] = dimension_counts[dimension]

    return rebuilt_dict


def rebuild_counts_from_dictionary(dictionary:dict, n_dims, shots):
    dataframe = pd.DataFrame(dictionary)
    return rebuild_counts_from_dataframe(dataframe=dataframe, n_dims=n_dims, shots=shots)


def get_stats_from_counts_dict(results_dict:dict):
    dataframe = pd.DataFrame(results_dict)
    return get_stats_from_counts_dataframe(dataframe)


def get_stats_from_counts_dataframe(counts_dataframe: pd.DataFrame)-> dict:
    results_dict = {}
    results_dict["corr"] = counts_dataframe.corr()
    results_dict["cov"] = counts_dataframe.cov()
    results_dict["mean"] = counts_dataframe.mean()
    results_dict['var'] = counts_dataframe.var()
    return results_dict
    
def get_n_steps_from_filepath(filepath)-> int:
    filename = filepath.split('/')[-1]
    return int(re.findall(r"\d+_steps",filename)[0].split('_')[0])

def get_n_shots_from_path(path)-> int:
    experiment_dir_name = path.split('/')[-1]
    nshots = int(re.findall(r"\d+shots",experiment_dir_name)[0].split('s')[0])
    return nshots

def get_n_dims_from_path(path)-> int:
    experiment_dir_name = path.split('/')[-1]
    ndims = int(re.findall(r"\d+D_",experiment_dir_name)[0].split('D')[0])
    return ndims

def extract_mean_variance_vs_nsteps(directory_path: str,dimension = 0):
    nshots = get_n_shots_from_path(directory_path)
    ndims = get_n_dims_from_path(directory_path)
    assert dimension < ndims, "queried dimension exceeds experiment space"
    files = glob.glob(directory_path+'/*/data/**.csv')
    files.sort(key = get_n_steps_from_filepath)

    n_steps = []
    variance = []
    mean = []

    for filepath in files:
        filename = filepath.split('/')[-1]
        nsteps = int(re.findall(r"\d+_steps",filename)[0].split('_')[0])
        rebuilt_dict = rebuild_counts_from_csv(filepath,n_dims=ndims,shots=nshots)
        stats = get_stats_from_counts_dict(rebuilt_dict)
        variance.append(stats['var'][dimension])
        mean.append(stats['mean'][dimension])
        n_steps.append(nsteps)

    return n_steps, variance, mean
     
