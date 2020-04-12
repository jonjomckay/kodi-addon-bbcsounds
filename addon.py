import datetime
import json
import sys
import urllib
import urlparse
from collections import OrderedDict
from operator import itemgetter
from time import mktime

import dateutil.parser
import feedparser
import requests
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from bs4 import BeautifulSoup

stations = {
    'p00fzl68': 'BBC Asian Network',
    'p00fzl78': 'BBC Coventry & Warwickshire',
    'p00fzl7f': 'BBC Essex',
    'p00fzl7q': 'BBC Hereford & Worcester',
    'p00fzl82': 'BBC Newcastle',
    'p00fzl86': 'BBC Radio 1',
    'p00fzl64': 'BBC Radio 1Xtra',
    'p00fzl8v': 'BBC Radio 2',
    'p00fzl8t': 'BBC Radio 3',
    'p00fzl7j': 'BBC Radio 4 FM',
    'p00fzl7k': 'BBC Radio 4 LW',
    'p00fzl7l': 'BBC Radio 4 Extra',
    'p00fzl7g': 'BBC Radio 5 live',
    'p00fzl7h': 'BBC Radio 5 live sports extra',
    'p00fzl65': 'BBC Radio 6 Music',
    'p00fzl74': 'BBC Radio Berkshire',
    'p00fzl75': 'BBC Radio Bristol',
    'p00fzl76': 'BBC Radio Cambridgeshire',
    'p00fzl77': 'BBC Radio Cornwall',
    'p00fzl79': 'BBC Radio Cumbria',
    'p00fzl7b': 'BBC Radio Cymru',
    'p00fzl7c': 'BBC Radio Derby',
    'p00fzl7d': 'BBC Radio Devon',
    'p00fzl7m': 'BBC Radio Foyle',
    'p00fzl7n': 'BBC Radio Gloucestershire',
    'p00fzl7p': 'BBC Radio Guernsey',
    'p00fzl7r': 'BBC Radio Humberside',
    'p00fzl7s': 'BBC Radio Jersey',
    'p00fzl7t': 'BBC Radio Kent',
    'p00fzl7v': 'BBC Radio Lancashire',
    'p00fzl7w': 'BBC Radio Leeds',
    'p00fzl7x': 'BBC Radio Leicester',
    'p00fzl7y': 'BBC Radio Lincolnshire',
    'p00fzl6f': 'BBC Radio London',
    'p00fzl7z': 'BBC Radio Manchester',
    'p00fzl80': 'BBC Radio Merseyside',
    'p00fzl81': 'BBC Radio Nan Gaidheal',
    'p00fzl83': 'BBC Radio Norfolk',
    'p00fzl84': 'BBC Radio Northampton',
    'p00fzl85': 'BBC Radio Nottingham',
    'p00fzl8c': 'BBC Radio Oxford',
    'p00fzl8d': 'BBC Radio Scotland (FM)',
    'p00fzl8g': 'BBC Radio Scotland (MW)',
    'p00fzl8b': 'BBC Radio Scotland (Orkney)',
    'p00fzl8j': 'BBC Radio Scotland (Shetland)',
    'p00fzl8h': 'BBC Radio Sheffield',
    'p00fzl8k': 'BBC Radio Shropshire',
    'p00fzl8l': 'BBC Radio Solent',
    'p00fzl8n': 'BBC Radio Stoke',
    'p00fzl8p': 'BBC Radio Suffolk',
    'p00fzl8w': 'BBC Radio Ulster',
    'p00fzl8y': 'BBC Radio Wales (FM)',
    'p00fzl8x': 'BBC Radio Wales (LW)',
    'p00fzl90': 'BBC Radio York',
    'p00fzl8m': 'BBC Somerset',
    'p00fzl8q': 'BBC Surrey',
    'p00fzl8r': 'BBC Sussex',
    'p00fzl93': 'BBC Tees',
    'p00fzl96': 'BBC Three Counties Radio',
    'p00fzl8z': 'BBC Wiltshire',
    'p00fzl9f': 'BBC WM 95.6',
    'p02zbmb3': 'BBC World Service',
    'p02jf21y': 'CBeebies Radio',
}

stations_ordered = OrderedDict(sorted(stations.items(), key=itemgetter(1)))


def get_page(url):
    # download the source HTML for the page using requests
    # and parse the page using BeautifulSoup
    return BeautifulSoup(requests.get(url).text, 'html.parser')


__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')

# Parse the stuff passed into the addon
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = dict(urlparse.parse_qsl(sys.argv[2][1:]))

xbmcplugin.setContent(addon_handle, 'audio')


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def mode_default():
    categories = {
        'podcasts': 'Podcasts',
        'stations': 'Stations'
    }

    for mode, category in categories.items():
        url = build_url({'mode': mode})
        li = xbmcgui.ListItem(category)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def mode_episode(pid):
    programme = requests.get('https://www.bbc.co.uk/programmes/' + pid + '.json')
    programme_json = programme.json()["programme"]

    url = None

    for version in programme_json["versions"]:
        playlist = requests.get(
            'https://open.live.bbc.co.uk/mediaselector/6/select/version/2.0/mediaset/iptv-all/vpid/' + version["pid"] + '/format/json')
        playlist_json = playlist.json()

        if "media" not in playlist_json:
            continue

        url = playlist_json["media"][0]["connection"][1]["href"]

        play_item = xbmcgui.ListItem(path=url)
        play_item.setArt({
            'thumb': 'https://ichef.bbci.co.uk/images/ic/480xn/' + programme_json["image"]["pid"] + '.jpg',
            'icon': 'https://ichef.bbci.co.uk/images/ic/480xn/' + programme_json["image"]["pid"] + '.jpg'
        })
        play_item.setInfo('music', {
            'title': programme_json["display_title"]["title"],
            'artist': programme_json["display_title"]["subtitle"],
            'comment': programme_json["short_synopsis"]
        })

        xbmc.Player().play(url, play_item)

    if url is None:
        xbmcgui.Dialog().notification(__addonname__, "Episode not available to stream", icon=xbmcgui.NOTIFICATION_ERROR)


def mode_podcasts():
    podcasts = requests.get('https://www.bbc.co.uk/podcasts.json')
    podcasts_json = podcasts.json()["podcasts"]

    # Sort the podcasts by title
    podcasts_ordered = sorted(podcasts_json, key=lambda x: x["title"])

    for podcast in podcasts_ordered:
        url = build_url({'mode': 'podcast', 'pid': podcast["shortTitle"]})
        li = xbmcgui.ListItem(podcast["title"])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def mode_podcast(pid):
    podcast = feedparser.parse('https://podcasts.files.bbci.co.uk/' + pid + '.rss')

    for entry in podcast.entries:
        entry_pid = entry.id.split(':')
        entry_date = datetime.datetime.fromtimestamp(mktime(entry.published_parsed)).strftime('%Y-%m-%d, %H:%M')
        entry_title = entry_date + ": " + entry.title

        url = build_url({'mode': 'episode', 'pid': entry_pid[3]})
        li = xbmcgui.ListItem(entry_title)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)


def mode_stations():
    for pid, station in stations_ordered.items():
        url = build_url({'mode': 'station', 'pid': pid})
        li = xbmcgui.ListItem(station)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def mode_station(pid):
    base = datetime.datetime.today()

    # Create a range of the last 30 days
    for delta in range(30):
        date = base - datetime.timedelta(days=delta)

        year = '%04d' % date.year
        month = '%02d' % date.month
        day = '%02d' % date.day

        url = build_url({'mode': 'station_date', 'pid': pid, 'year': year, 'month': month, 'day': day})
        list_item = xbmcgui.ListItem(date.strftime('%Y-%m-%d'))
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def mode_station_date(pid, year, month, day):
    # Load the schedules for the station
    schedule = get_page('https://www.bbc.co.uk/schedules/' + pid + '/' + year + '/' + month + '/' + day)

    result = None

    for tag in schedule.find_all('script', type='application/ld+json'):
        if 'RadioEpisode' in tag.contents[0]:
            result = json.loads(tag.contents[0])

    if result is None:
        # xbmc.log('schedule: ' + result['@context'], level=xbmc.LOGERROR)

        raise RuntimeError("TODO: Couldn't find the episode stuff in the HTML")

    for episode in result["@graph"]:
        date = dateutil.parser.parse(episode["publication"]["startDate"])

        time = date.strftime('%Y-%m-%d, %H:%M')

        if "partOfSeries" in episode:
            title = time + ": " + episode["partOfSeries"]["name"] + " - " + episode["name"]
        else:
            title = time + ": " + episode["name"]

        url = build_url({'mode': 'episode', 'pid': episode["identifier"]})
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item)

    xbmcplugin.endOfDirectory(addon_handle)


mode = args.get('mode', None)

if mode is None:
    mode_default()
elif mode == 'episode':
    mode_episode(args['pid'])
elif mode == 'podcasts':
    mode_podcasts()
elif mode == 'podcast':
    mode_podcast(args['pid'])
elif mode == 'stations':
    mode_stations()
elif mode == 'station':
    mode_station(args['pid'])
elif mode == 'station_date':
    mode_station_date(args['pid'], args['year'], args['month'], args['day'])
