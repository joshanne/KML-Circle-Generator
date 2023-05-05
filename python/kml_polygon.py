import time
import math

from config import config

PI = math.pi

DEGREES = 180.0 / PI
RADIANS = PI / 180.0
EARTH_MEAN_RADIUS = 6371.0 * 1000

def to_earth(point):
    ''' convert [x,y,z] on unit sphere back to [long, lat] '''
    if (point[0] == 0.0):
        lon = PI / 2.0
    else:
        lon = math.atan(point[1]/point[0])
    lat = PI / 2.0 - math.acos(point[2])

    # select correct branch of arctan
    if (point[0] < 0.0):
        if (point[1] <= 0.0):
            lon = -(PI - lon)
        else:
            lon = (PI + lon)
    return [lon * DEGREES, lat * DEGREES]

def to_cartesian(coord):
    ''' convert [long, lat] IN RADIANS to spherical/cartesian [x,y,z] '''
    theta = coord[0]
    # spherical coordinate use "co-latitude", not "latitude"

    # lat = [-90, 90] with 0 at equator
    # co-lat = [0, 180] with 0 at north pole
    phi = PI / 2.0 - coord[1]
    return [math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi)]

def spoints(lon, lat, radius, sides=20, rotate=0):

    rotate_radians = rotate * RADIANS

    # compute longitude degrees (in radians) at givent latitude
    r = radius / (EARTH_MEAN_RADIUS * math.cos(lat * RADIANS))

    vector = to_cartesian([lon * RADIANS, lat * RADIANS])
    point = to_cartesian([lon * RADIANS + r, lat * RADIANS])
    points = []

    for side in range(0, sides):
        points.append(to_earth(rotate_point(vector, point, rotate_radians + (2.0 * PI / sides) * side)))
    
    # Connect to starting point exactly
    # Not sure if required but seems to help when polygon is not filled
    points.append(points[0])
    return points

def rotate_point(vector, point, phi):
    # remap vector for sanity
    u, v, w, x, y, z = vector[0], vector[1], vector[2], point[0], point[1], point[2]

    a = u*x + v*y + w*z
    d = math.cos(phi)
    e = math.sin(phi)

    return [(a*u + (x - a*u)*d + (v*z - w*y) * e),
            (a*v + (y - a*v)*d + (w*x - u*z) * e),
            (a*w + (z - a*w)*d + (u*y - v*x) * e)]

def kml_regular_polygon(lon, lat, radius, segments=20, rotate=0):
    return points_to_kml(spoints(lon, lat, radius, segments, rotate))

def kml_star(lon, lat, radius, inner_radius, segments=10, rotate=0):
    outer_points = spoints(lon, lat, radius, segments, rotate)
    inner_points = spoints(lon, lat, inner_radius, segments, rotate + 180.0 / segments)

    # interweave the radius and inner_radius points
    # I'm sure there is a better way
    points = []
    for point in outer_points:
      points.append(outer_points[point])
      points.append(inner_points[point])

    # MTB - Drop the last overlapping point leaving start and end points connecting
    # (resulting output differs from orig, but is more correct)
    points.pop()

    return points_to_kml(points)

def points_to_kml(points):
    kmlOutput_points = f"""        <Polygon>
          <outerBoundaryIs>
            <LinearRing>
              <coordinates>
"""

    for point in points:
        kmlOutput_points += f"                {point[0]}, {point[1]}\n"

    kmlOutput_points += f"""              </coordinates>
            </LinearRing>
          </outerBoundaryIs>
        </Polygon>"""
    return kmlOutput_points

def generate_kml_styles():
    color_table = config["style_colors"]
    kml_string_style = ""
    for index, color_entry in reversed(list(enumerate(color_table))):
        calc_index=len(color_table)-index-1
        kml_string_style += f'''
    <Style id="polygon-{calc_index}-normal">
      <LineStyle>
        <color>{color_entry[0]:08x}</color>
        <width>2</width>
      </LineStyle>
      <PolyStyle>
        <color>{color_entry[1]:08x}</color>
        <fill>1</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>
    <Style id="polygon-{calc_index}-highlight">
      <LineStyle>
        <color>{color_entry[0]:08x}</color>
        <width>2.8</width>
      </LineStyle>
      <PolyStyle>
        <color>{color_entry[1]:08x}</color>
        <fill>1</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>
    <StyleMap id="polygon-{calc_index}">
      <Pair>
        <key>normal</key>
        <styleUrl>#polygon-{calc_index}-normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#polygon-{calc_index}-highlight</styleUrl>
      </Pair>
    </StyleMap>
'''
    return kml_string_style

def generate_kml_placemarks():
    array_radius = config["radius_list"]
    vertices = config["vertices"]
    location = config["location"]
    latitude = location["latitude"]
    longitude = location["longitude"]
    loc_name = location["name"]
    kmlOutput_Placemarks = ""
    for index, radius in reversed(list(enumerate(array_radius))):
        calc_index=len(array_radius)-index-1
        kmlOutput_Placemarks += f'''
      <Placemark>
        <name>{radius}m</name>
        <styleUrl>#polygon-{calc_index}</styleUrl>
{kml_regular_polygon(longitude, latitude, radius, vertices)}
      </Placemark>'''
    return kmlOutput_Placemarks

def banner():
    array_radius = config["radius_list"]
    vertices = config["vertices"]
    location = config["location"]
    latitude = location["latitude"]
    longitude = location["longitude"]
    loc_name = location["name"]

    print(f'''
  *******************************
    Generate Target Circles KML
  *******************************

Name: {loc_name}
Latitude: {latitude}
Longitude: {longitude}

Vertices: {vertices}
Radius: {array_radius}
''')

def generate_kml():
    banner()

    kmlOutput = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{config["location"]["name"]}</name>
    <description/>
{generate_kml_styles()}
    <Folder>
      <name>{config["folder_name"]}</name>
{generate_kml_placemarks()}
    </Folder>
  </Document>
</kml>
'''
    datestr = time.strftime("%Y%m%d")
    fname = f'{datestr}-target-{config["location"]["name"]}.kml'
    with open(fname, "w") as pFile:
        pFile.write(kmlOutput)

if __name__ == "__main__":
    generate_kml()
