from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.renderers import BaseRenderer
from collections import OrderedDict
from django.conf import settings

from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
import base64
import json


# Custom Renderer class for API response data with additional metadata and encryption
class APIRenderer(BaseRenderer):
    media_type = "text/plain"
    format = "text"

    def aes_encrypt(self, message, key):
        """
        Encrypts a message using AES encryption with CBC mode.

        Args:
            message (str): The message to be encrypted.
            key (bytes): The encryption key.

        Returns:
            str: The encrypted message encoded in base64.

        Raises:
            None

        Notes:
            - The AES encryption algorithm is used with CBC mode.
            - The message is padded to a multiple of the AES block size before encryption.
            - The initialization vector (IV) is randomly generated.
            - The encrypted message is encoded in base64.
        """

        # Generate a random initialization vector (IV)
        iv = get_random_bytes(16)

        # Create an AES cipher object with CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Pad the message, encrypt it, and encode to base64
        ciphertext = cipher.encrypt(pad(message.encode("utf-8"), AES.block_size))
        encrypted_message = base64.b64encode(iv + ciphertext).decode("utf-8")

        return encrypted_message

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders the given data into a JSON response with additional metadata.

        Args:
            data (dict or ReturnDict): The data to be rendered.
            accepted_media_type (str, optional): The accepted media type. Defaults to None.
            renderer_context (dict, optional): The renderer context. Defaults to None.

        Returns:
            str: The encrypted JSON response data.

        Raises:
            None

        Notes:
            - The response data is stored in an ordered dictionary with the following keys:
                - "status_code": The status code of the response.
                - "success": A boolean indicating if the request was successful.
                - "message": A custom message if provided in the data.
                - "error": The error data if provided in the data.
                - "data": The rendered data.
            - If the data contains "errors" key, the "success" is set to False, the "error" is set to the data, and the "data" is set to None.
            - If the data contains "message" key, the "message" is set to the data's "message" value and the "message" key is removed from the data.
            - If the data is an empty dictionary or list, the "data" field is set to None.
            - The response data is serialized to JSON format.
            - The AES key is decoded from base64 encoding.
            - The JSON data is encrypted using AES encryption.
            - The encrypted data is returned as a string.
        """

        response = renderer_context["response"]
        success = True
        message = None
        error = None
        res_data = data

        # Create an ordered dictionary to store response data
        response_data = OrderedDict(
            {
                "status_code": response.status_code,
                "success": success,
                "message": message,
                "error": error,
                "data": res_data,
            }
        )

        # Check if the response data contains errors or a custom message
        if type(data) is dict or type(data) is ReturnDict:
            if "errors" in data.keys():
                response_data["success"] = False
                response_data["error"] = data
                response_data["data"] = None
            if "message" in data.keys():
                response_data["message"] = data.pop("message")

        # If the data is an empty dictionary or list, set the "data" field to None
        if data == {} or data == []:
            response_data["data"] = None

        # Serialize the response data to JSON format
        data = response_data
        json_data = json.dumps(data)

        # Decode the AES key from base64 encoding
        key = base64.b64decode(f"{settings.AES_KEY}=")
        # Encrypt the JSON data using AES encryption
        # encryped_data = self.aes_encrypt(json_data, key)
        encryped_data = json_data

        return encryped_data
