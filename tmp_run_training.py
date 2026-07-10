from utils.model_training import run_training_pipeline

summary, report_path = run_training_pipeline()
print('SUMMARY')
print(summary.to_string(index=False))
print('REPORT', report_path)
