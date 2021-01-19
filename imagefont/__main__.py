from argparse import ArgumentParser, FileType

from . import ImageFont

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('image_files', nargs='+', type=FileType('rb'),
                        metavar='image')
    parser.add_argument('-o', dest='output_file', type=FileType('w'),
                        required=True)
    args = parser.parse_args()
    font = ImageFont()
    for image_file in args.image_files:
        font.add(image_file)
    font.write(args.output_file)
