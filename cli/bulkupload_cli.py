import argparse
from backend.core.bulk_runner import run_bulk_upload

parser = argparse.ArgumentParser()
parser.add_argument('--region', required=True)
parser.add_argument('--profile', required=True)
parser.add_argument('--csv', required=True)
args = parser.parse_args()

run_bulk_upload(args.region, args.profile, args.csv, "cli-run", "logs")
