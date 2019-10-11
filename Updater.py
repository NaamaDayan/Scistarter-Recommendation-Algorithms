import pickle
import os
import numpy as np
import pandas as pd
import urllib.request
import json
import re
import requests

from datetime import datetime

import Performance_Calculations
import Recommender
from FileReadWrite import FileReadWrite

historical_records_pkl = FileReadWrite('historical_records.pkl')
user_project_matrix_csv = FileReadWrite('user_project_matrix.csv')
page = 0
record = 0

if historical_records_pkl.exists() and user_project_matrix_csv.exists():
    historical_records = historical_records_pkl.get_data_pkl()
    user_project_matrix = user_project_matrix_csv.get_data_csv()
else:
    historical_records = pd.DataFrame(columns = ['profile', 'project', 'type', 'whens', 'origin', 'repetitions'])
    user_project_matrix = pd.DataFrame(columns=['user'])

page = int(historical_records.shape[0]/500)
record = int(historical_records.shape[0]%500)

def update_records():
    global page
    global record
    print('filter current page')
    cleaned = __filter_current_page(page, record)
    if len(cleaned['activity']) != 0:
        __update_data(cleaned)

    while True:
        page = int(page) + 1
        print('load page', page)
#     for testing
        # if page > 6:
        #     break

        page = str(page)
        url = 'https://scistarter.org/api/stream-page?page='+page+'&key=5255cf33e739e9ecc20b9b260cb68567fbc81f6b1bfb4808ba2c39548501f0a1523e2e97d79563645cba40a09894bfdb277779d1145a596f237ebdc166afcf50'
        content = __getPage(url)
        if len(content['activity']) == 0:
            break
        else:
            __update_data(content)

    historical_records_pkl.put_data_pkl(historical_records)
    user_project_matrix_csv.put_data_csv(user_project_matrix)
    __put_update_time()


def __getPage(url):
    page = urllib.request.urlopen(url)
    content = page.read().decode("utf8")
    page.close()
    JSON_full = {'activity': []}
    for entry in content.splitlines():
#         if '"project": null' in entry:
#             continue
        cleaned_text = __extractattribute(entry)
        JSON_single = __JSONconverter(cleaned_text)
        JSON_full['activity'].append(JSON_single)

    # return json.dumps(JSON_full)
    return JSON_full

def __filter_current_page(page, record):
    page = str(page)
    cleaned_data = {'activity': []}
    url = 'https://scistarter.org/api/stream-page?page='+page+'&key=5255cf33e739e9ecc20b9b260cb68567fbc81f6b1bfb4808ba2c39548501f0a1523e2e97d79563645cba40a09894bfdb277779d1145a596f237ebdc166afcf50'
    content = __getPage(url)
    cleaned = content['activity'][record:]
    cleaned_data['activity'] = cleaned
    return cleaned_data

def __JSONconverter (cleaned_text):
    ### input: cleaned attribute string: ['"profile": "c3174748ab29f73d8c6226d0c2171aeb"', '"when": "2016-07-22 14:07:43"', '"project": 25']
    ### output: JSON for one entry
    data = {}
    for a in cleaned_text:
        if ('"profile"') in a:
            index = [m.start() for m in re.finditer('"', a)]
            user = a[index[-2]+1:index[-1]]
            data['user'] = user
        elif ('"project"') in a:
            index = [m.start() for m in re.finditer(':', a)]
            project = a[index[-1]+2:]
            data['project'] = int(project)
        elif ('"when"') in a:
            index = [m.start() for m in re.finditer('"', a)]
            time = a[index[-2]+1:index[-1]]
            data['when'] = time
        elif ('"type"') in a:
            index = [m.start() for m in re.finditer('"', a)]
            mtype = a[index[-2]+1:index[-1]]
            data['type'] = mtype
        elif ('"origin"') in a:
            index = [m.start() for m in re.finditer('"', a)]
            origin = a[index[-2]+1:index[-1]]
            data['origin'] = origin
        elif ('"repetitions"') in a:
            index = [m.start() for m in re.finditer(':', a)]
            rep = a[index[-1]+2:]
            data['repetitions'] = int(rep)
        else:
            print("0")
    # json_data = json.dumps(data)

    return data

def __extractattribute (entry):
    ### input: single entry, such as "'{"origin": "Unspecified", "profile": "c3174748ab29f73d8c6226d0c2171aeb", "extra": "", "repetitions": 1, "profile_utm_campaign": "", "profile_referrer": "", "duration": 0.0, "profile_utm_term": "", "authenticated": true, "profile_origin": "", "where": null, "when": "2016-07-22 14:07:43", "profile_utm_medium": "", "project": 25, "magnitude": 1, "profile_utm_source": "", "profile_utm_content": "", "type": "Participated"}'"
    ### output: user, time, project, such as ['"profile": "c3174748ab29f73d8c6226d0c2171aeb"', '"when": "2016-07-22 14:07:43"', '"project": 25']
    attribute_list = entry.split(", ")
    cleaned_text = list(filter (lambda a: ('"profile"' in a or '"when"' in a or '"project"'in a or '"type"' in a or '"origin"' in a or '"repetitions"' in a), attribute_list))
    return cleaned_text

def __update_data(cleaned):
    for entry in cleaned['activity']:
        user = entry['user']
        project = entry['project']
        when = entry['when']
        origin = entry['origin']
        mtype = entry['type']
        repetitions = entry['repetitions']

        # Update user project matrix
        if not (user in list(user_project_matrix['user'])):
            new_row_number = user_project_matrix.shape[0]
            user_project_matrix.loc[new_row_number] = [user] + list(np.zeros(user_project_matrix.shape[1]-1,dtype=int))
        if not (str(project) in list(user_project_matrix)):
            user_project_matrix[str(project)] = 0
            update_project_info(int(project))
        # old_value = data[data['user']==user][str(project)]
        user_project_matrix.loc[user_project_matrix['user']==user, str(project)] = 1

        # Update historical records
        historical_row = historical_records.shape[0]
        historical_records.loc[historical_row] = [user, project, mtype, when, origin, repetitions]

def __put_update_time():
    if(os.path.isfile('update_times.txt')):
        file = open('update_times.txt', 'a+')
        file.write('\n'+datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
        file.close()
    else:
        file = open('update_times.txt', 'w+')
        file.write(datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
        file.close()


def update_project_info(project_id):
    csrf_token = requests.get('https://scistarter.org').text.split('csrfmiddlewaretoken" value="')[1].split('"')[0]
    try:
        r = requests.post('https://scistarter.org/ui/request', json={'key': 'entity', 'id': int(project_id)},
                          headers={'Referer': 'https://scistarter.org/',
                                   'X-CSRFToken': csrf_token},
                          cookies={'csrftoken': csrf_token})
        status = r.json()['messages'][0]['status']['value']
        if status != 1 and project_id not in Recommender.non_active_projects['project'].values:
            Recommender.non_active_projects.loc[len(Recommender.non_active_projects.index)] = project_id
            Recommender.non_active_projects.to_csv('non_active_projects.csv', index=False)
        #project data
        if project_id not in Performance_Calculations.projects_data.index:
            topics = [i['label'] for i in r.json()['messages'][0]['topics']]
            idea_age_group = " ".join([i['label'].split("(")[0] for i in r.json()['messages'][0]['audience']])
            outdoors = r.json()['messages'][0]['outdoors']
            indoors = r.json()['messages'][0]['indoors']
            place = ""
            if outdoors and indoors:
                place = "Indoors or Outdoors"
            elif outdoors:
                place = "Outdoors"
            elif indoors:
                place = "Indoors"
            tags = ", ".join(r.json()['messages'][0]['tags'])
            project_data = [topics, idea_age_group, place, tags]
            Performance_Calculations.projects_data.loc[project_id] = project_data
            Performance_Calculations.projects_data.to_csv('projects_data.csv')
        #project info
        if project_id not in Recommender.projects_info.index:
            region_info = r.json()['messages'][0]['regions']
            regions = json.loads(region_info)['coordinates'][0][0] if region_info != None else []
            is_active = region_info is None
            Recommender.projects_info.loc[project_id] = [is_active, regions]
            Recommender.projects_info.to_csv('projects_info.csv')
    except Exception as e:
        print("exception! project: ", project_id, e)

if __name__ == '__main__':
    update_records()