from collections import defaultdict


def artifacts_removal(results, time_window=0.5):
    # Create a list to hold all spikes and their channel
    spike_list = []

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
        channels_in_window = [channel for channel, count in channel_counts.items() if count >= 6]
        if len(channels_in_window) >= 6 and spike_list[end][0] not in added_spike_times:
            # If 6 or more channels have spikes in the window and the spike time has not already been added, 
            # add the spike time and the channels to common_spikes
            common_spikes.append((spike_list[end][0], channels_in_window))
            added_spike_times.add(spike_list[end][0])
    
        # Convert common_spikes_times to set for faster 'in' operations
    common_spikes_times = set(spike_time for spike_time, channels in common_spikes)

    # Create a new dictionary
    filtered_results = {}

    # Loop over the results dictionary
    for key in results:
        spikes, indexes = results[key]['spikes'], results[key]['indexes']
        not_common_indices = [i for i, spike in enumerate(spikes) if spike not in common_spikes_times]

        # Add new arrays to the new dictionary
        filtered_results[key] = {
            'spikes': spikes[not_common_indices],
            'indexes': indexes[not_common_indices],
        }


    return filtered_results
