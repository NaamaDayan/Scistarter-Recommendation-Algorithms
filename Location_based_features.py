from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import ast
from ip2geotools.databases.noncommercial import DbIpCity


def get_user_loc(ip_addr):
    try:
        response = DbIpCity.get(ip_addr, api_key='free')
        return [response.latitude, response.longitude]
    except Exception as e:
        print("Exception in get_user_loc: ", ip_addr, e)
        return [0, 0]


def is_location_in_project_range(user_location, project_regions):
    if project_regions != project_regions:  # online project
        return True
    point = Point(user_location[0], user_location[1])
    polygon = Polygon(project_regions)
    return polygon.contains(point)


def is_project_reachable_to_user(user_location,project):
    from Recommender import projects_info
    if int(project) in projects_info.index:
        regions = projects_info.loc[int(project)]['regions']
        if regions == regions:  # project has regions
            regions = [tuple(i) for i in ast.literal_eval(regions)]
        return is_location_in_project_range(user_location, regions)
    return False

