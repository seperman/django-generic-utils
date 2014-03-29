# from django.utils.safestring import mark_safe



class MessageAll(object):
    """ Messages all pages"""

    def process_template_response(self, request, response):

        # messaging only users who have logged in. We can't message anonymous users.
        if request.user.is_authenticated():
            criteria = {"status_of_user_messages__akhnowledge_date__isnull":True}
            msg = request.user.messages_of_user.flat_field_list_filtered(fields=('id', 'msg', 'button_txt',), criteria=criteria, output="list_of_dict")
            if msg:
                response.context_data['user_messages'] = msg
            #     msg[0] = mark_safe("""%s 
            #             <form id="confirm_msg" action="" method="post">
            #             <input type="hidden" name="csrfmiddlewaretoken" value="%s">
            #             <input type="submit" class="grp-button grp-default" name="_ok" value="Ok"/>
            #             </form>
            #             """ % (msg[0], request.META['CSRF_COOKIE']) )


        return response