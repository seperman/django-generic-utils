# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CeleryTasks'
        db.create_table(u'generics_celerytasks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='waiting', max_length=40, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks_of_user', to=orm['auth.User'])),
            ('key', self.gf('django.db.models.fields.CharField')(default='', max_length=50, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'generics', ['CeleryTasks'])


    def backwards(self, orm):
        # Deleting model 'CeleryTasks'
        db.delete_table(u'generics_celerytasks')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'generics.celerytasks': {
            'Meta': {'object_name': 'CeleryTasks'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'db_index': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'waiting'", 'max_length': '40', 'db_index': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks_of_user'", 'to': u"orm['auth.User']"})
        },
        u'generics.messages': {
            'Meta': {'object_name': 'Messages'},
            'button_txt': ('django.db.models.fields.CharField', [], {'default': "'Ok'", 'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msg': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'msg_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'messages_of_user'", 'symmetrical': 'False', 'through': u"orm['generics.MessagesStatus']", 'to': u"orm['auth.User']"})
        },
        u'generics.messagesstatus': {
            'Meta': {'unique_together': "(('message', 'user'),)", 'object_name': 'MessagesStatus'},
            'akhnowledge_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status_of_user_messages'", 'to': u"orm['generics.Messages']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status_of_messaged_users'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['generics']