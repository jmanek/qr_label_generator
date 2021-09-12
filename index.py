import qrcode
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image, ImageFont, ImageDraw
import argparse
from functools import reduce


def make_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=50,
        border=2,
    )
    qr.add_data(data)

    img = qr.make_image(fill_color="black", back_color="white")
    return (img, qr)


# for garagesalepup 1" square label sheet
# top 100px
# left 100px x 2 = 200px
# box 200px x 7 = 1400px
# margin ~17px x 6 ~= 100px
def overlay_label(qr_image, label, template, col, row):
    qr_image = qr_image.resize((195, 195))
    col_offset = col * 217 + 100
    row_offset = row * 225 + 100
    template.paste(qr_image, (col_offset, row_offset))

    draw = ImageDraw.Draw(template)

    font = ImageFont.truetype("arial.ttf", 10)
    draw.text((col_offset, row_offset-20),
              label[:40], font=font, fill=(0, 0, 0))


def create_template():
    template = Image.new('RGB', (1700, 2200), 'white')
    return template


# github.com/alishtory/qrcode-terminal
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
    parser.add_argument('row', type=int,
                        help='The row to start adding labels -- zero indexed')
    parser.add_argument('col', type=int,
                        help='The column to start adding labels -- zero indexed')
    parser.add_argument('data', nargs='+',
                        help='space separate list of links to convert into QR codes')

    args = parser.parse_args()
    row = args.row
    col = args.col

    template = create_template()
    # template = Image.open("template.png")

    for datum in args.data:
        if col == 7:
            if row >= 8:
                raise Exception(
                    'Reached end of template, no free spaces remain')
            else:
                col = 0
                row += 1
        qr_img, qr = make_qr_code(datum)
        print(datum)
        print_qr_code(qr)
        overlay_label(qr_img, datum, template, col, row)
        col += 1
    template.save('qr_label.pdf')
