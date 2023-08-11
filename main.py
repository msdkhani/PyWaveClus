from pywaveclus.waveclus import spike_sorting_pipeline

OUTPUT_FOLDER= '/'
PROJECT_NAME = 'test'


def main():
    bundle_dict = ...
    recording = ...
    recording_bp2 = ...
    recording_bp4 = ...
    
    spike_sorting_pipeline(recording, 
                       recording_bp2, 
                       recording_bp4, 
                       bundle_dict,
                       artifact_removal=True,
                       save_dir=f'{OUTPUT_FOLDER}/{PROJECT_NAME}/')
    
if __name__ == '__main__':
    main()