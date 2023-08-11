import scipy.io as sio
import numpy as np
# WaveClus imports
from WaveClus.pywaveclus.spike_detection import detect_spikes
from WaveClus.pywaveclus.artifacts_removal import artifacts_removal_for_bundle
from WaveClus.pywaveclus.feature_extraction import feature_extraction
from WaveClus.pywaveclus.waveform_extraction import extract_waveforms
from WaveClus.pywaveclus.clustering import SPC_clustering
import os
import yaml

import multiprocessing
import concurrent.futures



def spike_sorting_pipeline(recording, recording_bp2, recording_bp4, bundle_dict,artifact_removal=False, save_dir=None):
    """
    Perform the spike sorting pipeline.

    Parameters:
        recording (ndarray): Raw recording data.
        recording_bp2 (ndarray): Recording data after bandpass filter at 2Hz.
        recording_bp4 (ndarray): Recording data after bandpass filter at 4Hz.
        bundle_dict (dict): Dictionary containing parameters for artifacts removal.
    
    Save:

    Returns:
        None
    """
    # Step 1: Spike Detection
    print('start spike detection...')
    spike_detection_results = detect_spikes(recording, recording_bp2, recording_bp4)
    print('end spike detection!')
    # Step 3: Extract Waveforms
    print('start extract waveforms...')
    waveforms = extract_waveforms(spike_detection_results, recording_bp2)
    print('end extract waveforms!')
    if artifact_removal:
        # Step 2: Artifact Removal
        print('start artifact removal...')
        filtered_results,artifacts_times = artifacts_removal_for_bundle(spike_detection_results,bundle_dict)
        print('end artifact removal!')
        # Create a dictionary to store the filtered waveforms
        filtered_waveforms = extract_waveforms(filtered_results, recording_bp2)
        features = feature_extraction(filtered_waveforms)
        print('start clustering...')
        # Step 5: Clustering
        labels, metadata = SPC_clustering(features)
        print('end clustering!')
        # Save data for each channel in a separate MATLAB file
        for channel_id in labels.keys():
            save_channel_data_to_mat_artifact(recording,channel_id, spike_detection_results, filtered_results,waveforms,filtered_waveforms,features, labels, save_dir=save_dir)


    else:
        # Step 4: Feature Extraction
        print('start feature extraction')
        features = feature_extraction(waveforms)
        print('end feature extraction')
        
        print('start clustering')
        # Step 5: Clustering

        labels, metadata = SPC_clustering(features)
        
        print('end clustering')
        # Save data for each channel in a separate MATLAB file
        for channel_id in labels.keys():
            save_channel_data_to_mat(recording,channel_id, spike_detection_results, waveforms, features, labels, save_dir=save_dir)




# This function add removed spikes that was detected as an artifact to the spike_time_label_mapping
def add_missing_spikes(channel_id, spike_detection_results, filtered_results, spike_time_label_mapping):
    # Create a set of all the spikes from spike_detection_results
    all_spikes_set = set(spike_detection_results[channel_id]['spikes'])

    # Create a set of all the spikes present in spike_time_label_mapping
    existing_spikes_set = set(spike for _, spike in spike_time_label_mapping)

    # Find the missing spikes using set difference
    missing_spikes = all_spikes_set - existing_spikes_set

    # Create a list with label 500 for the missing spikes
    missing_spikes_list = [(500, spike) for spike in missing_spikes]

    # Extend the original spike_time_label_mapping with the missing spikes
    spike_time_label_mapping.extend(missing_spikes_list)
    spike_time_label_mapping.sort(key=lambda x: x[1])

    return spike_time_label_mapping



def create_mappings(spike_detection_results, waveforms, features, labels, channel_id):
    """
    Create mappings for different data combinations.

    Parameters:
        spike_detection_results (dict): Dictionary containing spike detection results.
        waveforms (dict): Dictionary containing waveforms data.
        features (dict): Dictionary containing feature data.
        labels (dict): Dictionary containing clustering labels.
        channel_id (int): ID of the current channel.

    Returns:
        tuple: Tuple containing spike_time_waveform_mapping, waveform_feature_mapping,
               label_feature_mapping, and spike_time_label_mapping.
    """
    spike_time_waveform_mapping = [(spike_detection_results[channel_id]['spikes'][i], waveforms[channel_id][i]) for i in range(len(spike_detection_results[channel_id]['spikes']))]
    waveform_feature_mapping = [(waveforms[channel_id][i], features[channel_id][i]) for i in range(len(waveforms[channel_id]))]
    label_feature_mapping = [(labels[channel_id][i], features[channel_id][i]) for i in range(len(labels[channel_id]))]
    spike_time_label_mapping = [(labels[channel_id][i],spike_detection_results[channel_id]['spikes'][i]) for i in range(len(spike_detection_results[channel_id]['spikes']))]
    
    return spike_time_waveform_mapping, waveform_feature_mapping, label_feature_mapping, spike_time_label_mapping


# def save_waveforms_to_npy(waveforms, labels, channel_id,save_dir):
#     waveforms_per_label = {}
#     for label, waveform in zip(labels, waveforms):
#         if label not in waveforms_per_label:
#             waveforms_per_label[label] = []
#         waveforms_per_label[label].append(waveform)
        
#     save_dir = os.path.join(save_dir, f'wf_ch_{channel_id}')
#     save_dir = os.path.join(save_dir, 'waveforms')
    
#     os.makedirs(save_dir, exist_ok=True)
#     for label, waveforms_list in waveforms_per_label.items():

#         file_name = f'{save_dir}/waveforms_{label}.npy'
#         np.save(file_name, np.array(waveforms_list))
#         print(f"Waveforms for label {label} saved to {file_name}")
        
    
        

def save_channel_data_to_mat(recording,channel_id, spike_detection_results, waveforms, features, labels, save_dir):
    """
    Save data for each channel in a separate MATLAB file.

    Parameters:
        channel_id (int): ID of the current channel.
        spike_detection_results (dict): Dictionary containing spike detection results.
        waveforms (dict): Dictionary containing waveforms data.
        features (dict): Dictionary containing feature data.
        labels (dict): Dictionary containing clustering labels.

    Returns:
        None
    """
    spike_time_waveform_mapping, waveform_feature_mapping, label_feature_mapping, spike_time_label_mapping = create_mappings(spike_detection_results, waveforms, features, labels, channel_id)
    
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    spike_time_label_mapping = [(9999 if labels[channel_id][i] == 0 else labels[channel_id][i], spike_detection_results[channel_id]['spikes'][i]) for i in range(len(spike_detection_results[channel_id]['spikes']))]
    config['sr'] = recording.get_sampling_frequency()
    data_dict = {
        'Spike_Time': spike_detection_results[channel_id]['spikes'],
        'spikes': waveforms[channel_id],
        'inspk': features[channel_id],
        'Label': labels[channel_id],
        'Spike_Time_Waveform': spike_time_waveform_mapping,
        'Waveform_Feature': waveform_feature_mapping,
        'Label_Feature': label_feature_mapping,
        'cluster_class': spike_time_label_mapping,
        'par': config
    }



    save_dir = os.path.join(save_dir, 'sorting')
    save_dir = os.path.join(save_dir, 'waveclus')
    save_dir = os.path.join(save_dir, 'output')
    
    os.makedirs(save_dir, exist_ok=True)

    
    file_name = f'{save_dir}/channel_{channel_id}_data.mat'
    sio.savemat(file_name, data_dict)
    print(f"Data for channel {channel_id} saved to {file_name}")
    
    #save_waveforms_to_npy(waveforms[channel_id], labels[channel_id], channel_id,save_dir)

def create_mappings_artifact(spike_detection_results,filtered_spikes, waveforms, filtered_waveform,features, labels, channel_id):
    """
    Create mappings for different data combinations.

    Parameters:
        spike_detection_results (dict): Dictionary containing spike detection results.
        waveforms (dict): Dictionary containing waveforms data.
        features (dict): Dictionary containing feature data.
        labels (dict): Dictionary containing clustering labels.
        channel_id (int): ID of the current channel.

    Returns:
        tuple: Tuple containing spike_time_waveform_mapping, waveform_feature_mapping,
               label_feature_mapping, and spike_time_label_mapping.
    """
    spike_time_waveform_mapping = [(spike_detection_results[channel_id]['spikes'][i], waveforms[channel_id][i]) for i in range(len(spike_detection_results[channel_id]['spikes']))]
    waveform_feature_mapping = [(filtered_waveform[channel_id][i], features[channel_id][i]) for i in range(len(filtered_waveform[channel_id]))]
    label_feature_mapping = [(labels[channel_id][i], features[channel_id][i]) for i in range(len(labels[channel_id]))]
    spike_time_label_mapping = [(labels[channel_id][i],filtered_spikes[channel_id]['spikes'][i]) for i in range(len(filtered_spikes[channel_id]['spikes']))]
    # Call the function to add missing spikes with label 500 for the specified channel_id

    
    return spike_time_waveform_mapping, waveform_feature_mapping, label_feature_mapping, spike_time_label_mapping


def save_channel_data_to_mat_artifact(recording,channel_id, spike_detection_results, filtered_spikes,waveforms, filtered_waveform,features, labels, save_dir):
    """
    Save data for each channel in a separate MATLAB file.

    Parameters:
        channel_id (int): ID of the current channel.
        spike_detection_results (dict): Dictionary containing spike detection results.
        waveforms (dict): Dictionary containing waveforms data.
        features (dict): Dictionary containing feature data.
        labels (dict): Dictionary containing clustering labels.

    Returns:
        None
    """
    spike_time_waveform_mapping, waveform_feature_mapping, label_feature_mapping, spike_time_label_mapping = create_mappings_artifact(spike_detection_results,filtered_spikes, waveforms, filtered_waveform,features, labels, channel_id)
    
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    spike_time_label_mapping = [(1000 if labels[channel_id][i] == 0 else labels[channel_id][i], filtered_spikes[channel_id]['spikes'][i]) for i in range(len(filtered_spikes[channel_id]['spikes']))]
    spike_time_label_mapping = add_missing_spikes(channel_id, spike_detection_results, filtered_spikes, spike_time_label_mapping)
    labels_only = [item[0] for item in spike_time_label_mapping]
    config['sr'] = recording.get_sampling_frequency()
    data_dict = {
        'Spike_Time': spike_detection_results[channel_id]['spikes'],
        'spikes': waveforms[channel_id],
        'inspk': features[channel_id],
        'Label': labels_only,
        'Spike_Time_Waveform': spike_time_waveform_mapping,
        'Waveform_Feature': waveform_feature_mapping,
        'Label_Feature': label_feature_mapping,
        'cluster_class': spike_time_label_mapping,
        'par': config
    }



    save_dir = os.path.join(save_dir, 'sorting')
    
    os.makedirs(save_dir, exist_ok=True)

    
    file_name = f'{save_dir}/channel_{channel_id}_data.mat'
    sio.savemat(file_name, data_dict)
    print(f"Data for channel {channel_id} saved to {file_name}")
    
    #save_waveforms_to_npy(waveforms[channel_id], labels[channel_id], channel_id,save_dir)

# Example Usage:
# Assuming you have the required inputs, recording, recording_bp2, recording_bp4, and bundle_dict
# spike_sorting_pipeline(recording, recording_bp2, recording_bp4, bundle_dict,save_dir)
