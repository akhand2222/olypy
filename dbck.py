'''
Database checker, similar to the one in the C code (check.c)
'''
import sys

from oid import to_oid


def check_firstline(data):
    '''Make sure everything in data has a firstline'''
    problem = 0
    for k, v in data.items():
        if 'firstline' not in v:
            print('Thing {} has no firstline'.format(k))
            problem += 1
    return problem


where_things = set(('loc', 'ship', 'char'))


def check_where_here(data):
    '''Make sure that every box that's where is here, and here is where.
    Does not check anything that is not where.'''
    problem = 0
    for k, v in data.items():
        if 'firstline' in v and ' loc region' not in v['firstline'][0]:
            _, kind, _ = v['firstline'][0].split(' ', maxsplit=2)
            if kind in where_things:
                try:
                    where = data[k]['LI']['wh'][0]
                except (KeyError, IndexError):
                    print('Thing {} is not anywhere'.format(k), file=sys.stderr)
                    problem += 1
                    continue
                try:
                    hl = data[where]['LI']['hl']
                    hl.index(k)
                except (KeyError, ValueError):
                    print('Thing {} is not in here list of thing {}'.format(k, where), file=sys.stderr)
                    problem += 1
                    continue

    for k, v in data.items():
        if 'LI' in v:
            if 'hl' in v['LI']:
                hl = v['LI']['hl']
                for unit in hl:
                    try:
                        where = data[unit]['LI']['wh'][0]
                        if where != k:
                            raise ValueError
                    except (KeyError, ValueError, IndexError):
                        print('Unit {} is in here list of unit {}, but is not there'.format(unit, k), file=sys.stderr)
                        problem += 1
                        continue

    return problem


def check_faction_units(data):
    "If a box is in a faction, make sure it's on the faction's unit list and vice versa."
    problem = 0
    for i in data:
        if 'CH' in data[i]:
            if 'lo' in data[i]['CH']:
                fact = data[i]['CH']['lo'][0]
                try:
                    un = data[fact]['PL']['un']
                    un.index(i)
                except (KeyError, ValueError):
                    print('Unit {} is in faction {} but not vice versa'.format(i, fact), file=sys.stderr)
                    problem += 1
                    continue

    for i in data:
        if ' player ' in data[i]['firstline'][0] and 'un' in data[i]['PL']:
            for unit in data[i]['PL']['un']:
                try:
                    lo = data[unit]['CH']['lo'][0]
                    if lo != i:
                        raise ValueError
                        print('lo {} i {}'.format(lo, i), file=sys.stderr)
                except (KeyError, ValueError):
                    print('Unit {} is not in faction {}'.format(unit, i), file=sys.stderr)
                    problem += 1
                    continue

    return problem


def sweep_independent_units(data):
    '''Move any unit not in a faction to being unsworn and owned by faction 100 (independent player)'''
    return 0


def check_unique_items(data):
    "Make sure unique items exist on exactly one inventory list, somewhere."
    problem = 0
    all_unique_items = {}
    for i in data:
        if int(i) > 399 and ' item ' in data[i]['firstline'][0]:
            if ' item tradegood' in data[i]['firstline'][0]:
                continue
            all_unique_items[i] = 1
            try:
                un = None
                un = data[i]['IT']['un'][0]
                il = data[un]['il']
                if not isinstance(il, list):
                    print('Whoops. id', i, 'il is', il)
                il.index(i)  # this might have false positive and match a qty XXX
            except (KeyError, ValueError):
                print('Unique item {} is not in inventory of unit {}'.format(i, un), file=sys.stderr)
                problem += 1
                continue

    all_inventory = {}
    for i in data:
        if 'il' in data[i]:
            il = data[i]['il'].copy()
            while len(il) > 0:
                item = il.pop(0)
                qty = int(il.pop(0))
                all_inventory[item] = all_inventory.get(item, 0) + qty

    for i in all_unique_items:
        if i not in all_inventory or all_inventory[i] != 1:
            print('Unique item {} does not have exactly one instance'.format(i), file=sys.stderr)
            problem += 1
            continue

    return problem


def check_moving(data):
    '''
    Make sure moving stack leaders have a running command cs=2
    If I'm a moving non-stack-leader make sure my mo == stack leader mo
    '''
    return 0


def check_prisoners(data):
    "Make sure prisoners are stacked under another character"
    problem = 0
    for i in data:
        if ' char ' in data[i]['firstline'][0]:
            if 'CH' in data[i]:
                if 'pr' in data[i]['CH']:
                    where = data[i]['LI']['wh'][0]
                    if ' char ' not in data[where]['firstline'][0]:
                        print('Prisoner {} is not stacked under a character.'.format(to_oid(i)))
                        problem += 1
    return problem


def check_db(data):
    problems = 0
    problems += check_firstline(data)
    problems += check_where_here(data)
    problems += check_faction_units(data)
    problems += sweep_independent_units(data)
    problems += check_unique_items(data)
    problems += check_moving(data)
    problems += check_prisoners(data)

    return problems