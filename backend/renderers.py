from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.renderers import BaseRenderer
from collections import OrderedDict
from django.conf import settings

from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
import base64
import json


class APIRenderer(BaseRenderer):
    media_type = "text/plain"
    format = "text"

    def aes_encrypt(self, message, key):
        # Generate a random initialization vector (IV)
        iv = get_random_bytes(16)

        # Create an AES cipher object with CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Pad the message, encrypt it, and encode to base64
        ciphertext = cipher.encrypt(pad(message.encode("utf-8"), AES.block_size))
        encrypted_message = base64.b64encode(iv + ciphertext).decode("utf-8")

        return encrypted_message

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]
        success = True
        message = None
        error = None
        res_data = data

        response_data = OrderedDict(
            {
                "status_code": response.status_code,
                "success": success,
                "message": message,
                "error": error,
                "data": res_data,
            }
        )

        if type(data) is dict or type(data) is ReturnDict:
            if "errors" in data.keys():
                response_data["success"] = False
                response_data["error"] = data
                response_data["data"] = None
            if "message" in data.keys():
                response_data["message"] = data.pop("message")

        if data == {} or data == []:
            response_data["data"] = None

        data = response_data
        json_data = json.dumps(data)
        key = base64.b64decode(f"{settings.AES_KEY}=")
        # encryped_data = self.aes_encrypt(json_data, key)
        encryped_data = json_data

        return encryped_data
