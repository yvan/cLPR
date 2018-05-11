'''
@yvan may 11 2018

converts bitmap (.bmp) files output by the pygame generator
to jpeg (.jpg) or PNG (.png) files with no compress/data loss. Can also
be used to resize the output files.

'''
import os
import sys
import glob
import argparse
from PIL import Image

def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument('-g', '--glob', type=str, help='Unix style glob path to the images you want to convert.')
    p.add_argument('-o', '--out', type=str, help='The output path (folder) to put all the files.')
    p.add_argument('-d1', '--dim1', type=int, help='The first (height) dimension of the image.')
    p.add_argument('-d2', '--dim2', type=int, help='The second (width) dimension of the image.')
    p.add_argument('-f', '--format', type=str, help='The output format, JPEG, or PNG, or BMP.')

if __name__ == '__main__':
    args = parse_args(sys.argv[1:]).__dict__
    glob = args['input']
    out = args['out']
    dim1 = args['dim1']
    dim2 = args['dim2']
    format = args['format'].upper()
    ext = format.lower()

    img_paths = glob.glob(glob)
    for img_path in img_paths:
        img = Image.open(img_path)
        path, basename = os.path.split(img_path)
        basename, _ = os.path.splitext(basename)
        if dim1 and dim2:
            img = img.resize((dim1,dim2))
        img.save(f'{out}/{basename}.{ext}', format=format, subsampling=0, quality=100)
