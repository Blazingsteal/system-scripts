"""Count files
This script counts files in directories and outputs their disk usage and # files.
Various flags can be set to change the output of the script."""
import subprocess as sp
import sys
import os
import datetime

TOTAL_FILES = 0
TOTAL_GB = 0
TOTAL_MB = 0

DIRECTORIES = []
FILES = []

OPTIONS = ["-t", "-T", "--triple", "-i", "--ignore", "-h", "-H", "--help"]
OPTIONS_FLAGS = {"Triplets": False, "Ignore": False}
OPTIONS_HELP_TEXT = {
    "-t": "{:>5}{:>3} {:<10}\tPrint triplets (files/3)".format(OPTIONS[0], OPTIONS[1], OPTIONS[2]),
    "-i": "{:>5}{:>3} {:<10}\tIgnore non-directories if present in args".format(OPTIONS[3], "", OPTIONS[4]),
    "-h": "{:>5}{:>3} {:<10}\tDisplay this help and exit".format(OPTIONS[-3], OPTIONS[-2], OPTIONS[-1])
}


def count_files(directory):
    """
    Count files in a given directory
    Ignores directories/files with insufficient permissions
    Parameters:
    directory: The wanted directory to count files in.
    """
    global TOTAL_FILES
    cmd = "find {} -type f 2>/dev/null | wc -l".format(directory)
    ret_val = sp.run(["/bin/bash", "-c", cmd], capture_output=True, check=False)
    if ret_val.returncode == 0:
        output = ret_val.stdout.decode("utf-8").split("\n")[0]
        TOTAL_FILES += int(output)
        return int(output)
    return None


def get_size(path):
    """
    Get the size of the given path
    Ignores directories/files with insufficient permissions
    Parameters:
    path: Path to directory or file to get size of
    """
    cmd = "du -s -B 1K {} 2>/dev/null".format(path)  # Retrieves size in 1024(bytes) units
    ret_val = sp.run(["/bin/bash", "-c", cmd], capture_output=True, check=False)
    output = ret_val.stdout.decode("utf-8").split("\t")[0]
    return compute_str_to_bytes(output)


def compute_str_to_bytes(string):
    """
    Given a string consisting of integers compute the MB and GB equivalent
    Parameters:
    string: string to read and compute into MB & GB
    """
    global TOTAL_GB, TOTAL_MB
    value = int(string)
    value_mb = (value * 2 ** -10)  # KB TO MB
    value_gb = (value * 2 ** -20)  # KB TO GB
    TOTAL_MB += value_mb
    TOTAL_GB += value_gb
    mb_size = "{:,.2f}mb".format(value_mb)
    if value_gb < 0.01:
        return mb_size
    gb_size = "{:,.2f}gb".format(value_gb)
    return "{:<12} / {:^12}".format(mb_size, gb_size)


def check_read_permission(directory):
    """Check if there is permission to read the given directory"""
    return os.access(directory, os.R_OK)


def summarize_directory():
    """Summarize directories in terms of files and disk usage"""
    if OPTIONS_FLAGS["Triplets"]:
        print("\n{:-<40}{:-<15}{:-<15}{:-<30}".format("DIRECTORY", "FILES", "TRIPLES", "SIZE(MB/GB)"))
    else:
        print("\n{:-<40}{:-<15}{:-<45}".format("DIRECTORY", "FILES", "SIZE"))
    for sub_dir in DIRECTORIES:
        permission = check_read_permission(sub_dir)
        if permission:
            files = count_files(sub_dir)
            dir_size = get_size(sub_dir)
            if OPTIONS_FLAGS["Triplets"]:
                print("{:<40}{:<15,}{:<15,.2f}{:<}".format(sub_dir, files, (files / 3), dir_size))
            else:
                print("{:<40}{:<15,}{:<}".format(sub_dir, files, dir_size))
        else:
            print("{} Permission denied".format(sub_dir))
    print("{:-<100}".format("-"))


def summarize_files():
    """Summarize files in terms of disk usage"""
    global TOTAL_FILES
    if OPTIONS_FLAGS["Ignore"]:
        return
    if len(FILES) <= 0:
        return
    print("\n{:-<40}{:-<60}".format("FILE", "SIZE"))
    TOTAL_FILES += len(FILES)
    for file in FILES:
        size = get_size(file)
        print("{:<40}{:<15}".format(file, size))
    print("{:-<100}".format("-"))


def print_result(triplets):
    """Print total summary when multiple paths are given as parameters to the script"""
    print("\n{:-^100}".format("TOTAL SUMMARY"))
    if triplets:
        print("{:<10}\t{:<,}".format("Files:", TOTAL_FILES))
        print("{:<10}\t{:<,.2f}".format("Triples:", TOTAL_FILES / 3))
        if TOTAL_GB >= 1:
            print("{:<10}\t{:<,.2f}GB".format("Size:", TOTAL_GB))
        else:
            print("{:<10}\t{:<,.2f}MB".format("Size:", TOTAL_MB))
    else:
        print("{:<10}\t{:<,}".format("Files:", TOTAL_FILES))
        if TOTAL_GB >= 1:
            print("{:<10}\t{:<,.2f}GB".format("Size:", TOTAL_GB))
        else:
            print("{:<10}\t{:<,.2f}MB".format("Size:", TOTAL_MB))
    print("{:-<100}\n".format("-"))


def validate_path(path):
    """Check if a path is a directory or a file"""
    if os.path.isfile(path):
        FILES.append(path)
    elif os.path.isdir(path):
        return


def check_args(args):
    """Separate args from paths"""
    for item in args:
        if item in OPTIONS:
            if not OPTIONS_FLAGS["Triplets"]:
                if item in OPTIONS[:3]:
                    OPTIONS_FLAGS["Triplets"] = True
            if not OPTIONS_FLAGS["Ignore"]:
                if item in OPTIONS[3:5]:
                    OPTIONS_FLAGS["Ignore"] = True
        else:
            DIRECTORIES.append(item)
    for sub_dir in DIRECTORIES:
        validate_path(sub_dir)
    for file in FILES:
        if file in DIRECTORIES:
            DIRECTORIES.remove(file)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: cf [OPTION]... [PATH]... ")
        sys.exit(1)
    else:
        if any(help_option in sys.argv for help_option in OPTIONS[-3:]):
            print("Usage: cf [OPTION]... [PATH]... ")
            print("Counts files")
            print("*NOTE* ignores directories/files with insufficient permissions!")
            print("Options:")
            for option in OPTIONS_HELP_TEXT.values():
                print(option)
            sys.exit(0)
        print("------------------")
        print("COUNT FILES SCRIPT")
        print("------------------")
        print("DATE: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("-------------------------")
        check_args(sys.argv[1:])
        summarize_directory()
        summarize_files()
        if len(DIRECTORIES) > 1:
            print_result(OPTIONS_FLAGS["Triplets"])


if __name__ == "__main__":
    main()
