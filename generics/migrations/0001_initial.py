# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CeleryTasks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.CharField(unique=True, max_length=50, verbose_name=b'task id', db_index=True)),
                ('status', models.CharField(default=b'waiting', max_length=40, verbose_name=b'state', db_index=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Creation Date')),
                ('start_date', models.DateTimeField(null=True, verbose_name=b'Start Date')),
                ('end_date', models.DateTimeField(default=None, null=True, verbose_name=b'End Date')),
                ('key', models.CharField(default=b'', max_length=50, verbose_name=b'Task Blocking Key', db_index=True, blank=True)),
                ('user', models.ForeignKey(related_name=b'tasks_of_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Task History',
                'verbose_name_plural': 'Tasks History',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('msg', models.CharField(default=b'Message', max_length=255, verbose_name=b'Message')),
                ('msg_code', models.CharField(unique=True, max_length=30, verbose_name=b'Message Unique Code', db_index=True)),
                ('button_txt', models.CharField(default=b'Ok', max_length=50, verbose_name=b'Button Text')),
                ('button_link', models.URLField(default=b'', verbose_name=b'Button Link', blank=True)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessagesStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('akhnowledge_date', models.DateTimeField(default=None, null=True, editable=False)),
                ('message', models.ForeignKey(related_name=b'status_of_user_messages', to='generics.Messages')),
                ('user', models.ForeignKey(related_name=b'status_of_messaged_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='messagesstatus',
            unique_together=set([('message', 'user')]),
        ),
        migrations.AddField(
            model_name='messages',
            name='users',
            field=models.ManyToManyField(help_text=b'Users who need to akhnowledge this message', related_name=b'messages_of_user', through='generics.MessagesStatus', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
