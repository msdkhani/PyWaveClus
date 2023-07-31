# main.py
import yaml
from spike_detection import detect_spikes, extract_waveforms
from feature_extraction import feature_extraction
from clustering import SPC_clustering
from artifacts_removal import artifacts_removal

def main():
    # Load your data and recording objects (recording_bp2, recording_bp4) here
    
    # Step 1: Spike Detection
    results = detect_spikes(recording, recording_bp2, recording_bp4)
    
    # Optional: Do artifact removal here - This part is not in the Waveclus pipeline
    filtered_results = artifacts_removal(results)

    # Step 2: Extract Waveforms
    waveforms = extract_waveforms(results, recording_bp2)

    # Step 3: Feature Extraction
    features = feature_extraction(waveforms)

    # Step 4: Clustering 
    labels, metadata = SPC_clustering(features)
    
    #Optional: do Clustering with artifacts removal results. You can compare the results to see the effect of artifacts removal
    #labels_filtered, metadata_filtered = SPC_clustering(features, filtered_results)


if __name__ == "__main__":
    main()
