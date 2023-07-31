import yaml
import numpy as np
from scipy.interpolate import splrep, splev
import os 

def load_waveform_extraction_config(config_file='config.yaml'):
    """Load waveform extraction configuration from a YAML file.

    Args:
        config_file (str): Path to the YAML configuration file. Default is 'config.yaml'.

    Returns:
        dict: A dictionary containing the waveform extraction configuration parameters.
    """
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
        return config['extract_waveform']


def extract_waveforms(results, recording_bp2, config_file='config.yaml'):
    """Extracts waveforms for detected spikes in all channels.

    Args:
        results (dict): A dictionary containing the spike detection results for each channel.
                        It can also be a single-channel result in the form of a dictionary.
        recording_bp2: The recording object for the channels' bandpass 2 data.
        config_file (str): Path to the YAML configuration file. Default is 'config.yaml'.

    Returns:
        dict: A dictionary where keys are the channel ids, and values are the extracted waveforms for detected spikes in each channel.
    """

    config = load_waveform_extraction_config(config_file)
    detect = config.get('detect_method', 'neg')
    w_pre = config.get('w_pre', 20)
    w_post = config.get('w_post', 44)
    int_factor = config.get('int_factor', 5)

    spikes_waveforms = {}
    for channel_id, result in results.items():
        spikes_waveforms[channel_id] = extract_waveforms_for_channel(result, recording_bp2, channel_id, detect, w_pre, w_post, int_factor)

    return spikes_waveforms


def extract_waveforms_for_channel(result, recording_bp2, channel_id, detect, w_pre, w_post, int_factor):
    spikes_times = result['spikes']
    indexes = result['indexes']

    xf = recording_bp2.get_traces(channel_ids=[channel_id], start_frame=0, end_frame=recording_bp2.get_num_frames())

    ls = w_pre + w_post
    nspk = len(spikes_times)
    spikes = np.zeros((nspk, ls + 4))

    indices = np.arange(-w_pre - 2, w_post + 2) + indexes[:, np.newaxis]
    spikes = np.take(xf, indices, axis=0).reshape(nspk, -1)

    extra = (spikes.shape[1] - ls) // 2
    s = np.arange(spikes.shape[1])
    ints = np.arange(0, spikes.shape[1], 1 / int_factor)
    spikes_waveforms = np.zeros((nspk, ls))

    if nspk > 0:
        intspikes = np.empty((nspk, len(ints)))
        for i in range(nspk):
            tck = splrep(s, spikes[i, :])
            intspikes[i, :] = splev(ints, tck)

        if detect == 'pos':
            iaux = intspikes[:, int((w_pre+extra-1)*int_factor):int((w_pre+extra+1)*int_factor)].argmax(axis=1)
        elif detect == 'neg':
            iaux = intspikes[:, int((w_pre+extra-1)*int_factor):int((w_pre+extra+1)*int_factor)].argmin(axis=1)
        elif detect == 'both':
            iaux = np.abs(intspikes[:, int((w_pre+extra-1)*int_factor):int((w_pre+extra+1)*int_factor)]).argmax(axis=1)

        iaux = iaux + (w_pre+extra-1)*int_factor - 1

        for i in range(nspk):
            spikes_waveforms[i, :] = intspikes[i, int(iaux[i]-w_pre*int_factor+int_factor):int(iaux[i]+w_post*int_factor+1):int_factor]

    return spikes_waveforms
