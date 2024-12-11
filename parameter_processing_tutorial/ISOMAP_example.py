import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import os
import time
import itertools
import multiprocessing
import pickle
import sys

# ISOMAP
from sklearn.manifold import Isomap

from mpl_toolkits.mplot3d import Axes3D

##############################################################

num_cpu = int(sys.argv[1]) # number of CPUs to use for parallel processing

list_of_n_neighbors = [10,20,40,80]
list_of_dist_metrics = ['cosine','euclidean']
list_of_n_components = [2,3,6]

plot = True # set to True to plot and save the embeddings
troubleshoot_frames = None # number of frames to use for troubleshooting; None will use all frames
downsample_factor = 20 # downsample factor for troubleshooting 1 = no downsampling, 2 = every other frame, 3 = every third frame, etc.

data_directory = os.getcwd()
save_dir = '/home/haqqeez/scratch/ISOMAP_results/'

##############################################################

def plot_embeddings(embeddings, n_neighbors, dist_metric, n_components, save_dir):
    if n_components == 2:
        fig, ax = plt.subplots()
        ax.scatter(embeddings[:, 0], embeddings[:, 1], c='r', marker='o')
        ax.set_xlabel('ISOMAP 1')
        ax.set_ylabel('ISOMAP 2')
        plt.title(f'ISOMAP n_neighbors={n_neighbors}, dist_metric={dist_metric}, n_components={n_components}')
        plt.savefig(f'{save_dir}ISOMAP_n_neighbors-{n_neighbors}_dist_metric-{dist_metric}_n_components-{n_components}.png')
        plt.close()
    elif n_components == 3:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(embeddings[:, 0], embeddings[:, 1], embeddings[:, 2], c='r', marker='o')
        ax.set_xlabel('ISOMAP 1')
        ax.set_ylabel('ISOMAP 2')
        ax.set_zlabel('ISOMAP 3')
        plt.title(f'ISOMAP n_neighbors={n_neighbors}, dist_metric={dist_metric}, n_components={n_components}')
        plt.savefig(f'{save_dir}ISOMAP_n_neighbors-{n_neighbors}_dist_metric-{dist_metric}_n_components-{n_components}.png')
        plt.close()
    else:
        fig, axes = plt.subplots(n_components - 1, n_components - 1, figsize=(15, 15))
        for i in range(n_components):
            for j in range(i + 1, n_components):
                ax = axes[i, j - 1] if n_components > 2 else axes
                ax.scatter(embeddings[:, i], embeddings[:, j], c='r', marker='o')
                ax.set_xlabel(f'ISOMAP {i + 1}')
                ax.set_ylabel(f'ISOMAP {j + 1}')
        plt.suptitle(f'ISOMAP n_neighbors={n_neighbors}, dist_metric={dist_metric}, n_components={n_components}')
        plt.savefig(f'{save_dir}ISOMAP_n_neighbors-{n_neighbors}_dist_metric-{dist_metric}_n_components-{n_components}.png')
        plt.close()

def run_isomap(params, data_to_use, plot=False):
    n_neighbors, dist_metric, n_components = params
    print(f'Running ISOMAP with n_neighbors={n_neighbors}, dist_metric={dist_metric}, n_components={n_components}')

    analysis_start_time = time.time()

    # Get embeddings
    reducer = Isomap(n_neighbors=n_neighbors, n_components=n_components, metric=dist_metric)
    fit = reducer.fit(data_to_use)
    embeddings = fit.transform(data_to_use)

    analysis_end_time = time.time()
    time_taken = analysis_end_time - analysis_start_time
    print(f'Analysis took {time_taken:.2f} seconds ({time_taken/60:.2f} minutes)')
    result = (n_neighbors, dist_metric, n_components, time_taken)

    # Save embeddings as pandas dataframe
    embeddings_df = pd.DataFrame(embeddings)
    embeddings_df.to_csv(f'{save_dir}ISOMAP_n_neighbors-{n_neighbors}_dist_metric-{dist_metric}_n_components-{n_components}.csv')

    # Save fit object ### it can be very large! ###
    # with open(f'{save_dir}ISOMAP_n_neighbors={n_neighbors}_dist_metric={dist_metric}_n_components={n_components}_fit.pkl', 'wb') as f:
    #     pickle.dump(fit, f)
    
    if plot:
        plot_embeddings(embeddings, n_neighbors, dist_metric, n_components, save_dir)

    return result


if __name__ == '__main__':

    data_files = glob.glob(f'{data_directory}*/**/*deconv.csv', recursive=True)

    if len(data_files) > 1:
        print('Error: Too many files found')
        raise FileNotFoundError
    elif len(data_files) == 0:
        print('Error: File not found')
        raise FileNotFoundError

    data_file = data_files[0]
    data = pd.read_csv(data_file, index_col=0)
    print(f'Loaded data from {data_file}')

    # Filename looks kinda like : ZHA029_2021_10_30_1345_deconv.csv
    # NOTE It is much better practice to have a metadata file with this info, rather than getting it from the filename or path
    file_basename = os.path.basename(data_file)
    animalID = file_basename.split('_')[0]
    date = '-'.join(file_basename.split('_')[1:4])

    save_dir = f'{save_dir}/{animalID}/{date}/'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Generate all combinations of parameters
    parameter_combinations = list(itertools.product(list_of_n_neighbors, list_of_dist_metrics, list_of_n_components))
    print(f'Number of combinations: {len(list(parameter_combinations))}')

    # downsample for troubleshooting
    data_to_use = data.iloc[0:troubleshoot_frames, :].values # use only the first 5000 frames for troubleshooting
    data_to_use = data_to_use[::downsample_factor, :] # downsample data

    print(f'Data Shape: {data_to_use.shape[1]} cells by {data_to_use.shape[0]} frames')

    # Run ISOMAP analysis
    results = []

    print(f'Using {num_cpu} CPUs for parallel processing')
    with multiprocessing.Pool(num_cpu) as pool:
        results = pool.starmap(run_isomap, [(params, data_to_use, plot) for params in parameter_combinations])

    # Save runtime results
    results_df = pd.DataFrame(results, columns=['n_neighbors', 'dist_metric', 'n_components', 'time_taken'])
    results_df.to_csv(f'{save_dir}/ISOMAP_runtime_results.csv')

    # Print summary
    print("\nSummary of analysis times:")
    for n_neighbors, dist_metric, n_components, time_taken in results:
        print(f'n_neighbors={n_neighbors}, dist_metric={dist_metric}, n_components={n_components}: {time_taken:.2f} seconds ({time_taken/60:.2f} minutes)')

    print(f'\nResults saved in {save_dir}')
    print('Done!')

        
