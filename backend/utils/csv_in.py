import csv

def parse_csv(csv_path):
with open(csv_path, newline='') as csvfile:
reader = csv.DictReader(csvfile)
return list(reader)
