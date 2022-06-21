import glob
from PIL import Image
import pathlib
import shutil
from pathlib import Path
import imghdr

def resize_logo(h,w,logo):
    wsize = int(min(h, w) * 0.20)
    wpercent = (wsize / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    simage = logo.resize((wsize, hsize), Image.ANTIALIAS)
    return simage

def resize_watermark(h,w,watermark):
    wsize = int(min(h,w) * 0.5)
    wpercent = (wsize / float(watermark.size[0]))
    hsize = int((float(watermark.size[1]) * float(wpercent)))
    wimage = watermark.resize((wsize, hsize))
    return wimage

def make_square(im, min_size=256, fill_color=(255, 255, 255, 255)):
    box = im.getbbox()
    x = box[2]
    y = box[3]

    x = x - box[0]
    y = y - box[1]

    size = max(min_size, x, y)
    new_im = Image.new('RGBA', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2) -
                      box[0], int((size - y) / 2)-box[1]), im)
    return new_im


def thumbnail_maker(base_images,output_directory,logo,watermark):
    base_images = glob.glob(base_images+"\\*")
    names = [x.rsplit('\\', 1)[-1] for x in base_images]
    extentions = [x.rsplit('.', 1)[-1] for x in base_images]
    if watermark:
        watermark_file = Path(watermark)
        if not watermark_file.is_file():
            print("No such file: "+str(watermark_file))
    if logo:
        logo_file = Path(logo)
        if not logo_file.is_file():
            print("No such file: "+str(logo_file))
        
    if pathlib.Path(output_directory).is_dir():
        print("Clean output directory")
        shutil.rmtree(output_directory, ignore_errors=True)

    pathlib.Path(output_directory).mkdir(exist_ok=True)

    for bimage, extention, name in zip(base_images, extentions, names):
        if Path(bimage).is_file() and imghdr.what(bimage):
            img = Image.open(bimage).convert("RGBA")
            outfname = name.replace(extention, "png")
            resized_image = make_square(img)
            height, width = resized_image.size
            resized_image.save(output_directory+"\\"+outfname)

            if watermark:
                if watermark_file.is_file():
                    watermark_img = Image.open(watermark)
                    wimage = resize_watermark(height, width,watermark_img)
                    # add watermark
                    wsize, hsize = wimage.size
                    transparent = Image.new('RGBA', (height,width), (0, 0, 0, 0))
                    transparent.paste(resized_image, (0, 0))
                    transparent.paste(wimage, (int(width/2-wsize/2),
                                            int(height/2-hsize/2)), mask=wimage)
                    transparent.save(output_directory+"\\"+outfname)
                    resized_image = Image.open(output_directory+"\\"+outfname)

            if logo:
                if logo_file.is_file():
                    logo_img = Image.open(logo)
                    simage = resize_logo(height, width,logo_img)
                    # add logo
                    mbox = resized_image.getbbox()
                    sbox = simage.getbbox()
                    resized_image = Image.open(output_directory+"\\"+outfname)
                    box = (int(mbox[2] - sbox[2]*1.05), int(mbox[3] - sbox[3]*1.05))
                    resized_image.paste(simage, box)

            resized_image.save(output_directory+"\\"+outfname)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create product thumbnail with white background, unified size, logo and watermark"
    )
    parser.add_argument(
        "input_directory",
        help="Input directory where the original images are stored.",
    )
    parser.add_argument(
        "output_directory",
        help="Output directory for the new images. Will be created if it does not exist.",
    )
    parser.add_argument(
        "-l",
        "--logo",
        help="Path to logo image file.",
        type=str,
        default="",
    )
    parser.add_argument(
        "-w",
        "--watermark",
        help="Path to watermark image file.",
        type=str,
        default="",
    )
    args = parser.parse_args()
    thumbnail_maker(
        base_images = args.input_directory,
        output_directory = args.output_directory,
        logo=args.logo,
        watermark=args.watermark,
    )
