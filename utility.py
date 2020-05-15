from math import floor

async def get_users(client, user_string=None, user_id=None, user_mention=None, guild=None, as_list=False):
    assert any([field != None for field in [user_string, user_id, user_mention]]), '\'user_name\', \'user_id\' or \'user_mention\' must be in query.'

    members = []
    if guild is None:
        for guild in client.guilds:
            members += guild.members
    else:
        members = guild.members

    if user_id != None: # 150318701323878401
        query = lambda user: user.id == user_id
    elif user_mention != None: # <@!150318701323878401>
        query = lambda user: user.id == int(user_mention[3:-1]) 
    elif user_string != None: # Tempia#0934
        query = lambda user: str(user) == user_string

    memberlist = [member for member in members if query(member)]
    return memberlist

def standardize_unit(unit):
    unit_dict = {
        'ns': ['ns', 'n', 'nanosecond', 'nanoseconds'], 
        'ms': ['ms', 'millisecond', 'milliseconds'], 
        's' : ['s', 'second', 'seconds'], 
        'm' : ['m', 'min', 'mins', 'minute', 'minutes'],
        'h' : ['h', 'hr', 'hrs', 'hour', 'hours'],
        'd' : ['d', 'day', 'days'],
        'M' : ['M', 'month', 'months'],
        'y' : ['y', 'year', 'years']}

    for key in unit_dict:
        if unit in unit_dict[key]:
            return key

def from_seconds(value, unit, floor_result=False):
    unit = standardize_unit(unit)
    if unit == None:
        return

    conversion = {'ns': 1e-6, 'ms': 1e-3, 's': 1, 'm': 60, 'h': 60**2, 'd': 24 * 60**2, 'M': 30 * 24 * 60**2, 'y': 365 * 60**2}

    value /= conversion[unit]

    if floor_result:
        value = floor(value)

    return value

def to_seconds(value, unit, floor_result=False):
    unit = standardize_unit(unit)
    if unit == None:
        return

    conversion = {'ns': 1e-6, 'ms': 1e-3, 's': 1, 'm': 60, 'h': 60**2, 'd': 24 * 60**2, 'M': 30 * 24 * 60**2, 'y': 365 * 60**2}

    value *= conversion[unit]

    if floor_result:
        value = floor(value)

    return value
