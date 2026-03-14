# WORKFLOW

1. Generate datakit input
        -> INPUT: realistic load profiles .parquet (from marcus)
        -> EXECUTE: 
                - Leipzig Cluster: phase1_generation\preprocessing\generate_precomputed_profile.py
                - Local: phase1_generation\preprocessing\generate_precomputed_profile.ipynb
        -> OUTPUT: phase1_generation\preprocessing\\*_precomputed_load_profiles.csv

2. Run datakit
        -> EXECUTE: phase1_generation\configs\phase1_config.yaml
        -> OUTPUT: .\data_out 


3. Generate Baseline Predictions
        -> TRANSFER: data to cluster bernard 
        -> RUN: Code in git repo: Thesis_Repo
