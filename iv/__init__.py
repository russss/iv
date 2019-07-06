import click
import shutil
from imgcat import imgcat
from PIL import Image, ImageDraw, ImageFont
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
import io

FONTS = [
    "Helvetica.ttf",
    "helvetica.ttf",
    "arial.ttf",
    "OpenSans-Regular.ttf",
    "Arial.ttf",
]

PIXELS_PER_LINE = 12

@click.command()
@click.version_option()
@click.option(
    "-s",
    "--size",
    default=1000,
    help="Maximum output image width in pixels.",
    envvar="IV_SIZE",
)
@click.argument("filename", nargs=-1, required=True, type=click.Path(exists=True))
def main(filename, size):
    """Display images within an iTerm2 terminal.

       iv will resize images to reduce the time taken to display them over SSH connections,
       and it will combine multiple images into a single image, with filenames.

       Usage:

        \b
        iv ./file.jpg # Display a single file, resizing as appropriate.
        iv *.jpg      # Display a number of files combined into a single image, with filenames.

       The IV_SIZE environment variable can be used to set the output image size
       instead of the -s/--size option.
    """
    tty_size = shutil.get_terminal_size((80, 20))
    if len(filename) == 1:
        size = min(tty_size.columns * PIXELS_PER_LINE, size)
        draw_single(filename[0], size)
    else:
        draw_multi(filename, tty_size.columns * PIXELS_PER_LINE)


def draw_single(path, size):
    im = read_image(path, size)
    imgcat(save_image(im), height=im.size[1] // PIXELS_PER_LINE)


def draw_multi(paths, size):
    """ Draw multiple images into a single "contact sheet" style image, with filenames."""
    min_image_size = 250
    h_spacing = 20
    v_spacing = 40

    per_line = size // (min_image_size + h_spacing)
    max_width = int(size / per_line - h_spacing)

    images = read_images(paths, max_width)

    row_heights = []
    for col_start in range(0, len(images), per_line):
        row_heights.append(
            max(im.height for im in images[col_start : col_start + per_line])
        )

    canvas = Image.new(
        "RGB",
        (
            per_line * (max_width + h_spacing) - h_spacing,
            sum(row_heights) + len(row_heights) * v_spacing,
        ),
        color=(255, 255, 255),
    )

    draw = ImageDraw.Draw(canvas)
    font = load_font(18)

    height = 0
    for row in range(0, len(row_heights)):
        for col in range(0, per_line):
            im_offset = row * per_line + col
            if im_offset >= len(images):
                break
            im = images[im_offset]
            im_pos = (col * (max_width + h_spacing), height)
            canvas.paste(im, box=im_pos)
            font_size = font.getsize(im.filename)
            if font_size[0] > max_width:
                # Don't draw if it'll overlap
                continue
            x_padding = (max_width - font_size[0]) // 2
            draw.text(
                (im_pos[0] + x_padding, im_pos[1] + im.size[1] + 5),
                im.filename,
                font=font,
                fill=(0, 0, 0),
            )
        height += row_heights[row] + v_spacing

    imgcat(save_image(canvas, fmt="JPEG"), height=canvas.size[1] // PIXELS_PER_LINE)


def load_font(size):
    """ Try and locate an appropriate truetype font on the local system to use with Pillow. """
    for font in FONTS:
        try:
            f = ImageFont.truetype(font, size=size)
        except OSError:
            continue
        return f
    return ImageFont.load_default()


def read_image(path, size):
    """ Load an image and resize it to fit the provided dimension """
    im = Image.open(path)
    im.thumbnail((size, size))
    return im


def read_images(paths, size):
    """ Load and resize a list of images in parallel """
    pool = ThreadPool(multiprocessing.cpu_count())
    images = pool.map(lambda fname: read_image(fname, size), paths)
    pool.close()
    pool.join()
    return images


def save_image(im, fmt=None):
    """ Render an image to the provided format """
    if fmt is None:
        fmt = im.format
    with io.BytesIO() as output:
        im.save(output, format=fmt)
        contents = output.getvalue()
    return contents
