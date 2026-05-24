"""WSGI entry point for PythonAnywhere.

In the PythonAnywhere web app config, set the WSGI file to import `application`
from this module. Example WSGI file content:

    import sys
    path = '/home/<your-username>/calc'
    if path not in sys.path:
        sys.path.insert(0, path)
    from wsgi import application
"""
from app import app as application

if __name__ == "__main__":
    application.run()
