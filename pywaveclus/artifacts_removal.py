from collections import defaultdict


def artifacts_removal(results, bundle_name,time_window=0.5):
    
    # Create a list to hold all spikes and their channel
    spike_list = []
    common_spikes_times = {}
    # Iterate over dictionary and store all spikes in spike_list
    for key in results:
        for spike_time in results[key]['spikes']:
            spike_list.append((spike_time, key))

    # Sort the list by spike times
    spike_list.sort(key=lambda x: x[0])

    # Create a defaultdict to hold the spike counts for each channel in the window
    channel_counts = defaultdict(int)

    # Initialize a list to hold the spike times that occur in 6 or more channels within the time window
    common_spikes = []

    # Initialize the start of the window
    start = 0

    # Initialize a set to keep track of spike times that have already been added to common_spikes
    added_spike_times = set()

    # Iterate over the spike_list
    for end in range(len(spike_list)):
        # Add the channel to the channel_counts
        channel_counts[spike_list[end][1]] += 1
        # Check if the spike time at the end of the window is within the time window from the start of the window
        while spike_list[end][0] - spike_list[start][0] > time_window:
            # If it's not, move the start of the window forward
            channel_counts[spike_list[start][1]] -= 1
            start += 1
        # After moving the start, check the total number of channels in the window
        channels_in_window = [channel for channel, count in channel_counts.items() if count >= 1]
        if len(channels_in_window) >= 6 and spike_list[end][0] not in added_spike_times:
            # If 6 or more channels have spikes in the window and the spike time has not already been added, 
            # add the spike time and the channels to common_spikes
            common_spikes.append((spike_list[end][0], channels_in_window))
            added_spike_times.add(spike_list[end][0])
        # Convert common_spikes_times to set for faster 'in' operations
    common_spikes_times[bundle_name] = set(spike_time for spike_time, channels in common_spikes)
    # Create a new dictionary
    filtered_results = {}

    # Loop over the results dictionary
    for key in results:
        spikes, indexes = results[key]['spikes'], results[key]['indexes']
        not_common_indices = [i for i, spike in enumerate(spikes) if spike not in common_spikes_times[bundle_name]]

        # Add new arrays to the new dictionary
        filtered_results[key] = {
            'spikes': spikes[not_common_indices],
            'indexes': indexes[not_common_indices],
        }
    return filtered_results, common_spikes_times


def artifacts_removal_for_bundle(results,bundle_dict):
    """
    Perform artifacts removal for each bundle in the results.

    Args:
        bundle_dict (dict): A dictionary with bundle names as keys and their corresponding channel information as values.
                           Example: {'mLAMY': [{'channel_id': 257, 'label': 'mLAMY01 raw'}]}
        results (dict): A dictionary containing the spike detection results for each channel.
        time_window (float): Time window in seconds to consider for artifacts removal. Default is 0.5 seconds.

    Returns:
        dict: A dictionary containing the filtered spike detection results after artifacts removal for each bundle.
    """

    # Create a dictionary to hold the results after artifacts removal for each bundle
    filtered_results_for_bundle = {}
    common_spikes = {}

    for bundle_name, channel_info_list in bundle_dict.items():
        # Create a new dictionary for this bundle
        bundle_results = {}

        # Filter the results for channels in the current bundle
        bundle_channels = [info['channel_id'] for info in channel_info_list]
        if len(bundle_channels)<=6:
            return results
        
        #bundle_results = {channel_id: results[channel_id] for channel_id in bundle_channels if channel_id in results}
        import copy

        # Inside the loop
        bundle_results = {channel_id: copy.deepcopy(results[channel_id]) for channel_id in bundle_channels if channel_id in results}

        # Perform artifacts removal for this bundle's results
        filtered_bundle_results,common_spikes_times = artifacts_removal(bundle_results, bundle_name)

        # Update the filtered results for the bundle
        filtered_results_for_bundle.update(filtered_bundle_results)
        common_spikes.update(common_spikes_times)
    
    return filtered_results_for_bundle,common_spikes
