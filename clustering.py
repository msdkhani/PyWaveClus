# clustering.py
# spclustering: Super Paramagnetic Clustering Wrapper
from spclustering import SPC, plot_temperature_plot
import yaml
import os

def load_clustering_config():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
        return config['clustering']

def SPC_clustering(features):
    config = load_clustering_config()
    min_clus = config['min_clus']
    plot_temperature = config['plot_temperature']

    clustering = SPC(mintemp=0, maxtemp=0.251)

    labels = {}
    metadata = {}

    for channel_id, feature in features.items():
        label, metadata[channel_id] = clustering.fit(feature, min_clus, return_metadata=True)
        labels[channel_id] = label

        if plot_temperature:
            plot_temperature_plot(metadata[channel_id])
            

    return labels, metadata
