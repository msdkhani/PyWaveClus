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
What We Did in This Pipeline

In this package, we implemented a Python version of WaveClus, which uses the SPC algorithm for clustering. The main components of the pipeline are:

Spike Detection (pywaveclus.spike_detection):
Implemented a detect_spikes function that detects spikes from electrophysiological recordings.
Extracted waveforms for detected spikes using the extract_waveforms function.
Feature Extraction (pywaveclus.feature_extraction):
Created a modular approach to feature extraction using Haar wavelets and PCA.
Implemented the haar_feature_extraction and pca_feature_extraction functions.
Designed a unified feature_extraction function that selects the appropriate method based on configuration.
Clustering (pywaveclus.clustering):
Utilized the SPC algorithm from the SPC repository for clustering.
Implemented the SPC_clustering function to perform clustering on the extracted features.
Added options for plotting temperature maps if desired.
Configuration (config.yaml)

The pipeline's behavior can be customized using the config.yaml file, which contains configuration parameters for spike detection, feature extraction, and clustering. The configuration can be easily modified to suit your specific dataset and analysis requirements.

Feedback and Contributions

We welcome feedback and contributions to enhance PyWaveClus. If you encounter any issues, have suggestions, or want to contribute to the project, please feel free to submit an issue or pull request on our GitHub repository here.

Acknowledgments

This package relies on the SPC algorithm from SPC repository. We would like to thank the authors for providing this valuable contribution to the neuroscience community.

License

PyWaveClus is licensed under the MIT License. You are free to use, modify, and distribute the code under the terms of this license.
