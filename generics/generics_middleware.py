


class MessageAll(object):
    """ Messages all pages"""

    def process_template_response(self, request, response):

        msg = request.user.messages_set.flat_field_list_filtered(field='msg',criteria={})

        if msg:
            response.context_data['user_messages'] = msg

        return response