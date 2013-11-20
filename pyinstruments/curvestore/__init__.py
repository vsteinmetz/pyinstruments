#http://stackoverflow.com/questions/4534992/place-to-set-sqlite-pragma-option-in-django-project
#from django.db.backends.signals import connection_created
#def activate_foreign_keys(sender, connection, **kwargs):
#    """Enable integrity constraint with sqlite."""
#    print "db dirty stuff about to be done"
#
#    if connection.vendor == 'sqlite':
#        cursor = connection.cursor()
#        cursor.execute('PRAGMA synchronous = 0')
#        cursor.execute('PRAGMA journal_mode = WAL')
#        print "db dirty stuff done"

#connection_created.connect(activate_foreign_keys)