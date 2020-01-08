from wrapper_warcraftlogs import getReportsGuild

print([key for key in getReportsGuild('Hive Mind')[0]])
print(getReportsGuild('Hive Mind')[0]['start'])