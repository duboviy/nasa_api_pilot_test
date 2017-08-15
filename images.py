import io

import requests
import scipy.misc


def _get_url_content(url):
    """ Return bytes of response content for specified URL. """
    return requests.get(url).content


def _load_img_bytes_in_memory(content):
    """ Use in-memory bytes buffer to store image bytes content instead of real file usage. """
    return io.BytesIO(content)


def _get_array_from_img_file(stream):
    """
    Return an array obtained by reading the image file like object (e.g. stream, BytesIO, etc)
    Uses PIL to read an image.
    """
    return scipy.misc.imread(stream)


def get_img(url):
    """ Load image as an array (scipy.misc.imread) from specified url. """
    bytes_content = _get_url_content(url)
    stream = _load_img_bytes_in_memory(bytes_content)
    img_array = _get_array_from_img_file(stream)
    return img_array


def is_equal_images(img1, img2):
    """ Calculate the image difference. Return True if images are equal, otherwise - False."""
    diff_array = img1 - img2  # elementwise for scipy arrays
    flatten_array = diff_array.ravel()
    is_equal = not sum(abs(flatten_array))  # sum of totally equal images = 0
    return is_equal
