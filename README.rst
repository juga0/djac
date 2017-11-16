=====
DjAC
=====

DjAC is a Django app to manage AC models and as a demo.
WIP

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "ac" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'ac',
    ]

2. Run `python manage.py migrate` to create the ac models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

4. Visit http://127.0.0.1:8000/admin/ to manage the models.
