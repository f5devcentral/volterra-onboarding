import logging
import requests
import json
from datetime import datetime

logging.getLogger("volterra-helper").setLevel(logging.INFO)


def sObj(op, status, res):
    now = datetime.now()
    step = {
        'operation': op,
        'status': status,
        'time': now.strftime("%m/%d/%Y, %H:%M:%S"),
        'resp': res
    }
    return step


def createVoltSession(token, tenantName):
    apiToken = "APIToken {0}".format(token)
    s = requests.Session()
    s.headers.update({'Authorization': apiToken})
    urlBase = "https://{0}.console.ves.volterra.io".format(tenantName)
    session = {'session': s, 'urlBase': urlBase}
    return session


def checkNS(email, s):
    # check if user is external
    userNS = ""
    if "#EXT#@" in email:
        logging.debug('external user email detected')
        userNS = email.split(
            '#EXT#@')[0].replace('.', '-').replace('_', '-').lower()
    else:
        userNS = email.split('@')[0].replace('.', '-').lower()
    # userNS = email.split('@')[0].replace('.', '-').lower()
    url = s['urlBase'] + "/api/web/namespaces/{0}".format(userNS)
    try:
        resp = s['session'].get(url)
        if 200 <= resp.status_code <= 299:
            return sObj('checkNS', 'present', resp.json())
        else:
            return sObj('checkNS', 'absent', resp.json())
    except requests.exceptions.RequestException as e:
        logging.error("Http Error: {0}".format(e))
        return None


def checkUser(email, s):
    # TBD: Find a better way to do this, this is too expensive
    # TBD: Fix this dictionary comprehension
    url = s['urlBase'] + "/api/web/custom/namespaces/system/user_roles"
    try:
        resp = s['session'].get(url)
        resp.raise_for_status()
        resp_dict = resp.json()
        #res = next((user for user in resp_dict['items'] if user['email'] == email), None)
        res = [e for e in resp_dict['items'] if e['email'] == email]
        if res:
            logging.info("User {0} already exists.")
            return sObj('checkUser', 'present', res)
        else:
            return sObj('checkUser', 'absent', None)
    except requests.exceptions.RequestException as e:
        logging.error("Http Error: {0}".format(e))
        return None


def createUserNS(email, s):
    url = s['urlBase'] + "/api/web/namespaces"
    # check if user is external
    userNS = ""
    if "#EXT#@" in email:
        logging.debug('external user email detected')
        userNS = email.split(
            '#EXT#@')[0].replace('.', '-').replace('_', '-').lower()
    else:
        userNS = email.split('@')[0].replace('.', '-').lower()
    nsPayload = {
        'metadata':
        {
            'annotations': {},
            'description': 'automatically generated by tenant admin',
            'disable': False,
            'labels': {},
            'name': userNS,
            'namespace': ''
        },
        'spec': {}
    }
    try:
        resp = s['session'].post(url, json=nsPayload)
        resp.raise_for_status()
        logging.info("Namespace {0} created.".format(userNS))
        return sObj('createUserNS', 'success', resp.json())
    except requests.exceptions.RequestException as e:
        logging.error("Http Error: {0}".format(e))
        return None


def delUserNS(email, s):
    # check if user is external
    userNS = ""
    if "#EXT#@" in email:
        logging.debug('external user email detected')
        userNS = email.split(
            '#EXT#@')[0].replace('.', '-').replace('_', '-').lower()
    else:
        userNS = email.split('@')[0].replace('.', '-').lower()
    # userNS = email.split('@')[0].replace('.', '-').lower()
    url = s['urlBase'] + \
        "/api/web/namespaces/{0}/cascade_delete".format(userNS)
    nsPayload = {
        "name": userNS
    }
    try:
        resp = s['session'].post(url, json=nsPayload)
        resp.raise_for_status()
        logging.info("Namespace {0} deleted.".format(userNS))
        return sObj('delUserNS', 'success', resp.json())
    except requests.exceptions.RequestException as e:
        logging.error("Http Error: {0}".format(e))
        return None


def createUserRoles(email, first_name, last_name, s, createdNS=None):
    url = s['urlBase'] + "/api/web/custom/namespaces/system/user_roles"
    userPayload = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'name': email,
        'idm_type': 'SSO',
        'namespace': 'system',
        'namespace_roles':
            [
                {'namespace': 'system', 'role': 'ves-io-power-developer-role'},
                {'namespace': 'system', 'role': 'f5-demo-infra-write'},
                {'namespace': '*', 'role': 'ves-io-monitor-role'},
                {'namespace': 'default', 'role': 'ves-io-power-developer-role'},
                {'namespace': 'shared', 'role': 'ves-io-power-developer-role'}
            ],
            'type': 'USER'
    }
    if createdNS:
        userPayload['namespace_roles'].append(
            {'namespace': createdNS, 'role': 'ves-io-admin-role'})
    try:
        resp = s['session'].post(url, json=userPayload)
        resp.raise_for_status()
        logging.info("User {0} created with appropriate roles.".format(email))
        return sObj('createUserRoles', 'success', resp.json())
    except requests.exceptions.RequestException as e:
        logging.error("Http Error: {0}".format(e))
        return None


def delUser(email, s):
    url = s['urlBase'] + "/api/web/custom/namespaces/system/users/cascade_delete"
    userPayload = {
        "email": email,
        "namespace": "system"
    }
    try:
        resp = s['session'].post(url, json=userPayload)
        resp.raise_for_status()
        logging.info("User {0} deleted.".format(email))
        return sObj('delUser', 'success', resp.json())
    except requests.exceptions.RequestException as e:
        logging.error("Http Error: {0}".format(e))
        return None


def cliAdd(token, tenant, email, first_name, last_name, createNS, oRide):
    steps = []
    createdNS = None
    s = createVoltSession(token, tenant)

    if oRide:
        if createNS:
            step = checkNS(email, s)
            steps.append(step)
            if step['status'] == 'present':  # NS exists
                step = delUserNS(email, s)
                steps.append(step)
            step = createUserNS(email, s)
            createdNS = step['resp']['metadata']['name']
            steps.append(step)
        #step = delUser(email, s)
        # steps.append(step)
        step = createUserRoles(email, first_name, last_name, s, createdNS)
        steps.append(step)
        return {'status': 'success', 'steps': steps}
    else:
        if createNS:
            step = checkNS(email, s)
            steps.append(step)
            if step['status'] == 'present':  # NS exists
                return {'status': 'failure', 'reason': 'NS already exists', 'steps': steps}
            else:
                step = createUserNS(email, s)
                createdNS = step['resp']['metadata']['name']
                steps.append(step)

        step = checkUser(email, s)
        steps.append(step)
        if step['status'] == 'present':  # User is present
            return {'status': 'failure', 'reason': 'User already exists',
                    'steps': steps}
        else:
            step = createUserRoles(email, first_name, last_name, s, createdNS)
            steps.append(step)
            return {'status': 'success', 'steps': steps}


def cliRemove(token, tenant, email):
    steps = []
    s = createVoltSession(token, tenant)
    step = delUserNS(email, s)
    steps.append(step)
    step = delUser(email, s)
    steps.append(step)
    return {'status': 'success', 'steps': steps}
