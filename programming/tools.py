from pyzbar.pyzbar import decode
from PIL import Image

class my_class(object):
    pass

class questionnaireTools(object):
    def decode_qr_code(self, file_path):
        try:
            with Image.open(file_path) as img:
                decoded_objects = decode(img)
                if decoded_objects:
                    return decoded_objects[0].data.decode('utf-8')
                else:
                    return None
        except Exception as e:
            print(f"二维码识别错误: {e}")
            return None




