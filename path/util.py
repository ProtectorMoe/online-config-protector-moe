import hashlib
import json
from rest_framework.response import Response
from rest_framework import status


def try_catch(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("发生错误:" + str(e))
            return Response({'errmsg': "内部错误" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper


def get_md5(text: str):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def get_salt(uid: int, username: str):
    return get_md5(f"{uid}{username},./,/./..,")


def pc_to_pe(data: str, desc: str):
    j = json.loads(data)
    global_map = j['map']
    global_name = j['name']
    global_point = j['point']
    global_format = j['format']
    global_skip = j['skip']
    global_hmChange = j['hmChange']
    global_qmChange = j['qmChange']
    global_qtChange = j['qtChange']
    global_resource = j['resource']
    global_nightFight = j['nightFight']
    global_detail = j['allDetail']

    pe_data = {
        'title': global_name,
        'map': global_map,
        'desc': desc,
        'skipMax': j['skipDeal'],
        'detail': {}
    }

    def get_in_detail(point, local_key, global_default):
        if point not in global_detail:
            return global_default
        if local_key not in global_detail[point]:
            return global_default
        return global_detail[point][local_key]

    for flag in global_point:
        is_format = get_in_detail(flag, 'isFormat', False)

        pe_data['detail'][flag] = {
            'format': get_in_detail(flag, 'format', global_format) if is_format else global_format,
            'night': get_in_detail(flag, 'nightFight', global_nightFight),
            'round_about': global_skip,
            'buff': get_in_detail(flag, 'buff', '-1'),
            'sl': global_resource,
            'detail': []
        }

        if get_in_detail(flag, 'foe1Switch', False):
            foe1Compare = int(get_in_detail(flag, 'foe1Compare', 1))
            foe1Num = int(get_in_detail(flag, 'foe1Num', 0))

            pe_data['detail'][flag]['detail'].append({
                'enemy': int(get_in_detail(flag, 'foe1Format', '')),
                'num': int(foe1Num if foe1Compare == 0 else foe1Num + 6),
                'deal': int(get_in_detail(flag, 'foe1Deal', ''))
            })

        if get_in_detail(flag, 'foe2Switch', False):
            foe2Compare = int(get_in_detail(flag, 'foe2Compare', 1))
            foe2Num = get_in_detail(flag, 'foe2Num', 0)

            pe_data['detail'][flag]['detail'].append({
                'enemy': int(get_in_detail(flag, 'foe2Format', '')),
                'num': int(foe2Num if foe2Compare == 0 else foe2Num + 6),
                'deal': int(get_in_detail(flag, 'foe2Deal', ''))
            })

        if global_hmChange:
            pe_data['detail'][flag]['detail'].append({
                'enemy': 1,
                'num': 1,
                'deal': 3
            })

        if global_qmChange:
            pe_data['detail'][flag]['detail'].append({
                'enemy': 2,
                'num': 1,
                'deal': 3
            })

        if global_qtChange:
            pe_data['detail'][flag]['detail'].append({
                'enemy': 14,
                'num': 1,
                'deal': 5
            })
    return pe_data


def pe_to_pc(data: str, name: str):
    j = json.loads(data)
    pc_data = {
        'map': j['map'],
        'name': name,
        'point': ''.join(j['detail'].keys()),
        'endPoint': '-',
        'format': 1,
        'skip': True,
        'skipDeal': j['skipMax'],
        'spyFail': 0,
        'hmChange': False,
        'qmChange': False,
        'qtChange': False,
        'reward': False,
        'nightFight': False,
        'resource': False,
        'allDetail': {}
    }

    pe_detail = j['detail']
    for flag, data in pe_detail.items():
        pc_data['allDetail'][flag] = {}
        pc_data['allDetail'][flag] = {
            'foe1Switch': False,
            'foe2Switch': False,
            'foe1Compare': 0,
            'foe2Compare': 0,
            'foe1Format': 0,
            'foe2Format': 0,
            'foe1Num': '1',
            'foe2Num': '1',
            'foe1Deal': 0,
            'foe2Deal': 0,
            'spy': False,
            'spyDeal': 0,
            'nightFight': data['night'],
            'isFormat': True,
            'format': int(data['format']),
        }
        index = 1
        for enemy in data['detail']:
            if index == 1:
                pc_data['allDetail'][flag]['foe1Switch'] = True,
                pc_data['allDetail'][flag]['foe1Format'] = enemy['enemy'],
                pc_data['allDetail'][flag]['foe1Compare'] = 0 if enemy['num'] <= 6 else 1,
                pc_data['allDetail'][flag]['foe1Num'] = str(enemy['num'] if enemy['num'] <= 6 else enemy['num'] - 6),
                pc_data['allDetail'][flag]['foe1Deal'] = enemy['deal']
            if index == 2:
                pc_data['allDetail'][flag]['foe2Switch'] = True,
                pc_data['allDetail'][flag]['foe2Format'] = enemy['enemy'],
                pc_data['allDetail'][flag]['foe2Compare'] = 0 if enemy['num'] <= 6 else 1,
                pc_data['allDetail'][flag]['foe2Num'] = str(enemy['num'] if enemy['num'] <= 6 else enemy['num'] - 6),
                pc_data['allDetail'][flag]['foe2Deal'] = enemy['deal']
    return pc_data


def parse_path(path: str, name: str, desc: str):
    j = json.loads(path.replace('\\', ""))
    if 'point' in j:
        return {
            'pc': path.replace('\\', ""),
            'pe': json.dumps(pc_to_pe(path.replace('\\', ""), desc))
        }
    return {
        'pc': json.dumps(pe_to_pc(path.replace('\\', ""), name)),
        'pe': path.replace('\\', "")
    }
