from django.core.cache import cache

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

        c.state="FINISHED"

        This will automatically update the progressbar state
    """
    def __init__(self, task, user_id, cache_time=200):
        self.task_stat_id = "celery-stat-%s" % task.request.id
        self.cache_time = cache_time
        self.result={'state':"IN PROGRESS", 'progress_percent': 0, 'user_id':user_id}
        self.no_error_caught = True

    def get_percent(self):
        return self.result["progress_percent"]

    def set_percent(self, val):
        self.result["progress_percent"] = val
        self.set_cache()

    def get_state(self):
        return self.result["state"]

    def set_state(self, val):
        self.result["state"] = val
        self.set_cache()

    def set_cache(self):
        cache.set(self.task_stat_id, self.result, self.cache_time)

    def raise_err(self, msg):
        # We check to see if an error is not already caught. Since we don't want to re-raise the same error up.
        # However you have to raise the error yourself in your code
        if self.no_error_caught:
            self.no_error_caught = False
            self.state = msg
            logger.error(msg)

    percent = property(get_percent, set_percent,) 
    state = property(get_state, set_state,) 
