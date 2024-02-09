# -*- coding: utf-8 -*-

from xbmc import getCondVisibility
from ..xbmc_helper import xbmc_helper
from .. import compat
from ..lib_joyn import lib_joyn

if compat.PY2:
	try:
		from simplejson import loads, dumps
	except ImportError:
		from json import loads, dumps
elif compat.PY3:
	from json import loads, dumps


def login(username=None, dont_check_account=False, failed=False, no_account_dialog=False):

	from xbmc import executebuiltin
	from xbmcgui import Dialog, INPUT_ALPHANUM, ALPHANUM_HIDE_INPUT

	autologin = False
	password = None

	if dont_check_account is False and lib_joyn().get_auth_token().get('has_account', False) is True:
		if no_account_dialog is False:
			executebuiltin('ActivateWindow(busydialognocancel)')
			account_info = lib_joyn().get_account_info(True)
			xbmc_helper().dialog(
			        msg=compat._format(xbmc_helper().translation('LOGGED_IN_LABEL'),
			                           account_info.get('me', {}).get('profile', {}).get('email', '')),
			        msg_line2=compat._format(
			                xbmc_helper().translation('ACCOUNT_INFO_LABEL'),
			                xbmc_helper().translation('NO_LABEL') if lib_joyn().get_account_subscription_config('hasActivePlus') is False
			                else xbmc_helper().translation('YES_LABEL'),
			                xbmc_helper().translation('NO_LABEL') if lib_joyn().get_account_subscription_config('hasActiveHD') is False
			                else xbmc_helper().translation('YES_LABEL')))
			return executebuiltin('Dialog.Close(busydialognocancel)')
		else:
			lib_joyn().get_account_info(True)
			return

	elif failed is False and xbmc_helper().get_bool_setting('save_encrypted_auth_data') is True:
		auth_data = get_auth_data()
		if isinstance(auth_data, dict) and 'username' in auth_data.keys() and 'password' in auth_data.keys():
			xbmc_helper().log_debug('Successfully received decrypted auth data')
			username = auth_data.get('username')
			password = auth_data.get('password')
			autologin = True

	if username is None:
		executebuiltin('Dialog.Close(all, true)')
		_username = Dialog().input(compat._unicode(xbmc_helper().translation('USERNAME_LABEL')), type=INPUT_ALPHANUM)
		if len(_username) > 0:
			from re import match as re_match
			if re_match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", _username) is not None:
				username = _username
			else:
				xbmc_helper().notification('Login', xbmc_helper().translation('MSG_INVALID_EMAIL'), lib_joyn().default_icon)
		else:
			return xbmc_helper().dialog_action(msg=compat._unicode(xbmc_helper().translation('LOGIN_FAILED_LABEL')),
			                                   yes_label_translation='RETRY',
			                                   cancel_label_translation='CONTINUE_ANONYMOUS',
			                                   ok_addon_parameters='mode=login&failed=true',
			                                   cancel_addon_parameters='mode=logout&dont_check_account=true')

		if username is None:
			return login(dont_check_account=dont_check_account, failed=failed, no_account_dialog=no_account_dialog)

	if password is None:
		executebuiltin('Dialog.Close(all, true)')
		_password = Dialog().input(compat._unicode(xbmc_helper().translation('PASSWORD_LABEL')),
		                           type=INPUT_ALPHANUM,
		                           option=ALPHANUM_HIDE_INPUT)

		if len(_password) >= 6:
			password = _password
		else:
			xbmc_helper().notification('Login', xbmc_helper().translation('MSG_INVALID_PASSWORD'), lib_joyn().default_icon)
			return login(username=username, dont_check_account=dont_check_account, failed=failed, no_account_dialog=no_account_dialog)

	if username is not None and password is not None:
		auth_token = lib_joyn().get_auth_token(username=username, password=password)
		if auth_token is False or auth_token.get('has_account', False) is False:
			return xbmc_helper().dialog_action(msg=compat._unicode(xbmc_helper().translation('LOGIN_FAILED_LABEL')),
			                                   yes_label_translation='RETRY',
			                                   cancel_label_translation='CONTINUE_ANONYMOUS',
			                                   ok_addon_parameters='mode=login&failed=true',
			                                   cancel_addon_parameters='mode=logout&dont_check_account=true')
		else:
			if autologin is False and xbmc_helper().get_bool_setting('save_encrypted_auth_data') is True:
				save_auth_data(username, password)
			login(no_account_dialog=False if autologin is False else True)
			executebuiltin("Container.Refresh")


def logout(dont_check_account=False):

	from xbmc import executebuiltin

	if dont_check_account is True:
		lib_joyn().get_auth_token(reset_anon=True)

		if lib_joyn().get_auth_token().get('has_account', False) is False:
			xbmc_helper().dialog(compat._unicode(xbmc_helper().translation('LOGOUT_OK_LABEL')))
			executebuiltin("Container.Refresh")
		else:
			xbmc_helper().dialog(compat._unicode(xbmc_helper().translation('LOGOUT_NOK_LABEL')))

	elif lib_joyn().get_auth_token().get('has_account', False) is True:
		xbmc_helper().log_debug('LOGOUT')
		lib_joyn().get_auth_token(logout=True)
		if lib_joyn().get_auth_token().get('has_account', False) is False:
			xbmc_helper().dialog(compat._unicode(xbmc_helper().translation('LOGOUT_OK_LABEL')))
			executebuiltin("Container.Refresh")
		else:
			xbmc_helper().dialog(compat._unicode(xbmc_helper().translation('LOGOUT_NOK_LABEL')))
	else:
		xbmc_helper().dialog(compat._unicode(xbmc_helper().translation('NOT_LOGGED_IN_LABEL')))


def encrypt_des(key, data):
	try:
		from Cryptodome.Cipher import DES3
		from Cryptodome.Util.Padding import pad
		from base64 import b64encode

		try:
			key_handle = DES3.new(key, DES3.MODE_CBC, iv=b'\0\0\0\0\0\0\0\0')
			encrypted = key_handle.encrypt(pad(data.encode('utf-8'), DES3.block_size))
			return b64encode(encrypted)
		except Exception as e:
			xbmc_helper().log_notice('DATA ENCRYPTION FAILED - {}', e)
			pass
			return False

	except ImportError as ie:
		xbmc_helper().log_notice('Could not import cryptodome: {}', ie)
		pass
		return False


def decrypt_des(key, encrypted_data):
	try:
		from Cryptodome.Cipher import DES3
		from Cryptodome.Util.Padding import unpad
		from base64 import b64decode

		try:
			key_handle = DES3.new(key, DES3.MODE_CBC, iv=b'\0\0\0\0\0\0\0\0')
			decrypted = unpad(key_handle.decrypt(b64decode(data)), DES3.block_size)
			return decrypted.decode('utf-8')
		except Exception as e:
			xbmc_helper().log_notice('DATA DECRYPTION FAILED - {}', e)
			pass
			return False

	except ImportError as ie:
		xbmc_helper().log_notice('Could not import pydes: {}', ie)
		pass
		return False


def save_auth_data(username, password):
	auth_data = dumps({'username': username, 'password': password})
	encrypted_auth_data = encrypt_des(key=get_device_uuid(prefix='JOYNAUTHDATA', return_bytes=True), data=auth_data)
	if encrypted_auth_data is not False:
		xbmc_helper().set_data('auth_data', encrypted_auth_data)
		return True
	else:
		xbmc_helper().log_notice('Failed to save encrypted auth data')
		return False


def get_auth_data():
	encrypted_auth_data = xbmc_helper().get_data('auth_data')

	if encrypted_auth_data is not None:
		decrypted_auth_data = decrypt_des(key=get_device_uuid(prefix='JOYNAUTHDATA', return_bytes=True),
		                                  encrypted_data=encrypted_auth_data)
		if decrypted_auth_data is not False:
			try:
				return loads(decrypted_auth_data)
			except Exception as e:
				xbmc_helper().log_notice('Could not load json data from decrypted auth_data - {}', e)
		else:
			xbmc_helper().log_notice('Could not decrypt auth_data')

	else:
		xbmc_helper().log_notice('Could not read auth_data')

	return False


def get_node_value():
	if getCondVisibility('System.Platform.Android') or getCondVisibility('System.Platform.Linux'):

		from subprocess import check_output

		if getCondVisibility('System.Platform.Android'):
			android_serial_no = xbmc_helper().get_android_prop('serialno', exact_match=False)
			if android_serial_no is not None and len(android_serial_no) != 0:
				xbmc_helper().log_debug('Got android serialno')
				return android_serial_no
			android_mac_addr = xbmc_helper().get_android_prop('macaddr', exact_match=False)
			if android_mac_addr is not None:
				android_mac_addr = android_mac_addr.replace(':', '').lower()
				if len(android_mac_addr) == 12 and android_mac_addr != ('0' * 12):
					xbmc_helper().log_debug('Got android macaddr')
					return android_mac_addr.replace(':', '')

		elif getCondVisibility('System.Platform.Linux'):
			try:
				machine_id_res = check_output(['/bin/cat', '/etc/machine-id']).splitlines()
				if isinstance(machine_id_res, list) and len(machine_id_res) == 1:
					xbmc_helper().log_debug('Got linux machine-id')
					return compat._decode(machine_id_res[0])

			except Exception as e:
				xbmc_helper().log_debug('Failed to get machine_id: {}', e)
				pass

		try:
			if getCondVisibility('System.Platform.Android'):
				exec_prefix = '/system'
			else:
				exec_prefix = ''

			interfaces = check_output([compat._format('{}/bin/ls', exec_prefix), '/sys/class/net/']).splitlines()
			for interface in interfaces:
				interface = compat._decode(interface)
				address_res = check_output(['{}/bin/cat'.format(exec_prefix),
				                            compat._format('/sys/class/net/{}/address', interface)]).splitlines()
				if isinstance(address_res, list) and len(address_res) == 1:
					node = compat._decode(address_res[0]).replace(':', '').lower()
					if len(node) == 12 and node != ('0' * 12):
						xbmc_helper().log_debug('Got macaddr from sysfs')
						return node

		except Exception as e:
			xbmc_helper().log_debug('Failed to get mac address from sysfs: {}', e)
			pass

		from uuid import getnode
		return '{:x}'.format(getnode())


def get_device_uuid(prefix='', random=False, return_bytes=False):

	if random is True:
		from random import getrandbits
		prefix = compat._format('{}{:x}', prefix, getrandbits(128))

	_uuid_str = compat._format('{}{}', str(prefix), lib_joyn().get_node())

	if compat.PY2 and str(xbmc_helper().get_android_prop('ro.hardware', exact_match=True)) == 'sun8iw7p1' and str(
	        xbmc_helper().get_android_prop('ro.build.version.sdk', exact_match=True)) == '24':
		xbmc_helper().log_debug('Matched bad device ... createing fake uuid')
		from hashlib import md5
		md5_sum = md5(_uuid_str.encode('utf-8'))
		if return_bytes is True:
			return md5_sum.digest()
		else:
			md5_sum_hex = md5_sum.hexdigest()
			fake_uuid = compat._format('{}-{}-{}-{}-{}', md5_sum_hex[0:8], md5_sum_hex[8:12], md5_sum_hex[12:16], md5_sum_hex[16:20],
			                           md5_sum_hex[20:])
			return fake_uuid

	from uuid import uuid5, NAMESPACE_DNS
	_uuid = uuid5(NAMESPACE_DNS, compat._encode(_uuid_str))

	if return_bytes is True:
		return _uuid.bytes

	return compat._format('{}', _uuid)
