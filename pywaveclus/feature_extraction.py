# feature_extraction.py
import numpy as np
import pywt
from sklearn.decomposition import PCA
from statsmodels.stats.diagnostic import lilliefors
import yaml
import os 

def load_feature_extraction_config():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
        return config['feature_extraction']
    
    
def haar_feature_extraction(spikes, level=4, ls=20+44, max_inputs=np.ceil(0.75 * 64), min_inputs=10, nd=10):
    features = {}
    for channel, spike_waveforms in spikes.items():
        features[channel] = haar_feature_extraction_for_channel(spike_waveforms, level, ls, max_inputs, min_inputs, nd)
    return features

def haar_feature_extraction_for_channel(spikes, level, ls, max_inputs, min_inputs, nd):
    nspk = len(spikes)
    # Determine the number of coefficients based on the desired level and the length of the original data
    # Create a 2D array 'cc' to store the wavelet coefficients for each spike
    cc = np.zeros((nspk, ls))

    for i in range(nspk):
        c = pywt.wavedec(spikes[i], 'haar', level=level)
        flattened_coeffs = np.hstack(c)[:ls]
        cc[i, :len(flattened_coeffs)] = flattened_coeffs
        
    ls = cc.shape[1]      
    ks = np.zeros(ls)

    for i in range(ls):
        thr_dist = np.std(cc[:, i]) * 3
        thr_dist_min = np.mean(cc[:, i]) - thr_dist
        thr_dist_max = np.mean(cc[:, i]) + thr_dist
        aux = cc[(cc[:, i] > thr_dist_min) & (cc[:, i] < thr_dist_max), i]

        if len(aux) > 10:
            ks[i] = lilliefors(aux, dist='norm', pvalmethod='table')[0]
        else:
            ks[i] = 0

    sorted_indices = np.argsort(ks)
    ind = sorted_indices[::]
    A = ks[sorted_indices][int(-max_inputs):]
    ncoeff = len(A)
    maxA = np.max(A)
    d = ((A[nd-1:] - A[:-nd+1]) / maxA) * (ncoeff / nd)
    all_above1 = np.where(d >= 1)[0]
    
    if len(all_above1) >= 2:
        aux2 = np.diff(all_above1)
        temp_bla = np.convolve(aux2, np.array([1, 1, 1]) / 3)
        temp_bla = temp_bla[1:len(aux2)-1]
        temp_bla[0] = aux2[0]
        temp_bla[-1] = aux2[-1]

        thr_knee_diff = all_above1[np.where(temp_bla[1:] == 1)[0][0]] + (nd / 2)
        inputs = max_inputs - thr_knee_diff 
    else:
        inputs = min_inputs

    if inputs > max_inputs:
        inputs = max_inputs
    elif inputs < min_inputs:
        inputs = min_inputs
        
    coeff = ind[-int(inputs):]
    inspk = np.zeros((nspk, int(inputs)))

    for i in range(nspk):
        for j in range(int(inputs)):
            inspk[i, j] = cc[i, coeff[j]]

    return inspk


def pca_feature_extraction(spikes, n_components):
    features = {}
    for channel, spike_waveforms in spikes.items():
        features[channel] = pca_feature_extraction_for_channel(spike_waveforms, n_components)
    return features

def pca_feature_extraction_for_channel(spikes, n_components=10):
    nspk = spikes.shape[0]
    pca = PCA(n_components=n_components)
    S = pca.fit_transform(spikes)
    C = pca.components_
    cc_pca = S
    coeff_pca = np.arange(0, S.shape[1] + 1)
    inputs = n_components
    inspk_pca = np.zeros((nspk, inputs))

    for i in range(nspk):
        for j in range(inputs):
            inspk_pca[i, j] = cc_pca[i, coeff_pca[j]]

    return inspk_pca

def feature_extraction(waveforms):
    config = load_feature_extraction_config()
    method = config['method']

    if method == 'haar':
        level = config['haar_level']
        ls = config['haar_ls']
        max_inputs = config['haar_max_inputs']
        min_inputs = config['haar_min_inputs']
        nd = config['haar_nd']
        return haar_feature_extraction(waveforms, level, ls, max_inputs, min_inputs, nd)
        
    elif method == 'pca':
        n_components = config['pca_n_components']
        return pca_feature_extraction(waveforms, n_components)
    else:
        raise ValueError(f"Invalid value {method} for argument 'method'. Must be 'haar' or 'pca'.")