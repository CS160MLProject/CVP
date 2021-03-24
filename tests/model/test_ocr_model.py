import io

# Standard Dist
import pytest

# Third Party Imports
import google

# Project Level Imports
from cvp.model.ocr_model import OCR_Model


class TestOCRModel():

    def test_init(self):
        #=== Test Inputs ===#
        model = OCR_Model()

        assert isinstance(model.client, google.cloud.vision_v1.ImageAnnotatorClient)
        with pytest.raises(FileNotFoundError):
            model = OCR_Model('WRONG/PATH')

    def test_predict(self):
        #=== Test Inputs ===#
        FOLDER_PATH = 'tests/model'
        PHOTO = 'Vaccine.png'
        model = OCR_Model()

        #=== Expected Outputs ===#
        expected = {
            'last': 'Kujo',
            'first': 'Jotaro',
            'mi': 'J',
            'dob': 'July 27 , 1970',
            'ssn': '0195',
            'product_1': 'PFIZER - 1234',
            'date_1': '01/01/21',
            'site_1': 'TKYH Dr. Star',
            'product_2': 'PFIZER - 1234',
            'date_2': '01/30/21',
            'site_2': 'TKYH Dr. Dio'
        }

        #=== Trigger Output ===#
        info = model.predict(PHOTO, FOLDER_PATH)

        assert len(info) == 11

        for key, value in info.items():
            assert info[key] == expected[key]

        with pytest.raises(FileNotFoundError):
            info = model.predict(PHOTO, 'WRONG/PATH')

        with pytest.raises(Exception):
            info = model.predict(PHOTO, FOLDER_PATH, False)

