from website import create_app
from flask import Flask
# from flask_debugtoolbar import DebugToolbarExtension
import time

print("+++++ Starting create_app: +++++")
app = create_app()
app.debug = True
# toolbar = DebugToolbarExtension(app)

if __name__ == '__main__': # will only execute if this file is run directly, not when it is imported!
    print('+++++ Starting app.run: +++++')
    app.run(host="0.0.0.0")