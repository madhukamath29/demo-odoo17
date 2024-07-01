from odoo import http
from odoo.exceptions import ValidationError
import logging
from io import BytesIO
import base64
logger = logging.getLogger()
try:
    import zxingcpp
    import numpy as np
    from PIL import Image,ImageEnhance
except:
    logger.error("Unable to import the required libraries for barcode processing. Try running: pip install zxingcpp numpy Pillow")
class MyController(http.Controller):

    @http.route('/code_scanner/scan', type="json", auth='user')
    def barcode_image_scan(self, **kw):
        try:
            image_data = kw['image_data']
            image = Image.open(BytesIO(base64.b64decode(image_data))).convert("L")
            image = ImageEnhance.Contrast(image).enhance(1.5)
            image = ImageEnhance.Sharpness(image).enhance(1.5)
            image_nparray = np.array(image)
            results = zxingcpp.read_barcodes(image_nparray)
            if len(results)>0:
                scanned_code = results[0].text
                status = "success"
            else:
                status = "unable to find any code"
                scanned_code = ''
            return {'status': status, 'scanned_code': scanned_code,}
        
        except Exception as e:
            msg = "Unable to process the images! Are you sure you have installed the required libraries: numpy, Pillow, zxingcpp"
            logger.error(str(e))
            return {'status': msg, 'scanned_code': ''}
    
