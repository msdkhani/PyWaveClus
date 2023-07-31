# spike_detection.py
import math
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from spikeinterface import ChannelSliceRecording
from scipy.interpolate import splev, splrep
import yaml
import os

def load_spike_detection_config():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
        return config['spike_detection']


def detect_spikes(recording, recording_bp2, recording_bp4):
    """Detects spikes from a given recording and all channels.

    Args:
        recording: The recording object to process.
        detect: The detection method ('neg', 'pos', 'both'). Default is 'neg'.
        segment_duration: Duration of each segment in seconds. Default is 5 minutes.
        stdmin: Threshold factor for detection. Default is 5.
        stdmax: Threshold factor for artifact removal. Default is 50.
        w_pre: Pre-event window size.
        w_post: Post-event window size.
        min_ref_per: Minimum refractory period in milliseconds. Default is 1.5.

    Returns:
        results: A dictionary where the keys are the channel ids, and the values are
                  another dictionary with the keys 'spikes', 'thresholds' and 'indexes'.
    """
    config = load_spike_detection_config()
    detect = config['detect_method']
    segment_duration = config['segment_duration'] * 60
    stdmin = config['std_min']
    stdmax = config['std_max']
    w_pre = config['w_pre']
    w_post = config['w_post']
    min_ref_per = config['min_ref_per']
    
    total_duration = recording_bp4.get_num_frames() / recording_bp4.get_sampling_frequency()
    num_segments = math.ceil(total_duration / segment_duration)

    sr = recording_bp4.get_sampling_frequency()
    ref = int(min_ref_per * sr / 1000)
    sample_ref = np.floor(ref/2)
    channel_ids = recording.get_channel_ids()
    results = {}

    def process_channel(channel_id):
        sub_recording_bp4 = ChannelSliceRecording(recording_bp4, [channel_id])
        sub_recording_bp2 = ChannelSliceRecording(recording_bp2, [channel_id])

        all_spikes = []
        thresholds = []
        indexes = []

        for segment_index in range(num_segments):
            start_time = segment_index * segment_duration
            end_time = min((segment_index + 1) * segment_duration, total_duration)

            trace_bp4 = sub_recording_bp4.get_traces(start_frame=int(start_time * sr), end_frame=int(end_time * sr))
            trace_bp2 = sub_recording_bp2.get_traces(start_frame=int(start_time * sr), end_frame=int(end_time * sr))

            thr = stdmin * np.median(np.abs(trace_bp4)) / 0.6745
            thrmax = stdmax * thr 
            if detect == 'neg':
                xaux = np.where((trace_bp4[w_pre + 2: -w_post - 2 - int(sample_ref)] < -thr))[0] + w_pre + 1
            elif detect == 'pos':
                xaux = np.where((trace_bp4[w_pre + 2: -w_post - 2 - int(sample_ref)] > thr))[0] + w_pre + 1
            elif detect == 'both':
                xaux = np.where((np.abs(trace_bp4[w_pre + 2: -w_post - 2 - int(sample_ref)]) > thr))[0] + w_pre + 1
            else:
                raise ValueError(f"Invalid value {detect} for argument 'detect'. Must be 'neg', 'pos', or 'both'.")

            xaux0 = 0
            index = []
            for i in range(len(xaux)):
                if xaux[i] >= xaux0 + ref:
                    iaux = np.argmin(trace_bp2[xaux[i]: xaux[i] + int(sample_ref)-1])
                    # Check and eliminate artifacts
                    if np.max(np.abs(trace_bp2[xaux[i] - w_pre: xaux[i] + w_post])) < thrmax:
                        index.append(iaux + xaux[i])
                        xaux0 = index[-1]

            spike_times = (np.array(index) / sr + start_time) * 1000

            all_spikes.extend(spike_times)
            indexes.extend(index)
            thresholds.append(thr)

        return {'spikes': np.array(all_spikes), 'thresholds': np.array(thresholds), 'indexes': np.array(indexes)}

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        # Submit tasks for each channel to the ThreadPoolExecutor
        futures = [executor.submit(process_channel, channel_id) for channel_id in channel_ids]

        # Collect the results for each channel as they become available
        results = {channel_id: future.result() for channel_id, future in zip(channel_ids, futures)}

    return results
