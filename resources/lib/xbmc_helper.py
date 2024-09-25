# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from io import open as io_open
from os.path import exists, join
from time import mktime
from xbmc import executeJSONRPC, executebuiltin, getCondVisibility, getInfoLabel, getSkinDir, log, \
    sleep as xbmc_sleep, LOGERROR, LOGDEBUG
from xbmcplugin import setContent, endOfDirectory, addDirectoryItems, setPluginCategory
from xbmcvfs import mkdirs, exists, listdir, delete
from xbmcgui import Dialog, NOTIFICATION_ERROR
from .external.singleton import Singleton
from . import compat as compat
from .const import CONST

if compat.PY2:
    from xbmc import translatePath, LOGNOTICE
    from urlparse import parse_qs
    try:
        from simplejson import loads, dumps
    except ImportError:
        from json import loads, dumps

elif compat.PY3:
    from xbmc import LOGINFO as LOGNOTICE
    from xbmcvfs import translatePath
    from urllib.parse import parse_qs
    from json import loads, dumps


class xbmc_helper(Singleton):


    def __init__(self):
        self.addon = None
        self.addon_version = None
        self.prop_cache = {}
        self.addon_params = None
        self.android_properties = {}
        self.kodi_version = None

        debug_rpc_res = self.json_rpc(method='Settings.GetSettingValue', params={'setting': 'debug.showloginfo'})
        if debug_rpc_res is not None and debug_rpc_res.get('value', False) is True:
            self.kodi_debug = True
        else:
            self.kodi_debug = False

        try:
            from xbmcaddon import Addon
            _kodi_python_version = Addon('xbmc.python').getAddonInfo('version')
            self.log_debug('Detected kodi.python version {}', _kodi_python_version)
        except Exception as e:
            self.log_notice('Could not detect kodi.python version: {}', e)
            pass

        try:
            _kodi_version = getInfoLabel('System.BuildVersion')
            self.log_debug('Detected kodi version: {}', _kodi_version)
            self.kodi_version = int(_kodi_version.split('.')[0])
        except Exception as e:
            self.log_notice('Could not detect kodi version version: {}', e)
            pass


    def __del__(self):
        self.addon = None


    def get_addon(self):

        if self.addon is None:
            from xbmcaddon import Addon
            self.addon = Addon()

        return self.addon


    def set_addon(self, addon):
        self.addon = addon


    def get_file_path(self, directory, filename):

        xbmc_profile_path = translatePath(self.get_addon().getAddonInfo('profile')).encode('utf-8').decode('utf-8')
        xbmc_directory = translatePath(join(xbmc_profile_path, directory, '')).encode('utf-8').decode('utf-8')

        if not exists(xbmc_directory):
            mkdirs(xbmc_directory)

        return translatePath(join(xbmc_directory, filename)).encode('utf-8').decode('utf-8')


    def get_resource_filepath(self, filename, subdir):
        return translatePath(join(self.get_addon().getAddonInfo('path'), 'resources', subdir,
                                          filename)).encode('utf-8').decode('utf-8')


    def get_media_filepath(self, filename):
        return self.get_resource_filepath(filename, 'media')


    def remove_dir(self, directory):

        xbmc_profile_path = translatePath(self.get_addon().getAddonInfo('profile')).encode('utf-8').decode('utf-8')
        xbmc_directory = translatePath(join(xbmc_profile_path, directory)).encode('utf-8').decode('utf-8')

        remove_ok = 1

        dirs, files = listdir(xbmc_directory)
        for _file in files:
            remove_ok = delete(join(xbmc_directory, _file))

        for directory in dirs:
            if directory != '.' and directory != '..':
                directory = directory.decode("utf-8")
                remove_ok = self.remove_dir(join(xbmc_directory, directory))

        return remove_ok == 1


    def json_rpc(self, method, params, id='1'):
        try:
            rpc_cmd = {'jsonrpc': '2.0', 'method': method, 'params': params, 'id': id}

            rpc_res = loads(executeJSONRPC(dumps(rpc_cmd)))

            if not isinstance(rpc_res, dict) or 'error' in rpc_res.keys() or 'result' not in rpc_res.keys():
                raise ValueError(compat._format('JSONRPC Command failed - result is: {}', rpc_res))

            return rpc_res.get('result')

        except Exception as e:
            self.log_error('Failed to execute json rpc command: {} with exception: {}', rpc_cmd, e)
            pass


    def addon_enabled(self, addon_id):

        rpc_res = self.json_rpc(method='Addons.GetAddonDetails', params={'addonid': addon_id, "properties": ["enabled"]})
        return rpc_res is not None and rpc_res.get('addon', {}).get('enabled') is True


    def get_setting(self, setting_id):
        return self.get_addon().getSetting(setting_id)


    def get_bool_setting(self, setting_id):
        return self.get_setting(setting_id) == 'true'


    def get_int_setting(self, setting_id):
        setting_val = self.get_setting(setting_id)
        if setting_val.isdigit():
            return int(setting_val, 10)
        else:
            return None


    def get_text_setting(self, setting_id):
        return str(self.get_setting(setting_id))


    def get_addon_version(self):
        if self.addon_version is None:
            self.addon_version = compat._format('{} - {}', self.get_addon().getAddonInfo('id'), self.get_addon().getAddonInfo('version'))

        return self.addon_version


    def notification(self, msg, description, icon=NOTIFICATION_ERROR):
        if icon == NOTIFICATION_ERROR:
            time = 10000
        else:
            time = 3000

        return Dialog().notification(msg, description, icon, time)


    def dialog(self, msg, msg_line2=None, msg_line3=None, header_appendix=None, open_settings_on_ok=False):
        if header_appendix is not None:
            header = compat._format('{} - {}', str(header_appendix), self.get_addon().getAddonInfo('name'))
        else:
            header = self.get_addon().getAddonInfo('name')

        ret = Dialog().ok(header, xbmc_helper.dialog_msg(msg, msg_line2, msg_line3))

        if open_settings_on_ok is True and ret == 1:
            self.get_addon().openSettings()

        return ret


    def dialog_action(self,
                      msg,
                      msg_line2=None,
                      msg_line3=None,
                      header_appendix=None,
                      yes_label_translation='OPEN_ADDON_SETTINGS',
                      ok_addon_parameters=None,
                      cancel_label_translation='CANCEL',
                      cancel_addon_parameters=None):

        if header_appendix is not None:
            header = compat._format('{} - {}', str(header_appendix), self.get_addon().getAddonInfo('name'))
        else:
            header = self.get_addon().getAddonInfo('name')

        dialog_res = Dialog().yesno(header,
                                    xbmc_helper.dialog_msg(msg, msg_line2, msg_line3),
                                    nolabel=self.translation(cancel_label_translation),
                                    yeslabel=self.translation(yes_label_translation))
        if dialog_res:
            if ok_addon_parameters is not None:
                executebuiltin(compat._format('RunPlugin(plugin://{}?{})', self.get_addon().getAddonInfo('id'), ok_addon_parameters))
            else:
                self.get_addon().openSettings()

        elif cancel_addon_parameters is not None:
            executebuiltin(compat._format('RunPlugin(plugin://{}?{})', self.get_addon().getAddonInfo('id'), cancel_addon_parameters))


    def dialog_id(self, id):
        return self.dialog(self.translation(id))


    @staticmethod
    def dialog_msg(msg, msg_line2=None, msg_line3=None):
        _msg = msg
        if msg_line2 is not None:
            _msg = compat._format('{}[CR]{}', _msg, msg_line2)
        if msg_line3 is not None:
            _msg = compat._format('{}[CR]{}', _msg, msg_line3)

        return _msg


    def set_folder(self, list_items, pluginurl, pluginhandle, pluginquery, folder_type, title=None):

        folder_defs = CONST['FOLDERS'].get(folder_type)
        old_pluginurl = getInfoLabel('Container.FolderPath')
        old_postion = getInfoLabel('Container.CurrentItem')

        addDirectoryItems(pluginhandle, list_items, len(list_items))

        if title is not None:
            setPluginCategory(pluginhandle, title)

        if 'content_type' in folder_defs.keys():
            self.log_debug('set_folder: set content_type: {}', folder_defs['content_type'])
            setContent(pluginhandle, folder_defs['content_type'])
        endOfDirectory(handle=pluginhandle,
                       cacheToDisc=(folder_defs.get('cacheable', False) and (self.get_bool_setting('disable_foldercache') is False)))

        self.wait_for_infolabel('Container.FolderPath', compat._format('{}{}', pluginurl, pluginquery))

        if 'view_mode' in folder_defs.keys():
            self.set_view_mode(folder_defs['view_mode'])

        if 'sort' in folder_defs.keys():
            self.set_folder_sort(folder_defs['sort'])

        # reset the postion to the last "known" if it is gt 1, if pluginurls matching -> likely to be a 'refresh'
        if getInfoLabel('Container.FolderPath') == old_pluginurl and old_postion.isdigit() and int(old_postion) > 1:
            from xbmcgui import Window, getCurrentWindowId, getCurrentWindowDialogId

            # wait untl all Dialogs are closed; 10099 => WINDOW_DIALOG_POINTER => smallest dialog_id; max 500 msecs
            dialog_wait_counter = 0
            while dialog_wait_counter <= 100 and getCurrentWindowDialogId() >= 10099:
                xbmc_sleep(5)
                dialog_wait_counter += 1
            self.log_debug('waited {} msecs for all dialogs to be closed', (dialog_wait_counter * 5))

            self.log_debug('FolderPath old pos {} ', old_postion)
            focus_id = Window(getCurrentWindowId()).getFocusId()
            set_postion = old_postion

            cmd = compat._format('Control.SetFocus({},{})', focus_id, set_postion)
            executebuiltin(cmd)
            self.log_debug('set current pos executebuiltin({})', cmd)

            # wait for the correct postion to be applied; max 500 msecs
            self.wait_for_infolabel('Container.CurrentItem', old_postion, cycles=100)


    def set_folder_sort(self, folder_sort_def):

        order = self.get_setting(folder_sort_def['setting_id'])
        self.log_debug('set_folder_sort {}: {}', folder_sort_def, order)

        if order != CONST['SETTING_VALS']['SORT_ORDER_DEFAULT']:
            executebuiltin(compat._format('Container.SetSortMethod({:s})', str(folder_sort_def['order_type'])))

            if (order == CONST['SETTING_VALS']['SORT_ORDER_DESC'] and
                (getInfoLabel('Container.SortOrder').lower() == self.translation('ASCENDING_LABEL')
                 or str(getCondVisibility('Container.SortDirection(ascending)')) == '1')) or (
                         order == CONST['SETTING_VALS']['SORT_ORDER_ASC'] and
                         (getInfoLabel('Container.SortOrder').lower() == self.translation('DESCENDING_LABEL')
                          or str(getCondVisibility('Container.SortDirection(descending)')) == '1')):
                self.log_debug('Toggle sort')
                executebuiltin('Container.SetSortDirection')


    def set_view_mode(self, setting_id):

        skin_name = str(getSkinDir())
        if self.get_bool_setting('enable_viewmodes') is True:

            setting_val = self.get_setting(setting_id)
            if setting_val == 'Custom':
                viewmode = self.get_setting(compat._format('{}_custom', setting_id))
            else:
                viewmode = CONST['VIEW_MODES'].get(setting_val, {}).get(skin_name, '0')

            self.log_debug('Viewmode :{}:{}:{}:{}', setting_id, setting_val, viewmode, skin_name)

            if viewmode != '0':
                executebuiltin(compat._format('Container.SetViewMode({})', viewmode))
                self.wait_for_infolabel('Container.Viewmode', setting_val)


    def wait_for_infolabel(self, label_name, expected_value, sleep_msecs=5, cycles=1000):

        # sadly it's necessary to wait until kodi has the new Container infolabel ...
        label_value = ''
        counter = 0

        while counter <= cycles:
            counter += 1
            xbmc_sleep(sleep_msecs)
            label_value = str(getInfoLabel(label_name))
            if label_value == expected_value:
                break

        self.log_debug('wait_for_infolabel {}: msecs waited: {} values do match {} final value {}', label_name,
                       (counter * sleep_msecs), (expected_value == label_value), label_value)


    def log_error(self, format, *args):
        self._log(compat._format(format, *args), LOGERROR)


    def log_notice(self, format, *args):
        self._log(compat._format(format, *args), LOGNOTICE)


    def log_debug(self, format, *args):
        if self.get_bool_setting('debug_mode') is True:
            self.log_notice(format, *args)
        elif self.kodi_debug is True:
            self._log(compat._format(format, *args), LOGDEBUG)


    def _log(self, msg, level=LOGNOTICE):
        log(compat._encode(compat._format('[{}] {}', self.get_addon_version(), msg)), level)


    def translation(self, id):
        return compat._encode(self.get_addon().getLocalizedString(CONST['MSG_IDS'][id]))


    def get_addon_params(self, pluginquery):
        self.addon_params = dict((k, v if len(v) > 1 else v[0]) for k, v in parse_qs(pluginquery[1:]).items())
        return self.addon_params


    def get_file_contents(self, file_path):
        data = None
        if exists(file_path):
            with io_open(file=file_path, mode='r', encoding='utf-8') as data_infile:
                data = data_infile.read()
        return data


    def get_data(self, filename, dir_type='DATA_DIR'):
        data_file_path = self.get_file_path(CONST[dir_type], filename)
        return self.get_file_contents(data_file_path)


    def set_data(self, filename, data, dir_type='DATA_DIR'):
        data_file_path = self.get_file_path(CONST[dir_type], filename)

        with io_open(file=data_file_path, mode='w', encoding='utf-8') as data_outfile:
            data_outfile.write(compat._decode(compat._unicode(data)))

        return data_file_path


    def del_data(self, filename, dir_type='DATA_DIR'):
        data_file_path = self.get_file_path(CONST[dir_type], filename)
        if exists(data_file_path):
            delete(data_file_path)


    def get_json_data(self, filename, dir_type='DATA_DIR'):
        data = self.get_data(filename, dir_type)

        if data is not None:
            try:
                data = loads(data)
            except ValueError:
                log(compat._format('Could not decode data as json {} ', filename))
                pass

        return data


    def set_json_data(self, filename, data, dir_type='DATA_DIR'):
        return self.set_data(filename, dumps(data), dir_type)


    def timestamp_to_datetime(self, timestamp, is_utc=False):
        try:

            if is_utc is True:
                dt = datetime.utcfromtimestamp(0) + timedelta(seconds=int(timestamp))
            else:
                dt = datetime.fromtimestamp(0) + timedelta(seconds=int(timestamp))

            return dt - timedelta(hours=datetime.timetuple(dt).tm_isdst)

        except Exception as e:

            self.log_notice('Could not convert timestamp {} to datetime - Exception: {}', timestamp, e)
            pass

        return False


    def get_android_prop(self, key, exact_match=False):

        if getCondVisibility('System.Platform.Android'):
            if len(self.android_properties.keys()) == 0:
                try:
                    from subprocess import check_output
                    prop_output = check_output(['/system/bin/getprop']).splitlines()
                    for prop in prop_output:
                        prop = compat._decode(prop)
                        prop_k_v = prop.split(']: [')
                        if len(prop_k_v) == 2 and prop_k_v[0].startswith('[') and prop_k_v[1].endswith(']'):
                            self.android_properties.update({prop_k_v[0][1:]: prop_k_v[1][:-1]})
                    self.log_debug('Found android properties {}', self.android_properties)
                except Exception as e:
                    self.log_error('Getting android properties failed with exception: {}', e)

            if exact_match is True and self.android_properties.get(key, None) is not None:
                return self.android_properties.get(key)
            else:
                for prop_key, prop_value in self.android_properties.items():
                    if prop_key.find(key) != -1:
                        return prop_value

            if exact_match is True:
                try:
                    from subprocess import check_output
                    prop_output = check_output(['/system/bin/getprop', key]).splitlines()
                    if len(prop_output) == 1 and len(prop_output) != 0:
                        prop = compat._decode(prop_output[0])
                        self.android_properties.update({key: prop})
                        return prop
                except Exception as e:
                    self.log_error('Getting android property {} with exception: {}', key, e)


    def set_videoinfo(self, listitem, infolabels):

        if self.kodi_version >= 20:
            videoinfotag = listitem.getVideoInfoTag()

            if infolabels.get('title') is not None:
                videoinfotag.setTitle(infolabels.get('title'))
            if infolabels.get('plot') is not None:
                videoinfotag.setPlot(infolabels.get('plot'))
            if infolabels.get('mpaa') is not None:
                videoinfotag.setMpaa(infolabels.get('mpaa'))
            if infolabels.get('genre') is not None:
                videoinfotag.setGenres(infolabels.get('genre'))
            if infolabels.get('studio') is not None:
                videoinfotag.setStudios(infolabels.get('studio'))
            if infolabels.get('episode') is not None:
                videoinfotag.setEpisode(infolabels.get('episode'))
            if infolabels.get('sortepisode') is not None:
                videoinfotag.setSortEpisode(infolabels.get('sortepisode'))
            if infolabels.get('tvshowtitle') is not None:
                videoinfotag.setTvShowTitle(infolabels.get('tvshowtitle'))
            if infolabels.get('premiered') is not None:
                videoinfotag.setPremiered(infolabels.get('premiered'))
            if infolabels.get('date') is not None:
                videoinfotag.setDateAdded(infolabels.get('date'))
            if infolabels.get('aired') is not None:
                videoinfotag.setFirstAired(infolabels.get('aired'))
            if infolabels.get('duration') is not None:
                videoinfotag.setDuration(infolabels.get('duration'))
            if infolabels.get('season') is not None:
                videoinfotag.setSeason(infolabels.get('season'))
            if infolabels.get('sortseason') is not None:
                videoinfotag.setSortSeason(infolabels.get('sortseason'))
            if infolabels.get('tagline') is not None:
                videoinfotag.setTagLine(infolabels.get('tagline'))
            if infolabels.get('mediatype') is not None:
                videoinfotag.setMediaType(infolabels.get('mediatype'))
        else:
            listitem.setInfo('video', infolabels)

        return listitem

