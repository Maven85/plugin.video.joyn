# -*- coding: utf-8 -*-

from re import search as re_search
from sys import exit
from xbmc import executebuiltin, log as xbmc_log
from xbmcgui import Dialog, ListItem, INPUT_ALPHANUM
from xbmcplugin import setResolvedUrl, addSortMethod
from xbmcplugin import SORT_METHOD_UNSORTED, SORT_METHOD_LABEL, SORT_METHOD_DATE, \
        SORT_METHOD_EPISODE, SORT_METHOD_DURATION, SORT_METHOD_TITLE
from copy import deepcopy
from .const import CONST
from . import compat as compat
from .xbmc_helper import xbmc_helper as xbmc_helper
from . import request_helper as request_helper
from .lib_joyn import lib_joyn as lib_joyn

if compat.PY2:
    from urllib import unquote_plus, urlencode, quote
    try:
        from simplejson import loads, dumps
    except ImportError:
        from json import loads, dumps

elif compat.PY3:
    from urllib.parse import unquote_plus, urlencode, quote
    from json import loads, dumps

if xbmc_helper().get_bool_setting('dont_verify_ssl_certificates') is True:

    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context


def get_list_items(response_items,
                   prefix_label=None,
                   subtype_merges=[],
                   override_fanart='',
                   additional_metadata={},
                   force_resume_pos=False,
                   check_license_type=True):

    from .submodules.libjoyn_video import get_video_client_data

    list_items = []

    response_items = lib_joyn().get_resume_positions(response_items)
    response_items = lib_joyn().get_bookmarks(response_items)

    for response_item in response_items:
        if response_item is None:
            continue

        if check_license_type is True and isinstance(response_item.get('licenseTypes', None),
                                                     list) and lib_joyn().check_license(response_item) is False:
            continue

        if force_resume_pos is True and (not isinstance(response_item.get('resumePosition', {}).get('position'), int)
                                         or response_item.get('resumePosition').get('position') == 0):
            continue

        if response_item['__typename'] in ['Movie', 'SportsMatch', 'Extra']:

            if 'resumePosition' in response_item and 'video' not in response_item:
                movie_data = lib_joyn().get_graphql_response('MOVIES', {
                        'path': response_item['path'],
                })

                if movie_data is not None and movie_data.get('page', {}).get('movie') is not None:
                    response_item.update({'video': movie_data.get('page').get('movie').get('video')})

            if response_item['__typename'] == 'SportsMatch':
                movie_metadata = lib_joyn().get_metadata(response_item, 'EPISODE', 'SPORTSMATCH')
            elif response_item['__typename'] == 'Extra':
                movie_metadata = lib_joyn().get_metadata(response_item, 'EPISODE', 'EXTRA')
            else:
                movie_metadata = lib_joyn().get_metadata(response_item, 'EPISODE', 'MOVIE')
            movie_metadata.update(additional_metadata)

            movie_metadata['infoLabels'].update({'mediatype': 'movie'})

            if prefix_label is not None:
                movie_metadata['infoLabels'].update(
                        {'title': compat._format(xbmc_helper().translation(prefix_label), movie_metadata['infoLabels'].get('title', ''))})

            if 'video' in response_item:
                video_id = response_item['video']['id']

                list_items.append(
                        get_dir_entry(is_folder=False,
                                      mode='play_video',
                                      movie_id=response_item['id'],
                                      metadata=movie_metadata,
                                      video_id=video_id,
                                      client_data=dumps(get_video_client_data(video_id, 'VOD', response_item)),
                                      override_fanart=override_fanart,
                                      path=response_item['path']))
            else:
                list_items.append(
                        get_dir_entry(is_folder=False,
                                      mode='play_movie',
                                      movie_id=response_item['id'],
                                      metadata=movie_metadata,
                                      override_fanart=override_fanart,
                                      path=response_item['path']))

        elif response_item['__typename'] in ['Brand', 'ChannelPage']:

            channel_metadata = lib_joyn().get_metadata(response_item, 'TVCHANNEL')
            if prefix_label is not None:
                channel_metadata['infoLabels'].update(
                        {'title': compat._format(xbmc_helper().translation(prefix_label), channel_metadata['infoLabels'].get('title', ''))})
                channel_metadata.update(additional_metadata)

            list_items.append(
                    get_dir_entry(mode='tvshows',
                                  metadata=channel_metadata,
                                  channel_id=response_item['brand']['id'] if response_item['__typename'] == 'ChannelPage' else response_item['id'],
                                  path=response_item['path'],
                                  override_fanart=override_fanart))

        elif response_item['__typename'] in ['Episode']:

            if 'EPSIODE_AS_SERIES_SEASON' in subtype_merges and 'series' in response_item.keys() and 'season' in response_item.keys():

                season_metadata = lib_joyn().get_metadata(response_item['series'], 'TVSHOW')
                season_metadata['infoLabels'].update({
                        'title':
                        compat._format('{} - {}', season_metadata['infoLabels'].get('title', ''),
                                       compat._format(xbmc_helper().translation('SEASON_NO'), str(response_item['season']['seasonNumber'])))
                })
                season_metadata.update(additional_metadata)

                if prefix_label is not None:
                    season_metadata['infoLabels'].update(
                            {'title': compat._format(xbmc_helper().translation(prefix_label), season_metadata['infoLabels'].get('title', ''))})

                list_items.append(
                        get_dir_entry(
                                mode='season_episodes',
                                season_id=response_item['season']['id'],
                                metadata=season_metadata,
                                override_fanart=override_fanart,
                        ))
            else:

                episode_metadata = lib_joyn().get_metadata(response_item, 'EPISODE')
                episode_metadata['infoLabels'].update({'mediatype': 'episode'})
                video_id = response_item.get('video', {}).get('id', response_item.get('id'))

                list_items.append(
                        get_dir_entry(is_folder=False,
                                      mode='play_video',
                                      metadata=episode_metadata,
                                      video_id=video_id,
                                      client_data=dumps(get_video_client_data(video_id, 'VOD', response_item)),
                                      override_fanart=override_fanart,
                                      season_id=response_item.get('season', {}).get('id', ''),
                                      path=response_item.get('path').rsplit('/', 1)[0]))

        elif response_item['__typename'] == 'CompilationItem':

            compilation_item_metadata = lib_joyn().get_metadata(response_item, 'EPISODE')
            compilation_item_metadata['infoLabels'].update({'mediatype': 'movie'})

            video_id = response_item.get('video', {}).get('id', response_item.get('id'))
            list_items.append(
                    get_dir_entry(is_folder=False,
                                  mode='play_video',
                                  metadata=compilation_item_metadata,
                                  video_id=video_id,
                                  client_data=dumps(get_video_client_data(video_id, 'VOD', response_item)),
                                  override_fanart=override_fanart,
                                  compilation_id=response_item.get('compilation', {}).get('id', '')))

        elif response_item['__typename'] in ['Series', 'Compilation']:

            tvshow_metadata = lib_joyn().get_metadata(response_item, 'TVSHOW')
            tvshow_metadata.update(additional_metadata)

            if prefix_label is not None:
                tvshow_metadata['infoLabels'].update(
                        {'title': compat._format(xbmc_helper().translation(prefix_label), tvshow_metadata['infoLabels'].get('title', ''))})

            if response_item['__typename'] == 'Series':
                list_items.append(
                        get_dir_entry(mode='season',
                                      tv_show_id=response_item['id'],
                                      metadata=tvshow_metadata,
                                      override_fanart=override_fanart,
                                      path=response_item['path']))
            elif response_item['__typename'] == 'Compilation':
                list_items.append(
                        get_dir_entry(mode='compilation_items',
                                      compilation_id=response_item['id'],
                                      metadata=tvshow_metadata,
                                      override_fanart=override_fanart,
                                      path=response_item['path']))

        elif response_item['__typename'] == 'Teaser':

            teaser_metadata = lib_joyn().get_metadata(response_item, 'TEASER')
            teaser_metadata.update(additional_metadata)

            if prefix_label is not None:
                teaser_metadata['infoLabels'].update(
                        {'title': compat._format(xbmc_helper().translation(prefix_label), teaser_metadata['infoLabels'].get('title', ''))})

            list_items.append(
                    get_dir_entry(mode='collection',
                                  teaser_id=response_item['id'],
                                  metadata=teaser_metadata,
                                  override_fanart=override_fanart,
                                  path=response_item['path']))

        elif response_item['__typename'] == 'EpgEntry':

            epg_metadata = lib_joyn().get_epg_metadata(response_item)

            if response_item.get('image') is not None and response_item.get('image').get('url') is not None:
                epg_metadata['art'].update({
                        'icon': response_item['image']['url'],
                        'thumb': response_item['image']['url'],
                })
            if response_item.get('livestream').get('brand', {}).get('logo') is not None:
                epg_metadata['art'].update({'clearlogo': compat._format('{}/profile:original', response_item['livestream']['brand']['logo']['url'].rsplit('/', 1)[0])})

            list_items.append(
                    get_dir_entry(is_folder=False,
                                  metadata=epg_metadata,
                                  mode='play_video',
                                  client_data=dumps(get_video_client_data(response_item['livestream']['id'], 'LIVE')),
                                  video_id=response_item['livestream']['id'],
                                  stream_type='LIVE'))

    return list_items


def index():

    request_helper.purge_etags_cache(ttl=CONST['ETAGS_TTL'])
    from .submodules.plugin_lastseen import show_lastseen
    list_items = show_lastseen(xbmc_helper().get_int_setting('max_lastseen'), default_fanart)
    max_recommendations = xbmc_helper().get_int_setting('max_recommendations')

    if max_recommendations > 0:
        recommendations = 0
        landingpage = deepcopy(lib_joyn().get_landingpage())

        for block in landingpage.get('page').get('blocks'):
            if block.get('__typename') == 'HeroLane':
                if block.get('assets', None) is not None and recommendations < max_recommendations:
                    list_items.extend(
                            get_list_items(block['assets'], prefix_label='RECOMMENDATION', override_fanart=default_fanart))
                    recommendations += 1

    list_items.append(
            get_dir_entry(metadata={
                    'infoLabels': {
                            'title': xbmc_helper().translation('MEDIA_LIBRARIES'),
                            'plot': xbmc_helper().translation('MEDIA_LIBRARIES_PLOT'),
                    },
                    'art': {}
            },
                          mode='channels',
                          stream_type='VOD'))

    list_items.append(
            get_dir_entry(metadata={
                    'infoLabels': {
                            'title': xbmc_helper().translation('LIVE_TV'),
                            'plot': xbmc_helper().translation('LIVE_TV_PLOT'),
                    },
                    'art': {}
            },
                          mode='channels',
                          stream_type='LIVE'))

    list_items.append(
            get_dir_entry(metadata={
                    'infoLabels': {
                            'title': xbmc_helper().translation('LIVE_TV_VOD'),
                    },
                    'art': {}
            },
                          mode='channels',
                          stream_type='LIVE_VOD'))

    list_items.append(
            get_dir_entry(metadata={
                    'infoLabels': {
                            'title': xbmc_helper().translation('TV_SHOWS'),
                            'plot': xbmc_helper().translation('TV_SHOWS_PLOT'),
                    },
                    'art': {}
            },
                          mode='categories',
                          path='/serien'))

    list_items.append(
            get_dir_entry(metadata={
                    'infoLabels': {
                            'title': xbmc_helper().translation('MOVIES'),
                            'plot': xbmc_helper().translation('MOVIES_PLOT'),
                    },
                    'art': {}
            },
                          mode='categories',
                          path='/filme'))

    list_items.append(
            get_dir_entry(metadata={
                    'infoLabels': {
                            'title': xbmc_helper().translation('SPORT'),
                            'plot': xbmc_helper().translation('SPORT_PLOT'),
                    },
                    'art': {}
            },
                          mode='categories',
                          path='/sport'))

    if xbmc_helper().get_bool_setting('show_categories_in_main_menu'):
        list_items.extend(categories('', '/', True))
    else:
        list_items.append(
                get_dir_entry(metadata={
                        'infoLabels': {
                                'title': xbmc_helper().translation('CATEGORIES'),
                                'plot': xbmc_helper().translation('CATEGORIES_PLOT'),
                        },
                        'art': {}
                },
                              mode='categories',
                              stream_type='VOD'))
    list_items.append(
            get_dir_entry(metadata={
                    'infoLabels': {
                            'title': xbmc_helper().translation('WATCHLIST'),
                            'plot': xbmc_helper().translation('WATCHLIST_PLOT'),
                    },
                    'art': {}
            },
                          mode='show_favs'))

    if lib_joyn().get_auth_token().get('has_account', False) is True:
        list_items.append(
                get_dir_entry(metadata={
                        'infoLabels': {
                                'title': xbmc_helper().translation('JOYN_BOOKMARKS'),
                                'plot': '',
                        },
                        'art': {}
                },
                              mode='show_joyn_bookmarks'))

    list_items.append(
            get_dir_entry(metadata={
                    'infoLabels': {
                            'title': xbmc_helper().translation('SEARCH'),
                            'plot': xbmc_helper().translation('SEARCH_PLOT'),
                    },
                    'art': {}
            },
                          mode='search',
                          is_folder=False))

    addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
    xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'INDEX')
    if str(xbmc_helper().get_data('asked_for_login')) != 'True':
        xbmc_helper().set_data('asked_for_login', 'True')

        if lib_joyn().get_auth_token().get('has_account', False) is False:
            xbmc_helper().dialog_action(msg=compat._unicode(xbmc_helper().translation('LOGIN_NOW_LABEL')),
                                        yes_label_translation='LOGIN_LABEL',
                                        cancel_label_translation='CONTINUE_ANONYMOUS',
                                        ok_addon_parameters='mode=login')


def channels(stream_type, title):

    list_items = []
    if stream_type == 'VOD':
        channels = lib_joyn().get_graphql_response('NAVIGATION').get('mediatheken')
        if channels is not None and channels.get('blocks', None) is not None:
            for channel_block in channels.get('blocks'):
                if channel_block.get('assets', None) is not None:
                    list_items.extend(get_list_items(channel_block['assets'], override_fanart=default_fanart))

        xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'CATEORIES', title)

    elif stream_type in ['LIVE', 'LIVE_VOD']:

        from .submodules.libjoyn_video import get_video_client_data
        epg = lib_joyn().get_epg(use_cache=False)
        for brand_epg in epg['liveStreams']:

            if stream_type == 'LIVE_VOD' and brand_epg['type'] != 'ON_DEMAND':
                continue

            if stream_type == 'LIVE' and brand_epg['type'] == 'ON_DEMAND':
                continue

            brand_epg.update({'licenseTypes': []})
            for marking in brand_epg['markings']:
                if marking in ['PREMIUM', 'PLUS']:
                    brand_epg.get('licenseTypes').append('SVOD')
                    break

            if isinstance(brand_epg.get('licenseTypes', None), list) and lib_joyn().check_license(brand_epg) is False:
                continue

            if 'epgEvents' in brand_epg.keys() and len(brand_epg['epgEvents']) > 0:
                metadata = lib_joyn().get_epg_metadata(brand_epg)

                if brand_epg['type'] == 'ON_DEMAND' and brand_epg['epgEvents'][0].get('program') is not None:
                    response_item = brand_epg['epgEvents'][0]['program']
                    list_items.append(
                            get_dir_entry(is_folder=False,
                                          mode='play_video',
                                          movie_id=response_item['id'],
                                          metadata=metadata,
                                          video_id=response_item['video']['id'],
                                          client_data=dumps(get_video_client_data(response_item['video']['id'], 'VOD', response_item)),
                                          path=response_item['path']))
                else:
                    list_items.append(
                            get_dir_entry(is_folder=False,
                                          metadata=metadata,
                                          mode='play_video',
                                          client_data=dumps(get_video_client_data(brand_epg['id'], 'LIVE')),
                                          video_id=brand_epg['id'],
                                          stream_type='LIVE'))

        xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'LIVE_TV', title)


def tvshows(channel_id, channel_path, title):

    from .submodules.plugin_favorites import get_favorite_entry
    list_items = []

    first = 32
    offset = 0
    while True:
        tvshows = lib_joyn().get_graphql_response('CHANNEL', {'path': channel_path, 'first': first, 'offset': offset})
        if tvshows is not None and tvshows.get('page', None) is not None and tvshows.get('page').get('assets', None) is not None and len(tvshows.get('page').get('assets')) > 0:
            list_items.extend(get_list_items(tvshows['page']['assets'], override_fanart=default_fanart))
            offset += first
        else:
            break;

    if len(list_items) == 0:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=pluginhandle, succeeded=False)

        return xbmc_helper().notification(xbmc_helper().translation('MEDIA_LIBRARY'),
                                          xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)

    addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
    addSortMethod(pluginhandle, SORT_METHOD_LABEL)
    list_items = sorted(list_items, key=lambda k: unquote_plus(re_search(r'title=([^&]*)', k[0]).group(1)).upper().replace('[/I]', '').replace('[I]', '').replace('[/COLOR]', '').replace('[COLOR BLUE]', ''))
    list_items.append(get_favorite_entry({'channel_id': channel_id, 'channel_path': channel_path}, 'MEDIA_LIBRARY'))
    xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'TV_SHOWS', title)


def seasons(tv_show_id, title, path):

    from .submodules.plugin_favorites import get_favorite_entry
    list_items = []

    seasons = lib_joyn().get_graphql_response('SEASONS', {
            'path': path,
            'licenseFilter': 'ALL',
    })

    if seasons is not None and seasons.get('page', {}).get('series') is not None:
        tvshow_metadata = lib_joyn().get_metadata(seasons['page']['series'], 'TVSHOW')
        counter = 1
        seasons_count = len(seasons['page']['series']['allSeasons'])

        for season in seasons['page']['series']['allSeasons']:

            if 'number' in season.keys():
                season_number = season['number']
            else:
                season_number = counter

            if isinstance(season.get('licenseTypes', None), list) and lib_joyn().check_license(season) is False:
                continue

            if xbmc_helper().get_bool_setting('show_episodes_immediately') and len(seasons['page']['series']['allSeasons']) == 1:
                return season_episodes(
                        season['id'],
                        compat._format('{} - {}', title, compat._format(xbmc_helper().translation('SEASON_NO'), str(season_number))))

            tvshow_metadata['infoLabels'].update({
                    'title': compat._format(xbmc_helper().translation('SEASON_NO'), str(season_number)),
                    'season': seasons_count,
                    'sortseason': season_number,
            })

            if len(seasons['page']['series']['allSeasons']) > 1:
                list_items.append(
                        get_dir_entry(mode='season_episodes',
                                      season_id=season['id'],
                                      metadata=tvshow_metadata,
                                      title_prefix=compat._format('{} - ', title)))
            else:
                list_items.append(
                        get_dir_entry(mode='series_episodes',
                                      tv_show_id=tv_show_id,
                                      metadata=tvshow_metadata,
                                      title_prefix=compat._format('{} - ', title)))
            counter += 1

    if len(list_items) == 0:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=pluginhandle, succeeded=False)

        return xbmc_helper().notification(xbmc_helper().translation('TV_SHOW'),
                                          xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)

    addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
    addSortMethod(pluginhandle, SORT_METHOD_LABEL)
    addSortMethod(pluginhandle, SORT_METHOD_TITLE)

    list_items.append(get_favorite_entry({'tv_show_id': tv_show_id, 'path': path}, 'TV_SHOW'))
    xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'SEASONS', title)


def series_episodes(tv_show_id, title):

    from .submodules.plugin_favorites import get_favorite_entry
    list_items = []
    tv_show_path = None
    season_id = None

    offset = 0
    episodes = {}
    while True:
        episodes = lib_joyn().get_graphql_response('RECENT_EPISODES', {
                'id': tv_show_id,
                'offset': offset
        })

        override_fanart = default_fanart
        if episodes is not None and episodes.get('series', None) is not None and isinstance(
                episodes.get('series').get('episodes', None), list) and len(episodes.get('series').get('episodes')) > 0:

            first_episode = episodes.get('series').get('episodes')[0]
            if 'series' in first_episode.keys():
                tvshow_meta = lib_joyn().get_metadata(first_episode['series'], 'TVSHOW')
                if 'fanart' in tvshow_meta['art']:
                    override_fanart = tvshow_meta['art']['fanart']

            if tv_show_path is None:
                tv_show_path = first_episode.get('path').rsplit('/', 1)[0]
            if season_id is None:
                season_id = first_episode.get('season').get('id')

            list_items.extend(get_list_items(episodes.get('series').get('episodes'), override_fanart=override_fanart, check_license_type=True))

            offset += 32
        else:
            break

    if len(list_items) == 0:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=pluginhandle, succeeded=False)

        return xbmc_helper().notification(xbmc_helper().translation('SEASON'),
                                          xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)

    addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
    addSortMethod(pluginhandle, SORT_METHOD_LABEL)
    addSortMethod(pluginhandle, SORT_METHOD_DURATION)
    addSortMethod(pluginhandle, SORT_METHOD_DATE)
    addSortMethod(pluginhandle, SORT_METHOD_EPISODE)

    list_items.append(get_favorite_entry({'tv_show_id': tv_show_id, 'tv_show_path': tv_show_path, 'season_id': season_id}, 'SEASON'))
    xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'EPISODES', title)


def season_episodes(season_id, title):

    from .submodules.plugin_favorites import get_favorite_entry
    list_items = []

    episodes = lib_joyn().get_graphql_response('EPISODES', {
            'id': season_id,
            'licenseFilter': 'ALL',
    })
    override_fanart = default_fanart
    if episodes is not None and episodes.get('season', None) is not None and isinstance(
            episodes.get('season').get('episodes', None), list) and len(episodes.get('season').get('episodes')) > 0:

        first_episode = episodes.get('season').get('episodes')[0]
        if 'series' in first_episode.keys():
            tvshow_meta = lib_joyn().get_metadata(first_episode['series'], 'TVSHOW')
            if 'fanart' in tvshow_meta['art']:
                override_fanart = tvshow_meta['art']['fanart']

        list_items = get_list_items(episodes.get('season').get('episodes'), override_fanart=override_fanart, check_license_type=True)

    if len(list_items) == 0:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=pluginhandle, succeeded=False)

        return xbmc_helper().notification(xbmc_helper().translation('SEASON'),
                                          xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)

    addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
    addSortMethod(pluginhandle, SORT_METHOD_LABEL)
    addSortMethod(pluginhandle, SORT_METHOD_DURATION)
    addSortMethod(pluginhandle, SORT_METHOD_DATE)
    addSortMethod(pluginhandle, SORT_METHOD_EPISODE)

    list_items.append(get_favorite_entry({'season_id': season_id, 'tv_show_path': episodes.get('season').get('episodes')[0].get('path').rsplit('/', 1)[0]}, 'SEASON'))
    xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'EPISODES', title)


def get_compilation_items(compilation_id, compilation_path, title):

    from .submodules.plugin_favorites import get_favorite_entry
    list_items = []
    compilation_items = lib_joyn().get_graphql_response('COMPILATION', {'path': compilation_path}).get('page', {})
    override_fanart = default_fanart

    if compilation_items is not None and compilation_items.get('compilation', None) is not None and isinstance(
            compilation_items.get('compilation').get('compilationItems', None),
            list) and len(compilation_items.get('compilation').get('compilationItems')) > 0:

        first_item = compilation_items.get('compilation').get('compilationItems')[0]
        if 'compilation' in first_item.keys():
            compilation_metadata = lib_joyn().get_metadata(first_item['compilation'], 'TVSHOW')
            if 'fanart' in compilation_metadata['art']:
                override_fanart = compilation_metadata['art']['fanart']

        list_items = get_list_items(compilation_items.get('compilation').get('compilationItems'), override_fanart=override_fanart)

    if len(list_items) == 0:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=pluginhandle, succeeded=False)

        return xbmc_helper().notification(xbmc_helper().translation('TV_SHOW'),
                                          xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)

    addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
    addSortMethod(pluginhandle, SORT_METHOD_LABEL)
    addSortMethod(pluginhandle, SORT_METHOD_DURATION)

    list_items.append(get_favorite_entry({'compilation_id': compilation_id, 'compilation_path': compilation_path}, 'TV_SHOW'))
    xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'EPISODES', title)


def search(stream_type, title, search_term=''):

    if len(search_term) != 0:
        xbmc_helper().log_debug('Search term: {}', search_term)
        search_response = lib_joyn().get_graphql_response('SEARCH', {'text': search_term})
        if 'search' in search_response.keys() and 'results' in search_response['search'] and len(
                search_response['search']['results']) > 0:

            return xbmc_helper().set_folder(get_list_items(search_response['search']['results'], override_fanart=default_fanart),
                                            pluginurl, pluginhandle, pluginquery, 'TV_SHOWS', title)
    else:
        _search_term = Dialog().input(xbmc_helper().translation('SEARCH'), type=INPUT_ALPHANUM)
        search_response = lib_joyn().get_graphql_response('SEARCH', {'text': _search_term})
        if 'search' in search_response.keys() and 'results' in search_response['search'] and len(
                search_response['search']['results']) > 0:
            _url = compat._format('Container.Update({}?{},replace)', pluginurl,
                                  urlencode({
                                          'mode': 'search',
                                          'search_term': _search_term,
                                  }))
            return executebuiltin(_url)
        else:
            xbmc_helper().notification(xbmc_helper().translation('SEARCH'),
                                       compat._format(xbmc_helper().translation('MSG_NO_SEARCH_RESULTS'), _search_term), default_icon)


def categories(title, path, return_list_items=False):

    list_items = []
    landingpage = deepcopy(lib_joyn().get_landingpage(path))

    blocks = landingpage.get('page').get('blocks')
    blocks.extend(landingpage.get('page').get('lazyBlocks'))

    for block in blocks:
        if block.get('__typename') in CONST['CATEGORY_LANES']:
            viewtype = 'TV_SHOWS'
            if block.get('__typename') == 'CollectionLane':
                viewtype = 'CATEORIES'
            elif block.get('__typename') == 'CollectionLane':
                viewtype = 'CATEORIES'
            elif block.get('__typename') == 'LiveLane':
                viewtype = 'LIVE_TV'

            list_items.append(
                    get_dir_entry(metadata={
                            'infoLabels': {
                                    'title': block['headline'],
                                    'plot': '',
                            },
                            'art': {}
                    },
                                  mode='category',
                                  viewtype=viewtype,
                                  block_id=block['id']))
    if return_list_items is True:
        return list_items
    else:
        xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'CATEORIES', title)


def category(block_id, title, viewtype='TV_SHOWS'):

    from .submodules.plugin_favorites import get_favorite_entry
    list_items = []
    category = lib_joyn().get_graphql_response('LANDINGBLOCKS', {'ids': [block_id]})

    if category is not None and category.get('blocks', None) is not None:
        for block in category.get('blocks'):
            if block.get('id') == block_id and block.get('assets', None) is not None:
                list_items = get_list_items(block['assets'],
                                            additional_metadata=dict(parent_block_id=block['id']),
                                            override_fanart=default_fanart,
                                            force_resume_pos=False if viewtype != 'EPISODES' else True)

    if len(list_items) == 0:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=pluginhandle, succeeded=False)

        return xbmc_helper().notification(xbmc_helper().translation('CATEGORY'),
                                          xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)

    addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
    addSortMethod(pluginhandle, SORT_METHOD_LABEL)

    list_items.append(get_favorite_entry({'block_id': block_id}, 'CATEGORY'))
    xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, viewtype, title)


def collection(collection_id, collection_path, title, parent_block_id):

    from .submodules.plugin_favorites import get_favorite_entry
    list_items = []
    viewtype = 'CATEORIES'

    collection = lib_joyn().get_graphql_response('COLLECTION', {'path': collection_path})
    if collection is not None and collection.get('page', None) is not None and collection.get('page').get('blocks', None) is not None:
        for block in collection.get('page').get('blocks'):
            if block.get('__typename') in CONST['COLLECTION_LANES']:
                list_items.append(
                    get_dir_entry(metadata={
                            'infoLabels': {
                                    'title': block['headline'],
                                    'plot': '',
                            },
                            'art': {}
                    },
                                  mode='category',
                                  viewtype='TV_SHOWS',
                                  block_id=block['id']))
            elif block.get('__typename') in CONST['COLLECTION_GRID']:
                list_items.extend(get_list_items(block['assets'], override_fanart=default_fanart))
                viewtype = 'TV_SHOWS'

    if len(list_items) == 0:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=pluginhandle, succeeded=False)

        return xbmc_helper().notification(xbmc_helper().translation('CATEGORY'),
                                          xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)

    addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
    addSortMethod(pluginhandle, SORT_METHOD_LABEL)
    list_items.append(get_favorite_entry({'collection_id': collection_id, 'collection_path': collection_path, 'parent_block_id': parent_block_id}, 'CATEGORY'))
    xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, viewtype, title)


def play_movie(path):

    movie_data = lib_joyn().get_graphql_response('MOVIES', {
            'path': path,
    })

    if movie_data is not None and movie_data.get('page', {}).get('movie') is not None:
        from .submodules.libjoyn_video import get_video_client_data

        from xbmc import log, LOGINFO

        movie = movie_data.get('page').get('movie')
        video_id = movie['video']['id']
        client_data = dumps(get_video_client_data(video_id, 'VOD', movie))
        movie_id = movie['id']
        play_video(video_id, client_data, 'VOD', movie_id=movie_id, path=path)
    else:
        from xbmcplugin import endOfDirectory
        endOfDirectory(handle=pluginhandle, succeeded=False)

        return xbmc_helper().notification(xbmc_helper().translation('MOVIE'),
                                          xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)


def play_video(video_id, client_data, stream_type, season_id=None, movie_id=None, compilation_id=None, path=None, retries=0):

    from xbmc import getCondVisibility
    xbmc_helper().log_debug('play_video: video_id {} - try no: {}', video_id, retries)
    succeeded = False
    list_item = ListItem()

    if not xbmc_helper().addon_enabled(CONST['INPUTSTREAM_ADDON']):
        xbmc_helper().dialog_id('MSG_INPUSTREAM_NOT_ENABLED')
        exit(0)

    if not getCondVisibility('System.Platform.Android'):
        from inputstreamhelper import Helper
        is_helper = Helper('mpd', drm='com.widevine.alpha')
        if not is_helper.check_inputstream():
            xbmc_helper().dialog_id('MSG_WIDEVINE_NOT_FOUND')
            exit(0)

    try:
        from .submodules.libjoyn_video import get_video_data
        video_data = get_video_data(video_id, stream_type, season_id, movie_id, compilation_id, path)

        xbmc_helper().log_debug('Got video data: {}', video_data)

        list_item.setContentLookup(False)
        list_item.setProperty('inputstreamaddon' if xbmc_helper().kodi_version <= 18 else 'inputstream', CONST['INPUTSTREAM_ADDON'])

        # DASH
        list_item.setMimeType('application/dash+xml')
        list_item.setProperty(compat._format('{}.manifest_type', CONST['INPUTSTREAM_ADDON']), 'mpd')
        list_item.setPath(video_data.get('manifestUrl', None))

        drm = video_data.get('drm', '')
        license_key = video_data.get('licenseUrl', None)
        license_cert = video_data.get('certificateUrl', None)
        xbmc_helper().log_debug('drm: {} key: {} cert: {}', drm, license_key, license_cert)

        if license_key is not None:
            if drm.lower() == 'widevine':
                xbmc_helper().log_notice('Using Widevine as DRM')

                list_item.setProperty(compat._format('{}.license_type', CONST['INPUTSTREAM_ADDON']), 'com.widevine.alpha')
                list_item.setProperty(
                        compat._format('{}.license_key', CONST['INPUTSTREAM_ADDON']),
                        compat._format(
                                '{}|{}|R{{SSM}}|', license_key,
                                request_helper.get_header_string({
                                        'User-Agent': lib_joyn().config.get('USER_AGENT'),
                                        'Content-Type': 'application/octet-stream'
                                })))
                list_item.setProperty(compat._format('{}.stream_headers', CONST['INPUTSTREAM_ADDON']),
                                      request_helper.get_header_string({'User-Agent': lib_joyn().config['USER_AGENT']}))

                if license_cert is not None and xbmc_helper().get_bool_setting('checkdrmcert') is True:
                    xbmc_helper().log_debug('Set DRM cert: {}', license_cert)
                    list_item.setProperty(compat._format('{}.server_certificate', CONST['INPUTSTREAM_ADDON']),
                                          lib_joyn().add_user_agent_http_header(license_cert))

            elif drm.lower() == 'playready':
                xbmc_helper().log_notice('Using PlayReady as DRM')
                list_item.setProperty(compat._format('{}.license_type', CONST['INPUTSTREAM_ADDON']), 'com.microsoft.playready')
                list_item.setProperty(
                        compat._format('{}.license_key', CONST['INPUTSTREAM_ADDON']),
                        compat._format(
                                '{}|{}|R{{SSM}}|', license_key,
                                request_helper.get_header_string({
                                        'User-Agent':
                                        CONST['EDGE_UA'],
                                        'Content-Type':
                                        'text/xml',
                                        'SOAPAction':
                                        'http://schemas.microsoft.com/DRM/2007/03/protocols/AcquireLicense'
                                })))

                list_item.setProperty(compat._format('{}.stream_headers', CONST['INPUTSTREAM_ADDON']),
                                      request_helper.get_header_string({'User-Agent': CONST['EDGE_UA']}))

        if stream_type == 'LIVE':
            list_item.setProperty(compat._format('{}.manifest_update_parameter', CONST['INPUTSTREAM_ADDON']), 'full')

        succeeded = True

        from .submodules.plugin_lastseen import add_lastseen
        if video_data.get('season_id') and video_data.get('path'):
            add_lastseen(season_id=video_data['season_id'], path=video_data['path'], max_lastseen=CONST['LASTSEEN_ITEM_COUNT'])
        elif video_data.get('movie_id') and video_data.get('path'):
            add_lastseen(movie_id=video_data['movie_id'], path=video_data['path'], max_lastseen=CONST['LASTSEEN_ITEM_COUNT'])
        elif 'compilation_id' in video_data.keys() and video_data['compilation_id'] is not None:
            add_lastseen(compilation_id=video_data['compilation_id'], path=video_data['path'], max_lastseen=CONST['LASTSEEN_ITEM_COUNT'])

    except Exception as e:
        if retries < CONST.get('MAX_VIDEO_TRIES'):
            xbmc_helper().log_notice('Getting videostream / manifest failed with Exception: {} - current try {} of {}', e, retries,
                                     CONST.get('MAX_VIDEO_TRIES'))
            play_video(video_id, client_data, stream_type, season_id=season_id, movie_id=movie_id, compilation_id=compilation_id, path=path, retries=(retries + 1))
        else:
            succeeded = False
            xbmc_helper().log_error('Getting videostream / manifest failed with Exception: {}', e)
            xbmc_helper().notification(compat._format(xbmc_helper().translation('ERROR'), 'Video-Stream'),
                                       xbmc_helper().translation('MSG_ERROR_NO_VIDEOSTEAM'))
        pass

    if succeeded is True and stream_type == 'VOD':
        from xbmcgui import Window, getCurrentWindowId
        Window(getCurrentWindowId()).setProperty('joyn_video_id', video_id)

    setResolvedUrl(pluginhandle, succeeded, list_item)


def get_dir_entry(mode,
                  metadata,
                  is_folder=True,
                  block_id='',
                  channel_id='',
                  movie_id='',
                  tv_show_id='',
                  season_id='',
                  teaser_id='',
                  video_id='',
                  stream_type='VOD',
                  override_fanart='',
                  fav_type='',
                  favorite_item=None,
                  title_prefix='',
                  client_data='',
                  compilation_id='',
                  viewtype='',
                  path=''):

    params = {
            'mode': mode,
            'parent_block_id': metadata.get('parent_block_id', ''),
            'block_id': block_id,
            'channel_id': channel_id,
            'movie_id': movie_id,
            'tv_show_id': tv_show_id,
            'season_id': season_id,
            'teaser_id': teaser_id,
            'video_id': video_id,
            'stream_type': stream_type,
            'fav_type': fav_type,
            'title': compat._encode(title_prefix) + compat._encode(metadata['infoLabels'].get('title', '')),
            'client_data': client_data,
            'compilation_id': compilation_id,
            'viewtype': viewtype,
            'path': path,
    }

    if favorite_item is not None:
        params.update({'favorite_item': dumps(favorite_item)})

    list_item = ListItem(label=metadata['infoLabels']['title'], offscreen=True)
    list_item = xbmc_helper().set_videoinfo(list_item, metadata['infoLabels'])

    if is_folder is True:
        list_item.setProperty('isPlayable', 'false')

    if 'poster' not in metadata['art'] and 'thumb' in metadata['art']:
        metadata['art'].update({'poster': metadata['art']['thumb']})
    elif 'thumb' not in metadata['art']:
        metadata['art'].update({'thumb': default_logo})
        metadata['art'].update({'poster': default_logo})

    if 'icon' not in metadata['art']:
        metadata['art'].update({'icon': default_icon})

    if override_fanart != '':
        metadata['art'].update({'fanart': override_fanart})

    if 'fanart' not in metadata['art']:
        metadata['art'].update({'fanart': default_fanart})

    for art_key, art_value in metadata['art'].items():
        metadata['art'].update({art_key: lib_joyn().add_user_agent_http_header(art_value)})

    list_item.setArt(metadata['art'])

    if (mode == 'play_video' and video_id != '' and client_data != '') or mode == 'play_movie':
        list_item.setProperty('IsPlayable', 'True')

        if 'resume_pos' in metadata.keys() and 'duration' in metadata['infoLabels'].keys():
            xbmc_helper().log_debug('Setting resume position - asset {} - pos {}', metadata['infoLabels']['title'],
                                    metadata.get('resume_pos'))
            list_item.setProperty('ResumeTime', metadata.get('resume_pos'))
            list_item.setProperty('TotalTime', str(float(metadata['infoLabels'].get('duration'))))

    if metadata.get('is_bookmarked', None) is not None and lib_joyn().get_auth_token().get('has_account', False) is True:
        asset_id = None

        if mode == 'season' and tv_show_id != '':
            asset_id = tv_show_id
        elif (mode == 'play_video' or mode == 'play_movie') and movie_id != '':
            asset_id = movie_id
        elif mode == 'compilation_items' and compilation_id != '':
            asset_id = compilation_id

        if asset_id is not None:
            if metadata.get('is_bookmarked', False) is True:
                list_item.addContextMenuItems([(xbmc_helper().translation('DEL_FROM_JOYN_BOOKMARKS_LABEL'),
                                                compat._format('RunPlugin({}?{})', pluginurl,
                                                               urlencode({
                                                                       'mode': 'remove_joyn_bookmark',
                                                                       'asset_id': asset_id
                                                               })))])
            else:
                list_item.addContextMenuItems([(xbmc_helper().translation('ADD_TO_JOYN_BOOKMARKS_LABEL'),
                                                compat._format('RunPlugin({}?{})', pluginurl,
                                                               urlencode({
                                                                       'mode': 'add_joyn_bookmark',
                                                                       'asset_id': asset_id
                                                               })))])

    return (compat._format('{}?{}', pluginurl, urlencode(params)), list_item, is_folder)


def clear_cache():
    if xbmc_helper().remove_dir(CONST['CACHE_DIR']) is True:
        xbmc_helper().notification('Cache', xbmc_helper().translation('CACHE_WAS_CLEARED'), default_icon)
    else:
        xbmc_helper().notification('Cache', xbmc_helper().translation('CACHE_COULD_NOT_BE_CLEARED'))


def logout(dont_check_account=False):
    from .submodules.libjoyn_auth import logout as libjoyn_logout
    return libjoyn_logout(dont_check_account=dont_check_account)


def login(dont_check_account=False, failed=False, no_account_dialog=False):
    from .submodules.libjoyn_auth import login as libjoyn_login
    return libjoyn_login(dont_check_account=dont_check_account, failed=failed, no_account_dialog=no_account_dialog)


def run(_pluginurl, _pluginhandle, _pluginquery, addon):

    global pluginurl
    pluginurl = _pluginurl

    global pluginhandle
    pluginhandle = _pluginhandle

    global pluginquery
    pluginquery = _pluginquery

    xbmc_helper().set_addon(addon)

    global default_icon
    default_icon = xbmc_helper().get_addon().getAddonInfo('icon')

    global default_fanart
    default_fanart = xbmc_helper().get_addon().getAddonInfo('fanart')

    params = xbmc_helper().get_addon_params(pluginquery)
    param_keys = params.keys()

    xbmc_helper().log_debug('params = {}', params)

    if 'mode' in param_keys:

        mode = params['mode']

        if mode == 'clear_cache':
            clear_cache()

        else:

            stream_type = params.get('stream_type', 'VOD')
            title = params.get('title', '')

            if mode == 'season' and 'tv_show_id' in param_keys and 'path' in param_keys:
                seasons(params['tv_show_id'], title, params['path'])

            elif mode == 'series_episodes' and 'tv_show_id' in param_keys:
                series_episodes(params['tv_show_id'], title)

            elif mode == 'season_episodes' and 'season_id' in param_keys:
                season_episodes(params['season_id'], title)

            elif mode == 'play_movie' and 'path' in param_keys:
                play_movie(params['path'])

            elif mode == 'play_video' and 'video_id' in param_keys:
                if 'client_data' in param_keys:
                    if 'season_id' in param_keys:
                        play_video(video_id=params['video_id'],
                                   client_data=params['client_data'],
                                   stream_type=stream_type,
                                   season_id=params['season_id'],
                                   path=params['path'])
                    elif 'movie_id' in param_keys:
                        play_video(video_id=params['video_id'],
                                   client_data=params['client_data'],
                                   stream_type=stream_type,
                                   movie_id=params['movie_id'],
                                   path=params['path'])
                    elif 'compilation_id' in param_keys:
                        play_video(video_id=params['video_id'],
                                   client_data=params['client_data'],
                                   stream_type=stream_type,
                                   compilation_id=params['compilation_id'])
                    else:
                        play_video(video_id=params['video_id'], client_data=params['client_data'], stream_type=stream_type)
                elif stream_type == 'LIVE':
                    from .submodules.libjoyn_video import get_video_client_data
                    play_video(video_id=params['video_id'],
                               client_data=params.get('client_data', dumps(get_video_client_data(params['video_id'], stream_type))),
                               stream_type=stream_type)

            elif mode == 'compilation_items' and 'compilation_id' in param_keys and 'path' in param_keys:
                get_compilation_items(params['compilation_id'], params['path'], title)

            elif mode == 'channels':
                channels(stream_type, title)

            elif mode == 'tvshows' and 'channel_id' in param_keys and 'path' in param_keys:
                tvshows(params['channel_id'], params['path'], title)

            elif mode == 'search':
                search(stream_type, title, search_term=params.get('search_term', ''))

            elif mode == 'categories':
                categories(title, params.get('path', '/'))

            elif mode == 'category' and 'block_id' in param_keys:
                category(params['block_id'], title, params.get('viewtype', 'TV_SHOWS'))

            elif mode == 'collection' and 'teaser_id' in param_keys and 'path' in param_keys:
                collection(params['teaser_id'], params['path'], title, params.get('parent_block_id'))

            elif mode == 'show_favs':
                from .submodules.plugin_favorites import show_favorites
                show_favorites(title, pluginurl, pluginhandle, pluginquery, default_fanart, default_icon)

            elif mode == 'add_fav' and 'favorite_item' in param_keys and 'fav_type' in param_keys:
                from .submodules.plugin_favorites import add_favorites
                add_favorites(loads(params['favorite_item']), default_icon, params['fav_type'])

            elif mode == 'drop_fav' and 'favorite_item' in param_keys and 'fav_type' in param_keys:
                from .submodules.plugin_favorites import drop_favorites
                drop_favorites(favorite_item=loads(params['favorite_item']), default_icon=default_icon, fav_type=params['fav_type'])

            elif mode == 'show_joyn_bookmarks':
                from .submodules.plugin_favorites import show_joyn_bookmarks
                show_joyn_bookmarks(title, pluginurl, pluginhandle, pluginquery, default_icon, default_fanart)

            elif mode == 'login':
                login_params = {}
                if 'dont_check_account' in param_keys:
                    login_params.update({'dont_check_account': True})
                if 'failed' in param_keys:
                    login_params.update({'failed': False if params.get('failed') != 'true' else True})
                if 'no_account_dialog' in param_keys:
                    login_params.update({'no_account_dialog': False if params.get('no_account_dialog') != 'true' else True})

                login(**login_params)

            elif mode == 'logout':
                if 'dont_check_account' in param_keys:
                    logout(dont_check_account=True)
                else:
                    logout()

            elif mode == 'remove_joyn_bookmark' and 'asset_id' in param_keys:
                from .submodules.plugin_favorites import remove_joyn_bookmark
                remove_joyn_bookmark(params['asset_id'], default_icon)

            elif mode == 'add_joyn_bookmark' and 'asset_id' in param_keys:
                from .submodules.plugin_favorites import add_joyn_bookmark
                add_joyn_bookmark(params['asset_id'], default_icon)

            else:
                index()
    else:
        index()


pluginurl = None
pluginhandle = None
pluginquery = None
default_icon = None
default_fanart = None
default_logo = xbmc_helper().get_media_filepath('logo.gif')
