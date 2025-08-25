"""
uuRest
===================================

Implementation of the main REST handler

import pip
from pip._internal import main as run_pip
from pip import main as run_pip
run_pip("install --upgrade pip".split(" "))
run_pip("install openpyxl".split(" "))

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

pip install wheel
in conda prompt change directory to c:/git/cams/toolkit/pypi/uurest
python setup.py sdist bdist_wheel
python -m pip install .
python setup.py sdist bdist_wheel && python -m pip install .

"""

from .uuRestLogin import uuRestLogin, uuRestLoginByToken, uuRestLoginGeneral, uuRestLoginEmpty
from .multipartEncoder import MultipartEncoder
from .uuCommon import (uuRestMethod, uuCharset, uuContentType, escape_text, convert_to_str, convert_to_dict,
                       dict_path_exists, dict_multiple_path_exists, dict_get_item_by_path)
from .uuCommand import uuCommand
from .uuStopwatch import Stopwatch

from typing import List, Dict
import requests
import urllib3
import json
from requests.auth import HTTPBasicAuth
from pathlib import Path


class BearerAuth(requests.auth.AuthBase):
    """
    Barer authentication
    """
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class uuRestException(Exception):
    def __init__(self, api_call_url: str, query: str, call_method: uuRestMethod, request, response, http_status_code):
        """
        Creates a Rest Exception
        :param request:
        :param response:
        """
        self.api_call_url = api_call_url
        self.query = query
        self.call_method = call_method
        self.request = request
        self.response = response
        self.http_status_code = http_status_code

    def __str__(self):
        result = f'Error when calling "{self.api_call_url}"\nusing query "{self.query}"\nMethod: "{self.call_method}"\nHttp code: "{self.http_status_code}"\n' \
                 f'Request was:\n{self.request}\nResponse was:\n{self.response}'
        return result


class uuRest:
    """
    class responsible to perform REST api calls
    """
    header_keyword = f'__header__'

    def __init__(self, login: uuRestLogin):
        """
        Initialize uuRest instance
        :param login: login class used to login to access REST api
        :param commands_url_prefix: optionally a prefix for the
        """
        self._login: uuRestLoginGeneral or uuRestLoginByToken or uuRestLoginEmpty = login
        self.stopwatch = Stopwatch()
        self.timeout = 120
        if type(self.login) == uuRestLoginByToken:
            self._token = self._login.token
            self._token_renew = 999999999
        elif type(self.login) == uuRestLoginGeneral:
            self._token = None
            self._token_renew = 0
            self._load_token()
        elif type(self.login) == uuRestLoginEmpty:
            self._token = None
            self._token_renew = 0
        else:
            raise Exception(f'Unkonown login method')

    @property
    def login(self):
        """
        Returns instance of uuRestLogin containing login information
        :return:
        """
        return self._login

    @property
    def token(self) -> str:
        """
        Returns currently valid token. If the token is not valid then the token is renewed
        :return:
        """
        if self.stopwatch.get_run_time_in_seconds() > self._token_renew:
            self._load_token()
        return self._token

    @token.setter
    def token(self, value: str):
        """
        Sets the token
        :param value:
        :return:
        """
        self._token = value

    def _load_token(self):
        """
        Loads token based on the login class
        :return:
        """
        if type(self._login) == uuRestLoginGeneral:
            self._load_token_general()
        # elif type(self._login) == uuRestLoginPlus4U:
        #     self._load_token_plus4u()
        elif type(self._login) == uuRestLoginEmpty:
            return
        else:
            raise Exception("Error when getting token. Unknown Login Class.")

    def _load_token_general(self):
        """
        Performs http, https call to obtain token data
        :return:
        """
        data_str = json.dumps(self._login.get_request_payload())
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        r = self._http_call(method=uuRestMethod.POST, api_call_url=self._login.oidc_url, data_str=data_str, verify=False, auth=None, headers=headers)
        # check if the response is OK and data contains token
        if r.status_code == 200:
            token_response = r.json()
            self._token = token_response['id_token']
            self._token_renew = token_response["expires_in"] - 1
        else:
            raise Exception(f'Cannot load token. Response status is {str(r.status_code)}.\n{r.text}')

    def _http_call(self, method: uuRestMethod, api_call_url: str, data_str: str, verify: bool, auth, headers, raise_exception_on_error: bool):
        """
        Performs a http, https call
        :param method:
        :param api_call_url:
        :param data_str:
        :param verify:
        :param auth:
        :param headers:
        :return:
        """
        urllib3.disable_warnings()
        # uses post
        if method == uuRestMethod.POST:
            try:
                result = requests.post(api_call_url, data=data_str, verify=False, auth=auth, headers=headers, timeout=self.timeout)
                return result
            except Exception as err:
                if raise_exception_on_error:
                    raise Exception(f'Error when calling "{str(api_call_url)}" with payload "{str(data_str)}" using method "{str(method)}". '
                                    f'Exception "{str(type(err))}" was triggered.\n\n{escape_text(str(err))}')
                return None
        # uses get
        elif method == uuRestMethod.GET:
            try:
                result = requests.get(api_call_url, data=data_str, verify=False, auth=auth, headers=headers, timeout=self.timeout)
                return result
            except Exception as err:
                if raise_exception_on_error:
                    raise Exception(f'Error when calling "{str(api_call_url)}" with payload "{str(data_str)}" using method "{str(method)}". '
                                    f'Exception "{str(type(err))}" was triggered.\n\n{escape_text(str(err))}')
                return None
        else:
            raise Exception(f'Unknown method in uuRest._http_call. Currently only GET and POST methods are supported.')

    def _get_response_payload(self, r: requests.Response, charset: uuCharset):
        """
        delete
        :param r:
        :param charset:
        :return:
        """
        # try to get response content
        try:
            result = r.content.decode(str(charset))
        except Exception as err:
            result = {"__error__": f'JSON CONTENT WAS NOT OBTAINED\nException "{type(err)}" was triggered.\n\n{escape_text(str(err))}'}
        return result

    def _get_response_content_type_and_charset(self, r):
        # sets default response content type
        response_content_type = str(uuContentType.APPLICATION_OCTET_STREAM)
        response_charset = uuCharset.UTF8
        if f'Content-Type' in r.headers.keys():
            content_type_str = str(r.headers[f'Content-Type']).lower().strip()
            # if Content-Type is application/json
            if content_type_str.find(str(uuContentType.APPLICATION_JSON)) >= 0:
                response_content_type = str(uuContentType.APPLICATION_JSON)
                # charset
                if content_type_str.replace(" ", "").replace("\t", "").find(f'charset=cp1250') >= 0:
                    response_charset = uuCharset.CP1250
            elif content_type_str.find("text/") >= 0:
                response_content_type = str(uuContentType.TEXT_PLAIN)
        return response_content_type, response_charset

    def _request_contains_files(self, request_payload) -> bool:
        result = False
        if request_payload is not None and isinstance(request_payload, dict):
            for key, value in request_payload.items():
                if str(value).lower().startswith(f'file:///'):
                    result = True
                    break
        return result

    def _call_including_files(self, api_call_url: str, request_payload: Dict or json or str or None = None, method: uuRestMethod = uuRestMethod.POST,
                              raise_exception_on_error: bool = True):
        # http method must be post
        if method != uuRestMethod.POST:
            raise Exception(f'The upload_file_raw function must be called with method parameter set to POST, but it is set with GET.')
        request_payload = convert_to_dict(request_payload)
        # create form fields
        fields = {}
        for key, value in request_payload.items():
            key_str = str(key)
            value_str = str(value)
            # if value is file then load file
            if value_str.lower().startswith(f'file:///'):
                value_str = value_str[len(f'file:///'):]
                # open file
                filename = Path(value_str).resolve()
                if not filename.exists():
                    raise Exception(f'Cannot load file from {str(filename)} in upload_file')
                pure_filename = filename.stem + ''.join(filename.suffixes)
                f = open(str(filename), 'rb')
                # add new field containing the file
                fields.update({key_str: (pure_filename, f, 'application/zip')})
            # else the value must be a string
            else:
                # add new field containing a string
                fields.update({key_str: value_str})
        # upload files
        m = MultipartEncoder(fields)
        if self.token is None:
            #r = requests.post(api_call_url, files=files, verify=False, auth=None, headers=headers)
            r = requests.post(api_call_url, headers={'Content-Type': m.content_type}, data=m.to_string(), verify=False, auth=None)
        else:
            fields = {'data': ('uuts.zip', open('C:/git/CaMS/Toolkit/metamodel/deploy/capacity/uuts.zip', 'rb'), 'application/zip')}
            m = MultipartEncoder(fields)
            r = requests.post(api_call_url, headers={'Content-Type': m.content_type}, data=m.to_string(), verify=False, auth=BearerAuth(self.token))
        return r

    def _call_without_files(self, api_call_url: str, request_payload: Dict or json or str or None = None, method: uuRestMethod = uuRestMethod.POST,
                            raise_exception_on_error: bool = True):
        # request content type must be application/json
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data_str = convert_to_str(request_payload)
        # performs http call
        if self.token is None:
            r = self._http_call(method=method, api_call_url=api_call_url, data_str=data_str, verify=False,
                                auth=None, headers=headers, raise_exception_on_error=raise_exception_on_error)
        else:
            r = self._http_call(method=method, api_call_url=api_call_url, data_str=data_str, verify=False,
                                auth=BearerAuth(self.token), headers=headers, raise_exception_on_error=raise_exception_on_error)
        return r

    def call_raw(self, api_call_url: str, request_payload: Dict or json or str or None = None, method: uuRestMethod = uuRestMethod.POST,
                 raise_exception_on_error: bool = True) -> dict or None:
        """
        Calls rest api endpoint
        :param api_call_url: URL of the REST api endpoint
        :param request_payload: json payload of the request
        :param method: POST or GET
        :param request_content_type: typically uuContentType.APPLICATION_JSON
        :param raise_exception_on_error: If true then the exception will be raised if any error occurs. Otherwise, errors will be suppressed.
        :return:
        """
        if self._request_contains_files(request_payload):
            r = self._call_including_files(api_call_url, request_payload, method, raise_exception_on_error)
        else:
            r = self._call_without_files(api_call_url, request_payload, method, raise_exception_on_error)
        # test if r is a valid Response
        if type(r) is not requests.Response:
            error_message = {
                "http_code": 504,
                "content_type": None,
                "payload": {"__error__": f'Unknown response type received when calling "{str(api_call_url)}" using method "{str(method)}". Server is unreachable.'}
            }
            if raise_exception_on_error:
                raise Exception(convert_to_str(error_message, True))
            return error_message
        # get response content type and charset
        response_content_type, response_charset = self._get_response_content_type_and_charset(r)

        # if there was an error then return error message
        if r.status_code < 200 or r.status_code >= 300:
            error_message = {
                "__error__": f'Http/Https error code "{str(r.status_code)}" occured. '
                             f'Cannot process text data when calling "{str(api_call_url)}" with payload "{convert_to_str(request_payload)}" using method "{str(method)}".'
            }
            response_payload = convert_to_dict(r.content, str(response_charset))
            response_payload = {} if response_payload is None else response_payload
            response_payload = {**error_message, **response_payload}
            error_message = {
                "http_code": r.status_code,
                "content_type": response_content_type,
                "payload": response_payload
            }
            if raise_exception_on_error:
                raise Exception(convert_to_str(error_message, True))
            return error_message

        # get payload
        response_payload = convert_to_dict(r.content, str(response_charset))
        # return result
        result = {
            "http_code": r.status_code,
            "content_type": response_content_type,
            "payload": response_payload
        }
        return result


def _get_example(version: int) -> dict:
    if version == 1:
        return {
            "__header__": {
                "token": "TOKEN",
                "url": "https://URL_OF_THE_REST_API_CALL",
                "method": "POST_or_GET_or_omit_method_to_auto_detect"
            }
        }
    if version == 2:
        return {
            "__header__": {
                "login": {
                    "oidc_url": "https://URL_OF_OIDC",
                    "username": "AWID_OWNER_1",
                    "password": "AWID_OWNER_2",
                    "scope": "SCOPE typically http:// https://"
                },
                "url": "https://URL_OF_THE_REST_API_CALL",
                "method": "POST_or_GET_or_omit_method_to_auto_detect"
            }
        }
    raise Exception(f'Unknown example version')


def _get_example_str() -> str:
    examplev1 = _get_example(1)
    examplev2 = _get_example(2)
    example_str = json.dumps(examplev1, indent=4) + f'\n\nor\n\n' + json.dumps(examplev2, indent=4)
    return example_str


def _get_method_from_json(uurest_json: dict) -> uuRestLoginGeneral or uuRestLoginByToken:
    method_str = f'post' if not dict_path_exists(uurest_json, f'method') else dict_get_item_by_path(uurest_json, f'method')
    method_str = method_str.lower().strip()
    if method_str == 'post':
        return uuRestMethod.POST
    else:
        return uuRestMethod.GET


def _get_login_from_json(header_json: dict) -> uuRestLoginGeneral or uuRestLoginByToken:
    """
    Create instance of login class based on configuration in header json
    :param header_json:
    :return:
    """
    def get_parameter(parameter_name: str):
        if not dict_path_exists(header_json, parameter_name):
            raise Exception(f'Parameter "{parameter_name}" must be defined in the login section.\nTry to use following structure:\n{_get_example_str()}')
        return dict_get_item_by_path(header_json, parameter_name)
    # return login
    if dict_multiple_path_exists(header_json, [f'login', f'login.scope', f'login.oidc_url', f'login.username', f'login.password']):
        scope = get_parameter(f'login.scope')
        oidc_url = get_parameter(f'login.oidc_url')
        username = get_parameter(f'login.username')
        password = get_parameter(f'login.password')
        return uuRestLoginGeneral(oidc_url, username, password, scope)
    elif dict_path_exists(header_json, f'token', is_null_value_allowed=False):
        return uuRestLoginByToken(header_json["token"])
    else:
        return uuRestLoginEmpty()


def call(request_header: Dict or json or str, request_payload: Dict or json or str, raise_exception_on_error: bool = True, timeout=120) -> uuCommand:
    """
    main method used to call REST api
    :param request_payload: dictionary (json) with the dtoin request.
    :param request_header: dictionary (json) containing url, method and optionally a token for example {"url": "...", "method": "POST", "token": "..."}
    :param raise_exception_on_error:
    :return:
    """
    # prepare request
    try:
        request = convert_to_dict(request_payload)
    except:
        raise Exception(f'Given payload was not recognized. It should be dict, json or string. See examples: \n{_get_example_str()}')
    # create header
    if request_header is None:
        raise Exception(f'You are missing a header attribute when using "call" function.\n'
                        f'See examples: \n{_get_example_str()}')
    header: dict = convert_to_dict(request_header)
    # header must contain url
    if "url" not in header.keys():
        raise Exception(f'There must be "url" element in the header.\n{_get_example_str()}')
    # get url, method and login
    url = str(header[f"url"])
    method = _get_method_from_json(header)
    login = _get_login_from_json(header)
    rest = uuRest(login)
    result = uuCommand(rest, url, request, method, raise_exception_on_error=raise_exception_on_error)
    return result


def _get_params_from_fetch(request_header: Dict or str, request_payload: Dict or None = None):
    """
    Returns header dict and payload dict from fetch command to translate it to call command
    :param request_header:
    :param request_payload:
    :return:
    """
    # get types of url and request body
    url_type = type(request_header)

    # if url is dict then there is nothing to change
    if url_type == dict:
        if "url" not in request_header.keys():
            raise Exception(f'ELement "url" must exist in the request_header')
        if "method" not in request_header.keys():
            raise Exception(f'ELement "method" must exist in the request_header. Method can be either "POST" or "GET".')
        return request_header, request_payload

    # if url is string and request_payload is none then the method is GET and there is no authorization token
    if url_type == str and request_payload is None:
        header = {"url": request_header, "method": "GET"}
        return header, None

    # if url is string and request_payload is dict then load data
    # create payload dict
    request = convert_to_dict(request_payload)
    if "body" not in request.keys():
        raise Exception(f'Parameter "body" must exist in the request_payload but it is not.\n{str(request_payload)}. '
                        f'If the first argument of the "fetch" fuction is a string (which is this case) '
                        f'the second argument must be either null or a dictionary containing "body" element '
                        f'for example "body": null, or "body": "some json".\n\nIt is assumed the "fetch" function was copied'
                        f'from chrome browser using "copy as fetch" item in the network popup menu')
    else:
        payload = request["body"]
    if payload is not None:
        payload = convert_to_dict(payload)
    # create header dict
    if "method" not in request.keys():
        raise Exception(f'Parameter "body" must exist in the request_payload but it is not.\n{str(request_payload)}. '
                        f'If the first argument of the "fetch" fuction is a string (which is this case) '
                        f'the second argument must be either null or a dictionary containing "body" element '
                        f'for example "body": null, or "body": "some json".\n\nIt is assumed the "fetch" function was copied'
                        f'from chrome browser using "copy as fetch" item in the network popup menu')
    method = request["method"]
    # token is by default equal to None
    token = None
    # try to obtain token
    if "headers" in request.keys():
        headers = request["headers"]
        if "authorization" in headers.keys():
            authorization = str(headers["authorization"])
            if not(authorization.startswith(f'Bearer ')):
                raise Exception(f'"authorization" parameter must start with the "Baerer " string but it does not.\n{str(request_payload)}.')
            token = authorization.lstrip(f'Baerer')
            token = token.strip()
    # create header
    header = {
        "url": request_header,
        "method": method,
        "token": token
    }
    # returns header and payload dictionaries
    return header, payload


# null is typically used in the fetch export
null = None
# default value for raise_exception_on_error
globals()["fetch_global_setup_raise_exception_on_error"] = True
# default value for fetch_timeout
globals()["fetch_global_setup_timeout"] = 120
# default value for verbose
globals()["fetch_global_setup_verbose"] = False


def fetch_global_setup(raise_exception_on_error: bool or None = None, timeout: int or None = None, verbose: bool or None = None):
    """
    Setup fetch global parameters
    :param raise_exception_on_error:
    :param timeout:
    :param verbose:
    :return:
    """
    if raise_exception_on_error is not None:
        globals()["fetch_global_setup_raise_exception_on_error"] = raise_exception_on_error
    if timeout is not None:
        globals()["fetch_global_setup_timeout"] = timeout
    if verbose is not None:
        globals()["fetch_global_setup_verbose"] = verbose


def fetch(request_header: Dict or str, request_payload: Dict or None = None, raise_exception_on_error: bool or None = None, timeout: int or None = None) -> uuCommand:
    """
    Calls rest api url and returns response.
    Fetch command is typically copied directly from the Chrome browser
    :param request_header: Contains url string or dictionary (json) containing url, method and optionally a token for example {"url": "...", "method": "POST", "token": "..."}
    :param request_payload: dictionary (json) with the dtoin request.
    :param raise_exception_on_error: Will raise exception if error occurs. Default value is True. Default value can be modified using fetch_global_setup(...)
    :param timeout: How long to wait for the http, https response. Default value is 120. Default value can be modified using fetch_global_setup(...)
    :return:
    """
    g = globals()
    if raise_exception_on_error is None:
        raise_exception_on_error = g["fetch_global_setup_raise_exception_on_error"]
    if timeout is None:
        timeout = g["fetch_global_setup_timeout"]
    verbose = g["fetch_global_setup_verbose"]
    header, payload = _get_params_from_fetch(request_header, request_payload)
    result = call(header, payload, raise_exception_on_error, timeout)
    if verbose:
        print(result)
    return result


def translate_fetch(url: str, request_payload: Dict or json or str):
    """
    Translate fetch command into call command and print generated source code
    :param url:
    :param request_payload:
    :param raise_exception_on_error:
    :param timeout:
    :return:
    """
    g = globals()
    verbose = g["fetch_global_setup_verbose"]
    header, payload = _get_params_from_fetch(url, request_payload)
    result = f''
    result += f'from uuRest import fetch, translate_fetch, call, null\n\n'
    result += f'url = "{header["url"]}"\n'
    result += f'method = "{header["method"]}"\n'
    if header["token"] is None:
        result += f'token = None\n'
    else:
        result += f'token = "{header["token"]}"\n'
    result += 'header = {"url": url, "method": method, "token": token}\n'
    if payload is None:
        result += f'payload = None\n'
    else:
        result += f'payload = {convert_to_str(payload, formatted=True)}\n'
    result += f'response = call(header, payload)\n'
    result += f'print(response)\n\n'
    if verbose:
        print(f'# ----------------------------------------\n')
        print(result)
        print(f'# ----------------------------------------')
    return result
