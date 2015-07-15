import psycopg2
import os
import urlparse
from flask import Flask, render_template, jsonify, send_from_directory, g, request
from time import time
import data

MAPBOX_TOKEN = "pk.eyJ1Ijoic2NvdHRvZnRoZXNjaSIsImEiOiJNZklwOUdNIn0.9cbLc1uMc3awc8_vWFMHsA"
MAPBOX_SECRET = "sk.eyJ1Ijoic2NvdHRvZnRoZXNjaSIsImEiOiJPbElNT1owIn0.OmMclM1IhPSLzdXlZOQQ4Q"
MAPBOX_EMAIL = "scottallencambo@gmail.com"
MB_PROJECT_ID = "scottofthesci.mm6je637"
'''Example taken from http://codepen.io/asommer70/blog/serving-a-static-directory-with-flask'''
app = Flask(__name__)
app.debug = True
'''
def connect_to_database():
				urlparse.uses_netloc.append("postgres")
				url = urlparse.urlparse(os.environ["DATABASE_URL"])

				conn = psycopg2.connect(
												database=url.path[1:],
												user=url.username,
												password=url.password,
												host=url.hostname,
												port=url.port
												)
				print "connection to postgres successfully retrieved"
				return conn

def get_db():
				db = getattr(g, '_database', None)
				if db is None:
								db = g._database = connect_to_database()
				return db

@app.teardown_appcontext
def close_connection(exception):
				db = getattr(g, '_database', None)
				if db is not None:
								db.close()

def get_sessions():
				sess_q = "SELECT DISTINCT(session) FROM locations"
				cur = get_db().cursor()
				cur.execute(sess_q)
				rows = cur.fetchall()
				cur.close()
				return [row[0] for row in rows]

def get_locations(session):
				loc_q = """SELECT * FROM locations WHERE session='%s'""" % session
				cur = get_db().cursor()
				cur.execute(loc_q)
				rows = cur.fetchall()
				print "%s rows returned" % len(rows)
				cur.close()
				stages = set([l[5] for l in rows])
				locs_by_stage = {s : [] for s in stages}
				for row in rows:
								locs_by_stage[row[5]].append((row[2],row[3]))
				return locs_by_stage

def get_centerLatLon():
				center_lat_q = """SELECT AVG(latitude) FROM locations"""
				cur = get_db().cursor()
				cur.execute(center_lat_q)
				center_lat = cur.fetchone()[0]

				center_lon_q = """SELECT AVG(longitude) FROM locations"""
				cur = get_db().cursor()
				cur.execute(center_lon_q)
				center_lon = cur.fetchone()[0]

				return center_lat, center_lon
'''
@app.route('/')
def send_index():
				sessions = data.get_sessions()
				center_lat, center_lon = data.get_centerLatLon()
				return render_template("map.html",
															 sessions=sessions,
															 center_lat=center_lat,
															 center_lon=center_lon,
															 token=MAPBOX_TOKEN,
															 mb_id=MB_PROJECT_ID)

@app.route('/<path:path>')
def send_static_html(path):
				return send_from_directory('static/static_html', path)

@app.route('/js/<path:path>')
def send_js(path):
				return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
				return send_from_directory('static/css', path)

@app.route('/get_session/<path:session>')
def session_request(session):
				session_locations = data.get_locations(session)
				stages = list(set([s['stage'] for s in session_locations]))
				locs_by_stage = {s : [] for s in stages}
				for l in session_locations:
					locs_by_stage[l['stage']].append(l)
				return jsonify({"locations" : locs_by_stage})

@app.route('/get_loop/<path:session>')
def loop_request(session):
	# get session
	session_locations = data.get_locations(session)
	# get loop set
	loop_set = data.checkForLoop(session_locations)
	# make list of loop set objectIds
	if loop_set != None:
		loop_objIds = [l['objectId'] for l in loop_set]
		for sl in session_locations:
			if sl['objectId'] in loop_objIds:
				sl['in_loop'] = True
			else:
				sl['in_loop'] = False
		return jsonify({"type" : "loops", "locations" : session_locations})
	else:
		return jsonify({"error" : "No loops found", "locations" : session_locations})
	# add an "in_loop" : True field for each location in loop set

if __name__ == "__main__":
				host_loc = "127.0.0.1"
				print "Running server at %s" % host_loc
				app.run(host=host_loc)
