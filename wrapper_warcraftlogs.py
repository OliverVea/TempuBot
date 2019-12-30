import json
import urllib.request
import numpy as np
from datetime import datetime

keep_in_memory = True # Uses extra memory but less bandwidth.

wcl_api_keys = [] # Tempia's API Key: 2ae1c2a2acd530ab067e93e93d317cd8
wcl_current_api_key = 0
def wclAddKey(key):
    global wcl_api_keys
    wcl_api_keys.append(key)
wclAddKey('2ae1c2a2acd530ab067e93e93d317cd8') # add Tempia's key.

def getAPIKey():
    global wcl_current_api_key
    wcl_current_api_key = (wcl_current_api_key + 1) % len(wcl_api_keys)
    return wcl_api_keys[wcl_current_api_key]

def makeStringIfIsNot(value, test, prefix):
    if (value is not test): return prefix + str(value)
    return ""

# Used to read pages with JSON formatted data.
def queryPage(url):
    print(url)
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()

    mystr = mybytes.decode("utf8")
    fp.close()

    return json.loads(mystr)

wclZones = False
# Gets an array of Zone objects. Each zone corresponds to a raid/dungeon instance in the game and has its own set of encounters.
def getZones(): 
    if (wclZones is not False): return wclZones
    url = 'https://classic.warcraftlogs.com:443/v1/zones?api_key=' + getAPIKey()
    return queryPage(url)
if (keep_in_memory): wclZones = getZones()

wclClasses = False
# Gets an array of Class objects. Each Class corresponds to a class in the game.
def getClasses():
    if (wclClasses is not False): return wclClasses
    url = 'https://classic.warcraftlogs.com:443/v1/classes?api_key=' + getAPIKey()
    return queryPage(url)
if (keep_in_memory): wclClasses = getClasses()

# Gets an object that contains a total count and an array of EncounterRanking objects and a total number of rankings for that encounter. 
# Each EncounterRanking corresponds to a single character or guild/team.
# Example use: getRankingsEncounterId(663,'dps','4','3',0,'zandalar-tribe','EU')
def getRankingsEncounterId(encounterID, queryMetric = 'dps', queryClass = '', querySpec = '', queryBracket = 0, queryServer = 'zandalar-tribe', queryRegion = 'EU', queryFilter = ''):
    queryClass = makeStringIfIsNot(querySpec, '', '&class=')
    querySpec = makeStringIfIsNot(queryClass, '', '&spec=')
    queryFilter = makeStringIfIsNot(queryFilter, '', '&filter=')
    if (len(queryServer) > 0 and len(queryRegion) > 0): 
        queryServer = '&server=' + queryServer
        queryRegion = '&region=' + queryRegion

    url = 'https://classic.warcraftlogs.com:443/v1/rankings/encounter/{}?metric={}{}{}&bracket={}{}{}{}&api_key='.format(encounterID, queryMetric, queryClass, querySpec, queryBracket, queryServer, queryRegion, queryFilter) + getAPIKey()
    return queryPage(url)

# Gets an array of CharacterRanking objects. Each CharacterRanking corresponds to a single rank on a fight for the specified character.
# Example use: getRankingsCharacterName('tempia','zandalar-tribe','EU', queryMetric='hps')
def getRankingsCharacterName(queryCharacter, queryServer = 'zandalar-tribe', queryRegion = 'EU', queryZone = '', queryEncounter = '', queryMetric = 'dps', queryBracket = 0, queryTimeframe = 'historical'):
    if (len(queryZone) > 0): queryZone = '&zone=' + queryZone
    if (len(queryEncounter) > 0): queryEncounter = '&encounter=' + queryEncounter

    url = 'https://classic.warcraftlogs.com:443/v1/rankings/character/{}/{}/{}?{}&{}&metric={}&bracket={}&timeframe={}&api_key='.format(queryCharacter, queryServer, queryRegion, queryZone, queryEncounter, queryMetric, queryBracket, queryTimeframe) + getAPIKey()
    return queryPage(url)

# Obtains all parses for a character in the zone across all specs. Every parse is included and not just rankings.
# Example use: getParses('izomi', queryMetric='hps', queryZone='1001')
def getParses(queryCharacter, queryServer = 'zandalar-tribe', queryRegion = 'EU', queryZone = '', queryEncounter = '', queryMetric = 'dps', queryBracket = 0, queryTimeframe = 'historical'):
    if (len(queryZone) > 0): queryZone = '&zone=' + queryZone
    if (len(queryEncounter) > 0): queryEncounter = '&encounter=' + queryEncounter

    url = 'https://classic.warcraftlogs.com:443/v1/parses/character/{}/{}/{}?{}&{}&metric={}&bracket={}&timeframe={}&api_key='.format(queryCharacter, queryServer, queryRegion, queryZone, queryEncounter, queryMetric, queryBracket, queryTimeframe) + getAPIKey()
    return queryPage(url)

# Gets an array of Report objects. Each Report corresponds to a single calendar report for the specified guild.
# Example use: getReportsGuild('Hive Mind')
def getReportsGuild(queryGuild, queryServer = 'zandalar-tribe', queryRegion = 'EU', queryStart = 0, queryEnd = -1):
    queryEnd = makeStringIfIsNot(queryEnd, -1, "&end=")
    queryGuild = queryGuild.replace(' ', '%20')

    url = 'https://classic.warcraftlogs.com:443/v1/reports/guild/{}/{}/{}?start={}{}&api_key='.format(queryGuild, queryServer, queryRegion, queryStart, queryEnd) + getAPIKey()
    return queryPage(url)

# Gets arrays of fights and the participants in those fights. Each Fight corresponds to a single pull of a boss.
# Example use: for a in getReportFightCode('Z9gyG3DxkVcfvq7z')['fights']: print(a['name'])
def getReportFightCode(queryCode):
    url = 'https://classic.warcraftlogs.com:443/v1/report/fights/{}?api_key='.format(queryCode) + getAPIKey()
    return queryPage(url)

# Gets a set of events based off the view you're asking for. This exactly corresponds to the Events view on the site.
# Example use: 
def getReportEvents(queryView, queryCode, queryStart = 0, queryEnd = -1, queryHostility = 0, querySourceID = -1, querySourceInstance = -1, querySourceClass = -1, queryTargetID = -1, queryTargetInstance = -1, queryTargetClass = -1, queryAbilityID = -1, queryDeath = -1, queryOptions = '', queryCutoff = -1, queryEncounter = -1, queryWipes = -1):
    queryEnd = makeStringIfIsNot(queryEnd, -1, "&end=")
    querySourceID = makeStringIfIsNot(querySourceID, -1, "&sourceid=")
    querySourceInstance = makeStringIfIsNot(querySourceInstance, -1, "&sourceinstance=")
    querySourceClass = makeStringIfIsNot(querySourceClass, -1, "&sourceclass=")
    queryTargetID = makeStringIfIsNot(queryTargetID, -1, "&targetid=")
    queryTargetInstance = makeStringIfIsNot(queryTargetInstance, -1, "&targetinstance=")
    queryTargetClass = makeStringIfIsNot(queryTargetClass, -1, "&targetclass=")
    queryAbilityID = makeStringIfIsNot(queryAbilityID, -1, "&abilityid=")
    queryDeath = makeStringIfIsNot(queryDeath, -1, "&death=")
    queryOptions = makeStringIfIsNot(queryOptions, '', "&options=")
    queryCutoff = makeStringIfIsNot(queryCutoff, -1, "&cutoff=")
    queryEncounter = makeStringIfIsNot(queryEncounter, -1, "&encounter=")
    queryWipes = makeStringIfIsNot(queryWipes, -1, "&wipes=")

    url = 'https://classic.warcraftlogs.com:443/v1/report/events/{}/{}?start={}{}&hostility={}{}{}{}{}{}{}{}{}{}{}{}{}&api_key='.format(queryView, queryCode, queryStart, queryEnd, queryHostility, querySourceID, querySourceInstance, querySourceClass, queryTargetID, queryTargetInstance, queryTargetClass, queryAbilityID, queryDeath, queryOptions, queryCutoff, queryEncounter, queryWipes) + getAPIKey()
    return queryPage(url)

# Gets a table of entries, either by actor or ability, of damage, healing and cast totals for each entry. 
# This API exactly follows what is returned for the Tables panes on the site. 
# It can and will change as the needs of those panes do, and as such should never be considered a frozen API. Use at your own risk.
# Example use: getReportTables('damage-done', 'Z9gyG3DxkVcfvq7z')
def getReportTables(queryView, queryCode, queryStart = 0, queryEnd = -1, queryBy = 'source', querySourceID = -1, querySourceInstance = -1, querySourceClass = -1, queryTargetID = -1, queryTargetInstance = -1, queryTargetClass = -1, queryAbilityID = -1, queryOptions = '', queryCutoff = -1, queryEncounter = -1, queryWipes = -1):
    queryEnd = makeStringIfIsNot(queryEnd, -1, "&end=")
    querySourceID = makeStringIfIsNot(querySourceID, -1, "&sourceid=")
    querySourceInstance = makeStringIfIsNot(querySourceInstance, -1, "&sourceinstance=")
    querySourceClass = makeStringIfIsNot(querySourceClass, -1, "&sourceclass=")
    queryTargetID = makeStringIfIsNot(queryTargetID, -1, "&targetid=")
    queryTargetInstance = makeStringIfIsNot(queryTargetInstance, -1, "&targetinstance=")
    queryTargetClass = makeStringIfIsNot(queryTargetClass, -1, "&targetclass=")
    queryAbilityID = makeStringIfIsNot(queryAbilityID, -1, "&abilityid=")
    queryOptions = makeStringIfIsNot(queryOptions, '', "&options=")
    queryCutoff = makeStringIfIsNot(queryCutoff, -1, "&cutoff=")
    queryEncounter = makeStringIfIsNot(queryEncounter, -1, "&encounter=")
    queryWipes = makeStringIfIsNot(queryWipes, -1, "&wipes=")

    url = 'https://classic.warcraftlogs.com:443/v1/report/tables/{}/{}?start={}{}&by={}{}{}{}{}{}{}{}{}{}{}{}&api_key='.format(queryView, queryCode, queryStart, queryEnd, queryBy, querySourceID, querySourceInstance, querySourceClass, queryTargetID, queryTargetInstance, queryTargetClass, queryAbilityID, queryOptions, queryCutoff, queryEncounter, queryWipes) + getAPIKey()
    return queryPage(url)
 
