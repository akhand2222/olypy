'''
Read and write Olympia state files.
'''

import os
import sys
from contextlib import redirect_stdout

from oid import to_oid
from formatters import print_one_thing, read_oly_file


def fixup_ms(data):
    '''
    For whatever reason, the value in IM/ms needs to have a trailing space
    '''
    for box in data:
        if 'IM' in data[box]:
            if 'ms' in data[box]['IM']:
                value = data[box]['IM']['ms']
                value[0] = value[0].strip() + ' '
                data[box]['IM']['ms'] = value


def write_oly_file(data, kind=False, verbose=False):
    '''
    The main function that drives outputting a file
    '''

    fixup_ms(data)

    order = sorted([int(box) for box in data.keys()])

    count = 0
    for box in order:
        box = str(box)
        if kind:
            if ' '+kind+' ' not in data[box].get('firstline', '')[0]:
                continue
        print_one_thing(data[box])
        del data[box]
        count += 1

    if verbose:
        print('wrote', count, verbose, 'boxes.', file=sys.stderr)


def write_player(data, box, verbose=False):
    player_box = box
    boxlist = data[box].get('PL', {}).get('un', {})
    print_one_thing(data[box])
    del data[box]
    count = 0
    for box in boxlist:
        print_one_thing(data[box])
        del data[box]
        count += 1
    if verbose:
        print('wrote', count, 'characters for player', to_oid(int(player_box)), file=sys.stderr)


def read_players(dir, verbose=False):
    '''
    read every fie in dir whose name is an integer
    '''
    ret = {}
    files = os.listdir(dir)
    for name in files:
        if name.isdigit():
            data = read_oly_file(dir + '/' + name, verbose='player ' + name)
            ret.update(data)
    return ret


def write_players(data, dir, verbose=False):
    boxlist = list(data.keys())  # we're deleting as we go
    for box in boxlist:
        if data.get(box) is None:
            continue
        if ' player ' in data[box]['firstline'][0]:
            filename = dir + '/fact/' + box
            with open(filename, 'w') as f:
                with redirect_stdout(f):
                    write_player(data, box, verbose=verbose)


def read_lib(libdir):
    data = read_oly_file(libdir+'/loc', verbose='loc')
    data.update(read_oly_file(libdir+'/item', verbose='item'))
    data.update(read_oly_file(libdir+'/skill', verbose='skill'))
    data.update(read_oly_file(libdir+'/gate', verbose='gate'))
    data.update(read_oly_file(libdir+'/road', verbose='road'))
    data.update(read_oly_file(libdir+'/ship', verbose='ship'))
    data.update(read_oly_file(libdir+'/unform', verbose='unform'))
    data.update(read_oly_file(libdir+'/misc', verbose='misc'))

    data.update(read_players(libdir+'/fact', verbose=True))

    return data


def write_lib(data, libdir):
    with open(libdir+'/loc', 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='loc', verbose='loc')
    with open(libdir+'/item', 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='item', verbose='item')
    with open(libdir+'/skill', 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='skill', verbose='skill')
    with open(libdir+'/gate', 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='gate', verbose='gate')
    with open(libdir+'/road', 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='road', verbose='road')
    with open(libdir+'/ship', 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='ship', verbose='ship')
    with open(libdir+'/unform', 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='unform', verbose='unform')

    write_players(data, libdir, verbose=True)

    with open(libdir+'/misc', 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, verbose='misc')  # catchall
