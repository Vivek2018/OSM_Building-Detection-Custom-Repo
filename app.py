import backend
import imagery
import os
import BuildingDetectionFromClick as bdfc
import geolocation
import PIL.ImageOps
import cv2
import numpy
import json
import building_detection_v2

from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, send_file

app = Flask(__name__)

imd = None


def result_to_dict(result):
    info = {}
    for k, v in result.items():
        info[k.lower()] = v
    return info


@app.route('/', methods=['POST', 'GET'])  # base page that loads up on start/accessing the website
def login():  # this method is called when the page starts up
    error = None
    if request.method == 'POST':
        result = request.form
        info = result_to_dict(result)
        status = backend.user_sign_in(info)
        if status:
            flash('You successfully made a new account')
            return redirect(url_for("home"))
        else:
            error = "Account does not exist"

    return render_template('Login.html', error=error)


@app.route('/home/')
def home():
    # x = send_from_directory("../templates/", "DisplayMap.html", as_attachment=True)
    # print(x)
    # return send_from_directory('./../templates/', 'DisplayMap.html')
    return render_template('DisplayMap.html')

@app.route('/home/deleterect', methods=['POST'])
def delete_rect():
    if request.method == 'POST':
        result = request.form
        info = result_to_dict(result)
        
        # Delete the rectangle with this ID
        rect_id = int(info['rect_id'])
        building_detection_v2.delete_rect(rect_id)
        
    return "Success"

@app.route('/home/mapclick', methods=['POST'])
def mapclick():
    if request.method == 'POST':
        result = request.form
        info = result_to_dict(result)

        lat = float(info['lat'])
        long = float(info['long'])
        zoom = int(info['zoom'])

        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(lat, long, zoom)

        # find x, y
        x, y = geolocation.deg_to_tilexy(lat, long, zoom)

        # Get those tiles
        backend_image = imd.get_tiles_around(xtile, ytile, zoom)
        # backend_image.show()
        backend_image = PIL.ImageOps.grayscale(backend_image)
        # backend_image.show()

        # create a rectangle from click
        # rect_data includes a tuple -> (list of rectangle references to add/draw, list of rectangle ids to remove)
        rect_id, rect_points, rectangles_id_to_remove = building_detection_v2.detect_rectangle(backend_image, xtile, ytile, lat, long, zoom)

        # update OpenStreetMap

        # node list keeps track of all nodes for the purpose of eventually creating a way (area) amongst the nodes
        # to update to OpenStreetMap
        node_list = []
        api = backend.sign_in()
        for coordinates in rect_points:
            lat = coordinates[0]
            long = coordinates[1]
            node = backend.node_create(api, lat, long, comment="Full stack node create test")
            node_list.append(node)
        backend.way_create(api, node_list, comment="Full stack way create test")

        # OpenStreetMap part over

        json_post = {"rectsToAdd": [{"id": rect_id,
                                    "points": rect_points}],
                     "rectsToDelete": {"ids": rectangles_id_to_remove}
                            }

        return json.dumps(json_post)


@app.route('/NewAccount/', methods=['GET', 'POST'])  # activates when create a new account is clicked
def new_account():
    error = None
    if request.method == 'POST':  # if the user hits the submit button. post is called
        result = request.form
        info = result_to_dict(result)
        status = backend.create_user(info)
        if status:  # true condition
            flash('You successfully made a new account')
            return redirect(url_for('home'))
        else:  # false condition
            error = "account already exists"
        return redirect(url_for('login'))

    return render_template('/NewAccount.html', error=error)  # links to the create a new account page


@app.route('/home/imagery/<zoom>/<x>/<y>.png', methods=['GET'])
def imagery_request(zoom, x, y):
    fname = imd.get_tile_filename(x, y, zoom)
    if not os.path.isfile(fname):
        imd.download_tile(x, y, zoom)
    return send_file(fname, mimetype="image/png")


def start_webapp(imagery_downloader):
    """Starts the Flask server."""
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    global imd
    imd = imagery_downloader

    app.debug = True
    app.run()
