from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.renderers import JSONRenderer
from collections import OrderedDict


class APIRenderer(JSONRenderer):
    '''
    Renderer which serializes to JSON.
    '''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        '''
        Render `data` into JSON, returning a bytestring.
        '''

        response = renderer_context['response']
        success = True
        message = None
        error = None
        res_data = data

        response_data = OrderedDict({
            'status_code': response.status_code,
            'success': success,
            'message': message,
            'error': error,
            'data': res_data,
        })

        if type(data) is dict or type(data) is ReturnDict:
            if 'errors' in data.keys():
                response_data['success'] = False
                response_data['error'] = data
                response_data['data'] = None
            if 'message' in data.keys():
                response_data['message'] = data.pop('message')

        if data == {} or data == []:
            response_data['data'] = None

        data = response_data
        return super().render(data, accepted_media_type, renderer_context)
