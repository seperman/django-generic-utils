# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from time import sleep

from celery import shared_task, current_task

# from celery.task.control import revoke
from generics.models import CeleryTasks

try:
    err_msg_length = settings.GENERICS_ERR_MSG_LENGTH
except AttributeError:
    err_msg_length = None


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class celery_progressbar_stat(object):
    """ updates the progress bar info for the task.
        
        Example usage:
        from celery import current_task
        from generics.tasks import celery_progressbar_stat 

        c = celery_progressbar_stat(current_task, user_id)
        c.percent=10

        c.msg="FINISHED"

        This will automatically update the progressbar msg
    """
    def __init__(self, task, user_id, cache_time=200):
        self.task_id = task.request.id
        self.task_stat_id = "celery-stat-%s" % self.task_id
        self.cache_time = cache_time
        self.result={'msg':"IN PROGRESS", 'sticky_msg':'', 'err':'', 'progress_percent': 0, 'is_killed':False, 'user_id':user_id}
        self.last_err = ""

        # Normally we want to have created the CeleryTasks object before even the task is run. Reason: if the task is in the queue, we want to know that.
        # In that case these lines are not even run yet! However, we need some delay here before the task is created and the CeleryTasks object created
        # so we can get the object. Otherwise it can't "get" the object and it thinks it doesn't exist
        for j in range(1,10):
            sleep(.3)
            try:
                self.celery_task_history_obj = CeleryTasks.objects.get(task_id = self.task_id)
                break
            except CeleryTasks.DoesNotExist:
                pass

        if j >= 9:
            raise Exception("Could not get the celery_task_history_obj")

        self.celery_task_history_obj.status="active"
        self.celery_task_history_obj.start_date=timezone.now()
        self.celery_task_history_obj.save(update_fields=["status", "start_date"])
        now = timezone.now()
        try:
            CeleryTasks.objects.filter(creation_date__lte=now-timezone.timedelta(hours=24), status__in=["active", "waiting"]).update(status="must have failed")
            CeleryTasks.objects.filter(creation_date__lte=now-timezone.timedelta(hours=600)).delete()
        except:
            logger.error("Error in cleaning up CeleryTasks History", exc_info=True)

    def __enter__(self):
        return self

    def __exit__(self, exit_type, exit_value, traceback):

        # logger.info("!!!Exiting Progress bar. Type: %s  ----  Value: %s" % (exit_type,exit_value) )
        if exit_type == SystemExit:
            self.celery_task_history_obj.status="killed"
            self.is_killed = True  #killed by error but we still set is_killed to true
            self.msg = "Terminated by the user."
        elif exit_type:
            self.celery_task_history_obj.status="error"
            self.is_killed = True  #killed by error but we still set is_killed to true
        else:
            self.celery_task_history_obj.status="finished"
        
        self.celery_task_history_obj.end_date=timezone.now()
        self.celery_task_history_obj.save(update_fields=["status", "end_date"])

    def get_percent(self):
        return self.result["progress_percent"]

    def set_percent(self, val):
        self.result["progress_percent"] = val
        self.set_cache()

    def get_msg(self):
        return self.result["msg"]

    def set_msg(self, val):
        self.result["msg"] = val
        self.set_cache()

    def get_err(self):
        return self.result["err"]

    def set_err(self, val):
        self.result["err"] = val
        self.set_cache()

    def get_sticky_msg(self):
        return self.result["sticky_msg"]

    def set_sticky_msg(self, val):
        self.result["sticky_msg"] = val
        self.set_cache()

    def get_is_killed(self):
        return self.result["is_killed"]

    def set_is_killed(self, val):
        self.result["is_killed"] = val
        self.set_cache()


    def set_cache(self):
        cache.set(self.task_stat_id, self.result, self.cache_time)

    def raise_err(self, msg, e=None, obj=None, field=None, fatal=False, sticky_msg=""):
        # msg is what the user sees. e is the actual error that was raised.
        # We check to see if an error is not already caught. Since we don't want to re-raise the same error up.
        # However you have to raise the error yourself in your code. e is basically Exception as e

        if sticky_msg:
            self.sticky_msg = sticky_msg
        elif fatal:
            self.sticky_msg = msg
        
        if fatal:
            self.is_killed = True
            raise SystemExit
            

        # This is to avoid raising the same error again as we raise exception and catching and re-raising it
        if e == self.last_err:
            return "The error was just raised"
        else:
            self.last_err = e

        self.msg = msg



        if obj and field:
            current_err_fields = getattr(obj, "err_fields")
            field += " "
            
            if field not in current_err_fields:
                current_err_fields = "%s %s" % (field, current_err_fields)

                try:
                    setattr(obj, "err_fields", current_err_fields)
                    setattr(obj, "is_fine", False)
                    if err_msg_length:
                        setattr(obj, "err_msg", msg[:err_msg_length])
                    else:
                        setattr(obj, "err_msg", msg)
                    
                    obj.save(update_fields=["err_fields", "is_fine", "err_msg", ])
                except:
                    self.msg = "Unable to set object's error fields. The model is not properly set up."

        if msg[:3].lower() == "err":
            logger.error("generics_raiseerr msg: %s, e: %s" % (msg, e) )
            self.err = msg
        elif msg[:4].lower() == "warn":
            logger.warning("generics_raiseerr msg: %s, e: %s" % (msg, e) )
            self.err = msg
        else:
            logger.info("generics_raiseerr msg: %s, e: %s" % (msg, e) )

        print(msg)


    def clean_err(self, obj, field, save=True):
        """
        Cleans the error fields on the object
        """
        current_err_fields = getattr(obj, "err_fields")

        if field == "all":
            current_err_fields = ""
        else:
            field += " "
            current_err_fields = current_err_fields.replace(field, "")

        try:
            setattr(obj, "err_fields", current_err_fields)
            setattr(obj, "err_msg", "")
            # It will only remove the is_fine flag if there is no error field left
            if not current_err_fields:
                setattr(obj, "is_fine", True)

            if save:
                obj.save(update_fields=["err_fields", "is_fine", "err_msg", ])
                msg = "obj err fields cleanup and saving obj %s" % obj.pk
                logger.info(msg)
                print(msg)
            else:
                msg = "obj err fields cleanup but NOT saving obj %s" % obj.pk
                logger.info(msg)
                print(msg)

        except:
            self.msg = "Unable to set object's error fields. The model is not properly set up."
            logger.error(self.msg)
            print(self.msg)

    percent = property(get_percent, set_percent,) 
    msg = property(get_msg, set_msg,)
    err = property(get_err, set_err,)
    sticky_msg = property(get_sticky_msg, set_sticky_msg,)
    is_killed = property(get_is_killed, set_is_killed,)




@shared_task
def test_progressbar(user_id=1):
    from time import sleep
    from django.utils.safestring import mark_safe
    
    with celery_progressbar_stat(current_task, user_id) as c_stat:
        c_stat.msg = "Tesing"

        for i in range(0,101):
            sleep(.3)
            if i==6:
                logger.info("test progress bar at 6%")
                c_stat.raise_err("Error: This error should show up", e="test_err", sticky_msg=mark_safe("<p>TEST STICKY ERROR.</p><img src='https://cdn0.iconfinder.com/data/icons/cosmo-medicine/40/test-tube_2-128.png'>"))

            if i==16:
                logger.info("test progress bar at 16%")
                c_stat.raise_err("Error again: This error should show up too", e="test_err2")


            if i==22:
                logger.info("test progress bar at 22%")
                c_stat.raise_err("Error: This error should show NOT up since it is raised before", e="test_err2")

            c_stat.percent = i
