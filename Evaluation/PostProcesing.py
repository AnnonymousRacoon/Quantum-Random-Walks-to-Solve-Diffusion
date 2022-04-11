import pandas as pd


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
    return results_dict
    



