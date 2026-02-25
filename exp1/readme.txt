# Goal: Perform Step 2, in the 2-Step Baseline Approach

Input: read in the predicted loads (which were predicted in Step 1 in the baseline approach)

PutPut: 
1. For each model. Take the predicted Loads, and transform into format, which can be fed into the datakit. in order to solve OPF
-> i THINK it is only about adding q_mvar, which can be retrieved just as scaling bus specific scalig factor (see generate_precomputed_profile.ipynb) 
2. Solve OPF for predicted loads
3. compute the same metrics as graphkit does

Output:
- for each model, output the metrics of 2-step approach