import io

# Standard Dist
import pytest

# Third Party Imports
import google
from google.cloud import vision

# Project Level Imports
from cvp.features.ocr_helper import *
from cvp.model.ocr_model import OCR_Model


class TestOCRHelper():

    def test_assemble_word(self):
        # === Test Inputs ===#
        folder_path = 'tests/features'
        photo_path = 'Test.png'
        model = OCR_Model()
        with io.open(os.path.join(folder_path, photo_path), 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = model.client.document_text_detection(image=image)
        document = response.full_text_annotation

        # === Expected Outputs ===#
        expected = ['NO', 'PASSING', 'ZONE']

        # === Trigger Output ===#
        output = []
        for page in document.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        assembled_word = assemble_word(word)
                        assert isinstance(assembled_word, str)
                        output.append(assembled_word)

        for i in range(len(output)):
            assert output[i] == expected[i]

    def test_find_word_location(self):
        # === Test Inputs ===#
        folder_path = 'tests/features'
        photo_path = 'Test.png'
        model = OCR_Model()
        with io.open(os.path.join(folder_path, photo_path), 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = model.client.document_text_detection(image=image)
        document = response.full_text_annotation

        # === Expected Outputs ===#
        expected = [
            {'x': 21, 'y': 34},
            {'x': 61, 'y': 34},
            {'x': 61, 'y': 70},
            {'x': 21, 'y': 70}
        ]

        # === Trigger Output ===#
        location = find_word_location(document, 'NO')
        assert isinstance(location, google.cloud.vision_v1.types.geometry.BoundingPoly)

        for i in range(len(location.vertices)):
            assert location.vertices[i].x == expected[i].get('x')
            assert location.vertices[i].y == expected[i].get('y')

    def test_text_within(self):
        # === Test Inputs ===#
        folder_path = 'tests/features'
        photo_path = 'Test.png'
        model = OCR_Model()
        with io.open(os.path.join(folder_path, photo_path), 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = model.client.document_text_detection(image=image)
        document = response.full_text_annotation

        # === Expected Outputs ===#
        expected = 'ZONE'

        # === Trigger Output ===#
        text = text_within(document, x1=15, y1=115, x2=110, y2=160)

        assert isinstance(text, str)
        assert text == expected