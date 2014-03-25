from django.core.management.base import BaseCommand, CommandError
from django.core.management import execute_from_command_line
from south.models import MigrationHistory
from django.conf import settings

class Command(BaseCommand):
    """
    Applies fake first migration for app[s] that already has migrations.
    Use it when you have the migrations in the repo but don't have applied them to the DB yet.
    Example: You have made changes locally and the local DB works. Now you want to do those changes on prod DB
    If you just run south migration, it is not going to work since it needs the first migration to be faked.
    So you use this management command to create a fake first migration for the app and it does it only once.
    That is the whole point of it. It won't do a fake migration if the app is already supported by south in the DB.
    Unlike the normal ./migration 0001 --fake which will apply it again and again and will mess up your DB. 
    """

    args = '<command to run [app1, app2,... ]>'
    help = ('Applies first fake migration for app[s]')


    def handle(self, *args, **options):
        # check XML file
        if not args:
            raise CommandError('Must specify the app[s] to do fake migrations on')
        
        apps = args
        apps_string = (" ").join(args)

        apps_migrated = set(MigrationHistory.objects.values_list('app_name', flat=True))

        apps_installed_in_django = settings.INSTALLED_APPS

        for app in apps:
            if app not in apps_migrated:
                if app in apps_installed_in_django:
                    print "doing fake migration on %s" % app
                    print __name__
                    print __file__
                    argv = ['manage.py', 'migrate', app, '0001', '--fake',]  #make sure this is a list and not a tuple!! It won'r work as a tuple
                    execute_from_command_line(argv)
                else:
                    print "app %s is not installed in Django settings" % app

            else:
                print "app %s is already migrated" % app

        