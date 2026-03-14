# WORFLOW
1. Load baseline predictions from cluster "bernard" to local
      -> scp tibo990i@login1.barnard.hpc.tu-dresden.de:/home/tibo990i/Thesis_Repo/phase1_baseline/*parquet exp1\data\data_in
2. Transform predictions into datakit input format called "precomputed_profiles"
      -> EXECUTE: exp1\generate_opf_inputs\exp1_step2_transform_benchmark_to_datakit.ipynb
      -> OUTPUT:  exp1\data\precomputed_profiles\
      -> OPTIONAL: Load precomputed_profiles .csv files to google drive 
3. Run datakit
      -> EXECUTE ONCE PER BASELINE MODEL: gridfm_datakit generate .\exp1\config\case14_generate_opf_for_forecast.yaml
      -> OUTPUT: exp1\data\data_out
4. Compare AC-OPF results derived from predictions with ground truth
      -> READ AND EXECUTE: exp1\generate_metrics\compare.py
      -> OUTPUT: exp1\results\case118_horizon1_3yr2019-2021

# NOTES
1. Qd is not forecasted by baseline models -> derived by applying scaling factor to Pd


# Abstarct Description
Input: read in the predicted loads (which were predicted in Step 1 in the baseline approach)

PutPut: 
1. For each model. Take the predicted Loads, and transform into format, which can be fed into the datakit. in order to solve OPF
-> i THINK it is only about adding q_mvar, which can be retrieved just as scaling bus specific scalig factor (see generate_precomputed_profile.ipynb) 
2. Solve OPF for predicted loads
3. compute the same metrics as graphkit does

Output:
- for each model, output the metrics of 2-step approach

