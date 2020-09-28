import datetime
import json
import os
import sys
import urllib
import urlparse
from collections import OrderedDict
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
    'p00fzl68': {'name': 'BBC Asian Network', 'image': 'bbc_asian_network_colour'},
    'p00fzl78': {'name': 'BBC Coventry & Warwickshire', 'image': 'bbc_radio_coventry_warwickshire_colour'},
    'p00fzl7f': {'name': 'BBC Essex', 'image': 'bbc_radio_essex_colour'},
    'p00fzl7q': {'name': 'BBC Hereford & Worcester', 'image': 'bbc_radio_hereford_worcester_colour'},
    'p00fzl82': {'name': 'BBC Newcastle', 'image': 'bbc_radio_newcastle_colour'},
    'p00fzl86': {'name': 'BBC Radio 1', 'image': 'bbc_radio_one_colour'},
    'p00fzl64': {'name': 'BBC Radio 1Xtra', 'image': 'bbc_1xtra_colour'},
    'p00fzl8v': {'name': 'BBC Radio 2', 'image': 'bbc_radio_two_colour'},
    'p00fzl8t': {'name': 'BBC Radio 3', 'image': 'bbc_radio_three_colour'},
    'p00fzl7j': {'name': 'BBC Radio 4 FM', 'image': 'bbc_radio_fourfm_colour'},
    'p00fzl7k': {'name': 'BBC Radio 4 LW', 'image': 'bbc_radio_four_colour'},
    'p00fzl7l': {'name': 'BBC Radio 4 Extra', 'image': 'bbc_radio_four_extra_colour'},
    'p00fzl7g': {'name': 'BBC Radio 5 live', 'image': 'bbc_radio_five_live_colour'},
    'p00fzl7h': {'name': 'BBC Radio 5 live sports extra', 'image': 'bbc_radio_five_live_sports_extra_colour'},
    'p00fzl65': {'name': 'BBC Radio 6 Music', 'image': 'bbc_6music_colour'},
    'p00fzl74': {'name': 'BBC Radio Berkshire', 'image': 'bbc_radio_berkshire_colour'},
    'p00fzl75': {'name': 'BBC Radio Bristol', 'image': 'bbc_radio_bristol_colour'},
    'p00fzl76': {'name': 'BBC Radio Cambridgeshire', 'image': 'bbc_radio_cambridge_colour'},
    'p00fzl77': {'name': 'BBC Radio Cornwall', 'image': 'bbc_radio_cornwall_colour'},
    'p00fzl79': {'name': 'BBC Radio Cumbria', 'image': 'bbc_radio_cumbria_colour'},
    'p00fzl7b': {'name': 'BBC Radio Cymru', 'image': 'bbc_radio_cymru_colour'},
    'p00fzl7c': {'name': 'BBC Radio Derby', 'image': 'bbc_radio_derby_colour'},
    'p00fzl7d': {'name': 'BBC Radio Devon', 'image': 'bbc_radio_devon_colour'},
    'p00fzl7m': {'name': 'BBC Radio Foyle', 'image': 'bbc_radio_foyle_colour'},
    'p00fzl7n': {'name': 'BBC Radio Gloucestershire', 'image': 'bbc_radio_gloucestershire_colour'},
    'p00fzl7p': {'name': 'BBC Radio Guernsey', 'image': 'bbc_radio_guernsey_colour'},
    'p00fzl7r': {'name': 'BBC Radio Humberside', 'image': 'bbc_radio_humberside_colour'},
    'p00fzl7s': {'name': 'BBC Radio Jersey', 'image': 'bbc_radio_jersey_colour'},
    'p00fzl7t': {'name': 'BBC Radio Kent', 'image': 'bbc_radio_kent_colour'},
    'p00fzl7v': {'name': 'BBC Radio Lancashire', 'image': 'bbc_radio_lancashire_colour'},
    'p00fzl7w': {'name': 'BBC Radio Leeds', 'image': 'bbc_radio_leeds_colour'},
    'p00fzl7x': {'name': 'BBC Radio Leicester', 'image': 'bbc_radio_leicester_colour'},
    'p00fzl7y': {'name': 'BBC Radio Lincolnshire', 'image': 'bbc_radio_lincolnshire_colour'},
    'p00fzl6f': {'name': 'BBC Radio London', 'image': 'bbc_london_colour'},
    'p00fzl7z': {'name': 'BBC Radio Manchester', 'image': 'bbc_radio_manchester_colour'},
    'p00fzl80': {'name': 'BBC Radio Merseyside', 'image': 'bbc_radio_merseyside_colour'},
    'p00fzl81': {'name': 'BBC Radio Nan Gaidheal', 'image': 'bbc_radio_nan_gaidheal_colour'},
    'p00fzl83': {'name': 'BBC Radio Norfolk', 'image': 'bbc_radio_norfolk_colour'},
    'p00fzl84': {'name': 'BBC Radio Northampton', 'image': 'bbc_radio_northampton_colour'},
    'p00fzl85': {'name': 'BBC Radio Nottingham', 'image': 'bbc_radio_nottingham_colour'},
    'p00fzl8c': {'name': 'BBC Radio Oxford', 'image': 'bbc_radio_oxford_colour'},
    'p00fzl8d': {'name': 'BBC Radio Scotland (FM)', 'image': 'bbc_radio_scotland_fm_colour'},
    'p00fzl8g': {'name': 'BBC Radio Scotland (MW)', 'image': 'bbc_radio_scotland_colour'},
    'p00fzl8b': {'name': 'BBC Radio Scotland (Orkney)', 'image': 'bbc_radio_scotland_colour'},
    'p00fzl8j': {'name': 'BBC Radio Scotland (Shetland)', 'image': 'bbc_radio_scotland_colour'},
    'p00fzl8h': {'name': 'BBC Radio Sheffield', 'image': 'bbc_radio_sheffield_colour'},
    'p00fzl8k': {'name': 'BBC Radio Shropshire', 'image': 'bbc_radio_shropshire_colour'},
    'p00fzl8l': {'name': 'BBC Radio Solent', 'image': 'bbc_radio_solent_colour'},
    'p00fzl8n': {'name': 'BBC Radio Stoke', 'image': 'bbc_radio_stoke_colour'},
    'p00fzl8p': {'name': 'BBC Radio Suffolk', 'image': 'bbc_radio_suffolk_colour'},
    'p00fzl8w': {'name': 'BBC Radio Ulster', 'image': 'bbc_radio_ulster_colour'},
    'p00fzl8y': {'name': 'BBC Radio Wales (FM)', 'image': 'bbc_radio_wales_fm_colour'},
    'p00fzl8x': {'name': 'BBC Radio Wales (LW)', 'image': 'bbc_radio_wales_colour'},
    'p00fzl90': {'name': 'BBC Radio York', 'image': 'bbc_radio_york_colour'},
    'p00fzl8m': {'name': 'BBC Somerset', 'image': 'bbc_radio_somerset_sound_colour'},
    'p00fzl8q': {'name': 'BBC Surrey', 'image': 'bbc_radio_surrey_colour'},
    'p00fzl8r': {'name': 'BBC Sussex', 'image': 'bbc_radio_sussex_colour'},
    'p00fzl93': {'name': 'BBC Tees', 'image': 'bbc_tees_colour'},
    'p00fzl96': {'name': 'BBC Three Counties Radio', 'image': 'bbc_three_counties_radio_colour'},
    'p00fzl8z': {'name': 'BBC Wiltshire', 'image': 'bbc_radio_wiltshire_colour'},
    'p00fzl9f': {'name': 'BBC WM 95.6', 'image': 'bbc_wm_colour'},
    'p02zbmb3': {'name': 'BBC World Service', 'image': 'bbc_world_service_colour'},
    'p02jf21y': {'name': 'CBeebies Radio', 'image': 'cbeebies_radio_colour'},
}

stations_ordered = OrderedDict(sorted(stations.items(), key=lambda x: x[1]['name']))


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

    picked_url = None

    for version in programme_json["versions"]:
        playlist = requests.get(
            'https://open.live.bbc.co.uk/mediaselector/6/select/version/2.0/mediaset/iptv-all/vpid/' + version["pid"] + '/format/json')
        playlist_json = playlist.json()

        if "media" not in playlist_json:
            # TODO
            continue

        # Filter by only audio items, and order with the highest bitrate first
        audio_items = [item for item in playlist_json['media'] if item['kind'] == 'audio']
        audio_items.sort(key=lambda x: x['bitrate'], reverse=True)

        xbmc.log('Found {0} audio items for the programme version {1}'.format(len(audio_items), version['pid']), level=xbmc.LOGNOTICE)

        # Pick the first stream available for the highest bitrate item
        picked_stream = audio_items[0]
        picked_url = picked_stream["connection"][1]["href"]

        xbmc.log('Picked the {0} stream with the bitrate {1}'.format(picked_stream['encoding'], picked_stream['bitrate']), level=xbmc.LOGNOTICE)

        play_item = xbmcgui.ListItem(path=picked_url)
        play_item.setArt({
            'thumb': 'https://ichef.bbci.co.uk/images/ic/480xn/' + programme_json["image"]["pid"] + '.jpg',
            'icon': 'https://ichef.bbci.co.uk/images/ic/480xn/' + programme_json["image"]["pid"] + '.jpg'
        })
        play_item.setInfo('music', {
            'title': programme_json["display_title"]["title"],
            'artist': programme_json["display_title"]["subtitle"],
            'album': programme_json["ownership"]["service"]["title"],
            'comment': programme_json["short_synopsis"]
        })

        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

    if picked_url is None:
        xbmcgui.Dialog().notification(__addonname__, "Episode not available to stream", icon=xbmcgui.NOTIFICATION_ERROR)


def mode_podcasts():
    podcasts = requests.get('https://www.bbc.co.uk/podcasts.json')
    podcasts_json = podcasts.json()["podcasts"]

    # Sort the podcasts by title
    podcasts_ordered = sorted(podcasts_json, key=lambda x: x["title"])

    for podcast in podcasts_ordered:
        url = build_url({'mode': 'podcast', 'pid': podcast["shortTitle"]})
        li = xbmcgui.ListItem(podcast["title"])
        li.setInfo('video', {'plot': podcast["description"]})

        if "imageUrl" in podcast:
            li.setThumbnailImage(podcast["imageUrl"].replace('{recipe}', '624x624'))

        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def mode_podcast(pid):
    podcast = feedparser.parse('https://podcasts.files.bbci.co.uk/' + pid + '.rss')

    image_url = None

    if "image" in podcast.feed:
        image_url = podcast.feed.image.url

    for entry in podcast.entries:
        entry_pid = entry.ppg_canonical.split('/')
        entry_date = datetime.datetime.fromtimestamp(mktime(entry.published_parsed)).strftime('%Y-%m-%d')
        entry_title = entry_date + ": " + entry.title

        if len(entry_pid) > 2:
            url = build_url({'mode': 'episode', 'pid': entry_pid[2]})
            li = xbmcgui.ListItem(entry_title)
            li.setInfo('video', {'plot': entry.description})
            li.setThumbnailImage(image_url)
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        else:
            xbmc.log('No pid could be found for the item at ' + entry.link, level=xbmc.LOGERROR)

    xbmcplugin.endOfDirectory(addon_handle)


def mode_stations():
    for pid, station in stations_ordered.items():
        url = build_url({'mode': 'station', 'pid': pid})
        li = xbmcgui.ListItem(station['name'])
        li.setThumbnailImage(xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources', station['image'] + '.png')))
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
        list_item = xbmcgui.ListItem(date.strftime('%Y-%m-%d (%A)'))
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
        xbmcgui.Dialog().notification(__addonname__, "Something went wrong parsing the station's schedule",
                                      icon=xbmcgui.NOTIFICATION_ERROR)
        return

    for episode in result["@graph"]:
        date = dateutil.parser.parse(episode["publication"]["startDate"])

        time = date.strftime('%Y-%m-%d, %H:%M')

        if "partOfSeries" in episode:
            title = time + ": " + episode["partOfSeries"]["name"] + " - " + episode["name"]
        else:
            title = time + ": " + episode["name"]

        url = build_url({'mode': 'episode', 'pid': episode["identifier"]})

        list_item = xbmcgui.ListItem(title)
        list_item.setInfo('video', {'plot': episode["description"]})
        list_item.setPath(url)
        list_item.setProperty('IsPlayable', "true")
        list_item.setThumbnailImage(episode["image"])

        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, isFolder=False)

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
