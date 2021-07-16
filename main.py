from website import create_app
from flask import Flask
import time

print("+++++ Starting create_app: +++++")
app = create_app()

if __name__ == '__main__': # will only execute if this file is run directly, not when it is imported!
    print('+++++ Starting app.run: +++++')
    app.run(debug=True, host="0.0.0.0")