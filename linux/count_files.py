"""Count files
This script counts files in any directory and out puts how many files there are in each folder
along with their disk usage. Various flags can be set to change the output of the script."""
import subprocess as sp
import sys
import os
import datetime

TOTAL_FILES = 0
TOTAL_GB = 0
TOTAL_MB = 0

FOLDERS = []
FILES = []

OPTIONS = ["-t", "-T", "--triple", "-i", "--ignore", "-h", "-H", "--help"]
OPTIONS_FLAGS = {"Triplets": False, "Ignore": False}
OPTIONS_HELP_TEXT = {
    "-t": "{:>5}{:>3} {:10} \tPrint triplets (files/3)".format(OPTIONS[0], OPTIONS[1], OPTIONS[2]),
    "-i": "{:>5} {:10} \tIgnore non-folders if present in args".format(OPTIONS[3], OPTIONS[4]),
    "-h": "{:>5}{:>3} {:10} \tDisplay this help and exit".format(OPTIONS[-3], OPTIONS[-2], OPTIONS[-1])
}


def count_files(folder):
    """
    Count files in a given folder
    Ignores folders/files with insufficient permissions
    Parameters:
    folder: The wanted folder to count files in.
    """
    global TOTAL_FILES
    cmd = "find {} -type f 2>/dev/null | wc -l".format(folder)
    ret_val = sp.run(["/bin/bash", "-c", cmd], capture_output=True, check=False)
    if ret_val.returncode == 0:
        output = ret_val.stdout.decode("utf-8").split("\n")[0]
        TOTAL_FILES += int(output)
        return int(output)
    return None


def get_size(path):
    """
    Get the size of folder
    Ignores folder with insufficient permissions
    Parameters:
    folder: Folder to get size of
    """
    cmd = "du -s -B 1K {} 2>/dev/null".format(path)  # Retrieves folder size in 1024(bytes) units
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


def check_read_permission(folder):
    """Check if there is permission to read the given folder"""
    return os.access(folder, os.R_OK)


def summarize_folder():
    """Summarize folder in terms of files and disk usage"""
    if OPTIONS_FLAGS["Triplets"]:
        print("\n{:-<40}{:-<15}{:-<15}{:-<30}".format("FOLDER", "FILES", "TRIPLES", "SIZE(MB/GB)"))
    else:
        print("\n{:-<40}{:-<15}{:-<30}".format("FOLDER", "FILES", "SIZE"))
    for subfolder in FOLDERS:
        permission = check_read_permission(subfolder)
        if permission:
            files = count_files(subfolder)
            folder_size = get_size(subfolder)
            if OPTIONS_FLAGS["Triplets"]:
                print("{:<40}{:<15,}{:<15,.2f}{:<}".format(subfolder, files, (files / 3), folder_size))
            else:
                print("{:<40}{:<15,}{:<}".format(subfolder, files, folder_size))
        else:
            print("{} Permission denied".format(subfolder))
    print("{:-<100}".format("-"))


def summarize_files():
    """Summarize files in terms of disk usage"""
    global TOTAL_FILES
    if OPTIONS_FLAGS["Ignore"]:
        return
    if not len(FILES) > 0:
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


def validate_folder(folder):
    """Check if a folder is a valid folder, or remove it if the ignore flag is set"""
    if os.path.isdir(folder):
        return
    elif os.path.isfile(folder):
        FILES.append(folder)
        return
    else:
        print("ERROR! {} is not a folder/file".format(folder))
        print("You can ignore non-folders with the '-i' flag")
        sys.exit(1)


def check_args(args):
    """Separate args from folders"""
    for item in args:
        if item in OPTIONS:
            if not OPTIONS_FLAGS["Triplets"]:
                if item in OPTIONS[:3]:
                    OPTIONS_FLAGS["Triplets"] = True
            if not OPTIONS_FLAGS["Ignore"]:
                if item in OPTIONS[3:5]:
                    OPTIONS_FLAGS["Ignore"] = True
        else:
            FOLDERS.append(item)
    for subfolder in FOLDERS:
        validate_folder(subfolder)
    for file in FILES:
        if file in FOLDERS:
            FOLDERS.remove(file)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: cf [OPTION]... [FOLDER]... ")
        sys.exit(1)
    else:
        if any(help_option in sys.argv for help_option in OPTIONS[-3:]):
            print("Usage: cf [OPTION]... [FOLDER(S)]... ")
            print("Counts files")
            print("*NOTE* ignores folders/files with insufficient permissions!")
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
        summarize_folder()
        summarize_files()
        if len(FOLDERS) > 1:
            print_result(OPTIONS_FLAGS["Triplets"])


if __name__ == "__main__":
    main()
