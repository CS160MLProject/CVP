"""OCR_Helper Operation

OCR_Helper operations module currently contains functions for the following:
- assemble_word
- find_word_location
- text_within

USAGE
-----

$ python cvp/features/ocr_helper.py

"""
# Standard Dist
import coloredlogs
import logging
import os

# Third Party Imports

# Project Level Imports

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


def assemble_word(word):
    """Join characters into a complete word

    Usage:

    >>> from cvp.features.ocr_helper import assemble_word
    >>> assembled_word = assemble_word(word)

    Args:
        word (google.cloud.vision_v1.types.text_annotation.Word):

    Returns:
        assembled_word (str): a complete word
    """
    assembled_word = ""
    for symbol in word.symbols:
        assembled_word += symbol.text
    return assembled_word


def find_word_location(document, word_to_find):
    """Find the target word's location in the image

    Usage:

    >>> from from cvp.features.ocr_helper import find_word_location
    >>> location = find_word_location(document, word_to_find)

    Args:
        document (google.cloud.vision_v1.types.text_annotation.TextAnnotation): json file of the image
        word_to_find (str): target word

    Return:
        word.bouding_box (google.cloud.vision_v1.types.geometry.BoundingPoly): Position (x,y) of the word in the image
    """
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    assembled_word = assemble_word(word)
                    if assembled_word == word_to_find:
                        return word.bounding_box


def text_within(document, x1, y1, x2, y2):
    """Find the target text within the given boundary

    Usage:

    >>> from cvp.features.ocr_helper import text_within
    >>> text = text_within(document, x1, y1, x2, y2)

    Args:

        document (google.cloud.vision_v1.types.text_annotation.TextAnnotation): json file of the image
        x1 (int): lowest x position of the boundary
        y1 (int): lowest y position of the boundary
        x2 (int): highest x position of the boundary
        y2 (int): highest y position of the boundary

    Returns:
        text (str): the word within the boundary, None if boundary is empty
    """
    text = ""
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        min_x = min(symbol.bounding_box.vertices[0].x, symbol.bounding_box.vertices[1].x,
                                    symbol.bounding_box.vertices[2].x, symbol.bounding_box.vertices[3].x)
                        max_x = max(symbol.bounding_box.vertices[0].x, symbol.bounding_box.vertices[1].x,
                                    symbol.bounding_box.vertices[2].x, symbol.bounding_box.vertices[3].x)
                        min_y = min(symbol.bounding_box.vertices[0].y, symbol.bounding_box.vertices[1].y,
                                    symbol.bounding_box.vertices[2].y, symbol.bounding_box.vertices[3].y)
                        max_y = max(symbol.bounding_box.vertices[0].y, symbol.bounding_box.vertices[1].y,
                                    symbol.bounding_box.vertices[2].y, symbol.bounding_box.vertices[3].y)

                        if min_x >= x1 and max_x <= x2 and min_y >= y1 and max_y <= y2:
                            text += symbol.text

                    text += ' '

        return text.strip()