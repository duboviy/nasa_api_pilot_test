from datetime import datetime, timedelta
from collections import Counter
import requests
# Python 2 and 3 compatible code
try:
    from urllib.parse import urljoin  # py 3.x series
except ImportError:
     from urlparse import urljoin  # py 2.x series

from config import API_KEY, MAIN_URL, MANIFESTS_URL, ROVER_PHOTOS_URL, RATIO


class APIErrorException(RuntimeError):
    pass


class IllegalArgumentError(ValueError):
    pass


def get_rover_cameras(rover):
    partial_url = MANIFESTS_URL.format(rover=rover)
    rover_manifest = _request(partial_url)

    photos = rover_manifest['photo_manifest']['photos']
    cameras = (cam for rover_photos in photos for cam in rover_photos['cameras'])
    return set(cameras)


def get_rover_photos(rover, camera=None, sol=None, earth_date=None, page=None):
    params = {'camera': camera,
              'page': page}

    if sol and earth_date:
        raise IllegalArgumentError("You should specify only sol or earth_date, can't use both of them")

    if sol:
        params['sol'] = sol
    else:
        params['earth_date'] = earth_date

    partial_url = ROVER_PHOTOS_URL.format(rover=rover)
    photos = _request(partial_url, params)['photos']
    return photos


def sol_to_earth_date_by_formula(sol, landing_date):
    sol_to_earth_date = round(sol * RATIO)
    str_earth_date = datetime.strptime(landing_date, "%Y-%m-%d") + timedelta(days=sol_to_earth_date)
    earth_date = datetime.strftime(str_earth_date, "%Y-%m-%d")
    return earth_date


def photo_cameras_distribution(rover, sol):
    cam_dist = {}

    for cam in get_rover_cameras(rover):
        cam_dist[cam] = len(get_rover_photos(rover, camera=cam, sol=sol))

    return cam_dist


def low_dist_cameras(cam_dist, threshold):
    max_photos = max(cam_dist.values())

    low_dist_cameras = {camera: photos for camera, photos in cam_dist.items()
                        if photos * threshold <= max_photos}

    return low_dist_cameras


def _request(partial_url, params=None):
    """ Sends a GET request. Used as a base function to request data from NASA API. """
    url = urljoin(MAIN_URL, partial_url)

    params = params or {}
    params['api_key'] = API_KEY

    data = _get_api_data(url, params=params)
    return data


def _get_api_data(url, params=None):
    response = requests.get(url, params=params)
    data = response.json()

    if 'errors' in data:
        raise APIErrorException('error getting %s: %s' % (response.url,
                                                          data['errors']))
    return data


def get_rover_cameras_naive_brute_force_way(by_sol_all, rover):
    """
    Not efficient way as get_rover_cameras and photo_cameras_distribution usage,
    but function can be used for additional check.
    """
    counter = Counter(photo['camera']['name'] for photo in by_sol_all)

    # also need to add cameras with no (zero) photos
    all_cams = Counter({cam: 0 for cam in get_rover_cameras(rover)})
    counter.update(all_cams)

    return counter


def rover_landing_date_from_api(by_sol):
    """ Pass list of photos data by sol to get rover landing value from api. """
    return by_sol[0]["rover"]["landing_date"]


def earth_date_equals_to_sol_from_api(by_sol):
    """ Pass list of photos data by sol to get earth date value from api. """
    return by_sol[0]['earth_date']
