# -*- coding: utf-8 -*-

from xbmc import executebuiltin
from copy import deepcopy
from ..xbmc_helper import xbmc_helper
from ..const import CONST
from .. import compat
from ..lib_joyn import lib_joyn


def get_favorites():
	favorites = xbmc_helper().get_json_data('favorites')

	if favorites is not None:
		return favorites

	return []


def get_favorite_entry(favorite_item, favorite_type):

	from ..plugin import get_dir_entry

	fav_del_art = {
	        'thumb': xbmc_helper().get_media_filepath('fav_del_thumb.png'),
	        'icon': xbmc_helper().get_media_filepath('fav_del_icon.png')
	}
	fav_add_art = {
	        'thumb': xbmc_helper().get_media_filepath('fav_add_thumb.png'),
	        'icon': xbmc_helper().get_media_filepath('fav_add_icon.png')
	}

	if check_favorites(favorite_item) is False:
		return get_dir_entry(is_folder=False,
		                     metadata={
		                             'infoLabels': {
		                                     'title':
		                                     xbmc_helper().translation('ADD_TO_WATCHLIST'),
		                                     'plot':
		                                     compat._format(xbmc_helper().translation('ADD_TO_WATCHLIST_PRX'),
		                                                    xbmc_helper().translation(favorite_type)),
		                             },
		                             'art': fav_add_art
		                     },
		                     mode='add_fav',
		                     favorite_item=favorite_item,
		                     fav_type=xbmc_helper().translation(favorite_type))
	else:
		return get_dir_entry(is_folder=False,
		                     metadata={
		                             'infoLabels': {
		                                     'title':
		                                     xbmc_helper().translation('REMOVE_FROM_WATCHLIST'),
		                                     'plot':
		                                     compat._format(xbmc_helper().translation('REMOVE_FROM_WATCHLIST_PRFX'),
		                                                    xbmc_helper().translation(favorite_type)),
		                             },
		                             'art': fav_del_art
		                     },
		                     mode='drop_fav',
		                     favorite_item=favorite_item,
		                     fav_type=xbmc_helper().translation(favorite_type))


def add_favorites(favorite_item, default_icon, fav_type=''):

	from time import time

	if check_favorites(favorite_item) is False:
		favorites = get_favorites()
		favorite_item.update({'added': time()})
		favorites.append(favorite_item)
		xbmc_helper().set_json_data('favorites', favorites)

		executebuiltin("Container.Refresh")
		xbmc_helper().notification(xbmc_helper().translation('WATCHLIST'),
		                           compat._format(xbmc_helper().translation('WL_TYPE_ADDED'), fav_type), default_icon)


def drop_favorites(favorite_item, default_icon, silent=False, fav_type=''):

	xbmc_helper().log_debug('drop_favorites  - item {}: ', favorite_item)
	favorites = get_favorites()
	found = False

	for favorite in favorites:

		if 'season_id' in favorite_item.keys() and 'season_id' in favorite.keys(
		) and favorite_item['season_id'] == favorite['season_id']:
			favorites.remove(favorite)
			found = True

		elif 'tv_show_id' in favorite_item.keys() and 'tv_show_id' in favorite.keys(
		) and favorite_item['tv_show_id'] == favorite['tv_show_id']:
			favorites.remove(favorite)
			found = True

		elif 'channel_id' in favorite_item.keys() and 'channel_id' in favorite.keys(
		) and favorite_item['channel_id'] == favorite['channel_id']:
			favorites.remove(favorite)
			found = True

		elif 'movie_id' in favorite_item.keys() and 'movie_id' in favorite.keys(
		) and favorite_item['movie_id'] == favorite['movie_id']:
			favorites.remove(favorite)
			found = True

		elif 'block_id' in favorite_item.keys() and 'block_id' in favorite.keys(
		) and favorite_item['block_id'] == favorite['block_id']:
			favorites.remove(favorite)
			found = True

		elif 'category_name' in favorite_item.keys() and 'category_name' in favorite.keys(
		) and favorite_item['category_name'] == favorite['category_name']:
			favorites.remove(favorite)
			found = True

		elif 'collection_id' in favorite_item.keys() and 'collection_id' in favorite.keys(
		) and favorite_item['collection_id'] == favorite['collection_id']:
			favorites.remove(favorite)
			found = True

		elif 'compilation_id' in favorite_item.keys() and 'compilation_id' in favorite.keys(
		) and favorite_item['compilation_id'] == favorite['compilation_id']:
			favorites.remove(favorite)
			found = True

	xbmc_helper().set_json_data('favorites', favorites)

	if silent is False and found is True:
		xbmc_helper().notification(xbmc_helper().translation('WATCHLIST'),
		                           compat._format(xbmc_helper().translation('WL_TYPE_REMOVED'), fav_type), default_icon)
		executebuiltin("Container.Refresh")


def check_favorites(favorite_item):

	favorites = get_favorites()
	for favorite in favorites:
		if 'season_id' in favorite_item.keys() and 'season_id' in favorite.keys(
		) and favorite_item['season_id'] == favorite['season_id']:
			return True

		elif 'tv_show_id' in favorite_item.keys() and 'tv_show_id' in favorite.keys(
		) and favorite_item['tv_show_id'] == favorite['tv_show_id']:
			return True

		elif 'block_id' in favorite_item.keys() and 'block_id' in favorite.keys(
		) and favorite_item['block_id'] == favorite['block_id']:
			return True

		elif 'movie_id' in favorite_item.keys() and 'movie_id' in favorite.keys(
		) and favorite_item['movie_id'] == favorite['movie_id']:
			return True

		elif 'channel_id' in favorite_item.keys() and 'channel_id' in favorite.keys(
		) and favorite_item['channel_id'] == favorite['channel_id']:
			return True

		elif 'collection_id' in favorite_item.keys() and 'collection_id' in favorite.keys(
		) and favorite_item['collection_id'] == favorite['collection_id']:
			return True

		elif 'compilation_id' in favorite_item.keys() and 'compilation_id' in favorite.keys(
		) and favorite_item['compilation_id'] == favorite['compilation_id']:
			return True

	return False


def show_favorites(title, pluginurl, pluginhandle, pluginquery, default_fanart, default_icon):

	from xbmcplugin import addSortMethod, SORT_METHOD_UNSORTED, SORT_METHOD_LABEL, SORT_METHOD_DATEADDED
	from datetime import datetime
	from ..plugin import get_list_items, get_dir_entry

	favorites = get_favorites()
	list_items = []

	if len(favorites) == 0:
		from xbmcplugin import endOfDirectory
		endOfDirectory(handle=pluginhandle, succeeded=False)
		return xbmc_helper().notification(xbmc_helper().translation('WATCHLIST'),
		                                  xbmc_helper().translation('MSG_NO_FAVS_YET'), default_icon)

	for favorite_item in favorites:
		if 'added' in favorite_item.keys():
			add_meta = {'dateadded': datetime.fromtimestamp(favorite_item['added']).strftime('%Y-%m-%d %H:%M:%S')}
		else:
			add_meta = {}

		if favorite_item.get('season_id', None) is not None:
			tvshow_data = lib_joyn().get_graphql_response('SEASONS', {
			        'path': favorite_item['tv_show_path'],
			        'licenseFilter': lib_joyn().get_license_filter()
			})

			if tvshow_data.get('page') is not None and tvshow_data.get('page').get('series', None) is not None:
				for season in tvshow_data.get('page').get('series').get('allSeasons'):
					if favorite_item['season_id'] == season['id'] and season['numberOfEpisodes'] > 0:
						season_metadata = lib_joyn().get_metadata(tvshow_data.get('page').get('series'), 'TVSHOW')
						season_metadata['infoLabels'].update({
						        'title':
						        compat._format('{} - {}', season_metadata['infoLabels'].get('title', ''),
						                       compat._format(xbmc_helper().translation('SEASON_NO'), str(season['number'])))
						})

						if 'added' in favorite_item.keys():
							season_metadata.update({'dateadded': datetime.fromtimestamp(favorite_item['added']).strftime('%Y-%m-%d %H:%M:%S')})

						list_items.append(
						        get_dir_entry(
						                mode='season_episodes',
						                season_id=favorite_item['season_id'],
						                metadata=season_metadata,
						                override_fanart=default_fanart,
						        ))

		elif favorite_item.get('tv_show_id', None) is not None:
			tvshow_data = lib_joyn().get_graphql_response('SEASONS', {
					'path': favorite_item['path'],
					'licenseFilter': lib_joyn().get_license_filter()
			})
			if tvshow_data.get('page') is not None and tvshow_data.get('page').get('series', None) is not None:
				list_items.extend(get_list_items([tvshow_data.get('page').get('series')], additional_metadata=add_meta, override_fanart=default_fanart))

		elif favorite_item.get('block_id', None) is not None:
			block_data = lib_joyn().get_graphql_response('LANDINGBLOCKS', {'ids': [favorite_item['block_id']]})
			if block_data is not None and block_data.get('blocks', None) is not None:
				for block in block_data.get('blocks'):
					if favorite_item['block_id'] == block.get('id'):
						list_items.append(
						        get_dir_entry(metadata={
						                'infoLabels': {
						                        'title': compat._format('{}: {}',
						                                                xbmc_helper().translation('CATEGORY'), block.get('headline')),
						                        'plot': ''
						                },
						                'art': {}
						        },
						                      mode='category',
						                      viewtype='TV_SHOWS' if block.get('__typename') != 'LiveLane' else 'LIVE_TV',
						                      block_id=block.get('id')))
						break

		elif favorite_item.get('channel_id', None) is not None:
			channel_data = lib_joyn().get_graphql_response('CHANNEL', {'path': favorite_item.get('channel_path')})
			if channel_data.get('page') is not None and channel_data.get('page') is not None:
				list_items.extend(get_list_items([channel_data.get('page')], additional_metadata=add_meta, override_fanart=default_fanart))

		elif favorite_item.get('collection_id', None) is not None:
			block_data = lib_joyn().get_graphql_response('LANDINGBLOCKS', {'ids': [favorite_item['parent_block_id']]})
			if block_data is not None and block_data.get('blocks', None) is not None:
				for block in block_data['blocks']:
					for asset in block['assets']:
						if favorite_item['collection_id'] == asset.get('id'):
							list_items.extend(get_list_items([asset], additional_metadata=add_meta, override_fanart=default_fanart))
							break

		elif favorite_item.get('compilation_id', None) is not None:
			compilation_data = lib_joyn().get_graphql_response('COMPILATION', {'path': favorite_item['compilation_path']})
			if compilation_data.get('page') is not None and compilation_data.get('page', {}).get('compilation', None) is not None:
				compilation_data['page']['compilation'].update({'path': compilation_data['page']['path']})
				list_items.extend(
				        get_list_items([compilation_data['page']['compilation']], additional_metadata=add_meta, override_fanart=default_fanart))

	if len(list_items) == 0:
		from xbmcplugin import endOfDirectory
		endOfDirectory(handle=pluginhandle, succeeded=False)
		return xbmc_helper().notification(xbmc_helper().translation('WATCHLIST'),
		                                  xbmc_helper().translation('MSG_NO_FAVS_YET'), default_icon)

	addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
	addSortMethod(pluginhandle, SORT_METHOD_LABEL)
	addSortMethod(pluginhandle, SORT_METHOD_DATEADDED)

	xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'WATCHLIST', title)


def add_joyn_bookmark(asset_id, default_icon):

	add_joyn_bookmark_res = lib_joyn().get_graphql_response('ADD_BOOKMARK', {'assetId': asset_id})
	executebuiltin("Container.Refresh")
	return xbmc_helper().notification(
	        xbmc_helper().translation('JOYN_BOOKMARKS'),
	        xbmc_helper().translation('MSG_JOYN_BOOKMARK_ADD_SUCC' if add_joyn_bookmark_res.get('setBookmark', '') != '' else
	                                  'MSG_JOYN_BOOKMARK_ADD_FAIL'), default_icon)


def remove_joyn_bookmark(asset_id, default_icon):

	del_bookmark_res = lib_joyn().get_graphql_response('DEL_BOOKMARK', {'assetId': asset_id})
	executebuiltin("Container.Refresh")
	return xbmc_helper().notification(
	        xbmc_helper().translation('JOYN_BOOKMARKS'),
	        xbmc_helper().translation('MSG_JOYN_BOOKMARK_DEL_SUCC' if del_bookmark_res.get('removeBookmark', False) is True else
	                                  'MSG_JOYN_BOOKMARK_DEL_FAIL'), default_icon)


def show_joyn_bookmarks(title, pluginurl, pluginhandle, pluginquery, default_icon, default_fanart):

	from ..plugin import get_list_items
	from xbmcplugin import addSortMethod, SORT_METHOD_UNSORTED, SORT_METHOD_LABEL

	list_items = []

	landingpage = deepcopy(lib_joyn().get_landingpage('/fuer-dich'))

	blocks = landingpage.get('page').get('blocks')
	blocks.extend(landingpage.get('page').get('lazyBlocks'))

	for block in blocks:
		if block.get('__typename') == 'BookmarkLane':
			bookmark_lane = lib_joyn().get_graphql_response('LANEBOOKMARK', {'blockId': block['id']})
			if bookmark_lane.get('block', None) is not None and bookmark_lane.get('block').get('assets', None) is not None:
				list_items.extend(get_list_items(bookmark_lane['block']['assets'], override_fanart=default_fanart))

	if len(list_items) == 0:
		from xbmcplugin import endOfDirectory
		endOfDirectory(handle=pluginhandle, succeeded=False)

		return xbmc_helper().notification(xbmc_helper().translation('JOYN_BOOKMARKS'),
		                                  xbmc_helper().translation('MSG_NO_CONTENT'), default_icon)

	addSortMethod(pluginhandle, SORT_METHOD_UNSORTED)
	addSortMethod(pluginhandle, SORT_METHOD_LABEL)
	xbmc_helper().set_folder(list_items, pluginurl, pluginhandle, pluginquery, 'TV_SHOWS', title)
