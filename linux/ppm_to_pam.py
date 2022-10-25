"""
Combine two .ppm files (RGB & NIR) into a single .pam file
"""
import sys
import numpy as np
import imageio

class PpmToPam(object):
    """
    Combine two .ppm files (RGB & NIR) into a single .pam file
    """
    def __init__(self, rgbfile, nirfile):
        print("RGB:", rgbfile)
        print("Nir:", nirfile)

        self.nirfile = nirfile
        self.rgbfile = rgbfile
        self.max_value = 0
        self.width = 0
        self.height = 0
        self.channels = 3

        self.rgb_img = None
        self.nir_img = None

        if rgbfile[-4:] != ".ppm":
            print("Files does not have a ppm file extension")
            return

        if not self.read_files(rgbfile, nirfile):
            print("Error when reading files!")

    def __str__(self):
        return ""

    def read_files(self, rgbfile, nirfile):
        """Read two files, rgb and nir"""
        try:
            with open(rgbfile, "rb") as _f:
                line = _f.readline().decode("latin-1")
                if not line[:2] in ["P6", "P3"]:
                    print("This is not a ppm format, returning")
                    return False

                line = _f.readline().decode("latin-1")
                self.width = int(line.strip().split(" ")[0])
                self.height = int(line.strip().split(" ")[1])

                line = _f.readline().decode("latin-1")
                self.max_value = int(line)
            self.rgb_img = imageio.imread(rgbfile)

            with open(nirfile, "rb") as _f:
                line = _f.readline().decode("latin-1")
                if not line[:2] in ["P6", "P3"]:
                    print("This is not a ppm format, returning")
                    return False

                line = _f.readline().decode("latin-1")
                if self.width != int(line.strip().split(" ")[0]):
                    print("Files do not have the same dimensions (width)")
                    return False

                if self.height != int(line.strip().split(" ")[1]):
                    print("Files do not have the same dimension (height)")
                    return False

                line = _f.readline().decode("latin-1")
                if self.max_value != int(line):
                    print("Files do not have the same max values")
                    return False
            self.nir_img = imageio.imread(nirfile)

        except Exception as _e:
            print("Execption while reading rgbfile: %s \n%s" %(rgbfile, str(_e)))
            return False
        return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Not enough files")
        exit()
    PAM = PpmToPam(sys.argv[1], sys.argv[2])
    RGBN = np.ndarray(shape=(4, PAM.height * PAM.width), dtype=np.uint8)
    RGBN = np.concatenate((PAM.rgb_img, PAM.nir_img[:, :, :1]), axis=2)
    RGBN = np.moveaxis(RGBN, 2, 0)

    NEW_FILE = PAM.rgbfile.split("/")[-1][:-4]
    F = open("/tmp/nir/nir-09-12-21/%s_RGBN.pam" %NEW_FILE, "wb")
    F.write(b"P7\n")
    F.write(b"WIDTH %d\n" %PAM.width)
    F.write(b"HEIGHT %d\n" %PAM.height)
    F.write(b"DEPTH 4\n")
    F.write(b"MAXVAL %d\n" %PAM.max_value)
    F.write(b"ENDHDR\n")
    print("Output file:", F.name)

    for i in RGBN.flatten():
        F.write(b"%c" %i)
    F.close()
