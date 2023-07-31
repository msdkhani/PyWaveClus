# PyWaveClus: Python Spike Detection and Clustering

PyWaveClus is a Python package for spike detection, feature extraction, and clustering in neuroscience data. It utilizes the SPC (Spike-phase clustering) algorithm from the [SPC repository](https://github.com/ferchaure/SPC) for clustering.

## Overview

This package provides a streamlined pipeline for analyzing electrophysiological data commonly used in neuroscience research. The pipeline consists of the following main steps:

1. **Spike Detection**: Detecting spikes from the input electrophysiological recording using wavelet-based thresholding.

2. **Feature Extraction**: Extracting relevant features from the detected spikes to prepare them for clustering.

3. **Clustering**: Performing clustering on the extracted features using the SPC algorithm.

## Installation

You can install PyWaveClus using pip:

```bash
pip install pywaveclus
```

## Getting Start
Here's a brief overview of how to use PyWaveClus in your project:

```python
import pywaveclus.spike_detection as sd
import pywaveclus.feature_extraction as fe
import pywaveclus.clustering as clu

# Load your electrophysiological recording
# (recordings_bp2, recording_bp4 should be initialized with the appropriate data)
recording = ...  # Your spikeinterface recording object
recording_bp2 = ...  # Preprocessed recording (bandpass 2)
recording_bp4 = ...  # Preprocessed recording (bandpass 4)

# Step 1: Spike Detection
spike_detection_results = sd.detect_spikes(recording, recording_bp2, recording_bp4)

# Step 2: Feature Extraction
spikes_waveforms = sd.extract_waveforms(spike_detection_results, recording_bp2)
features = fe.feature_extraction(spikes_waveforms)

# Step 3: Clustering
labels, metadata = clu.SPC_clustering(features)

# Further analysis and visualization of clustering results can be done here
```
#What We Did in This Pipeline

In this package, we implemented a Python version of WaveClus, which uses the SPC algorithm for clustering. The main components of the pipeline are:

# Spike Detection (pywaveclus.spike_detection):
Implemented a detect_spikes function that detects spikes from electrophysiological recordings.
Extracted waveforms for detected spikes using the extract_waveforms function.
# Feature Extraction (pywaveclus.feature_extraction):
Created a modular approach to feature extraction using Haar wavelets and PCA.
Implemented the haar_feature_extraction and pca_feature_extraction functions.
Designed a unified feature_extraction function that selects the appropriate method based on configuration.
# Clustering (pywaveclus.clustering):
Utilized the SPC algorithm from the SPC repository for clustering.
Implemented the SPC_clustering function to perform clustering on the extracted features.
Added options for plotting temperature maps if desired.

# Configuration (config.yaml)
The pipeline's behavior can be customized using the config.yaml file, which contains configuration parameters for spike detection, feature extraction, and clustering. The configuration can be easily modified to suit your specific dataset and analysis requirements.

# Feedback and Contributions

We welcome feedback and contributions to enhance PyWaveClus. If you encounter any issues, have suggestions, or want to contribute to the project, please feel free to submit an issue or pull request on our GitHub repository here.

# Acknowledgments
This package relies on the SPC algorithm from SPC repository. We would like to thank the authors for providing this valuable contribution to the neuroscience community.


## Citations
### Original SPC 
Blatt, M., Wiseman, S., & Domany, E. (1996). Superparamagnetic clustering of data. Physical review letters, 76(18), 3251.


### Cluster Selection
#### Waveclus 1 (WC1)

Quian Quiroga R, Nadasdy Z, Ben-Shaul Y. Unsupervised spike detection and sorting with wavelets and superparamagnetic clustering. Neural computation 16: 1661–1687, 2004.

#### Waveclus 3 (WC3)

Chaure FJ, Rey HG, Quian Quiroga R. A novel and fully automatic spike sorting implementation with variable number of features. J Neurophysiol , 2018. doi:10.1152/jn.00339.2018.

### Bibtex
```bibtex
@article{spc,
  title={Superparamagnetic clustering of data},
  author={Blatt, Marcelo and Wiseman, Shai and Domany, Eytan},
  journal={Physical review letters},
  volume={76},
  number={18},
  pages={3251},
  year={1996},
  publisher={APS}
}

@article{WC1,
	title = {Unsupervised spike detection and sorting with wavelets and superparamagnetic clustering},
	volume = {16},
	number = {8},
	journal = {Neural computation},
	author = {Quian Quiroga, R and Nadasdy, Zoltan and Ben-Shaul, Yoram},
	year = {2004},
	pages = {1661--1687},
	file = {48b6995f327440100e0d7382ff2652c17c6f.pdf:I\:\\My Drive\\zotero\\storage\\GXTC9KF8\\48b6995f327440100e0d7382ff2652c17c6f.pdf:application/pdf},
}

@article{WC3,
	title = {A novel and fully automatic spike sorting implementation with variable number of features},
	issn = {1522-1598},
	doi = {10.1152/jn.00339.2018},
	journal = {Journal of Neurophysiology},
	author = {Chaure, Fernando Julian and Rey, Hernan Gonzalo and Quian Quiroga, Rodrigo},
	month = jul,
	year = {2018},
	pmid = {29995603},
	keywords = {neurophysiology, single-neuron recordings, spike sorting, tetrode}
}
```
