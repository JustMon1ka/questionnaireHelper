from pyzbar.pyzbar import decode
from PIL import Image
import openai
from random import randint


class my_class(object):
    pass


class questionnaireTools(object):
    def __init__(self, apiKey, maxToken):
        self.apikey = apiKey
        self.proxy = {
            'http': 'http://localhost:7890',
            'https': 'http://localhost:7890'
        }
        openai.proxy = self.proxy
        openai.api_key = self.apikey
        self.maxToken = maxToken

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

    def getAIResponse(self, prompt):
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt + "请用全中文回答",
                max_tokens=int(self.maxToken),
                temperature=1
            )
        except Exception as e:
            print(e)

        # print(response)
        replyList = response.choices[0].text.split("\n")
        reply = replyList[len(replyList) - 1]
        print(reply)
        return reply

    def getSelections(self, total, choices, expectations):
        result = []
        choices = [int(char) for char in choices]
        selections = range(1, total + 1)
        otherSelections = [x for x in selections if x not in choices]
        for choice in choices:
            array = []  # 生成一个数组，1代表抽中choices中的某个数，0代表没有抽中
            for _ in range(expectations):
                array.append(True)
            for _ in range(100 - expectations):
                array.append(False)
            random = array[randint(0, 99)]
            if random:
                result.append(choice)
            else:
                result.append(otherSelections[randint(0, len(otherSelections) - 1)])

        return result
