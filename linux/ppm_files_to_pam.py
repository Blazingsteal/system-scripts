"""Combine two or more .ppm files (RGB & NIR) into a .pam file"""
from glob import glob
import sys
import os
import subprocess as sp
import numpy as np
from ppm_to_pam import PpmToPam

FILE_CONVERT_COUNT = 0

FOLDERS = []

OPTIONS = ["-f", "-file", "--file", "-d", "-folder", "-h", "-H", "--help"]
OPTIONS_FLAGS = {"File_mode": False, "Folder_mode": False}
OPTIONS_HELP_TEXT = {
    "-f": "{:>5}{:>3} {:10} \tFile mode: Combine a RGB and Nir image to a 4channel pam image\n\t\t\tRGB 1st Nir 2nd".format(OPTIONS[0], OPTIONS[1], OPTIONS[2]),
    "-d": "{:>5} {:10} \tDir/Folder mode: Convert entire folder requires proper organizing of files.\n\t\t\tE.g.. RGB and Nir file names must match so if 'unsheard' was to be swapped with 'nir' you would have the nir file.".format(OPTIONS[3], OPTIONS[4]),
    "-h": "{:>5}{:>3} {:10} \tDisplay this help and exit".format(OPTIONS[-3], OPTIONS[-2], OPTIONS[-1])
}


def combine_rgb_nir(rgbfile, nirfile, outputdir):
    """Combine an rgbfile and a nirfile into a 4channel .pam file."""
    global FILE_CONVERT_COUNT
    pam = PpmToPam(rgbfile, nirfile)
    rgbn = np.ndarray(shape=(4, pam.height * pam.width), dtype=np.uint8)
    rgbn = np.concatenate((pam.rgb_img, pam.nir_img[:, :, :1]), axis=2)
    rgbn = np.moveaxis(rgbn, 2, 0)

    new_file = outputdir + pam.rgbfile.split("/")[-1][:-4]
    _f = open("%s_with_nir.pam" %new_file, "wb")
    _f.write(b"P7\n")
    _f.write(b"WIDTH %d\n" %pam.width)
    _f.write(b"HEIGHT %d\n" %pam.height)
    _f.write(b"DEPTH 4\n")
    _f.write(b"MAXVAL %d\n" %pam.max_value)
    _f.write(b"ENDHDR\n")
    print("RGBN file:", _f.name)
    for i in rgbn.flatten():
        _f.write(b"%c" %i)
    _f.close
    FILE_CONVERT_COUNT += 1


def pair_file():
    """
    Paring nir files with their respective rgb files
    and combines them into a 4channel .pam file.
    """
    if len(FOLDERS) < 1:
        print("Error not enough files")
        exit(1)
    if OPTIONS_FLAGS["File_mode"]:
        rgb = FOLDERS[0]
        nir = FOLDERS[1]
        outputdir = os.path.abspath("", *rgb.split("/")[:-1]) + "/nir_images/"
        if create_dir(outputdir):
            combine_rgb_nir(rgb, nir, outputdir)
    if OPTIONS_FLAGS["Folder_mode"]:
        for folder in FOLDERS:
            outputdir = os.path.abspath(folder) + "/nir_images/"
            files = sorted(glob(os.path.abspath(folder)+"/*.ppm"))
            for file in files:
                if "nir" in file:
                    for subfile in files:
                        if "unsheared" in subfile:
                            rgb = subfile.replace("unsheared", "nir")
                            if rgb == file:
                                print(subfile.split("/")[-1], "|", file.split("/")[-1])
                                if create_dir(outputdir):
                                    combine_rgb_nir(subfile, file, outputdir)
                                else:
                                    exit(1)
                        elif "sheared" in subfile:
                            rgb = subfile.replace("sheared", "nir")
                            if rgb == file:
                                print(subfile.split("/")[-1], "|", file.split("/")[-1])
                                if create_dir(outputdir):
                                    combine_rgb_nir(subfile, file, outputdir)
                                else:
                                    exit(1)
    if FILE_CONVERT_COUNT == 0:
        print("Error couldn't find any matching files")
    else:
        print("Combined %d files into %d files" %(FILE_CONVERT_COUNT*2, FILE_CONVERT_COUNT))


def create_dir(_dir):
    """Create a directory unless it exists."""
    if os.path.isdir(_dir):
        print("Output _dir already exists, moving on")
        return True
    cmd = "mkdir {}".format(_dir)
    ret_val = sp.run(["/bin/bash", "-c", cmd], capture_output=True)
    if ret_val.returncode == 0:
        return True
    print("Error creating output _dir: {}".format(_dir))
    return False


def validate_dir(path):
    """
    Validate a path checking if it is a directory.
    Ignore if in filemode.
    """
    if os.path.isdir(path):
        return
    elif OPTIONS_FLAGS["File_mode"]:
        return # In file mode, so we dont do anything to the list as it only contains 2 files
    else:
        print("ERROR! {} is not a folder".format(path))
        exit(1)


def check_args(args):
    """Seperate args from folders"""
    arg_count = 0
    for item in args:
        if item in OPTIONS:
            print("arg found", item)
            arg_count += 1
            if item in OPTIONS[:3]:
                OPTIONS_FLAGS["File_mode"] = True
            if item in OPTIONS[3:5]:
                OPTIONS_FLAGS["Folder_mode"] = True
        else:
            FOLDERS.append(item)
    for subfolder in FOLDERS:
        validate_dir(subfolder)
    if not arg_count > 0:
        print("Bad args!")
        print("Usage: ppam [OPTION]... [IMAGE/FOLDER]...")
        exit(3)


def main():
    """Main method"""
    if len(sys.argv) < 3:
        if any(help_option in sys.argv for help_option in OPTIONS[-3:]):
            print("Usage: ppam [OPTION]... [IMAGE/FOLDER]...")
            print("Combine rgb and nir images, or entire folders containing rbg and nir images")
            print("Options:")
            for _v in OPTIONS_HELP_TEXT.values():
                print(_v)
            exit(0)
        print("Usage: ppam [OPTION]... [IMAGE/FOLDER]... \nTry 'ppam --help' for more information.")
        exit(1)
    else:
        if any(help_option in sys.argv for help_option in OPTIONS[-3:]):
            print("Usage: ppam [OPTION]... [IMAGE/FOLDER]...")
            print("Combine rgb and nir images, or entire folders containing rbg and nir images")
            print("Options:")
            for _v in OPTIONS_HELP_TEXT.values():
                print(_v)
            exit(0)
        check_args(sys.argv[1:])
        pair_file()


if __name__ == "__main__":
    main()
