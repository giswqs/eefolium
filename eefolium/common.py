"""This module contains some common functions for both folium and ipyleaflet to interact with the Earth Engine Python API.
"""

import csv
import math
import os
import subprocess
import shutil
import tarfile
import urllib.request
import zipfile
import ee


########################################
# EE Authentication and Initialization #
########################################

def ee_initialize(token_name='EARTHENGINE_TOKEN'):
    """Authenticates Earth Engine and initialize an Earth Engine session

    """
    if ee.data._credentials is None:
        try:
            ee_token = os.environ.get(token_name)
            if ee_token is not None:
                credential_file_path = os.path.expanduser("~/.config/earthengine/")
                if not os.path.exists(credential_file_path):
                    credential = '{"refresh_token":"%s"}' % ee_token
                    os.makedirs(credential_file_path, exist_ok=True)
                    with open(credential_file_path + 'credentials', 'w') as file:
                        file.write(credential)
            elif in_colab_shell():
                if credentials_in_drive() and (not credentials_in_colab()):
                    copy_credentials_to_colab()
                elif not credentials_in_colab:
                    ee.Authenticate()
                    if is_drive_mounted() and (not credentials_in_drive()):
                        copy_credentials_to_drive()
                else:
                    if is_drive_mounted():
                        copy_credentials_to_drive()

            ee.Initialize()
        except:
            ee.Authenticate()
            ee.Initialize()

def set_proxy(port=1080, ip='http://127.0.0.1'):
    """Sets proxy if needed. This is only needed for countries where Google services are not available.

    Args:
        port (int, optional): The proxy port number. Defaults to 1080.
        ip (str, optional): The IP address. Defaults to 'http://127.0.0.1'.
    """
    import os
    import requests

    try:

        if not ip.startswith('http'):
            ip = 'http://' + ip
        proxy = '{}:{}'.format(ip, port)

        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy

        a = requests.get('https://earthengine.google.com/')

        if a.status_code != 200:
            print(
                'Failed to connect to Earth Engine. Please double check the port number and ip address.')

    except Exception as e:
        print(e)


def in_colab_shell():
    """Tests if the code is being executed within Google Colab."""
    try:
        import google.colab  # pylint: disable=unused-variable
        return True
    except ImportError:
        return False


def is_drive_mounted():
    """Checks whether Google Drive is mounted in Google Colab.

    Returns:
        bool: Returns True if Google Drive is mounted, False otherwise.
    """
    drive_path = '/content/drive/My Drive'
    if os.path.exists(drive_path):
        return True
    else:
        return False


def credentials_in_drive():
    """Checks if the ee credentials file exists in Google Drive.

    Returns:
        bool: Returns True if Google Drive is mounted, False otherwise.
    """
    credentials_path = '/content/drive/My Drive/.config/earthengine/credentials'
    if os.path.exists(credentials_path):
        return True
    else:
        return False


def credentials_in_colab():
    """Checks if the ee credentials file exists in Google Colab.

    Returns:
        bool: Returns True if Google Drive is mounted, False otherwise.
    """
    credentials_path = '/root/.config/earthengine/credentials'
    if os.path.exists(credentials_path):
        return True
    else:
        return False


def copy_credentials_to_drive():
    """Copies ee credentials from Google Colab to Google Drive.
    """
    src = '/root/.config/earthengine/credentials'
    dst = '/content/drive/My Drive/.config/earthengine/credentials'

    wd = os.path.dirname(dst)
    if not os.path.exists(wd):
        os.makedirs(wd)

    shutil.copyfile(src, dst)


def copy_credentials_to_colab():
    """Copies ee credentials from Google Drive to Google Colab.
    """
    src = '/content/drive/My Drive/.config/earthengine/credentials'
    dst = '/root/.config/earthengine/credentials'

    wd = os.path.dirname(dst)
    if not os.path.exists(wd):
        os.makedirs(wd)

    shutil.copyfile(src, dst)


########################################
#         Package Installation         #
########################################

def check_install(package):
    """Checks whether a package is installed. If not, it will install the package.

    Args:
        package (str): The name of the package to check.
    """
    import subprocess

    try:
        __import__(package)
        # print('{} is already installed.'.format(package))
    except ImportError:
        print('{} is not installed. Installing ...'.format(package))
        try:
            subprocess.check_call(["python", '-m', 'pip', 'install', package])
        except Exception as e:
            print('Failed to install {}'.format(package))
            print(e)
        print("{} has been installed successfully.".format(package))


def update_package():
    """Updates the eefolium package from the eefolium GitHub repository without the need to use pip or conda.
        In this way, I don't have to keep updating pypi and conda-forge with every minor update of the package.

    """
    import shutil
    try:
        download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        clone_repo(out_dir=download_dir)

        pkg_dir = os.path.join(download_dir, 'eefolium-master')
        work_dir = os.getcwd()
        os.chdir(pkg_dir)

        if shutil.which('pip') is None:
            cmd = 'pip3 install .'
        else:
            cmd = 'pip install .'

        os.system(cmd)
        os.chdir(work_dir)

        print("\nPlease comment out 'eefolium.update_package()' and restart the kernel to take effect:\nJupyter menu -> Kernel -> Restart & Clear Output")

    except Exception as e:
        print(e)


def clone_repo(out_dir='.', unzip=True):
    """Clones the eefolium GitHub repository.

    Args:
        out_dir (str, optional): Output folder for the repo. Defaults to '.'.
        unzip (bool, optional): Whether to unzip the repository. Defaults to True.
    """
    url = 'https://github.com/giswqs/eefolium/archive/master.zip'
    filename = 'eefolium-master.zip'
    download_from_url(url, out_file_name=filename,
                      out_dir=out_dir, unzip=unzip)


def install_from_github(url):
    """Install a package from a GitHub repository.

    Args:
        url (str): The URL of the GitHub repository.
    """

    try:
        download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        repo_name = os.path.basename(url)
        zip_url = os.path.join(url, 'archive/master.zip')
        filename = repo_name + '-master.zip'
        download_from_url(url=zip_url, out_file_name=filename,
                          out_dir=download_dir, unzip=True)

        pkg_dir = os.path.join(download_dir, repo_name + '-master')
        pkg_name = os.path.basename(url)
        work_dir = os.getcwd()
        os.chdir(pkg_dir)
        print('Installing {}...'.format(pkg_name))
        cmd = 'pip install .'
        os.system(cmd)
        os.chdir(work_dir)
        print('{} has been installed successfully.'.format(pkg_name))
        # print("\nPlease comment out 'install_from_github()' and restart the kernel to take effect:\nJupyter menu -> Kernel -> Restart & Clear Output")

    except Exception as e:
        print(e)


def check_git_install():
    """Checks if Git is installed.

    Returns:
        bool: Returns True if Git is installed, otherwise returns False.
    """
    import webbrowser

    cmd = 'git --version'
    output = os.popen(cmd).read()

    if 'git version' in output:
        return True
    else:
        url = 'https://git-scm.com/downloads'
        print(
            "Git is not installed. Please download Git from {} and install it.".format(url))
        webbrowser.open_new_tab(url)
        return False


def clone_github_repo(url, out_dir):
    """Clones a GitHub repository.

    Args:
        url (str): The link to the GitHub repository
        out_dir (str): The output directory for the cloned repository. 
    """

    import zipfile

    repo_name = os.path.basename(url)
    # url_zip = os.path.join(url, 'archive/master.zip')
    url_zip = url + '/archive/master.zip'

    if os.path.exists(out_dir):
        print(
            'The specified output directory already exists. Please choose a new directory.')
        return

    parent_dir = os.path.dirname(out_dir)
    out_file_path = os.path.join(parent_dir, repo_name + '.zip')

    try:
        urllib.request.urlretrieve(url_zip, out_file_path)
    except:
        print("The provided URL is invalid. Please double check the URL.")
        return

    with zipfile.ZipFile(out_file_path, "r") as zip_ref:
        zip_ref.extractall(parent_dir)

    src = out_file_path.replace('.zip', '-master')
    os.rename(src, out_dir)
    os.remove(out_file_path)


def clone_google_repo(url, out_dir=None):
    """Clones an Earth Engine repository from https://earthengine.googlesource.com, such as https://earthengine.googlesource.com/users/google/datasets

    Args:
        url (str): The link to the Earth Engine repository
        out_dir (str, optional): The output directory for the cloned repository. Defaults to None.
    """
    repo_name = os.path.basename(url)

    if out_dir is None:
        out_dir = os.path.join(os.getcwd(), repo_name)

    if not os.path.exists(os.path.dirname(out_dir)):
        os.makedirs(os.path.dirname(out_dir))

    if os.path.exists(out_dir):
        print(
            'The specified output directory already exists. Please choose a new directory.')
        return

    if check_git_install():

        cmd = 'git clone "{}" "{}"'.format(url, out_dir)
        os.popen(cmd).read()


def open_github(subdir=None):
    """Opens the GitHub repository for this package.

    Args:
        subdir (str, optional): Sub-directory of the repository. Defaults to None.
    """
    import webbrowser

    url = 'https://github.com/giswqs/eefolium'

    if subdir == 'source':
        url += '/tree/master/eefolium/'
    elif subdir == 'examples':
        url += '/tree/master/examples'
    elif subdir == 'tutorials':
        url += '/tree/master/tutorials'

    webbrowser.open_new_tab(url)


def open_youtube():
    """Opens the YouTube tutorials for eefolium.
    """
    import webbrowser

    url = 'https://www.youtube.com/playlist?list=PLAxJ4-o7ZoPccOFv1dCwvGI6TYnirRTg3'
    webbrowser.open_new_tab(url)


########################################
#           Python Utilities           #
########################################

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    from shutil import which

    return which(name) is not None


def random_string(string_length=3):
    """Generates a random string of fixed length. 

    Args:
        string_length (int, optional): Fixed length. Defaults to 3.

    Returns:
        str: A random string
    """
    import random
    import string

    # random.seed(1001)
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


########################################
#           Color and Fonts            #
########################################

def rgb_to_hex(rgb=(255, 255, 255)):
    """Converts RGB to hex color. In RGB color R stands for Red, G stands for Green, and B stands for Blue, and it ranges from the decimal value of 0 – 255.

    Args:
        rgb (tuple, optional): RGB color code as a tuple of (red, green, blue). Defaults to (255, 255, 255).

    Returns:
        str: hex color code
    """
    return '%02x%02x%02x' % rgb


def hex_to_rgb(value='FFFFFF'):
    """Converts hex color to RGB color. 

    Args:
        value (str, optional): Hex color code as a string. Defaults to 'FFFFFF'.

    Returns:
        tuple: RGB color as a tuple.
    """
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))


########################################
#           Data Download              #
########################################

def download_from_url(url, out_file_name=None, out_dir='.', unzip=True):
    """Download a file from a URL (e.g., https://github.com/giswqs/whitebox/raw/master/examples/testdata.zip)

    Args:
        url (str): The HTTP URL to download.
        out_file_name (str, optional): The output file name to use. Defaults to None.
        out_dir (str, optional): The output directory to use. Defaults to '.'.
        unzip (bool, optional): Whether to unzip the downloaded file if it is a zip file. Defaults to True.
    """
    in_file_name = os.path.basename(url)

    if out_file_name is None:
        out_file_name = in_file_name
    out_file_path = os.path.join(os.path.abspath(out_dir), out_file_name)

    print('Downloading {} ...'.format(url))

    try:
        urllib.request.urlretrieve(url, out_file_path)
    except:
        print("The URL is invalid. Please double check the URL.")
        return

    final_path = out_file_path

    if unzip:
        # if it is a zip file
        if '.zip' in out_file_name:
            print("Unzipping {} ...".format(out_file_name))
            with zipfile.ZipFile(out_file_path, "r") as zip_ref:
                zip_ref.extractall(out_dir)
            final_path = os.path.join(os.path.abspath(
                out_dir), out_file_name.replace('.zip', ''))

        # if it is a tar file
        if '.tar' in out_file_name:
            print("Unzipping {} ...".format(out_file_name))
            with tarfile.open(out_file_path, "r") as tar_ref:
                tar_ref.extractall(out_dir)
            final_path = os.path.join(os.path.abspath(
                out_dir), out_file_name.replace('.tart', ''))

    print('Data downloaded to: {}'.format(final_path))


def download_from_gdrive(gfile_url, file_name, out_dir='.', unzip=True):
    """Download a file shared via Google Drive 
       (e.g., https://drive.google.com/file/d/18SUo_HcDGltuWYZs1s7PpOmOq_FvFn04/view?usp=sharing)

    Args:
        gfile_url (str): The Google Drive shared file URL
        file_name (str): The output file name to use.
        out_dir (str, optional): The output directory. Defaults to '.'.
        unzip (bool, optional): Whether to unzip the output file if it is a zip file. Defaults to True.
    """
    try:
        from google_drive_downloader import GoogleDriveDownloader as gdd
    except ImportError:
        print('GoogleDriveDownloader package not installed. Installing ...')
        subprocess.check_call(
            ["python", '-m', 'pip', 'install', 'googledrivedownloader'])
        from google_drive_downloader import GoogleDriveDownloader as gdd

    file_id = gfile_url.split('/')[5]
    print('Google Drive file id: {}'.format(file_id))

    dest_path = os.path.join(out_dir, file_name)
    gdd.download_file_from_google_drive(file_id, dest_path, True, unzip)


########################################
#           Data Conversion            #
########################################

def xy_to_points(in_csv, latitude='latitude', longitude='longitude'):
    """Converts a csv containing points (latitude and longitude) into an ee.FeatureCollection.

    Args:
        in_csv (str): File path or HTTP URL to the input csv file. For example, https://raw.githubusercontent.com/giswqs/data/main/world/world_cities.csv
        latitude (str, optional): Column name for the latitude column. Defaults to 'latitude'.
        longitude (str, optional): Column name for the longitude column. Defaults to 'longitude'.

    Returns:
        ee.FeatureCollection: The ee.FeatureCollection containing the points converted from the input csv.
    """

    if in_csv.startswith('http') and in_csv.endswith('.csv'):
        out_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        out_name = os.path.basename(in_csv)
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        download_from_url(in_csv, out_dir=out_dir)
        in_csv = os.path.join(out_dir, out_name)

    in_csv = os.path.abspath(in_csv)
    if not os.path.exists(in_csv):
        raise Exception('The provided csv file does not exist.')

    points = []
    with open(in_csv) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lat, lon = float(row[latitude]), float(row[longitude])
            points.append([lon, lat])

    ee_list = ee.List(points)
    ee_points = ee_list.map(lambda xy: ee.Feature(ee.Geometry.Point(xy)))
    return ee.FeatureCollection(ee_points)


def geojson_to_ee(geo_json, geodesic=True):
    """Converts a geojson to ee.Geometry()

    Args:
        geo_json (dict): A geojson geometry dictionary or file path.

    Returns:
        ee_object: An ee.Geometry object
    """
    # ee_initialize()

    try:

        import json

        if not isinstance(geo_json, dict) and os.path.isfile(geo_json):
            with open(os.path.abspath(geo_json)) as f:
                geo_json = json.load(f)

        if geo_json['type'] == 'FeatureCollection':
            features = ee.FeatureCollection(geo_json['features'])
            return features
        elif geo_json['type'] == 'Feature':
            geom = None
            keys = geo_json['properties']['style'].keys()
            if 'radius' in keys:  # Checks whether it is a circle
                geom = ee.Geometry(geo_json['geometry'])
                radius = geo_json['properties']['style']['radius']
                geom = geom.buffer(radius)
            elif geo_json['geometry']['type'] == 'Point':  # Checks whether it is a point
                coordinates = geo_json['geometry']['coordinates']
                longitude = coordinates[0]
                latitude = coordinates[1]
                geom = ee.Geometry.Point(longitude, latitude)
            else:
                geom = ee.Geometry(geo_json['geometry'], "", geodesic)
            return geom
        else:
            print("Could not convert the geojson to ee.Geometry()")

    except Exception as e:
        print("Could not convert the geojson to ee.Geometry()")
        print(e)


def ee_to_geojson(ee_object, out_json=None):
    """Converts Earth Engine object to geojson.

    Args:
        ee_object (object): An Earth Engine object.

    Returns:
        object: GeoJSON object.
    """
    from json import dumps
    # ee_initialize()

    try:
        if isinstance(ee_object, ee.geometry.Geometry) or isinstance(ee_object, ee.feature.Feature) or isinstance(ee_object, ee.featurecollection.FeatureCollection):
            json_object = ee_object.getInfo()
            if out_json is not None:
                out_json = os.path.abspath(out_json)
                if not os.path.exists(os.path.dirname(out_json)):
                    os.makedirs(os.path.dirname(out_json))
                geojson = open(out_json, "w")
                geojson.write(
                    dumps({"type": "FeatureCollection", "features": json_object}, indent=2) + "\n")
                geojson.close()
            return json_object
        else:
            print("Could not convert the Earth Engine object to geojson")
    except Exception as e:
        print(e)


def shp_to_geojson(in_shp, out_json=None):
    """Converts a shapefile to GeoJSON.

    Args:
        in_shp (str): File path of the input shapefile.
        out_json (str, optional): File path of the output GeoJSON. Defaults to None.

    Returns:
        object: The json object representing the shapefile.
    """
    # check_install('pyshp')
    # ee_initialize()
    try:
        import json
        import shapefile
        in_shp = os.path.abspath(in_shp)

        if out_json is None:
            out_json = os.path.splitext(in_shp)[0] + ".json"

            if os.path.exists(out_json):
                out_json = out_json.replace('.json', '_bk.json')

        elif not os.path.exists(os.path.dirname(out_json)):
            os.makedirs(os.path.dirname(out_json))

        reader = shapefile.Reader(in_shp)
        fields = reader.fields[1:]
        field_names = [field[0] for field in fields]
        buffer = []
        for sr in reader.shapeRecords():
            atr = dict(zip(field_names, sr.record))
            geom = sr.shape.__geo_interface__
            buffer.append(dict(type="Feature", geometry=geom, properties=atr))

        from json import dumps
        geojson = open(out_json, "w")
        geojson.write(dumps({"type": "FeatureCollection",
                             "features": buffer}, indent=2) + "\n")
        geojson.close()

        with open(out_json) as f:
            json_data = json.load(f)

        return json_data

    except Exception as e:
        print(e)


def shp_to_ee(in_shp):
    """Converts a shapefile to Earth Engine objects. Note that the CRS of the shapefile must be EPSG:4326

    Args:
        in_shp (str): File path to a shapefile.

    Returns:
        object: Earth Engine objects representing the shapefile.
    """
    # ee_initialize()
    try:
        json_data = shp_to_geojson(in_shp)
        ee_object = geojson_to_ee(json_data)
        return ee_object
    except Exception as e:
        print(e)


########################################
#              Export Data             #
########################################

def filter_polygons(ftr):
    """Converts GeometryCollection to Polygon/MultiPolygon

    Args:
        ftr (object): ee.Feature

    Returns:
        object: ee.Feature
    """
    # ee_initialize()
    geometries = ftr.geometry().geometries()
    geometries = geometries.map(lambda geo: ee.Feature(
        ee.Geometry(geo)).set('geoType',  ee.Geometry(geo).type()))

    polygons = ee.FeatureCollection(geometries).filter(
        ee.Filter.eq('geoType', 'Polygon')).geometry()
    return ee.Feature(polygons).copyProperties(ftr)


def ee_export_vector(ee_object, filename, selectors=None):
    """Exports Earth Engine FeatureCollection to other formats, including shp, csv, json, kml, and kmz.

    Args:
        ee_object (object): ee.FeatureCollection to export.
        filename (str): Output file name.
        selectors (list, optional): A list of attributes to export. Defaults to None.
    """
    import requests
    import zipfile
    # ee_initialize()

    if not isinstance(ee_object, ee.FeatureCollection):
        raise ValueError('ee_object must be an ee.FeatureCollection')

    allowed_formats = ['csv', 'geojson', 'kml', 'kmz', 'shp']
    # allowed_formats = ['csv', 'kml', 'kmz']
    filename = os.path.abspath(filename)
    basename = os.path.basename(filename)
    name = os.path.splitext(basename)[0]
    filetype = os.path.splitext(basename)[1][1:].lower()

    if filetype == 'shp':
        filename = filename.replace('.shp', '.zip')

    if not (filetype.lower() in allowed_formats):
        print('The file type must be one of the following: {}'.format(
            ', '.join(allowed_formats)))
        print('Earth Engine no longer supports downloading featureCollection as shapefile or json. \nPlease use eefolium.ee_export_vector_to_drive() to export featureCollection to Google Drive.')
        raise ValueError

    if selectors is None:
        selectors = ee_object.first().propertyNames().getInfo()
        if filetype == 'csv':
            # remove .geo coordinate field
            ee_object = ee_object.select([".*"], None, False)

    if filetype == 'geojson':
        selectors = ['.geo'] + selectors

    elif not isinstance(selectors, list):
        raise ValueError(
            "selectors must be a list, such as ['attribute1', 'attribute2']")
    else:
        allowed_attributes = ee_object.first().propertyNames().getInfo()
        for attribute in selectors:
            if not (attribute in allowed_attributes):
                raise ValueError('Attributes must be one chosen from: {} '.format(
                    ', '.join(allowed_attributes)))

    try:
        print('Generating URL ...')
        url = ee_object.getDownloadURL(
            filetype=filetype, selectors=selectors, filename=name)
        print('Downloading data from {}\nPlease wait ...'.format(url))
        r = requests.get(url, stream=True)

        if r.status_code != 200:
            print('An error occurred while downloading. \n Retrying ...')
            try:
                new_ee_object = ee_object.map(filter_polygons)
                print('Generating URL ...')
                url = new_ee_object.getDownloadURL(
                    filetype=filetype, selectors=selectors, filename=name)
                print('Downloading data from {}\nPlease wait ...'.format(url))
                r = requests.get(url, stream=True)
            except Exception as e:
                print(e)
                raise ValueError

        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)
    except Exception as e:
        print('An error occurred while downloading.')
        raise ValueError(e)

    try:
        if filetype == 'shp':
            z = zipfile.ZipFile(filename)
            z.extractall(os.path.dirname(filename))
            z.close()
            os.remove(filename)
            filename = filename.replace('.zip', '.shp')

        print('Data downloaded to {}'.format(filename))
    except Exception as e:
        raise ValueError(e)


def ee_export_vector_to_drive(ee_object, description, folder, file_format='shp', selectors=None):
    """Exports Earth Engine FeatureCollection to Google Drive. other formats, including shp, csv, json, kml, and kmz.

    Args:
        ee_object (object): ee.FeatureCollection to export.
        description (str): File name of the output file.
        folder (str): Folder name within Google Drive to save the exported file.
        file_format (str, optional): The supported file format include shp, csv, json, kml, kmz, and TFRecord. Defaults to 'shp'.
        selectors (list, optional): The list of attributes to export. Defaults to None.
    """
    if not isinstance(ee_object, ee.FeatureCollection):
        print('The ee_object must be an ee.FeatureCollection.')
        return

    allowed_formats = ['csv', 'json', 'kml', 'kmz', 'shp', 'tfrecord']
    if not (file_format.lower() in allowed_formats):
        print('The file type must be one of the following: {}'.format(
            ', '.join(allowed_formats)))
        return

    task_config = {
        'folder': folder,
        'fileFormat': file_format,
    }

    if selectors is not None:
        task_config['selectors'] = selectors
    elif (selectors is None) and (file_format.lower() == 'csv'):
        # remove .geo coordinate field
        ee_object = ee_object.select([".*"], None, False)

    print('Exporting {}...'.format(description))
    task = ee.batch.Export.table.toDrive(ee_object, description, **task_config)
    task.start()


def ee_export_geojson(ee_object, filename=None, selectors=None):
    """Exports Earth Engine FeatureCollection to geojson.

    Args:
        ee_object (object): ee.FeatureCollection to export.
        filename (str): Output file name. Defaults to None.
        selectors (list, optional): A list of attributes to export. Defaults to None.
    """
    import requests
    import zipfile
    # ee_initialize()

    if not isinstance(ee_object, ee.FeatureCollection):
        print('The ee_object must be an ee.FeatureCollection.')
        return

    if filename is None:
        out_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        filename = os.path.join(out_dir, random_string(6) + '.geojson')

    allowed_formats = ['geojson']
    filename = os.path.abspath(filename)
    basename = os.path.basename(filename)
    name = os.path.splitext(basename)[0]
    filetype = os.path.splitext(basename)[1][1:].lower()

    if not (filetype.lower() in allowed_formats):
        print('The output file type must be geojson.')
        return

    if selectors is None:
        selectors = ee_object.first().propertyNames().getInfo()
        selectors = ['.geo'] + selectors

    elif not isinstance(selectors, list):
        print("selectors must be a list, such as ['attribute1', 'attribute2']")
        return
    else:
        allowed_attributes = ee_object.first().propertyNames().getInfo()
        for attribute in selectors:
            if not (attribute in allowed_attributes):
                print('Attributes must be one chosen from: {} '.format(
                    ', '.join(allowed_attributes)))
                return

    try:
        # print('Generating URL ...')
        url = ee_object.getDownloadURL(
            filetype=filetype, selectors=selectors, filename=name)
        # print('Downloading data from {}\nPlease wait ...'.format(url))
        r = requests.get(url, stream=True)

        if r.status_code != 200:
            print('An error occurred while downloading. \n Retrying ...')
            try:
                new_ee_object = ee_object.map(filter_polygons)
                print('Generating URL ...')
                url = new_ee_object.getDownloadURL(
                    filetype=filetype, selectors=selectors, filename=name)
                print('Downloading data from {}\nPlease wait ...'.format(url))
                r = requests.get(url, stream=True)
            except Exception as e:
                print(e)

        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)
    except Exception as e:
        print('An error occurred while downloading.')
        print(e)
        return

    with open(filename) as f:
        geojson = f.read()

    return geojson


def ee_to_shp(ee_object, filename, selectors=None):
    """Downloads an ee.FeatureCollection as a shapefile.

    Args:
        ee_object (object): ee.FeatureCollection
        filename (str): The output filepath of the shapefile.
        selectors (list, optional): A list of attributes to export. Defaults to None.
    """
    # ee_initialize()
    try:
        if filename.lower().endswith('.shp'):
            ee_export_vector(ee_object=ee_object,
                             filename=filename, selectors=selectors)
        else:
            print('The filename must end with .shp')

    except Exception as e:
        print(e)


def ee_to_csv(ee_object, filename, selectors=None):
    """Downloads an ee.FeatureCollection as a CSV file.

    Args:
        ee_object (object): ee.FeatureCollection
        filename (str): The output filepath of the CSV file.
        selectors (list, optional): A list of attributes to export. Defaults to None.
    """
    # ee_initialize()
    try:
        if filename.lower().endswith('.csv'):
            ee_export_vector(ee_object=ee_object,
                             filename=filename, selectors=selectors)
        else:
            print('The filename must end with .csv')

    except Exception as e:
        print(e)


def dict_to_csv(data_dict, out_csv, by_row=False):
    """Downloads an ee.Dictionary as a CSV file.

    Args:
        data_dict (ee.Dictionary): The input ee.Dictionary.
        out_csv (str): The output file path to the CSV file.
        by_row (bool, optional): Whether to use by row or by column. Defaults to False.
    """
    import eefolium

    out_dir = os.path.dirname(out_csv)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if not by_row:
        csv_feature = ee.Feature(None, data_dict)
        csv_feat_col = ee.FeatureCollection([csv_feature])
    else:
        keys = data_dict.keys()
        data = keys.map(lambda k: ee.Dictionary({'name': k, 'value': data_dict.get(k)}))
        csv_feature = data.map(lambda f: ee.Feature(None, f))
        csv_feat_col = ee.FeatureCollection(csv_feature)

    ee_export_vector(csv_feat_col, out_csv)


def ee_export_image(ee_object, filename, scale=None, crs=None, region=None, file_per_band=False):
    """Exports an ee.Image as a GeoTIFF.

    Args:
        ee_object (object): The ee.Image to download.
        filename (str): Output filename for the exported image.
        scale (float, optional): A default scale to use for any bands that do not specify one; ignored if crs and crs_transform is specified. Defaults to None.
        crs (str, optional): A default CRS string to use for any bands that do not explicitly specify one. Defaults to None.
        region (object, optional): A polygon specifying a region to download; ignored if crs and crs_transform is specified. Defaults to None.
        file_per_band (bool, optional): Whether to produce a different GeoTIFF per band. Defaults to False.
    """
    import requests
    import zipfile
    # ee_initialize()

    if not isinstance(ee_object, ee.Image):
        print('The ee_object must be an ee.Image.')
        return

    filename = os.path.abspath(filename)
    basename = os.path.basename(filename)
    name = os.path.splitext(basename)[0]
    filetype = os.path.splitext(basename)[1][1:].lower()
    filename_zip = filename.replace('.tif', '.zip')

    if filetype != 'tif':
        print('The filename must end with .tif')
        return

    try:
        print('Generating URL ...')
        params = {'name': name, 'filePerBand': file_per_band}
        if scale is None:
            scale = ee_object.projection().nominalScale().multiply(10)
        params['scale'] = scale
        if region is None:
            region = ee_object.geometry()
        params['region'] = region
        if crs is not None:
            params['crs'] = crs

        url = ee_object.getDownloadURL(params)
        print('Downloading data from {}\nPlease wait ...'.format(url))
        r = requests.get(url, stream=True)

        if r.status_code != 200:
            print('An error occurred while downloading.')
            return

        with open(filename_zip, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)

    except Exception as e:
        print('An error occurred while downloading.')
        print(e)
        return

    try:
        z = zipfile.ZipFile(filename_zip)
        z.extractall(os.path.dirname(filename))
        z.close()
        os.remove(filename_zip)

        if file_per_band:
            print('Data downloaded to {}'.format(os.path.dirname(filename)))
        else:
            print('Data downloaded to {}'.format(filename))
    except Exception as e:
        print(e)


def ee_export_image_collection(ee_object, out_dir, scale=None, crs=None, region=None, file_per_band=False):
    """Exports an ImageCollection as GeoTIFFs.

    Args:
        ee_object (object): The ee.Image to download.
        out_dir (str): The output directory for the exported images.
        scale (float, optional): A default scale to use for any bands that do not specify one; ignored if crs and crs_transform is specified. Defaults to None.
        crs (str, optional): A default CRS string to use for any bands that do not explicitly specify one. Defaults to None.
        region (object, optional): A polygon specifying a region to download; ignored if crs and crs_transform is specified. Defaults to None.
        file_per_band (bool, optional): Whether to produce a different GeoTIFF per band. Defaults to False.
    """

    import requests
    import zipfile
    # ee_initialize()

    if not isinstance(ee_object, ee.ImageCollection):
        print('The ee_object must be an ee.ImageCollection.')
        return

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    try:

        count = int(ee_object.size().getInfo())
        print("Total number of images: {}\n".format(count))

        for i in range(0, count):
            image = ee.Image(ee_object.toList(count).get(i))
            name = image.get('system:index').getInfo() + '.tif'
            filename = os.path.join(os.path.abspath(out_dir), name)
            print('Exporting {}/{}: {}'.format(i+1, count, name))
            ee_export_image(image, filename=filename, scale=scale,
                            crs=crs, region=region, file_per_band=file_per_band)
            print('\n')

    except Exception as e:
        print(e)


def ee_export_image_to_drive(ee_object, description, folder=None, region=None, scale=None, crs=None, max_pixels=1.0E13, file_format='GeoTIFF', format_options={}):
    """Creates a batch task to export an Image as a raster to Google Drive.

    Args:
        ee_object (object): The image to export.
        description (str): A human-readable name of the task. 
        folder (str, optional): The Google Drive Folder that the export will reside in. Defaults to None.
        region (object, optional): A LinearRing, Polygon, or coordinates representing region to export. These may be specified as the Geometry objects or coordinates serialized as a string. If not specified, the region defaults to the viewport at the time of invocation. Defaults to None.
        scale (float, optional): Resolution in meters per pixel. Defaults to 10 times of the image resolution.
        crs (str, optional): CRS to use for the exported image.. Defaults to None.
        max_pixels (int, optional): Restrict the number of pixels in the export. Defaults to 1.0E13.
        file_format (str, optional): The string file format to which the image is exported. Currently only 'GeoTIFF' and 'TFRecord' are supported. Defaults to 'GeoTIFF'.
        format_options (dict, optional): A dictionary of string keys to format specific options, e.g., {'compressed': True, 'cloudOptimized': True}
    """
    # ee_initialize()

    if not isinstance(ee_object, ee.Image):
        print('The ee_object must be an ee.Image.')
        return

    try:
        params = {}

        if folder is not None:
            params['driveFolder'] = folder
        if region is not None:
            params['region'] = region
        if scale is None:
            scale = ee_object.projection().nominalScale().multiply(10)
        params['scale'] = scale
        if crs is not None:
            params['crs'] = crs
        params['maxPixels'] = max_pixels
        params['fileFormat'] = file_format
        params['formatOptions'] = format_options

        task = ee.batch.Export.image(ee_object, description, params)
        task.start()

        print('Exporting {} ...'.format(description))

    except Exception as e:
        print(e)


def ee_export_image_collection_to_drive(ee_object, descriptions=None, folder=None, region=None, scale=None, crs=None, max_pixels=1.0E13, file_format='GeoTIFF', format_options={}):
    """Creates a batch task to export an ImageCollection as raster images to Google Drive.

    Args:
        ee_object (object): The image to export.
        descriptions (list): A list of human-readable names of the tasks. 
        folder (str, optional): The Google Drive Folder that the export will reside in. Defaults to None.
        region (object, optional): A LinearRing, Polygon, or coordinates representing region to export. These may be specified as the Geometry objects or coordinates serialized as a string. If not specified, the region defaults to the viewport at the time of invocation. Defaults to None.
        scale (float, optional): Resolution in meters per pixel. Defaults to 10 times of the image resolution.
        crs (str, optional): CRS to use for the exported image.. Defaults to None.
        max_pixels (int, optional): Restrict the number of pixels in the export. Defaults to 1.0E13.
        file_format (str, optional): The string file format to which the image is exported. Currently only 'GeoTIFF' and 'TFRecord' are supported. Defaults to 'GeoTIFF'.
        format_options (dict, optional): A dictionary of string keys to format specific options, e.g., {'compressed': True, 'cloudOptimized': True}
    """
    # ee_initialize()

    if not isinstance(ee_object, ee.ImageCollection):
        print('The ee_object must be an ee.ImageCollection.')
        return

    try:
        count = int(ee_object.size().getInfo())
        print("Total number of images: {}\n".format(count))

        if (descriptions is not None) and (len(descriptions) != count):
            print('The number of descriptions is not equal to the number of images.')
            return

        if descriptions is None:
            descriptions = ee_object.aggregate_array('system:index').getInfo()

        images = ee_object.toList(count)

        for i in range(0, count):
            image = ee.Image(images.get(i))
            name = descriptions[i]
            ee_export_image_to_drive(
                image, name, folder, region, scale, crs, max_pixels, file_format, format_options)

    except Exception as e:
        print(e)


def ee_to_numpy(ee_object, bands=None, region=None, properties=None, default_value=None):
    """Extracts a rectangular region of pixels from an image into a 2D numpy array per band.

    Args:
        ee_object (object): The image to sample.
        bands (list, optional): The list of band names to extract. Please make sure that all bands have the same spatial resolution. Defaults to None. 
        region (object, optional): The region whose projected bounding box is used to sample the image. The maximum number of pixels you can export is 262,144. Resampling and reprojecting all bands to a fixed scale can be useful. Defaults to the footprint in each band.
        properties (list, optional): The properties to copy over from the sampled image. Defaults to all non-system properties.
        default_value (float, optional): A default value used when a sampled pixel is masked or outside a band's footprint. Defaults to None.

    Returns:
        array: A 3D numpy array.
    """
    import numpy as np
    if not isinstance(ee_object, ee.Image):
        print('The input must be an ee.Image.')
        return

    if region is None:
        region = ee_object.geometry()

    try:

        if bands is not None:
            ee_object = ee_object.select(bands)
        else:
            bands = ee_object.bandNames().getInfo()

        band_arrs = ee_object.sampleRectangle(
            region=region, properties=properties, defaultValue=default_value)
        band_values = []

        for band in bands:
            band_arr = band_arrs.get(band).getInfo()
            band_value = np.array(band_arr)
            band_values.append(band_value)

        image = np.dstack(band_values)
        return image

    except Exception as e:
        print(e)


def download_ee_video(collection, video_args, out_gif):
    """Downloads a video thumbnail as a GIF image from Earth Engine.

    Args:
        collection (object): An ee.ImageCollection.
        video_args (object): Parameters for expring the video thumbnail.
        out_gif (str): File path to the output GIF.
    """
    import requests

    out_gif = os.path.abspath(out_gif)
    if not out_gif.endswith(".gif"):
        print('The output file must have an extension of .gif.')
        return

    if not os.path.exists(os.path.dirname(out_gif)):
        os.makedirs(os.path.dirname(out_gif))

    if 'region' in video_args.keys():
        roi = video_args['region']

        if not isinstance(roi, ee.Geometry):

            try:
                roi = roi.geometry()
            except Exception as e:
                print('Could not convert the provided roi to ee.Geometry')
                print(e)
                return

        video_args['region'] = roi

    try:
        print('Generating URL...')
        url = collection.getVideoThumbURL(video_args)

        print('Downloading GIF image from {}\nPlease wait ...'.format(url))
        r = requests.get(url, stream=True)

        if r.status_code != 200:
            print('An error occurred while downloading.')
            return
        else:
            with open(out_gif, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)
            print('The GIF image has been saved to: {}'.format(out_gif))
    except Exception as e:
        print(e)


########################################
#     EE Timeseries and Timelapse      #
########################################

def naip_timeseries(roi=None, start_year=2009, end_year=2018):
    """Creates NAIP annual timeseries

    Args:
        roi (object, optional): An ee.Geometry representing the region of interest. Defaults to None.
        start_year (int, optional): Starting year for the timeseries. Defaults to2009.
        end_year (int, optional): Ending year for the timeseries. Defaults to 2018.

    Returns:
        object: An ee.ImageCollection representing annual NAIP imagery.
    """
    # ee_initialize()
    try:

        def get_annual_NAIP(year):
            try:
                collection = ee.ImageCollection('USDA/NAIP/DOQQ')
                if roi is not None:
                    collection = collection.filterBounds(roi)
                start_date = ee.Date.fromYMD(year, 1, 1)
                end_date = ee.Date.fromYMD(year, 12, 31)
                naip = collection.filterDate(start_date, end_date) \
                    .filter(ee.Filter.listContains("system:band_names", "N"))
                naip = ee.Image(ee.ImageCollection(naip).mosaic())
                return naip
            except Exception as e:
                print(e)

        years = ee.List.sequence(start_year, end_year)
        collection = years.map(get_annual_NAIP)
        return collection

    except Exception as e:
        print(e)


def sentinel2_timeseries(roi=None, start_year=2015, end_year=2019, start_date='01-01', end_date='12-31'):
    """Generates an annual Sentinel 2 ImageCollection. This algorithm is adapted from https://gist.github.com/jdbcode/76b9ac49faf51627ebd3ff988e10adbc. A huge thank you to Justin Braaten for sharing his fantastic work.
       Images include both level 1C and level 2A imagery.
    Args:

        roi (object, optional): Region of interest to create the timelapse. Defaults to None.
        start_year (int, optional): Starting year for the timelapse. Defaults to 2015.
        end_year (int, optional): Ending year for the timelapse. Defaults to 2019.
        start_date (str, optional): Starting date (month-day) each year for filtering ImageCollection. Defaults to '01-01'.
        end_date (str, optional): Ending date (month-day) each year for filtering ImageCollection. Defaults to '12-31'.
    Returns:
        object: Returns an ImageCollection containing annual Sentinel 2 images.
    """
    ################################################################################

    ################################################################################
    # Input and output parameters.
    import re
    import datetime

    # ee_initialize()

    if roi is None:
        # roi = ee.Geometry.Polygon(
        #     [[[-180, -80],
        #       [-180, 80],
        #         [180, 80],
        #         [180, -80],
        #         [-180, -80]]], None, False)
        roi = ee.Geometry.Polygon(
            [[[-115.471773, 35.892718],
              [-115.471773, 36.409454],
                [-114.271283, 36.409454],
                [-114.271283, 35.892718],
                [-115.471773, 35.892718]]], None, False)

    if not isinstance(roi, ee.Geometry):

        try:
            roi = roi.geometry()
        except Exception as e:
            print('Could not convert the provided roi to ee.Geometry')
            print(e)
            return

    # Adjusts longitudes less than -180 degrees or greater than 180 degrees.
    geojson = ee_to_geojson(roi)
    geojson = adjust_longitude(geojson)
    roi = ee.Geometry(geojson)

    ################################################################################
    # Setup vars to get dates.
    if isinstance(start_year, int) and (start_year >= 2015) and (start_year <= 2020):
        pass
    else:
        print('The start year must be an integer >= 2015.')
        return

    if isinstance(end_year, int) and (end_year >= 2015) and (end_year <= 2020):
        pass
    else:
        print('The end year must be an integer <= 2020.')
        return

    if re.match("[0-9]{2}\-[0-9]{2}", start_date) and re.match("[0-9]{2}\-[0-9]{2}", end_date):
        pass
    else:
        print('The start data and end date must be month-day, such as 06-10, 09-20')
        return

    try:
        datetime.datetime(int(start_year), int(
            start_date[:2]), int(start_date[3:5]))
        datetime.datetime(int(end_year), int(end_date[:2]), int(end_date[3:5]))
    except Exception as e:
        print('The input dates are invalid.')
        print(e)
        return

    try:
        start_test = datetime.datetime(int(start_year), int(
            start_date[:2]), int(start_date[3:5]))
        end_test = datetime.datetime(
            int(end_year), int(end_date[:2]), int(end_date[3:5]))
        if start_test > end_test:
            raise ValueError('Start date must be prior to end date')
    except Exception as e:
        print(e)
        return

    def days_between(d1, d2):
        d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    n_days = days_between(str(start_year) + '-' + start_date,
                          str(start_year) + '-' + end_date)
    start_month = int(start_date[:2])
    start_day = int(start_date[3:5])
    start_date = str(start_year) + '-' + start_date
    end_date = str(end_year) + '-' + end_date

    # # Define a collection filter by date, bounds, and quality.
    # def colFilter(col, aoi):  # , startDate, endDate):
    #     return(col.filterBounds(aoi))

    # Get Sentinel 2 collections, both Level-1C (top of atmophere) and Level-2A (surface reflectance)
    MSILCcol = ee.ImageCollection('COPERNICUS/S2')
    MSI2Acol = ee.ImageCollection('COPERNICUS/S2_SR')

    # Define a collection filter by date, bounds, and quality.
    def colFilter(col, roi, start_date, end_date):
        return(col
               .filterBounds(roi)
               .filterDate(start_date, end_date))
        # .filter('CLOUD_COVER < 5')
        # .filter('GEOMETRIC_RMSE_MODEL < 15')
        # .filter('IMAGE_QUALITY == 9 || IMAGE_QUALITY_OLI == 9'))

    # Function to get and rename bands of interest from MSI
    def renameMSI(img):
        return(img.select(
            ['B2', 'B3', 'B4', 'B5', 'B6', 'B7',
                'B8', 'B8A', 'B11', 'B12', 'QA60'],
            ['Blue', 'Green', 'Red', 'Red Edge 1', 'Red Edge 2', 'Red Edge 3', 'NIR', 'Red Edge 4', 'SWIR1', 'SWIR2', 'QA60']))

    # Add NBR for LandTrendr segmentation.

    def calcNbr(img):
        return(img.addBands(img.normalizedDifference(['NIR', 'SWIR2'])
                            .multiply(-10000).rename('NBR')).int16())

    # Define function to mask out clouds and cloud shadows in images.
    # Use CFmask band included in USGS Landsat SR image product.

    def fmask(img):
        cloudOpaqueBitMask = 1 << 10
        cloudCirrusBitMask = 1 << 11
        qa = img.select('QA60')
        mask = qa.bitwiseAnd(cloudOpaqueBitMask).eq(0) \
            .And(qa.bitwiseAnd(cloudCirrusBitMask).eq(0))
        return(img.updateMask(mask))

    # Define function to prepare MSI images.
    def prepMSI(img):
        orig = img
        img = renameMSI(img)
        img = fmask(img)
        return(ee.Image(img.copyProperties(orig, orig.propertyNames()))
               .resample('bicubic'))

    # Get annual median collection.
    def getAnnualComp(y):
        startDate = ee.Date.fromYMD(
            ee.Number(y), ee.Number(start_month), ee.Number(start_day))
        endDate = startDate.advance(ee.Number(n_days), 'day')

        # Filter collections and prepare them for merging.
        MSILCcoly = colFilter(MSILCcol, roi, startDate, endDate).map(prepMSI)
        MSI2Acoly = colFilter(MSI2Acol, roi, startDate, endDate).map(prepMSI)

        # Merge the collections.
        col = MSILCcoly.merge(MSI2Acoly)

        yearImg = col.median()
        nBands = yearImg.bandNames().size()
        yearImg = ee.Image(ee.Algorithms.If(
            nBands,
            yearImg,
            dummyImg))
        return(calcNbr(yearImg)
               .set({'year': y, 'system:time_start': startDate.millis(), 'nBands': nBands}))

    ################################################################################

    # Make a dummy image for missing years.
    bandNames = ee.List(['Blue', 'Green', 'Red', 'Red Edge 1',
                         'Red Edge 2', 'Red Edge 3', 'NIR',
                         'Red Edge 4', 'SWIR1', 'SWIR2', 'QA60'])
    fillerValues = ee.List.repeat(0, bandNames.size())
    dummyImg = ee.Image.constant(fillerValues).rename(bandNames) \
        .selfMask().int16()

    ################################################################################
    # Get a list of years
    years = ee.List.sequence(start_year, end_year)

    ################################################################################
    # Make list of annual image composites.
    imgList = years.map(getAnnualComp)

    # Convert image composite list to collection
    imgCol = ee.ImageCollection.fromImages(imgList)

    imgCol = imgCol.map(lambda img: img.clip(roi))

    return imgCol


def landsat_timeseries(roi=None, start_year=1984, end_year=2020, start_date='06-10', end_date='09-20', apply_fmask=True):
    """Generates an annual Landsat ImageCollection. This algorithm is adapted from https://gist.github.com/jdbcode/76b9ac49faf51627ebd3ff988e10adbc. A huge thank you to Justin Braaten for sharing his fantastic work.

    Args:
        roi (object, optional): Region of interest to create the timelapse. Defaults to None.
        start_year (int, optional): Starting year for the timelapse. Defaults to 1984.
        end_year (int, optional): Ending year for the timelapse. Defaults to 2020.
        start_date (str, optional): Starting date (month-day) each year for filtering ImageCollection. Defaults to '06-10'.
        end_date (str, optional): Ending date (month-day) each year for filtering ImageCollection. Defaults to '09-20'.
        apply_fmask (bool, optional): Whether to apply Fmask (Function of mask) for automated clouds, cloud shadows, snow, and water masking.
    Returns:
        object: Returns an ImageCollection containing annual Landsat images.
    """

    ################################################################################
    # Input and output parameters.
    import re
    import datetime

    if roi is None:
        roi = ee.Geometry.Polygon(
            [[[-115.471773, 35.892718],
              [-115.471773, 36.409454],
                [-114.271283, 36.409454],
                [-114.271283, 35.892718],
                [-115.471773, 35.892718]]], None, False)

    if not isinstance(roi, ee.Geometry):

        try:
            roi = roi.geometry()
        except Exception as e:
            print('Could not convert the provided roi to ee.Geometry')
            print(e)
            return

    ################################################################################

    # Setup vars to get dates.
    if isinstance(start_year, int) and (start_year >= 1984) and (start_year < 2020):
        pass
    else:
        print('The start year must be an integer >= 1984.')
        return

    if isinstance(end_year, int) and (end_year > 1984) and (end_year <= 2020):
        pass
    else:
        print('The end year must be an integer <= 2020.')
        return

    if re.match("[0-9]{2}\-[0-9]{2}", start_date) and re.match("[0-9]{2}\-[0-9]{2}", end_date):
        pass
    else:
        print('The start date and end date must be month-day, such as 06-10, 09-20')
        return

    try:
        datetime.datetime(int(start_year), int(
            start_date[:2]), int(start_date[3:5]))
        datetime.datetime(int(end_year), int(end_date[:2]), int(end_date[3:5]))
    except Exception as e:
        print('The input dates are invalid.')
        return

    def days_between(d1, d2):
        d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    n_days = days_between(str(start_year) + '-' + start_date,
                          str(start_year) + '-' + end_date)
    start_month = int(start_date[:2])
    start_day = int(start_date[3:5])
    start_date = str(start_year) + '-' + start_date
    end_date = str(end_year) + '-' + end_date

    # # Define a collection filter by date, bounds, and quality.
    # def colFilter(col, aoi):  # , startDate, endDate):
    #     return(col.filterBounds(aoi))

    # Landsat collection preprocessingEnabled
    # Get Landsat surface reflectance collections for OLI, ETM+ and TM sensors.
    LC08col = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
    LE07col = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')
    LT05col = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')
    LT04col = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR')

    # Define a collection filter by date, bounds, and quality.
    def colFilter(col, roi, start_date, end_date):
        return(col
               .filterBounds(roi)
               .filterDate(start_date, end_date))
        # .filter('CLOUD_COVER < 5')
        # .filter('GEOMETRIC_RMSE_MODEL < 15')
        # .filter('IMAGE_QUALITY == 9 || IMAGE_QUALITY_OLI == 9'))

    # Function to get and rename bands of interest from OLI.
    def renameOli(img):
        return(img.select(
            ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'],
            ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']))

    # Function to get and rename bands of interest from ETM+.
    def renameEtm(img):
        return(img.select(
            ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
            ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']))

    # Add NBR for LandTrendr segmentation.
    def calcNbr(img):
        return(img.addBands(img.normalizedDifference(['NIR', 'SWIR2'])
                            .multiply(-10000).rename('NBR')).int16())

    # Define function to mask out clouds and cloud shadows in images.
    # Use CFmask band included in USGS Landsat SR image product.
    def fmask(img):
        cloudShadowBitMask = 1 << 3
        cloudsBitMask = 1 << 5
        qa = img.select('pixel_qa')
        mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) \
            .And(qa.bitwiseAnd(cloudsBitMask).eq(0))
        return(img.updateMask(mask))

    # Define function to prepare OLI images.
    def prepOli(img):
        orig = img
        img = renameOli(img)
        if apply_fmask:
            img = fmask(img)
        return (ee.Image(img.copyProperties(orig, orig.propertyNames()))
                .resample('bicubic'))

    # Define function to prepare ETM+ images.
    def prepEtm(img):
        orig = img
        img = renameEtm(img)
        if apply_fmask:
            img = fmask(img)
        return(ee.Image(img.copyProperties(orig, orig.propertyNames()))
               .resample('bicubic'))

    # Get annual median collection.
    def getAnnualComp(y):
        startDate = ee.Date.fromYMD(
            ee.Number(y), ee.Number(start_month), ee.Number(start_day))
        endDate = startDate.advance(ee.Number(n_days), 'day')

        # Filter collections and prepare them for merging.
        LC08coly = colFilter(LC08col, roi, startDate, endDate).map(prepOli)
        LE07coly = colFilter(LE07col, roi, startDate, endDate).map(prepEtm)
        LT05coly = colFilter(LT05col, roi, startDate, endDate).map(prepEtm)
        LT04coly = colFilter(LT04col, roi, startDate, endDate).map(prepEtm)

        # Merge the collections.
        col = LC08coly.merge(LE07coly).merge(LT05coly).merge(LT04coly)

        yearImg = col.median()
        nBands = yearImg.bandNames().size()
        yearImg = ee.Image(ee.Algorithms.If(
            nBands,
            yearImg,
            dummyImg))
        return(calcNbr(yearImg)
               .set({'year': y, 'system:time_start': startDate.millis(), 'nBands': nBands}))

    ################################################################################

    # Make a dummy image for missing years.
    bandNames = ee.List(['Blue', 'Green', 'Red', 'NIR',
                         'SWIR1', 'SWIR2', 'pixel_qa'])
    fillerValues = ee.List.repeat(0, bandNames.size())
    dummyImg = ee.Image.constant(fillerValues).rename(bandNames) \
        .selfMask().int16()

    ################################################################################
    # Get a list of years
    years = ee.List.sequence(start_year, end_year)

    ################################################################################
    # Make list of annual image composites.
    imgList = years.map(getAnnualComp)

    # Convert image composite list to collection
    imgCol = ee.ImageCollection.fromImages(imgList)

    imgCol = imgCol.map(lambda img: img.clip(
        roi).set({'coordinates': roi.coordinates()}))

    return imgCol

    # ################################################################################
    # # Run LandTrendr.
    # lt = ee.Algorithms.TemporalSegmentation.LandTrendr(
    #     timeSeries=imgCol.select(['NBR', 'SWIR1', 'NIR', 'Green']),
    #     maxSegments=10,
    #     spikeThreshold=0.7,
    #     vertexCountOvershoot=3,
    #     preventOneYearRecovery=True,
    #     recoveryThreshold=0.5,
    #     pvalThreshold=0.05,
    #     bestModelProportion=0.75,
    #     minObservationsNeeded=6)

    # ################################################################################
    # # Get fitted imagery. This starts export tasks.
    # def getYearStr(year):
    #     return(ee.String('yr_').cat(ee.Algorithms.String(year).slice(0,4)))

    # yearsStr = years.map(getYearStr)

    # r = lt.select(['SWIR1_fit']).arrayFlatten([yearsStr]).toShort()
    # g = lt.select(['NIR_fit']).arrayFlatten([yearsStr]).toShort()
    # b = lt.select(['Green_fit']).arrayFlatten([yearsStr]).toShort()

    # for i, c in zip([r, g, b], ['r', 'g', 'b']):
    #     descr = 'mamore-river-'+c
    #     name = 'users/user/'+descr
    #     print(name)
    #     task = ee.batch.Export.image.toAsset(
    #     image=i,
    #     region=roi.getInfo()['coordinates'],
    #     assetId=name,
    #     description=descr,
    #     scale=30,
    #     crs='EPSG:3857',
    #     maxPixels=1e13)
    #     task.start()


def landsat_ts_gif(roi=None, out_gif=None, start_year=1984, end_year=2019, start_date='06-10', end_date='09-20', bands=['NIR', 'Red', 'Green'], vis_params=None, dimensions=768, frames_per_second=10, apply_fmask=True, nd_bands=None, nd_threshold=0, nd_palette=['black', 'blue']):
    """Generates a Landsat timelapse GIF image. This function is adapted from https://emaprlab.users.earthengine.app/view/lt-gee-time-series-animator. A huge thank you to Justin Braaten for sharing his fantastic work.

    Args:
        roi (object, optional): Region of interest to create the timelapse. Defaults to None.
        out_gif (str, optional): File path to the output animated GIF. Defaults to None.
        start_year (int, optional): Starting year for the timelapse. Defaults to 1984.
        end_year (int, optional): Ending year for the timelapse. Defaults to 2019.
        start_date (str, optional): Starting date (month-day) each year for filtering ImageCollection. Defaults to '06-10'.
        end_date (str, optional): Ending date (month-day) each year for filtering ImageCollection. Defaults to '09-20'.
        bands (list, optional): Three bands selected from ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']. Defaults to ['NIR', 'Red', 'Green'].
        vis_params (dict, optional): Visualization parameters. Defaults to None.
        dimensions (int, optional): a number or pair of numbers in format WIDTHxHEIGHT) Maximum dimensions of the thumbnail to render, in pixels. If only one number is passed, it is used as the maximum, and the other dimension is computed by proportional scaling. Defaults to 768.
        frames_per_second (int, optional): Animation speed. Defaults to 10.
        apply_fmask (bool, optional): Whether to apply Fmask (Function of mask) for automated clouds, cloud shadows, snow, and water masking.
        nd_bands (list, optional): A list of names specifying the bands to use, e.g., ['Green', 'SWIR1']. The normalized difference is computed as (first − second) / (first + second). Note that negative input values are forced to 0 so that the result is confined to the range (-1, 1).  
        nd_threshold (float, optional): The threshold for extacting pixels from the normalized difference band. 
        nd_palette (list, optional): The color palette to use for displaying the normalized difference band. 

    Returns:
        str: File path to the output GIF image.
    """

    # ee_initialize()

    if roi is None:
        roi = ee.Geometry.Polygon(
            [[[-115.471773, 35.892718],
              [-115.471773, 36.409454],
                [-114.271283, 36.409454],
                [-114.271283, 35.892718],
                [-115.471773, 35.892718]]], None, False)
    elif isinstance(roi, ee.Feature) or isinstance(roi, ee.FeatureCollection):
        roi = roi.geometry()
    elif isinstance(roi, ee.Geometry):
        pass
    else:
        print('The provided roi is invalid. It must be an ee.Geometry')
        return

    if out_gif is None:
        out_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        filename = 'landsat_ts_' + random_string() + '.gif'
        out_gif = os.path.join(out_dir, filename)
    elif not out_gif.endswith('.gif'):
        print('The output file must end with .gif')
        return
    # elif not os.path.isfile(out_gif):
    #     print('The output file must be a file')
    #     return
    else:
        out_gif = os.path.abspath(out_gif)
        out_dir = os.path.dirname(out_gif)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    allowed_bands = ['Blue', 'Green', 'Red',
                     'NIR', 'SWIR1', 'SWIR2', 'pixel_qa']

    if len(bands) == 3 and all(x in allowed_bands for x in bands):
        pass
    else:
        raise Exception('You can only select 3 bands from the following: {}'.format(
            ', '.join(allowed_bands)))

    if nd_bands is not None:
        if len(nd_bands) == 2 and all(x in allowed_bands[:-1] for x in nd_bands):
            pass
        else:
            raise Exception('You can only select two bands from the following: {}'.format(
                ', '.join(allowed_bands[:-1])))

    try:
        col = landsat_timeseries(
            roi, start_year, end_year, start_date, end_date, apply_fmask)

        if vis_params is None:
            vis_params = {}
            vis_params['bands'] = bands
            vis_params['min'] = 0
            vis_params['max'] = 4000
            vis_params['gamma'] = [1, 1, 1]

        video_args = vis_params.copy()
        video_args['dimensions'] = dimensions
        video_args['region'] = roi
        video_args['framesPerSecond'] = frames_per_second
        video_args['crs'] = 'EPSG:3857'

        if 'bands' not in video_args.keys():
            video_args['bands'] = bands

        if 'min' not in video_args.keys():
            video_args['min'] = 0

        if 'max' not in video_args.keys():
            video_args['max'] = 4000

        if 'gamma' not in video_args.keys():
            video_args['gamma'] = [1, 1, 1]

        download_ee_video(col, video_args, out_gif)

        if nd_bands is not None:
            nd_images = landsat_ts_norm_diff(
                col, bands=nd_bands, threshold=nd_threshold)
            out_nd_gif = out_gif.replace('.gif', '_nd.gif')
            landsat_ts_norm_diff_gif(nd_images, out_gif=out_nd_gif, vis_params=None,
                                     palette=nd_palette, dimensions=dimensions, frames_per_second=frames_per_second)

        return out_gif

    except Exception as e:
        print(e)


def landsat_ts_norm_diff(collection, bands=['Green', 'SWIR1'], threshold=0):
    """Computes a normalized difference index based on a Landsat timeseries.

    Args:
        collection (ee.ImageCollection): A Landsat timeseries.
        bands (list, optional): The bands to use for computing normalized difference. Defaults to ['Green', 'SWIR1'].
        threshold (float, optional): The threshold to extract features. Defaults to 0.

    Returns:
        ee.ImageCollection: An ImageCollection containing images with values greater than the specified threshold. 
    """
    nd_images = collection.map(lambda img: img.normalizedDifference(
        bands).gt(threshold).copyProperties(img, img.propertyNames()))
    return nd_images


def landsat_ts_norm_diff_gif(collection, out_gif=None, vis_params=None, palette=['black', 'blue'], dimensions=768, frames_per_second=10):
    """[summary]

    Args:
        collection (ee.ImageCollection): The normalized difference Landsat timeseires.
        out_gif (str, optional): File path to the output animated GIF. Defaults to None.
        vis_params (dict, optional): Visualization parameters. Defaults to None.
        palette (list, optional): The palette to use for visualizing the timelapse. Defaults to ['black', 'blue']. The first color in the list is the background color.
        dimensions (int, optional): a number or pair of numbers in format WIDTHxHEIGHT) Maximum dimensions of the thumbnail to render, in pixels. If only one number is passed, it is used as the maximum, and the other dimension is computed by proportional scaling. Defaults to 768.
        frames_per_second (int, optional): Animation speed. Defaults to 10.

    Returns:
        str: File path to the output animated GIF.
    """
    coordinates = ee.Image(collection.first()).get('coordinates')
    roi = ee.Geometry.Polygon(coordinates, None, False)

    if out_gif is None:
        out_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        filename = 'landsat_ts_nd_' + random_string() + '.gif'
        out_gif = os.path.join(out_dir, filename)
    elif not out_gif.endswith('.gif'):
        raise Exception('The output file must end with .gif')

    bands = ['nd']
    if vis_params is None:
        vis_params = {}
        vis_params['bands'] = bands
        vis_params['palette'] = palette

    video_args = vis_params.copy()
    video_args['dimensions'] = dimensions
    video_args['region'] = roi
    video_args['framesPerSecond'] = frames_per_second
    video_args['crs'] = 'EPSG:3857'

    if 'bands' not in video_args.keys():
        video_args['bands'] = bands

    download_ee_video(collection, video_args, out_gif)

    return out_gif


########################################
#               eefolium GUI             #
########################################

def api_docs():
    """Open a browser and navigate to the eefolium API documentation.
    """
    import webbrowser

    url = 'https://giswqs.github.io/eefolium'
    webbrowser.open_new_tab(url)


def minimum_bounding_box(geojson):
    """Gets the minimum bounding box for a geojson polygon.

    Args:
        geojson (dict): A geojson dictionary.

    Returns:
        tuple: Returns a tuple containing the minimum bounding box in the format of (lower_left(lat, lon), upper_right(lat, lon)), such as ((13, -130), (32, -120)).
    """
    coordinates = []
    try:
        if 'geometry' in geojson.keys():
            coordinates = geojson['geometry']['coordinates'][0]
        else:
            coordinates = geojson['coordinates'][0]
        lower_left = min([x[1] for x in coordinates]), min(
            [x[0] for x in coordinates])  # (lat, lon)
        upper_right = max([x[1] for x in coordinates]), max([x[0]
                                                             for x in coordinates])  # (lat, lon)
        bounds = (lower_left, upper_right)
        return bounds
    except Exception as e:
        raise Exception(e)


def is_latlon_valid(location):
    """Checks whether a pair of coordinates is valid.

    Args:
        location (str): A pair of latlon coordinates separated by comma or space.

    Returns:
        bool: Returns True if valid.
    """
    latlon = []
    if ',' in location:
        latlon = [float(x) for x in location.split(',')]
    elif ' ' in location:
        latlon = [float(x) for x in location.split(' ')]
    else:
        print(
            'The coordinates should be numbers only and separated by comma or space, such as 40.2, -100.3')
        return False

    try:
        lat, lon = float(latlon[0]), float(latlon[1])
        if lat >= -90 and lat <= 90 and lon >= -180 and lat <= 180:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def latlon_from_text(location):
    """Extracts latlon from text.

    Args:
        location (str): A pair of latlon coordinates separated by comma or space.

    Returns:
        bool: Returns (lat, lon) if valid.
    """
    latlon = []
    try:
        if ',' in location:
            latlon = [float(x) for x in location.split(',')]
        elif ' ' in location:
            latlon = [float(x) for x in location.split(' ')]
        else:
            print(
                'The lat-lon coordinates should be numbers only and separated by comma or space, such as 40.2, -100.3')
            return None

        lat, lon = latlon[0], latlon[1]
        if lat >= -90 and lat <= 90 and lon >= -180 and lat <= 180:
            return lat, lon
        else:
            return None

    except Exception as e:
        print(e)
        print('The lat-lon coordinates should be numbers only and separated by comma or space, such as 40.2, -100.3')
        return None


def search_ee_data(keywords):
    """Searches Earth Engine data catalog.

    Args:
        keywords (str): Keywords to search for can be id, provider, tag and so on

    Returns:
        list: Returns a lit of assets.
    """
    try:
        cmd = 'geeadd search --keywords "{}"'.format(str(keywords))
        output = os.popen(cmd).read()
        start_index = output.index('[')
        assets = eval(output[start_index:])

        results = []
        for asset in assets:
            asset_dates = asset['start_date'] + ' - ' + asset['end_date']
            asset_snippet = asset['ee_id_snippet']
            start_index = asset_snippet.index("'") + 1
            end_index = asset_snippet.index("'", start_index)
            asset_id = asset_snippet[start_index:end_index]

            asset['dates'] = asset_dates
            asset['id'] = asset_id
            asset['uid'] = asset_id.replace('/', '_')
            # asset['url'] = 'https://developers.google.com/earth-engine/datasets/catalog/' + asset['uid']
            # asset['thumbnail'] = 'https://mw1.google.com/ges/dd/images/{}_sample.png'.format(
            #     asset['uid'])
            results.append(asset)

        return results

    except Exception as e:
        print(e)
        

def ee_data_html(asset):
    """Generates HTML from an asset to be used in the HTML widget.

    Args:
        asset (dict): A dictionary containing an Earth Engine asset.

    Returns:
        str: A string containing HTML.
    """
    template = '''
        <html>
        <body>
            <h3>asset_title</h3>
            <h4>Dataset Availability</h4>
                <p style="margin-left: 40px">asset_dates</p>
            <h4>Earth Engine Snippet</h4>
                <p style="margin-left: 40px">ee_id_snippet</p>
            <h4>Earth Engine Data Catalog</h4>
                <p style="margin-left: 40px"><a href="asset_url" target="_blank">asset_id</a></p>
            <h4>Dataset Thumbnail</h4>
                <img src="thumbnail_url">
        </body>
        </html>
    '''

    try:

        text = template.replace('asset_title', asset['title'])
        text = text.replace('asset_dates', asset['dates'])
        text = text.replace('ee_id_snippet', asset['ee_id_snippet'])
        text = text.replace('asset_id', asset['id'])
        text = text.replace('asset_url', asset['asset_url'])
        # asset['thumbnail'] = ee_data_thumbnail(asset['id'])
        text = text.replace('thumbnail_url', asset['thumbnail_url'])

        return text

    except Exception as e:
        print(e)


########################################
#             EE Utilities             #
########################################

def date_sequence(start, end, unit, date_format='YYYY-MM-dd'):
    """Creates a date sequence.

    Args:
        start (str): The start date, e.g., '2000-01-01'.
        end (str): The end date, e.g., '2000-12-31'.
        unit (str): One of 'year', 'month' 'week', 'day', 'hour', 'minute', or 'second'.
        date_format (str, optional): A pattern, as described at http://joda-time.sourceforge.net/apidocs/org/joda/time/format/DateTimeFormat.html. Defaults to 'YYYY-MM-dd'.

    Returns:
        ee.List: A list of date sequence.
    """
    start_date = ee.Date(start)
    end_date = ee.Date(end)
    count = ee.Number(end_date.difference(start_date, unit)).toInt()
    num_seq = ee.List.sequence(0, count)
    date_seq = num_seq.map(
        lambda d: start_date.advance(d, unit).format(date_format))
    return date_seq


def legend_from_ee(ee_class_table):
    """Extract legend from an Earth Engine class table on the Earth Engine Data Catalog page
    such as https://developers.google.com/earth-engine/datasets/catalog/MODIS_051_MCD12Q1

    Value	Color	Description
    0	1c0dff	Water
    1	05450a	Evergreen needleleaf forest
    2	086a10	Evergreen broadleaf forest
    3	54a708	Deciduous needleleaf forest
    4	78d203	Deciduous broadleaf forest
    5	009900	Mixed forest
    6	c6b044	Closed shrublands
    7	dcd159	Open shrublands
    8	dade48	Woody savannas
    9	fbff13	Savannas
    10	b6ff05	Grasslands
    11	27ff87	Permanent wetlands
    12	c24f44	Croplands
    13	a5a5a5	Urban and built-up
    14	ff6d4c	Cropland/natural vegetation mosaic
    15	69fff8	Snow and ice
    16	f9ffa4	Barren or sparsely vegetated
    254	ffffff	Unclassified

    Args:
        ee_class_table (str): An Earth Engine class table with triple quotes.

    Returns:
        dict: Returns a legend dictionary that can be used to create a legend.
    """
    try:
        ee_class_table = ee_class_table.strip()
        lines = ee_class_table.split('\n')[1:]

        if lines[0] == 'Value\tColor\tDescription':
            lines = lines[1:]

        legend_dict = {}
        for _, line in enumerate(lines):
            items = line.split("\t")
            items = [item.strip() for item in items]
            color = items[1]
            key = items[0] + " " + items[2]
            legend_dict[key] = color

        return legend_dict

    except Exception as e:
        print(e)


def vis_to_qml(ee_class_table, out_qml):
    """Create a QGIS Layer Style (.qml) based on an Earth Engine class table from the Earth Engine Data Catalog page
    such as https://developers.google.com/earth-engine/datasets/catalog/MODIS_051_MCD12Q1

    Value	Color	Description
    0	1c0dff	Water
    1	05450a	Evergreen needleleaf forest
    2	086a10	Evergreen broadleaf forest
    3	54a708	Deciduous needleleaf forest
    4	78d203	Deciduous broadleaf forest
    5	009900	Mixed forest
    6	c6b044	Closed shrublands
    7	dcd159	Open shrublands
    8	dade48	Woody savannas
    9	fbff13	Savannas
    10	b6ff05	Grasslands
    11	27ff87	Permanent wetlands
    12	c24f44	Croplands
    13	a5a5a5	Urban and built-up
    14	ff6d4c	Cropland/natural vegetation mosaic
    15	69fff8	Snow and ice
    16	f9ffa4	Barren or sparsely vegetated
    254	ffffff	Unclassified

    Args:
        ee_class_table (str): An Earth Engine class table with triple quotes.
        out_qml (str): File path to the output QGIS Layer Style (.qml).
    """
    import pkg_resources

    pkg_dir = os.path.dirname(
        pkg_resources.resource_filename("eefolium", "eefolium.py"))
    data_dir = os.path.join(pkg_dir, 'data')
    template_dir = os.path.join(data_dir, 'template')
    qml_template = os.path.join(template_dir, 'NLCD.qml')

    out_dir = os.path.dirname(out_qml)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(qml_template) as f:
        lines = f.readlines()
        header = lines[:31]
        footer = lines[51:]

    entries = []
    try:
        ee_class_table = ee_class_table.strip()
        lines = ee_class_table.split('\n')[1:]

        if lines[0] == 'Value\tColor\tDescription':
            lines = lines[1:]

        for line in lines:
            items = line.split("\t")
            items = [item.strip() for item in items]
            value = items[0]
            color = items[1]
            label = items[2]
            entry = '        <paletteEntry alpha="255" color="#{}" value="{}" label="{}"/>\n'.format(color, value, label)
            entries.append(entry)

        out_lines = header + entries + footer
        with open(out_qml, "w") as f:
            f.writelines(out_lines)        

    except Exception as e:
        print(e)


def create_nlcd_qml(out_qml):
    """Create a QGIS Layer Style (.qml) for NLCD data

    Args:
        out_qml (str): File path to the ouput qml.  
    """
    import pkg_resources
    import shutil

    pkg_dir = os.path.dirname(
        pkg_resources.resource_filename("eefolium", "eefolium.py"))
    data_dir = os.path.join(pkg_dir, 'data')
    template_dir = os.path.join(data_dir, 'template')
    qml_template = os.path.join(template_dir, 'NLCD.qml')

    out_dir = os.path.dirname(out_qml)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    shutil.copyfile(qml_template, out_qml)

        
def load_GeoTIFF(URL):
    """Loads a Cloud Optimized GeoTIFF (COG) as an Image. Only Google Cloud Storage is supported. The URL can be one of the following formats:
    Option 1: gs://pdd-stac/disasters/hurricane-harvey/0831/20170831_172754_101c_3B_AnalyticMS.tif
    Option 2: https://storage.googleapis.com/pdd-stac/disasters/hurricane-harvey/0831/20170831_172754_101c_3B_AnalyticMS.tif
    Option 3: https://storage.cloud.google.com/gcp-public-data-landsat/LC08/01/044/034/LC08_L1TP_044034_20131228_20170307_01_T1/LC08_L1TP_044034_20131228_20170307_01_T1_B5.TIF

    Args:
        URL (str): The Cloud Storage URL of the GeoTIFF to load.

    Returns:
        ee.Image: an Earth Engine image.
    """

    uri = URL.strip()

    if uri.startswith('https://storage.googleapis.com/'):
        uri = uri.replace('https://storage.googleapis.com/', 'gs://')
    elif uri.startswith('https://storage.cloud.google.com/'):
        uri = uri.replace('https://storage.cloud.google.com/', 'gs://')

    if not uri.startswith('gs://'):
        raise Exception(
            'Invalid GCS URL: {}. Expected something of the form "gs://bucket/path/to/object.tif".'.format(uri))

    if not uri.lower().endswith('.tif'):
        raise Exception(
            'Invalid GCS URL: {}. Expected something of the form "gs://bucket/path/to/object.tif".'.format(uri))

    cloud_image = ee.Image.loadGeoTIFF(uri)
    return cloud_image


def load_GeoTIFFs(URLs):
    """Loads a list of Cloud Optimized GeoTIFFs (COG) as an ImageCollection. URLs is a list of URL, which can be one of the following formats:
    Option 1: gs://pdd-stac/disasters/hurricane-harvey/0831/20170831_172754_101c_3B_AnalyticMS.tif
    Option 2: https://storage.googleapis.com/pdd-stac/disasters/hurricane-harvey/0831/20170831_172754_101c_3B_AnalyticMS.tif
    Option 3: https://storage.cloud.google.com/gcp-public-data-landsat/LC08/01/044/034/LC08_L1TP_044034_20131228_20170307_01_T1/LC08_L1TP_044034_20131228_20170307_01_T1_B5.TIF

    Args:
        URLs (list): A list of Cloud Storage URL of the GeoTIFF to load.

    Returns:
        ee.ImageCollection: An Earth Engine ImageCollection.
    """

    if not isinstance(URLs, list):
        raise Exception('The URLs argument must be a list.')

    URIs = []
    for URL in URLs:
        uri = URL.strip()

        if uri.startswith('https://storage.googleapis.com/'):
            uri = uri.replace('https://storage.googleapis.com/', 'gs://')
        elif uri.startswith('https://storage.cloud.google.com/'):
            uri = uri.replace('https://storage.cloud.google.com/', 'gs://')

        if not uri.startswith('gs://'):
            raise Exception(
                'Invalid GCS URL: {}. Expected something of the form "gs://bucket/path/to/object.tif".'.format(uri))

        if not uri.lower().endswith('.tif'):
            raise Exception(
                'Invalid GCS URL: {}. Expected something of the form "gs://bucket/path/to/object.tif".'.format(uri))

        URIs.append(uri)

    URIs = ee.List(URIs)
    collection = URIs.map(lambda uri: ee.Image.loadGeoTIFF(uri))
    return ee.ImageCollection(collection)


def image_props(img, date_format='YYYY-MM-dd'):
    """Gets image properties.

    Args:
        img (ee.Image): The input image.
        date_format (str, optional): The output date format. Defaults to 'YYYY-MM-dd HH:mm:ss'.

    Returns:
        dd.Dictionary: The dictionary containing image properties.
    """
    if not isinstance(img, ee.Image):
        print('The input object must be an ee.Image')
        return

    keys = img.propertyNames().remove('system:footprint').remove('system:bands')
    values = keys.map(lambda p: img.get(p))

    bands = img.bandNames()
    scales = bands.map(lambda b: img.select([b]).projection().nominalScale())
    scale = ee.Algorithms.If(scales.distinct().size().gt(
        1), ee.Dictionary.fromLists(bands.getInfo(), scales), scales.get(0))
    image_date = ee.Date(img.get('system:time_start')).format(date_format)
    time_start = ee.Date(img.get('system:time_start')
                         ).format('YYYY-MM-dd HH:mm:ss')
    # time_end = ee.Date(img.get('system:time_end')).format('YYYY-MM-dd HH:mm:ss')
    time_end = ee.Algorithms.If(ee.List(img.propertyNames()).contains('system:time_end'), ee.Date(
        img.get('system:time_end')).format('YYYY-MM-dd HH:mm:ss'), time_start)
    asset_size = ee.Number(img.get('system:asset_size')).divide(
        1e6).format().cat(ee.String(' MB'))

    props = ee.Dictionary.fromLists(keys, values)
    props = props.set('system:time_start', time_start)
    props = props.set('system:time_end', time_end)
    props = props.set('system:asset_size', asset_size)
    props = props.set('NOMINAL_SCALE', scale)
    props = props.set('IMAGE_DATE', image_date)

    return props


def image_stats(img, region=None, scale=None):
    """Gets image descriptive statistics.

    Args:
        img (ee.Image): The input image to calculate descriptive statistics.
        region (object, optional): The region over which to reduce data. Defaults to the footprint of the image's first band.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.

    Returns:
        ee.Dictionary: A dictionary containing the description statistics of the input image.
    """

    if not isinstance(img, ee.Image):
        print('The input object must be an ee.Image')
        return

    stat_types = ['min', 'max', 'mean', 'std', 'sum']

    image_min = image_min_value(img, region, scale)
    image_max = image_max_value(img, region, scale)
    image_mean = image_mean_value(img, region, scale)
    image_std = image_std_value(img, region, scale)
    image_sum = image_sum_value(img, region, scale)

    stat_results = ee.List(
        [image_min, image_max, image_mean, image_std, image_sum])

    stats = ee.Dictionary.fromLists(stat_types, stat_results)

    return stats


def adjust_longitude(in_fc):
    """Adjusts longitude if it is less than -180 or greater than 180.

    Args:
        in_fc (dict): The input dictionary containing coordinates.

    Returns:
        dict: A dictionary containing the converted longitudes
    """
    try:

        keys = in_fc.keys()

        if 'geometry' in keys:

            coordinates = in_fc['geometry']['coordinates']

            if in_fc['geometry']['type'] == 'Point':
                longitude = coordinates[0]
                if longitude < - 180:
                    longitude = 360 + longitude
                elif longitude > 180:
                    longitude = longitude - 360
                in_fc['geometry']['coordinates'][0] = longitude

            elif in_fc['geometry']['type'] == 'Polygon':
                for index1, item in enumerate(coordinates):
                    for index2, element in enumerate(item):
                        longitude = element[0]
                        if longitude < - 180:
                            longitude = 360 + longitude
                        elif longitude > 180:
                            longitude = longitude - 360
                        in_fc['geometry']['coordinates'][index1][index2][0] = longitude

            elif in_fc['geometry']['type'] == 'LineString':
                for index, element in enumerate(coordinates):
                    longitude = element[0]
                    if longitude < - 180:
                        longitude = 360 + longitude
                    elif longitude > 180:
                        longitude = longitude - 360
                    in_fc['geometry']['coordinates'][index][0] = longitude

        elif 'type' in keys:

            coordinates = in_fc['coordinates']

            if in_fc['type'] == 'Point':
                longitude = coordinates[0]
                if longitude < - 180:
                    longitude = 360 + longitude
                elif longitude > 180:
                    longitude = longitude - 360
                in_fc['coordinates'][0] = longitude

            elif in_fc['type'] == 'Polygon':
                for index1, item in enumerate(coordinates):
                    for index2, element in enumerate(item):
                        longitude = element[0]
                        if longitude < - 180:
                            longitude = 360 + longitude
                        elif longitude > 180:
                            longitude = longitude - 360
                        in_fc['coordinates'][index1][index2][0] = longitude

            elif in_fc['type'] == 'LineString':
                for index, element in enumerate(coordinates):
                    longitude = element[0]
                    if longitude < - 180:
                        longitude = 360 + longitude
                    elif longitude > 180:
                        longitude = longitude - 360
                    in_fc['coordinates'][index][0] = longitude

        return in_fc

    except Exception as e:
        print(e)
        return None


def zonal_statistics(in_value_raster, in_zone_vector, out_file_path, statistics_type='MEAN', scale=None, crs=None, tile_scale=1.0, **kwargs):
    """Summarizes the values of a raster within the zones of another dataset and exports the results as a csv, shp, json, kml, or kmz.

    Args:
        in_value_raster (object): An ee.Image that contains the values on which to calculate a statistic.
        in_zone_vector (object): An ee.FeatureCollection that defines the zones.
        out_file_path (str): Output file path that will contain the summary of the values in each zone. The file type can be: csv, shp, json, kml, kmz
        statistics_type (str, optional): Statistic type to be calculated. Defaults to 'MEAN'. For 'HIST', you can provide three parameters: max_buckets, min_bucket_width, and max_raw. For 'FIXED_HIST', you must provide three parameters: hist_min, hist_max, and hist_steps.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.
        crs (str, optional): The projection to work in. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale. Defaults to None.
        tile_scale (float, optional): A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default. Defaults to 1.0.
    """

    if not isinstance(in_value_raster, ee.Image):
        print('The input raster must be an ee.Image.')
        return

    if not isinstance(in_zone_vector, ee.FeatureCollection):
        print('The input zone data must be an ee.FeatureCollection.')
        return

    allowed_formats = ['csv', 'json', 'kml', 'kmz', 'shp']
    filename = os.path.abspath(out_file_path)
    basename = os.path.basename(filename)
    # name = os.path.splitext(basename)[0]
    filetype = os.path.splitext(basename)[1][1:].lower()

    if not (filetype in allowed_formats):
        print('The file type must be one of the following: {}'.format(
            ', '.join(allowed_formats)))
        return

    # Parameters for histogram
    # The maximum number of buckets to use when building a histogram; will be rounded up to a power of 2.
    max_buckets = None
    # The minimum histogram bucket width, or null to allow any power of 2.
    min_bucket_width = None
    # The number of values to accumulate before building the initial histogram.
    max_raw = None
    hist_min = 1.0  # The lower (inclusive) bound of the first bucket.
    hist_max = 100.0  # The upper (exclusive) bound of the last bucket.
    hist_steps = 10  # The number of buckets to use.

    if 'max_buckets' in kwargs.keys():
        max_buckets = kwargs['max_buckets']
    if 'min_bucket_width' in kwargs.keys():
        min_bucket_width = kwargs['min_bucket']
    if 'max_raw' in kwargs.keys():
        max_raw = kwargs['max_raw']

    if statistics_type.upper() == 'FIXED_HIST' and ('hist_min' in kwargs.keys()) and ('hist_max' in kwargs.keys()) and ('hist_steps' in kwargs.keys()):
        hist_min = kwargs['hist_min']
        hist_max = kwargs['hist_max']
        hist_steps = kwargs['hist_steps']
    elif statistics_type.upper() == 'FIXED_HIST':
        print('To use fixedHistogram, please provide these three parameters: hist_min, hist_max, and hist_steps.')
        return

    allowed_statistics = {
        'MEAN': ee.Reducer.mean(),
        'MAXIMUM': ee.Reducer.max(),
        'MEDIAN': ee.Reducer.median(),
        'MINIMUM': ee.Reducer.min(),
        'STD': ee.Reducer.stdDev(),
        'MIN_MAX': ee.Reducer.minMax(),
        'SUM': ee.Reducer.sum(),
        'VARIANCE': ee.Reducer.variance(),
        'HIST': ee.Reducer.histogram(maxBuckets=max_buckets, minBucketWidth=min_bucket_width, maxRaw=max_raw),
        'FIXED_HIST': ee.Reducer.fixedHistogram(hist_min, hist_max, hist_steps)
    }

    if not (statistics_type.upper() in allowed_statistics.keys()):
        print('The statistics type must be one of the following: {}'.format(
            ', '.join(list(allowed_statistics.keys()))))
        return

    if scale is None:
        scale = in_value_raster.projection().nominalScale().multiply(10)

    try:
        print('Computing statistics ...')
        result = in_value_raster.reduceRegions(
            collection=in_zone_vector, reducer=allowed_statistics[statistics_type], scale=scale, crs=crs, tileScale=tile_scale)
        ee_export_vector(result, filename)
    except Exception as e:
        print(e)


def zonal_statistics_by_group(in_value_raster, in_zone_vector, out_file_path, statistics_type='SUM', decimal_places=0, denominator=1.0, scale=None, crs=None, tile_scale=1.0):
    """Summarizes the area or percentage of a raster by group within the zones of another dataset and exports the results as a csv, shp, json, kml, or kmz.

    Args:
        in_value_raster (object): An integer Image that contains the values on which to calculate area/percentage.
        in_zone_vector (object): An ee.FeatureCollection that defines the zones.
        out_file_path (str): Output file path that will contain the summary of the values in each zone. The file type can be: csv, shp, json, kml, kmz
        statistics_type (str, optional): Can be either 'SUM' or 'PERCENTAGE' . Defaults to 'SUM'.
        decimal_places (int, optional): The number of decimal places to use. Defaults to 0.
        denominator (float, optional): To covert area units (e.g., from square meters to square kilometers). Defaults to 1.0.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.
        crs (str, optional): The projection to work in. If unspecified, the projection of the image's first band is used. If specified in addition to scale, rescaled to the specified scale. Defaults to None.
        tile_scale (float, optional): A scaling factor used to reduce aggregation tile size; using a larger tileScale (e.g. 2 or 4) may enable computations that run out of memory with the default. Defaults to 1.0.

    """
    if not isinstance(in_value_raster, ee.Image):
        print('The input raster must be an ee.Image.')
        return

    band_count = in_value_raster.bandNames().size().getInfo()

    band_name = ''
    if band_count == 1:
        band_name = in_value_raster.bandNames().get(0)
    else:
        print('The input image can only have one band.')
        return

    band_types = in_value_raster.bandTypes().get(band_name).getInfo()
    band_type = band_types.get('precision')
    if band_type != 'int':
        print('The input image band must be integer type.')
        return

    if not isinstance(in_zone_vector, ee.FeatureCollection):
        print('The input zone data must be an ee.FeatureCollection.')
        return

    allowed_formats = ['csv', 'json', 'kml', 'kmz', 'shp']
    filename = os.path.abspath(out_file_path)
    basename = os.path.basename(filename)
    # name = os.path.splitext(basename)[0]
    filetype = os.path.splitext(basename)[1][1:]

    if not (filetype.lower() in allowed_formats):
        print('The file type must be one of the following: {}'.format(
            ', '.join(allowed_formats)))
        return

    out_dir = os.path.dirname(filename)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    allowed_statistics = ['SUM', 'PERCENTAGE']
    if not (statistics_type.upper() in allowed_statistics):
        print('The statistics type can only be one of {}'.format(
            ', '.join(allowed_statistics)))
        return

    if scale is None:
        scale = in_value_raster.projection().nominalScale().multiply(10)

    try:

        print('Computing ... ')
        geometry = in_zone_vector.geometry()

        hist = in_value_raster.reduceRegion(ee.Reducer.frequencyHistogram(
        ), geometry=geometry, bestEffort=True, scale=scale)
        class_values = ee.Dictionary(hist.get(band_name)).keys().map(
            lambda v: ee.Number.parse(v)).sort()

        class_names = class_values.map(
            lambda c: ee.String('Class_').cat(ee.Number(c).format()))

        # class_count = class_values.size().getInfo()
        dataset = ee.Image.pixelArea().divide(denominator).addBands(in_value_raster)

        init_result = dataset.reduceRegions(**{
            'collection': in_zone_vector,
            'reducer': ee.Reducer.sum().group(**{
                'groupField': 1,
                'groupName': 'group',
            }),
            'scale': scale
        })

        # def build_dict(input_list):

        #     decimal_format = '%.{}f'.format(decimal_places)
        #     in_dict = input_list.map(lambda x: ee.Dictionary().set(ee.String('Class_').cat(
        #         ee.Number(ee.Dictionary(x).get('group')).format()), ee.Number.parse(ee.Number(ee.Dictionary(x).get('sum')).format(decimal_format))))
        #     return in_dict

        def get_keys(input_list):
            return input_list.map(lambda x: ee.String('Class_').cat(ee.Number(ee.Dictionary(x).get('group')).format()))

        def get_values(input_list):
            decimal_format = '%.{}f'.format(decimal_places)
            return input_list.map(lambda x: ee.Number.parse(ee.Number(ee.Dictionary(x).get('sum')).format(decimal_format)))

        def set_attribute(f):
            groups = ee.List(f.get('groups'))
            keys = get_keys(groups)
            values = get_values(groups)
            total_area = ee.List(values).reduce(ee.Reducer.sum())

            def get_class_values(x):
                cls_value = ee.Algorithms.If(
                    keys.contains(x), values.get(keys.indexOf(x)), 0)
                cls_value = ee.Algorithms.If(ee.String(statistics_type).compareTo(ee.String(
                    'SUM')), ee.Number(cls_value).divide(ee.Number(total_area)), cls_value)
                return cls_value

            full_values = class_names.map(lambda x: get_class_values(x))
            attr_dict = ee.Dictionary.fromLists(class_names, full_values)
            attr_dict = attr_dict.set('Class_sum', total_area)

            return f.set(attr_dict).set('groups', None)

        final_result = init_result.map(set_attribute)
        ee_export_vector(final_result, filename)

    except Exception as e:
        print(e)


def vec_area(fc):
    """Calculate the area (m2) of each each feature in a feature collection.

    Args:
        fc (object): The feature collection to compute the area.

    Returns:
        object: ee.FeatureCollection
    """
    return fc.map(lambda f: f.set({'area_m2': f.area(1).round()}))


def vec_area_km2(fc):
    """Calculate the area (km2) of each each feature in a feature collection.

    Args:
        fc (object): The feature collection to compute the area.

    Returns:
        object: ee.FeatureCollection
    """
    return fc.map(lambda f: f.set({'area_km2': f.area(1).divide(1e6).round()}))


def vec_area_mi2(fc):
    """Calculate the area (square mile) of each each feature in a feature collection.

    Args:
        fc (object): The feature collection to compute the area.

    Returns:
        object: ee.FeatureCollection
    """
    return fc.map(lambda f: f.set({'area_mi2': f.area(1).divide(2.59e6).round()}))


def vec_area_ha(fc):
    """Calculate the area (hectare) of each each feature in a feature collection.

    Args:
        fc (object): The feature collection to compute the area.

    Returns:
        object: ee.FeatureCollection
    """
    return fc.map(lambda f: f.set({'area_ha': f.area(1).divide(1e4).round()}))


def remove_geometry(fc):
    """Remove .geo coordinate field from a FeatureCollection

    Args:
        fc (object): The input FeatureCollection.

    Returns:
        object: The output FeatureCollection without the geometry field.
    """
    return fc.select([".*"], None, False)


def image_cell_size(img):
    """Retrieves the image cell size (e.g., spatial resolution)

    Args:
        img (object): ee.Image

    Returns:
        float: The nominal scale in meters.
    """
    bands = img.bandNames()
    scales = bands.map(lambda b: img.select([b]).projection().nominalScale())
    scale = ee.Algorithms.If(scales.distinct().size().gt(1), ee.Dictionary.fromLists(bands.getInfo(), scales), scales.get(0))
    return scale


def image_scale(img):
    """Retrieves the image cell size (e.g., spatial resolution)

    Args:
        img (object): ee.Image

    Returns:
        float: The nominal scale in meters.
    """
    # bands = img.bandNames()
    # scales = bands.map(lambda b: img.select([b]).projection().nominalScale())
    # scale = ee.Algorithms.If(scales.distinct().size().gt(1), ee.Dictionary.fromLists(bands.getInfo(), scales), scales.get(0))
    return img.select(0).projection().nominalScale()


def image_band_names(img):
    """Gets image band names.

    Args:
        img (ee.Image): The input image.

    Returns:
        ee.List: The returned list of image band names.
    """
    return img.bandNames()


def image_date(img, date_format='YYYY-MM-dd'):
    """Retrieves the image acquisition date.

    Args:
        img (object): ee.Image
        date_format (str, optional): The date format to use. Defaults to 'YYYY-MM-dd'.

    Returns:
        str: A string representing the acquisition of the image.
    """
    return ee.Date(img.get('system:time_start')).format(date_format)


def image_area(img, region=None, scale=None, denominator=1.0):
    """Calculates the the area of an image.

    Args:
        img (object): ee.Image
        region (object, optional): The region over which to reduce data. Defaults to the footprint of the image's first band.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.
        denominator (float, optional): The denominator to use for converting size from square meters to other units. Defaults to 1.0.

    Returns:
        object: ee.Dictionary
    """
    if region is None:
        region = img.geometry()

    if scale is None:
        scale = image_scale(img)

    pixel_area = img.unmask().neq(ee.Image(0)).multiply(
        ee.Image.pixelArea()).divide(denominator)
    img_area = pixel_area.reduceRegion(**{
        'geometry': region,
        'reducer': ee.Reducer.sum(),
        'scale': scale,
        'maxPixels': 1e12
    })
    return img_area


def image_max_value(img, region=None, scale=None):
    """Retrieves the maximum value of an image.

    Args:
        img (object): The image to calculate the maximum value.
        region (object, optional): The region over which to reduce data. Defaults to the footprint of the image's first band.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.

    Returns:
        object: ee.Number
    """
    if region is None:
        region = img.geometry()

    if scale is None:
        scale = image_scale(img)

    max_value = img.reduceRegion(**{
        'reducer': ee.Reducer.max(),
        'geometry': region,
        'scale': scale,
        'maxPixels': 1e12
    })
    return max_value


def image_min_value(img, region=None, scale=None):
    """Retrieves the minimum value of an image.

    Args:
        img (object): The image to calculate the minimum value.
        region (object, optional): The region over which to reduce data. Defaults to the footprint of the image's first band.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.

    Returns:
        object: ee.Number
    """
    if region is None:
        region = img.geometry()

    if scale is None:
        scale = image_scale(img)

    min_value = img.reduceRegion(**{
        'reducer': ee.Reducer.min(),
        'geometry': region,
        'scale': scale,
        'maxPixels': 1e12
    })
    return min_value


def image_mean_value(img, region=None, scale=None):
    """Retrieves the mean value of an image.

    Args:
        img (object): The image to calculate the mean value.
        region (object, optional): The region over which to reduce data. Defaults to the footprint of the image's first band.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.

    Returns:
        object: ee.Number
    """
    if region is None:
        region = img.geometry()

    if scale is None:
        scale = image_scale(img)

    mean_value = img.reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': region,
        'scale': scale,
        'maxPixels': 1e12
    })
    return mean_value


def image_std_value(img, region=None, scale=None):
    """Retrieves the standard deviation of an image.

    Args:
        img (object): The image to calculate the standard deviation.
        region (object, optional): The region over which to reduce data. Defaults to the footprint of the image's first band.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.

    Returns:
        object: ee.Number
    """
    if region is None:
        region = img.geometry()

    if scale is None:
        scale = image_scale(img)

    std_value = img.reduceRegion(**{
        'reducer': ee.Reducer.stdDev(),
        'geometry': region,
        'scale': scale,
        'maxPixels': 1e12
    })
    return std_value


def image_sum_value(img, region=None, scale=None):
    """Retrieves the sum of an image.

    Args:
        img (object): The image to calculate the standard deviation.
        region (object, optional): The region over which to reduce data. Defaults to the footprint of the image's first band.
        scale (float, optional): A nominal scale in meters of the projection to work in. Defaults to None.

    Returns:
        object: ee.Number
    """
    if region is None:
        region = img.geometry()

    if scale is None:
        scale = image_scale(img)

    sum_value = img.reduceRegion(**{
        'reducer': ee.Reducer.sum(),
        'geometry': region,
        'scale': scale,
        'maxPixels': 1e12
    })
    return sum_value


def extract_values_to_points(in_points, img, label, scale=None):
    """Extracts image values to points.

    Args:
        in_points (object): ee.FeatureCollection
        img (object): ee.Image
        label (str): The column name to keep.
        scale (float, optional): The image resolution to use. Defaults to None.

    Returns:
        object: ee.FeatureCollection
    """
    if scale is None:
        scale = image_scale(img)

    out_fc = img.sampleRegions(**{
        'collection': in_points,
        'properties': [label],
        'scale': scale
    })

    return out_fc


def image_reclassify(img, in_list, out_list):
    """Reclassify an image.

    Args:
        img (object): The image to which the remapping is applied.
        in_list (list): The source values (numbers or EEArrays). All values in this list will be mapped to the corresponding value in 'out_list'.
        out_list (list): The destination values (numbers or EEArrays). These are used to replace the corresponding values in 'from'. Must have the same number of values as 'in_list'.

    Returns:
        object: ee.Image
    """
    image = img.remap(in_list, out_list)
    return image


def image_smoothing(img, reducer, kernel):
    """Smooths an image.

    Args:
        img (object): The image to be smoothed.
        reducer (object): ee.Reducer
        kernel (object): ee.Kernel

    Returns:
        object: ee.Image
    """
    image = img.reduceNeighborhood(**{
        'reducer': reducer,
        'kernel': kernel,
    })
    return image


def rename_bands(img, in_band_names, out_band_names):
    """Renames image bands.

    Args:
        img (object): The image to be renamed.
        in_band_names (list): The list of of input band names.
        out_band_names (list): The list of output band names.

    Returns:
        object: The output image with the renamed bands.
    """
    return img.select(in_band_names, out_band_names)


def bands_to_image_collection(img):
    """Converts all bands in an image to an image collection.

    Args:
        img (object): The image to convert.

    Returns:
        object: ee.ImageCollection
    """
    collection = ee.ImageCollection(
        img.bandNames().map(lambda b: img.select([b])))
    return collection


def find_landsat_by_path_row(landsat_col, path_num, row_num):
    """Finds Landsat images by WRS path number and row number.

    Args:
        landsat_col (str): The image collection id of Landsat. 
        path_num (int): The WRS path number.
        row_num (int): the WRS row number.

    Returns:
        object: ee.ImageCollection
    """
    try:
        if isinstance(landsat_col, str):
            landsat_col = ee.ImageCollection(landsat_col)
            collection = landsat_col.filter(ee.Filter.eq('WRS_PATH', path_num)) \
                .filter(ee.Filter.eq('WRS_ROW', row_num))
            return collection
    except Exception as e:
        print(e)


def str_to_num(in_str):
    """Converts a string to an ee.Number.

    Args:
        in_str (str): The string to convert to a number.

    Returns:
        object: ee.Number
    """
    return ee.Number.parse(str)


def array_sum(arr):
    """Accumulates elements of an array along the given axis.

    Args:
        arr (object): Array to accumulate.

    Returns:
        object: ee.Number
    """
    return ee.Array(arr).accum(0).get([-1])


def array_mean(arr):
    """Calculates the mean of an array along the given axis.

    Args:
        arr (object): Array to calculate mean.

    Returns:
        object: ee.Number
    """
    total = ee.Array(arr).accum(0).get([-1])
    size = arr.length()
    return ee.Number(total.divide(size))


def get_annual_NAIP(year, RGBN=True):
    """Filters NAIP ImageCollection by year.

    Args:
        year (int): The year to filter the NAIP ImageCollection.
        RGBN (bool, optional): Whether to retrieve 4-band NAIP imagery only. Defaults to True.

    Returns:
        object: ee.ImageCollection
    """
    try:
        collection = ee.ImageCollection('USDA/NAIP/DOQQ')
        start_date = str(year) + '-01-01'
        end_date = str(year) + '-12-31'
        naip = collection.filterDate(start_date, end_date)
        if RGBN:
            naip = naip.filter(ee.Filter.listContains(
                "system:band_names", "N"))
        return naip
    except Exception as e:
        print(e)


def get_all_NAIP(start_year=2009, end_year=2019):
    """Creates annual NAIP imagery mosaic.

    Args:
        start_year (int, optional): The starting year. Defaults to 2009.
        end_year (int, optional): The ending year. Defaults to 2019.

    Returns:
        object: ee.ImageCollection
    """
    try:

        def get_annual_NAIP(year):
            try:
                collection = ee.ImageCollection('USDA/NAIP/DOQQ')
                start_date = ee.Date.fromYMD(year, 1, 1)
                end_date = ee.Date.fromYMD(year, 12, 31)
                naip = collection.filterDate(start_date, end_date) \
                    .filter(ee.Filter.listContains("system:band_names", "N"))
                return ee.ImageCollection(naip)
            except Exception as e:
                print(e)

        years = ee.List.sequence(start_year, end_year)
        collection = years.map(get_annual_NAIP)
        return collection

    except Exception as e:
        print(e)


def annual_NAIP(year, region):
    """Create an NAIP mosaic of a specified year for a specified region. 

    Args:
        year (int): The specified year to create the mosaic for. 
        region (object): ee.Geometry

    Returns:
        object: ee.Image
    """

    start_date = ee.Date.fromYMD(year, 1, 1)
    end_date = ee.Date.fromYMD(year, 12, 31)
    collection = ee.ImageCollection('USDA/NAIP/DOQQ') \
        .filterDate(start_date, end_date) \
        .filterBounds(region)

    time_start = ee.Date(
        ee.List(collection.aggregate_array('system:time_start')).sort().get(0))
    time_end = ee.Date(
        ee.List(collection.aggregate_array('system:time_end')).sort().get(-1))
    image = ee.Image(collection.mosaic().clip(region))
    NDWI = ee.Image(image).normalizedDifference(
        ['G', 'N']).select(['nd'], ['ndwi'])
    NDVI = ee.Image(image).normalizedDifference(
        ['N', 'R']).select(['nd'], ['ndvi'])
    image = image.addBands(NDWI)
    image = image.addBands(NDVI)
    return image.set({'system:time_start': time_start, 'system:time_end': time_end})


def find_NAIP(region, add_NDVI=True, add_NDWI=True):
    """Create annual NAIP mosaic for a given region.

    Args:
        region (object): ee.Geometry
        add_NDVI (bool, optional): Whether to add the NDVI band. Defaults to True.
        add_NDWI (bool, optional): Whether to add the NDWI band. Defaults to True.

    Returns:
        object: ee.ImageCollection
    """

    init_collection = ee.ImageCollection('USDA/NAIP/DOQQ') \
        .filterBounds(region) \
        .filterDate('2009-01-01', '2019-12-31') \
        .filter(ee.Filter.listContains("system:band_names", "N"))

    yearList = ee.List(init_collection.distinct(
        ['system:time_start']).aggregate_array('system:time_start'))
    init_years = yearList.map(lambda y: ee.Date(y).get('year'))

    # remove duplicates
    init_years = ee.Dictionary(init_years.reduce(
        ee.Reducer.frequencyHistogram())).keys()
    years = init_years.map(lambda x: ee.Number.parse(x))
    # years = init_years.map(lambda x: x)

    # Available NAIP years with NIR band
    def NAIPAnnual(year):
        start_date = ee.Date.fromYMD(year, 1, 1)
        end_date = ee.Date.fromYMD(year, 12, 31)
        collection = init_collection.filterDate(start_date, end_date)
        # .filterBounds(geometry)
        # .filter(ee.Filter.listContains("system:band_names", "N"))
        time_start = ee.Date(
            ee.List(collection.aggregate_array('system:time_start')).sort().get(0)).format('YYYY-MM-dd')
        time_end = ee.Date(
            ee.List(collection.aggregate_array('system:time_end')).sort().get(-1)).format('YYYY-MM-dd')
        col_size = collection.size()
        image = ee.Image(collection.mosaic().clip(region))

        if add_NDVI:
            NDVI = ee.Image(image).normalizedDifference(
                ['N', 'R']).select(['nd'], ['ndvi'])
            image = image.addBands(NDVI)

        if add_NDWI:
            NDWI = ee.Image(image).normalizedDifference(
                ['G', 'N']).select(['nd'], ['ndwi'])
            image = image.addBands(NDWI)

        return image.set({'system:time_start': time_start, 'system:time_end': time_end, 'tiles': col_size})

    # remove years with incomplete coverage
    naip = ee.ImageCollection(years.map(NAIPAnnual))
    mean_size = ee.Number(naip.aggregate_mean('tiles'))
    total_sd = ee.Number(naip.aggregate_total_sd('tiles'))
    threshold = mean_size.subtract(total_sd.multiply(1))
    naip = naip.filter(ee.Filter.Or(ee.Filter.gte(
        'tiles', threshold), ee.Filter.gte('tiles', 15)))
    naip = naip.filter(ee.Filter.gte('tiles', 7))

    naip_count = naip.size()
    naip_seq = ee.List.sequence(0, naip_count.subtract(1))

    def set_index(index):
        img = ee.Image(naip.toList(naip_count).get(index))
        return img.set({'system:uid': ee.Number(index).toUint8()})

    naip = naip_seq.map(set_index)

    return ee.ImageCollection(naip)


def filter_NWI(HUC08_Id, region, exclude_riverine=True):
    """Retrives NWI dataset for a given HUC8 watershed.

    Args:
        HUC08_Id (str): The HUC8 watershed id.
        region (object): ee.Geometry
        exclude_riverine (bool, optional): Whether to exclude riverine wetlands. Defaults to True.

    Returns:
        object: ee.FeatureCollection
    """
    nwi_asset_prefix = 'users/wqs/NWI-HU8/HU8_'
    nwi_asset_suffix = '_Wetlands'
    nwi_asset_path = nwi_asset_prefix + HUC08_Id + nwi_asset_suffix
    nwi_huc = ee.FeatureCollection(nwi_asset_path).filterBounds(region)

    if exclude_riverine:
        nwi_huc = nwi_huc.filter(ee.Filter.notEquals(
            **{'leftField': 'WETLAND_TY', 'rightValue': 'Riverine'}))
    return nwi_huc


def filter_HUC08(region):
    """Filters HUC08 watersheds intersecting a given region.

    Args:
        region (object): ee.Geometry

    Returns:
        object: ee.FeatureCollection
    """

    USGS_HUC08 = ee.FeatureCollection('USGS/WBD/2017/HUC08')   # Subbasins
    HUC08 = USGS_HUC08.filterBounds(region)
    return HUC08


# Find HUC10 intersecting a geometry
def filter_HUC10(region):
    """Filters HUC10 watersheds intersecting a given region.

    Args:
        region (object): ee.Geometry

    Returns:
        object: ee.FeatureCollection
    """

    USGS_HUC10 = ee.FeatureCollection('USGS/WBD/2017/HUC10')   # Watersheds
    HUC10 = USGS_HUC10.filterBounds(region)
    return HUC10


def find_HUC08(HUC08_Id):
    """Finds a HUC08 watershed based on a given HUC08 ID

    Args:
        HUC08_Id (str): The HUC08 ID.

    Returns:
        object: ee.FeatureCollection
    """

    USGS_HUC08 = ee.FeatureCollection('USGS/WBD/2017/HUC08')   # Subbasins
    HUC08 = USGS_HUC08.filter(ee.Filter.eq('huc8', HUC08_Id))
    return HUC08


def find_HUC10(HUC10_Id):
    """Finds a HUC10 watershed based on a given HUC08 ID

    Args:
        HUC10_Id (str): The HUC10 ID.

    Returns:
        object: ee.FeatureCollection
    """

    USGS_HUC10 = ee.FeatureCollection('USGS/WBD/2017/HUC10')   # Watersheds
    HUC10 = USGS_HUC10.filter(ee.Filter.eq('huc10', HUC10_Id))
    return HUC10


# find NWI by HUC08
def find_NWI(HUC08_Id, exclude_riverine=True):
    """Finds NWI dataset for a given HUC08 watershed.

    Args:
        HUC08_Id (str): The HUC08 watershed ID.
        exclude_riverine (bool, optional): Whether to exclude riverine wetlands. Defaults to True.

    Returns:
        object: ee.FeatureCollection
    """

    nwi_asset_prefix = 'users/wqs/NWI-HU8/HU8_'
    nwi_asset_suffix = '_Wetlands'
    nwi_asset_path = nwi_asset_prefix + HUC08_Id + nwi_asset_suffix
    nwi_huc = ee.FeatureCollection(nwi_asset_path)
    if exclude_riverine:
        nwi_huc = nwi_huc.filter(ee.Filter.notEquals(
            **{'leftField': 'WETLAND_TY', 'rightValue': 'Riverine'}))
    return nwi_huc


def nwi_add_color(fc):
    """Converts NWI vector dataset to image and add color to it.

    Args:
        fc (object): ee.FeatureCollection

    Returns:
        object: ee.Image
    """
    emergent = ee.FeatureCollection(
        fc.filter(ee.Filter.eq('WETLAND_TY', 'Freshwater Emergent Wetland')))
    emergent = emergent.map(lambda f: f.set(
        'R', 127).set('G', 195).set('B', 28))
    # print(emergent.first())

    forested = fc.filter(ee.Filter.eq(
        'WETLAND_TY', 'Freshwater Forested/Shrub Wetland'))
    forested = forested.map(lambda f: f.set('R', 0).set('G', 136).set('B', 55))

    pond = fc.filter(ee.Filter.eq('WETLAND_TY', 'Freshwater Pond'))
    pond = pond.map(lambda f: f.set('R', 104).set('G', 140).set('B', 192))

    lake = fc.filter(ee.Filter.eq('WETLAND_TY', 'Lake'))
    lake = lake.map(lambda f: f.set('R', 19).set('G', 0).set('B', 124))

    riverine = fc.filter(ee.Filter.eq('WETLAND_TY', 'Riverine'))
    riverine = riverine.map(lambda f: f.set(
        'R', 1).set('G', 144).set('B', 191))

    fc = ee.FeatureCollection(emergent.merge(
        forested).merge(pond).merge(lake).merge(riverine))

#   base = ee.Image(0).mask(0).toInt8()
    base = ee.Image().byte()
    img = base.paint(fc, 'R') \
        .addBands(base.paint(fc, 'G')
                  .addBands(base.paint(fc, 'B')))

    return img


def nwi_rename(names):

    name_dict = ee.Dictionary({
        'Freshwater Emergent Wetland': 'Emergent',
        'Freshwater Forested/Shrub Wetland': 'Forested',
        'Estuarine and Marine Wetland': 'Estuarine',
        'Freshwater Pond': 'Pond',
        'Lake': 'Lake',
        'Riverine': 'Riverine',
        'Estuarine and Marine Deepwater': 'Deepwater',
        'Other': 'Other'
    })

    new_names = ee.List(names).map(lambda name: name_dict.get(name))
    return new_names


def summarize_by_group(collection, column, group, group_name, stats_type, return_dict=True):
    """Calculates summary statistics by group.

    Args:
        collection (object): The input feature collection
        column (str): The value column to calculate summary statistics.
        group (str): The name of the group column.
        group_name (str): The new group name to use.
        stats_type (str): The type of summary statistics.
        return_dict (bool): Whether to return the result as a dictionary.

    Returns:
        object: ee.Dictionary or ee.List
    """
    stats_type = stats_type.lower()
    allowed_stats = ['min', 'max', 'mean',
                     'median', 'sum', 'stdDev', 'variance']
    if stats_type not in allowed_stats:
        print('The stats type must be one of the following: {}'.format(
            ','.join(allowed_stats)))
        return

    stats_dict = {
        'min': ee.Reducer.min(),
        'max': ee.Reducer.max(),
        'mean': ee.Reducer.mean(),
        'median': ee.Reducer.median(),
        'sum': ee.Reducer.sum(),
        'stdDev': ee.Reducer.stdDev(),
        'variance': ee.Reducer.variance()
    }

    selectors = [column, group]
    stats = collection.reduceColumns(**{
        'selectors': selectors,
        'reducer': stats_dict[stats_type].group(**{
            'groupField': 1,
            'groupName': group_name
        })
    })
    results = ee.List(ee.Dictionary(stats).get('groups'))
    if return_dict:
        keys = results.map(lambda k: ee.Dictionary(k).get(group_name))
        values = results.map(lambda v: ee.Dictionary(v).get(stats_type))
        results = ee.Dictionary.fromLists(keys, values)

    return results


def summary_stats(collection, column):
    """Aggregates over a given property of the objects in a collection, calculating the sum, min, max, mean, 
    sample standard deviation, sample variance, total standard deviation and total variance of the selected property.

    Args:
        collection (FeatureCollection): The input feature collection to calculate summary statistics.
        column (str): The name of the column to calculate summary statistics.

    Returns:
        dict: The dictionary containing information about the summary statistics.
    """
    stats = collection.aggregate_stats(column).getInfo()
    return eval(str(stats))


def column_stats(collection, column, stats_type):
    """Aggregates over a given property of the objects in a collection, calculating the sum, min, max, mean, 
    sample standard deviation, sample variance, total standard deviation and total variance of the selected property.

    Args:
        collection (FeatureCollection): The input feature collection to calculate statistics.
        column (str): The name of the column to calculate statistics.
        stats_type (str): The type of statistics to calculate.

    Returns:
        dict: The dictionary containing information about the requested statistics.
    """
    stats_type = stats_type.lower()
    allowed_stats = ['min', 'max', 'mean',
                     'median', 'sum', 'stdDev', 'variance']
    if stats_type not in allowed_stats:
        print('The stats type must be one of the following: {}'.format(
            ','.join(allowed_stats)))
        return

    stats_dict = {
        'min': ee.Reducer.min(),
        'max': ee.Reducer.max(),
        'mean': ee.Reducer.mean(),
        'median': ee.Reducer.median(),
        'sum': ee.Reducer.sum(),
        'stdDev': ee.Reducer.stdDev(),
        'variance': ee.Reducer.variance()
    }

    selectors = [column]
    stats = collection.reduceColumns(**{
        'selectors': selectors,
        'reducer': stats_dict[stats_type]
    })

    return stats


def ee_num_round(num, decimal=2):
    """Rounds a number to a specified number of decimal places.

    Args:
        num (ee.Number): The number to round.
        decimal (int, optional): The number of decimal places to round. Defaults to 2.

    Returns:
        ee.Number: The number with the specified decimal places rounded.
    """
    format_str = '%.{}f'.format(decimal)
    return ee.Number.parse(ee.Number(num).format(format_str))


def num_round(num, decimal=2):
    """Rounds a number to a specified number of decimal places.

    Args:
        num (float): The number to round.
        decimal (int, optional): The number of decimal places to round. Defaults to 2.

    Returns:
        float: The number with the specified decimal places rounded.
    """
    return round(num, decimal)
