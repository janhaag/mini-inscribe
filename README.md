mini-inscribe
=============

This is a tiny webinscribe system, designed for absolute simplicity.
The python script runs under CGI (yes - that plain, old and slow
interface virtually any server supports without much setup).
It reads an associated form.html containing the actual user-visible
components and stores its sqlite-database in '''db/results.db'''.

In order to get everything set up, make sure your webserver has access
to everything it needs (especially write access to the database), then
point your web browser to '''http://host/path/to/index.py?system.init'''
and fill the form with representative values. These will only be used
to deduce the types, never actually stored.

Now, every time the script is run (no query string magic neccessary) it
will present you with the form and on submission store the values provided.

To enter query mode, go to '''http://host/path/to/index.py?system.query'''.
