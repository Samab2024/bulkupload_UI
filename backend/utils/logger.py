import logging
import os

def get_logger(run_id, log_dir):
logger = logging.getLogger(run_id)
logger.setLevel(logging.INFO)

log_file = os.path.join(log_dir, f"{run_id}.log")
handler = logging.FileHandler(log_file)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

if not logger.handlers:
logger.addHandler(handler)

return logger
