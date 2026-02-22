# Anomaly detection in process monitoring using prmon 

This project uses prmon and its built-in burner tests to generate synthetic system monitoring data with artificial anomalies.
It then applies ```IsolationForest``` from ```scikit-learn``` library and evaluates it.

# GitHub repository structure

├── generate.py              # process workload generator (uses prmon)
├── analysis.ipynb           # Data analysis and anomaly detection
├── report.pdf               # report
├── anomalies_csv.txt        # Ground-truth anomaly windows
├── dataset.csv              # Generated prmon dataset (optional)
├── requirements.txt         # list of dependencies
└── README.md

# Generating the Dataset with anomalies

Please run prmon while executing the workload generator:

prmon -i 0.5 -f dataset.csv-j summary.json -- python generate.py --samples <NSAMPLES> --contamination <CONTAMINATION_RATE>\
This generates:
- dataset.csv (time-series metrics)
- summary.json (aggregated metrics)
- anomalies_start.csv (ground-truth anomaly windows)

We used -i 0.5 as this makes prmon generate 1 data entry per second, otherwise it is 2 seconds for -i 1.

# Note on reproducibility
The results obtained are fully reproducible as all the seed set in Python code are fixed, so the output will be the same.

# Running anomaly detector

Open Jupyter Notebook:

jupyter notebook anomaly_detection.ipynb

This notebook will load ```dataset.csv``` from the same folder, will plot the data and visualize the anomalies.
Lastly, it evaluates statistical metrics, such as precision, recall and F1 score.

# Methodology used for the test

* Synthetic time series with anomalies is being generate using prmon and burner test + noise
* We created 3 anomaly types: memory, process and thread anomalies.
* We also run background load + noise to simulate background resource consumption.
* To detect anomalies for multivariate data series, we use ```IsolationForest```
* We evaluate the method applied using statistical methods and ratio of anomalies detected by ```IsolationForest```

# Short summary

```IsolationForest```'s performance is:
* Precision score: 74.5 %
* Recall score: 0.74
* F1 score: 74.25%
- Initial anomaly detection rate: 100% (15/15 anomalies detected as on the event level)

Detailed analysis is available is report.pdf.
All the information on the test is available in anomaly_detection.ipynb