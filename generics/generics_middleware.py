from django.core.cache import cache



class MessageAll(object):
    """ Messages all pages"""

    def process_template_response(self, request, response):

        # has to be a list??
        msg = cache.get("messageall")


        if msg:

            try:

                response.context_data['messages'].append(msg)
            
            except KeyError:
            
                response.context_data['messages'] = msg


        return response