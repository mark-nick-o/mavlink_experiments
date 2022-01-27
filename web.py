# =====================================================================
#
#    web.py
#    Host a webserver which will provide url to the camera definitions 
#
# =====================================================================

import numpy as np

# ================= webserver ==========================================
#
# raspbian os
# sudo apt-get install python3-flask
# https://www.instructables.com/Python-WebServer-With-Flask-and-Raspberry-Pi/
# https://www.instructables.com/Reading-JSON-With-Raspberry-Pi/
# https://mjrobot.org/
#
# ubuntu
# pip install jsons
# pip install Flask
#
import json
from flask import Flask, render_template
#app = Flask(__name__)
app = Flask(__name__, template_folder='template')

#
# https://habr.com/ru/post/472126/ ref client server / alternative
#
   
@app.route('/take_a_photo')
def take_a_photo_handler():
    #if camera.ready:
    #res = saveOnePicture()
    res="/home/pi/cams/src/acp/sonyCam"
    return render_template('one_photo.html', photo_path=res, user="shithead")
    #return render_template('one_photo.html')
    #else:
    #    return "Failure to take picture"

@app.route('/cam_defs')
def send_cam_defs_handler():
    return render_template('alpha_cam_new.xml')


@app.route('/cam_default')
def send_cam_default_handler():
    return render_template('cam_default.xml')

if __name__ == '__main__':

    # run flask server
    app.run(host='0.0.0.0', port=80, debug=True) 
    
