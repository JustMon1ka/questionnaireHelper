from pyzbar.pyzbar import decode
from PIL import Image
import openai



class my_class(object):
    pass

class questionnaireTools(object):
    def __init__(self,apiKey,maxToken):
        self.apikey=apiKey
        self.proxy= {
            'http': 'http://localhost:7890',
            'https': 'http://localhost:7890'
        }
        openai.proxy = self.proxy
        openai.api_key = self.apikey
        self.maxToken = int(maxToken)

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

    def getAIResponse(self,prompt):
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt+"请用全中文回答",
                max_tokens=self.maxToken,
                temperature=1
            )
        except Exception as e:
            print(e)

        #print(response)
        replyList=response.choices[0].text.split("\n")
        reply=replyList[len(replyList)-1]
        print(reply)
        return reply




