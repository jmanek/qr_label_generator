import qrcode
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image, ImageFont, ImageDraw
import argparse
from functools import reduce
import math
import numpy as np
import cv2 as cv
import platform


def make_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        box_size=20,
        border=2,
    )
    qr.add_data(data)

    img = qr.make_image(fill_color="black", back_color="white")
    return (img, qr)


def overlay_label(qr_image, qr, label, template, rect):
    width, height = template.size
    qr_image = qr_image.resize((rect[2]-10, rect[3]-10))

    template.paste(qr_image, (rect[0] + 5, rect[1] + 5))
    # Font size based on template dimensions
    font = ImageFont.truetype("arial.ttf", 42)
    ImageDraw.Draw(template).text((rect[0], rect[1]-20),
                                  label[:40], font=font, fill=(0, 0, 0))
    print(label)
    print_qr_code(qr)


def create_template(template_path):
    template = Image.new('RGB', (8500, 11000), 'white')
    if template_path.endswith('pdf'):
        if platform.system() == 'Windows':
            img = convert_from_path(
                template_path, poppler_path='./external/poppler-win64-21.09.0/Library/bin')[0]
        else:
            img = convert_from_path(template_path)
    else:
        img = Image.open(template_path)
    t_width, t_height = template.size
    width, height = img.size
    img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)

    imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, thresh = cv.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv.findContours(
        thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    if len(list(filter(lambda cc: cc[3] == -1, hierarchy[0]))) == 1:
        contour_level = 0
    else:
        contour_level = -1
    rects = list(map(lambda cc: (t_width*cc[0]//width, t_height*cc[1]//height, t_width*cc[2]//width, t_height*cc[3]//height),
                     map(lambda cc: cv.boundingRect(cc[1]),
                     filter(lambda cc: cc[0][3] == contour_level,
                            zip(hierarchy[0], contours)))))
    rects.reverse()
    return template, rects


# adapated from github.com/alishtory/qrcode-terminal
def print_qr_code(qr):
    white_block = '\033[0;37;47m  '
    black_block = '\033[0;37;40m  '
    new_line = '\033[0m\n'

    code = white_block + f'{white_block + new_line + white_block}'.join(map(
        lambda mn: reduce(lambda uu, vv: uu +
                          black_block if vv else uu + white_block, mn, ''),
        qr.modules))
    border = white_block*(qr.modules_count+2) + new_line

    print(border + code + white_block + new_line + border)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create printable QR code label')
    parser.add_argument('template', type=str,
                        help='The template to use')
    parser.add_argument('start', type=int,
                        help='The square to start adding labels -- zero indexed')
    parser.add_argument('data', nargs='+',
                        help='spaced separate list of links to convert into QR codes')
    args = parser.parse_args()

    start = args.start
    template, rects = create_template(args.template)
    if start + len(args.data) > len(rects):
        raise Exception('Not enough space left in template')
    rects = rects[start: start + len(rects)]
    rects.reverse()

    list(map(lambda qr: overlay_label(*qr[0], qr[1], template, rects.pop()),
             map(lambda dd: (make_qr_code(dd), dd), args.data)))

    print('Saved to qr_label.pdf/png')
    # Resolution based on template dimensions
    template.save('qr_label.pdf', resolution=1000)
    template.save('qr_label.png')
    template.show()
