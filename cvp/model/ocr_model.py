"""OCR Model

OCR Model operations module currently contains OCR class and the following functions:
- predict

USAGE
-----

$ python cvp/model/ocr_model.py

"""

# Standard Dist
import coloredlogs
import logging
import os
import io

# Third Party Imports
from google.cloud import vision

# Project Level Imports
from cvp.features.ocr_helper import text_within

COORDINATE = {
    "last": [38, 212, 450, 323],
    'first': [451, 212, 1000, 322],
    'mi': [1001, 212, 1100, 322],
    'dob': [38, 304, 560, 408],
    'ssn': [562, 303, 1100, 410],
    'product_1': [200, 530, 580, 600],
    'date_1': [600, 470, 810, 570],
    'site_1': [820, 530, 1100, 600],
    'product_2': [200, 620, 580, 700],
    'date_2': [600, 600, 810, 680],
    'site_2': [820, 620, 1100, 700]
}


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

GOOGLE_CREDENTIALS_KEY = r'Google_Cloud_Vison_Key.json'
FOLDER_PATH = 'dataset/raw/vaccine_record_photos'


class OCR_Model(object):
    def __init__(self):
        if not os.path.exists(GOOGLE_CREDENTIALS_KEY):
            logger.warning(f"File {GOOGLE_CREDENTIALS_KEY} was not found. Current dir: {os.getcwd()}")
            raise FileNotFoundError("Could not initialize OCR_Model because Google Credentials Key not found.")

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CREDENTIALS_KEY
        self.client = vision.ImageAnnotatorClient()

    def predict(self, photo_path: str):
        """Get the model prediction on the data point

        Usage

        >>> from cvp.model.ocr_model import OCR_Model
        >>> model = OCR_Model()
        >>> model.predict(photo_path)

        Args:
            photo_path (str): Path to data point

        Returns:
            info (dict): user's information; order of dict - last, first, mi, dob, ssn, 1st product, 1st date, 1st site,
                2nd product, 2nd date, 2nd site
        """
        logger.info("Preparing ...")
        relative_path = os.path.join(FOLDER_PATH, photo_path)
        if not os.path.exists(relative_path):
            raise FileNotFoundError(f"File {relative_path} was not found. Current dir: {os.getcwd()}")

        with io.open(relative_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        logger.info('Loading image into OCR Model ...')
        response = self.client.document_text_detection(image=image)

        document = response.full_text_annotation
        if response.error.message:
            raise Exception(f'{response.error.message}\nFor more info on error messages, check: '
                            f'https://cloud.google.com/apis/design/errors')

        logger.info('Finding keywords ...')
        info = dict()
        for key, value in COORDINATE.items():
            info[key] = text_within(document, value[0], value[1], value[2], value[3])
            if key == 'date_1' or key == 'date_2':
                info[key] = info[key].replace(',', '/')

            logger.debug(f"{key}: {info[key]}")

        logger.info('Finished!')
        info