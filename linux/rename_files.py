"""
Rename files
This script renames all files in a directory.
This can be done in several ways:
    prefix: adding a prefix to the file/files.
    suffix: adding a suffix to the file/files.
    full-rename: rename all files to a given string with a integer suffix.
"""
import subprocess as sp
import sys
import os

PREFIX = ""
SUFFIX = ""
FULL_OVERWRITE = ""

FILES = []

OPTIONS = ["-px", "--prefix", "-sx", "--suffix", "-rename", "-h", "-H", "--help"]
OPTIONS_FLAGS = {"prefix": False, "suffix": False, "full_overwrite": False}
OPTIONS_HELP_TEXT = {
    "--prefix": "{} {:>3} \tAdd a prefix to the file/files.".format(OPTIONS[0], OPTIONS[1]),
    "--suffix": "{} {:>3} \tAdd a suffix to the file/files.".format(OPTIONS[2], OPTIONS[3]),
    "--rename": "{} \tRename the file/files. If multiple files will be suffixed with an integer.".format(OPTIONS[4]),
    "--help": "{}{:>3} {} \tDisplay this help and exit.".format(OPTIONS[-3], OPTIONS[-2], OPTIONS[-1])
}


def rename_file(file, new_name):
    """
    Rename a file.

    Parameters:
        file: path of file that needs renaming.
        new_name: new name of the file.
    """
    cmd = "mv {} {}".format(file, new_name)
    print(cmd)
    ret_val = sp.run(["/bin/bash", "-c", cmd], capture_output=True)
    if ret_val.returncode == 0:
        return True
    return False


def extract_file_name(file):
    """
    Extract filename from a string.
    Folder, filename and extension(if present) is extracted and returned.
    Parameters:
        file: path to file in form of a string.
    Returns:
        folder: folder containing the file.
        name: name of the file.
        ext: if the file has an extension else None.
        """
    if file[0] == ".":
        folder, name = file.split("/")
        folder = "{}/".format(folder)
        if "." in name:
            name, ext = name.split(".")
            return folder, name, ext
        return folder, name, None
    elif "." in file:
        name, ext = file.split(".")
        folder, name = "/".join(name.split("/")[:-1]), name.split("/")[-1]
        return folder, name, ext
    folder, name = "/".join(file.split("/")[:-1]), file.split("/")[-1]
    if "/" not in folder:
        folder = folder+"/"
    return folder, name, None


def rename_files():
    """
    Renames files in the global list FILES
    """
    if OPTIONS_FLAGS["prefix"]:
        for file in FILES:
            if OPTIONS_FLAGS["suffix"]:
                folder, name, ext = extract_file_name(file)
                if "." in file[1:]: # with extension
                    new_file_name = folder+PREFIX+name+SUFFIX+"."+ext
                else: # no extension
                    new_file_name = folder+PREFIX+name+SUFFIX
            else:
                folder, name, ext = extract_file_name(file)
                if "." in file[1:]: # with extension
                    new_file_name = folder+PREFIX+name+"."+ext
                else: # no extension
                    new_file_name = folder+PREFIX+name
            if not rename_file(file, new_file_name):
                print("Error renaming files!")
                exit(1)
    elif OPTIONS_FLAGS["suffix"]:
        for file in FILES:
            folder, name, ext = extract_file_name(file)
            if "." in file[1:]: # with extension
                new_file_name = folder+name+SUFFIX+"."+ext
            else: # no extension
                new_file_name = folder+name+SUFFIX
            if not rename_file(file, new_file_name):
                print("Error renaming files!")
                exit(1)
    elif OPTIONS_FLAGS["full_overwrite"]:
        if FULL_OVERWRITE.count(".") > 1:
            print("Error too many '.' in new filename!")
            exit(1)
        for idx, file in enumerate(FILES):
            folder, _, __ = extract_file_name(file)
            if "." in FULL_OVERWRITE:
                name, ext = FULL_OVERWRITE.split(".")
                new_file_name = folder+name+"_"+str(idx)+"."+ext
            else:
                name = FULL_OVERWRITE
                new_file_name = folder+name+"_"+str(idx)
            if not rename_file(file, new_file_name):
                print("Error renaming files!")
                exit(1)


def extract_files(folder):
    """
    Extract all files from a given folder.

    Parameters:
        folder: path to folder containing files.
    Returns:
        files: list of files from the given folder."""
    if folder == "." or folder == ".*":
        folder = folder+"/"
        cmd = "find {} -maxdepth 1 -type f | grep -v ../".format(folder)
    else:
        cmd = "find {} -maxdepth 1 -type f".format(folder)
    print(cmd)
    ret_val = sp.run(["/bin/bash", "-c", cmd], capture_output=True)
    files = []
    if ret_val.returncode == 0:
        files = ret_val.stdout.decode("utf-8").split("\n")[:-1]
    return files


def check_path(path):
    """
    Checks a if a path is a directory or a file,
    if the path is a directory the files within is appended to FILES
    else the file is appended to FILES.
    """
    if os.path.isdir(path):
        for element in extract_files(path):
            FILES.append(element)
    else:
        FILES.append(path)



def check_args(args):
    """Seperate args from folders"""
    global PREFIX, SUFFIX, FULL_OVERWRITE
    for idx, item in enumerate(args):
        if OPTIONS_FLAGS["prefix"]:
            if args[idx-1] in OPTIONS[0:2]:
                PREFIX = item
                continue
        if OPTIONS_FLAGS["suffix"]:
            if args[idx-1] in OPTIONS[2:4]:
                print("Suffix set to", item)
                SUFFIX = item
                continue
        if OPTIONS_FLAGS["full_overwrite"]:
            if args[idx-1] == OPTIONS[4]:
                FULL_OVERWRITE = item
                continue
        if item in OPTIONS:
            if item in OPTIONS[0:2]:
                OPTIONS_FLAGS["prefix"] = True
            if item in OPTIONS[2:4]:
                OPTIONS_FLAGS["suffix"] = True
            if item in OPTIONS[4]:
                OPTIONS_FLAGS["full_overwrite"] = True
        else:
            check_path(item)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: rf [OPTION] [OPTION-ARG].. [FOLDER/FILES]... ")
        exit(-1)
    else:
        if any(help_option in sys.argv for help_option in OPTIONS[-3:]):
            print("Rename files")
            print("Usage: rf [OPTION] [OPTION-ARG].. [FOLDER/FILES]... ")
            print("Options:")
            for option in OPTIONS_HELP_TEXT.values():
                print(option)
            exit(0)
        check_args(sys.argv[1:])
        rename_files()

if __name__ == "__main__":
    main()
