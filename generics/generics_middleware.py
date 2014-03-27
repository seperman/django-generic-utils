from django.utils.safestring import mark_safe



class MessageAll(object):
    """ Messages all pages"""

    def process_template_response(self, request, response):

        msg = request.user.messages_set.flat_field_list_filtered(field='msg', criteria={}, output="list_of_strings")


        if msg:
            msg[0] = mark_safe("""%s 
                    <form id="confirm_msg" action="" method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="%s">
                    <input type="submit" class="grp-button grp-default" name="_ok" value="Ok"/>
                    </form>
                    """ % (msg[0], request.META['CSRF_COOKIE']) )

            response.context_data['user_messages'] = msg

        return response