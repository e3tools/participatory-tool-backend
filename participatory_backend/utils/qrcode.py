import frappe

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, GappedSquareModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode import constants
import base64
from io import BytesIO

def get_qrcode(input_data, overlay_image=None):
    """Generate a QR Code
    Args:
        input_data: Data to generate QR Code for
        overlay_image: An image that can be overlaid on top of the QR Code. E.g your company logo. Defaults to None. 
    """
    qr = qrcode.QRCode(
        version=7,
        box_size=6,
        border=3,
        error_correction=constants.ERROR_CORRECT_H
    )
    qr.add_data(input_data)
    qr.make(fit=True)

    img = qr.make_image(image_factory=StyledPilImage)
    img = qr.make_image(image_factory=StyledPilImage, 
                        color_mask=RadialGradiantColorMask(back_color = (255,255,255), 
                        center_color = (70,130,180), edge_color = (0,0,0)), 
                        module_drawer=GappedSquareModuleDrawer(), 
                        eye_drawer=SquareModuleDrawer(), 
                        embeded_image_path=overlay_image
                        )
    temp = BytesIO()
    img.save(temp, "PNG")
    temp.seek(0)
    b64 = base64.b64encode(temp.read())
    return "data:image/png;base64,{0}".format(b64.decode("utf-8"))