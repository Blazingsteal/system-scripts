import yaml
import sys

file_to_validate = sys.argv[1]

print(f"Validating file: {file_to_validate}")

with open(file_to_validate, "r") as stream:
    try:
        yaml.safe_load(stream)
        print("Valid")
    except yaml.YAMLError as exc:
        print(exc)