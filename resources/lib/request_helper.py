# -*- coding: utf-8 -*-

from io import BytesIO
from gzip import GzipFile
from sys import exit
from time import time
from hashlib import sha512
from datetime import datetime, timedelta
from copy import deepcopy
from .xbmc_helper import xbmc_helper as xbmc_helper
from . import cache as cache
from . import compat as compat

if compat.PY2:
    from urllib import quote, urlencode
    from urllib2 import Request, urlopen, HTTPError, ProxyHandler, build_opener, install_opener, HTTPCookieProcessor
    from cookielib import MozillaCookieJar, LoadError
    try:
        from simplejson import loads, dumps
    except ImportError:
        from json import loads, dumps

elif compat.PY3:
    from urllib.parse import quote, urlencode
    from urllib.request import Request, urlopen, ProxyHandler, build_opener, install_opener, HTTPCookieProcessor
    from urllib.error import HTTPError
    from http.cookiejar import MozillaCookieJar, LoadError
    from json import loads, dumps


def get_url(url,
            config,
            method='GET',
            additional_headers=None,
            additional_query_string=None,
            post_data=None,
            fail_silent=False,
            no_cache=False,
            return_json_errors=[],
            return_final_url=False,
            cookie_file=None):

    response_content = ''
    request_hash = sha512(
            (url + dumps(additional_headers) + dumps(additional_query_string) + dumps(post_data)).encode('utf-8')).hexdigest()

    final_url = url

    if xbmc_helper().get_bool_setting('debug_requests') is True:
        xbmc_helper().log_debug(
                'get_url - url: {} method {} headers {} query {} post {} no_cache {} silent {} request_hash {} return_json_errors {}, cookie_file {}',
                url, method, additional_headers, additional_query_string, post_data, no_cache, fail_silent, request_hash, return_json_errors,
                cookie_file)

    if no_cache is True:
        etags_data = None
    else:
        etags_data = get_etags_data(request_hash)

    try:

        headers = {
                'Accept-Encoding': 'gzip, deflate',
                'User-Agent': config['USER_AGENT'],
                'Accept': '*/*',
        }

        if additional_headers is not None:
            headers.update(additional_headers)

        if config.get('http_headers', None) is not None:
            headers.update(config.get('http_headers', []))

        if etags_data is not None:
            headers.update({'If-None-Match': etags_data['etag']})

        if additional_query_string is not None:
            _url = compat._format('{}{}{}', url, '?' if url.find('?') == -1 else '&', urlencode(additional_query_string))
            url = _url
        if post_data and isinstance(post_data, dict):
            post_data = urlencode(post_data)

        cookie_processor = None
        cookie_jar = None
        if cookie_file is not None:
            cookie_jar = MozillaCookieJar(cookie_file)
            try:
                cookie_jar.load()
            except LoadError:
                xbmc_helper().log_debug('Failed to load from cookiefile {} with error {} - new session?', cookie_file, LoadError.strerror)
                pass
            cookie_processor = HTTPCookieProcessor(cookie_jar)

        if xbmc_helper().get_bool_setting('use_https_proxy') is True and xbmc_helper().get_text_setting(
                'https_proxy_host') != '' and xbmc_helper().get_int_setting('https_proxy_port') != 0:

            proxy_uri = compat._format('{}:{}',
                                       xbmc_helper().get_text_setting('https_proxy_host'),
                                       xbmc_helper().get_text_setting('https_proxy_port'))

            xbmc_helper().log_debug('Using proxy uri {}', proxy_uri)
            prxy_handler = ProxyHandler({
                    'http': proxy_uri,
                    'https': proxy_uri,
            })
            if cookie_processor is None:
                install_opener(build_opener(prxy_handler))
            else:
                install_opener(build_opener(prxy_handler, cookie_processor))

        elif cookie_processor is not None:
            install_opener(build_opener(cookie_processor))

        if post_data is not None or method == 'POST':
            if post_data:
                request = Request(url, data=post_data.encode('utf-8'), headers=headers)
            else:
                request = Request(url, headers=headers, method='POST')
        else:
            request = Request(url, headers=headers)

        response = urlopen(request, timeout=40)

        if response.info().get('Content-Encoding') == 'gzip':
            response_content = compat._decode(GzipFile(fileobj=BytesIO(response.read())).read())
        else:
            response_content = compat._decode(response.read())

        if cookie_jar is not None:
            cookie_jar.save()

        final_url = response.geturl()
        _etag = response.info().get('etag', None)
        if no_cache is False and _etag is not None:
            set_etags_data(request_hash, _etag, response_content)

    except HTTPError as http_error:

        if http_error.code == 304 and etags_data.get('data', None) is not None:
            response_content = etags_data.get('data')
        else:
            try:
                if http_error.info().get('Content-Encoding') == 'gzip':
                    error_body = compat._decode(GzipFile(fileobj=BytesIO(http_error.read())).read())
                else:
                    error_body = compat._decode(http_error.read())

                xbmc_helper().log_debug('HTTP ERROR: {}', error_body)
                json_errors = loads(error_body)
                xbmc_helper().log_debug('JSON ERRORS: {}', json_errors)

                has_decoded_error = False
                if isinstance(json_errors, dict) and 'errors' not in json_errors.keys() and 'code' in json_errors.keys():
                    json_errors = {'errors': [json_errors]}
                elif isinstance(json_errors, list) and len(json_errors) == 1 and isinstance(json_errors[0], dict):
                    json_errors = {'errors': json_errors}
                err_str = str(http_error.code)
                return_errors = []

                if isinstance(json_errors, dict):
                    for error in json_errors.get('errors', []):
                        if 'msg' in error.keys():
                            err_str = compat._format('{}|{}', err_str, error.get('msg'))
                            has_decoded_error = True
                        if 'code' in error.keys() and error['code'] in return_json_errors:
                            return_errors.append(error['code'])
                            has_decoded_error = True

                xbmc_helper().log_debug('return_json_errors {}', return_errors)

                if len(return_errors) > 0:
                    response_content = dumps({'json_errors': return_errors})

                elif has_decoded_error is True:
                    xbmc_helper().notification(
                            'Error',
                            err_str,
                    )
                    exit(0)

            except Exception:
                raise http_error

    except Exception as e:
        xbmc_helper().log_error('Failed to load url: {} headers {} post_data {} - Exception: {}', url, headers, post_data, e)

        if fail_silent is True:
            pass
        else:
            xbmc_helper().notification(compat._format(xbmc_helper().translation('ERROR'), 'URL Access'),
                                       compat._format(xbmc_helper().translation('MSG_NO_ACCESS_TO_URL'), str(url)))
            exit(0)

    if return_final_url:
        return final_url, response_content

    return response_content


def post_json(url,
              config,
              data=None,
              additional_headers=[],
              additional_query_string=None,
              no_cache=False,
              silent=False,
              return_json_errors=[],
              cookie_file=None):

    additional_headers.append(('Content-Type', 'application/json'))
    return get_json_response(url=url,
                             config=config,
                             method='POST',
                             headers=additional_headers,
                             params=additional_query_string,
                             post_data=dumps(data) if data else None,
                             no_cache=no_cache,
                             silent=silent,
                             return_json_errors=return_json_errors,
                             cookie_file=cookie_file)


def get_json_response(url,
                      config,
                      method='GET',
                      headers=[],
                      params=None,
                      post_data=None,
                      silent=False,
                      no_cache=False,
                      return_json_errors=[],
                      cookie_file=None):

    try:
        headers.append(('Accept', 'application/json'))
        return loads(
                get_url(url=url,
                        config=config,
                        method=method,
                        additional_headers=headers,
                        additional_query_string=params,
                        post_data=post_data,
                        fail_silent=silent,
                        no_cache=no_cache,
                        return_json_errors=return_json_errors,
                        cookie_file=cookie_file))

    except ValueError:
        if silent is False:
            xbmc_helper().notification(compat._format(xbmc_helper().translation('ERROR'), 'Decoding'),
                                       xbmc_helper().translation('MSG_ERR_TRY_AGAIN'))
            pass
        else:
            raise

    return None


def get_header_string(headers):

    header_string = ''
    for header_key, header_value in headers.items():
        header_string += compat._format('&{}={}', quote(header_key), quote(header_value))

    return header_string[1:]


def base64_encode_urlsafe(string):

    from base64 import urlsafe_b64encode

    if compat.PY2:
        encoded = urlsafe_b64encode(string)
        return encoded.rstrip(b'=').encode('utf-8').decode('utf-8')
    else:
        return urlsafe_b64encode(string.encode('utf-8')).decode('utf-8')


def get_etags_data(request_hash):

    etags_data = cache.get_json('ETAGS').get('data')
    if etags_data is None:
        etags_data = {}

    etag_data = etags_data.get(request_hash, None)
    if etag_data is not None:
        etags_data[request_hash].update({'access': int(time())})
        cache.set_json('ETAGS', etags_data)
        data = cache._get('ETAGS', request_hash + '.etag').get('data', None)
        if data is not None:
            etag_data.update({'data': data})
            return etag_data
    return None


def set_etags_data(request_hash, etag, data):

    etags_data = cache.get_json('ETAGS').get('data', {})
    if etags_data is None:
        etags_data = {}

    etags_data.update({request_hash: {'etag': etag, 'access': int(time())}})
    cache._set('ETAGS', request_hash + '.etag', data)
    cache.set_json('ETAGS', etags_data)


def purge_etags_cache(ttl):

    etags_ttl = datetime.now() - timedelta(seconds=ttl)
    xbmc_helper().log_debug('Removing etags older than: {}', etags_ttl)

    etags_data = cache.get_json('ETAGS').get('data')
    if etags_data is not None:
        _etags_data_cpy = deepcopy(etags_data)
        for request_hash, etag_data in etags_data.items():
            if xbmc_helper().timestamp_to_datetime(etags_data.get(request_hash, {}).get('access', 0)) <= etags_ttl:
                xbmc_helper().log_debug('Removing etags hash: {}', request_hash)
                cache._remove('ETAGS', request_hash + '.etag')
                del _etags_data_cpy[request_hash]

        cache.set_json('ETAGS', _etags_data_cpy)
