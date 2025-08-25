"""

uuRest
===================================

Implementation of the Command structure used in rest API
by most Unicorn applications

"""

from .uuCommon import uuRestMethod, uuContentType, convert_to_dict, convert_to_str, uuDict
from .uuIO import save_json, save_textfile, save_binary

import json
import math
from enum import Enum
from typing import List, Dict


class uuResponseStatus(Enum):
    OK = 0
    WARNING_IN_UUAPPERRORMAP = 100
    ERROR_IN_UUAPPERRORMAP = 200
    NETWORK_ERROR = 400


class uuRequest:
    """
    class containing all important http, https request properties
    """
    def __init__(self, command, url: str, payload: dict or json or str, method: uuRestMethod, content_type: uuContentType, raise_exception_on_error: bool):
        self._command: uuCommand = command
        self.url: str = url
        self._payload = convert_to_dict(payload)
        self.method = method
        self.content_type = content_type
        self.raise_exception_on_error = raise_exception_on_error

    def create_copy(self):
        return uuRequest(self._command, self.url, self._payload, self.method, self.content_type, self.raise_exception_on_error)

    @property
    def payload_json(self) -> uuDict:
        return self._payload

    @payload_json.setter
    def payload_json(self, value):
        self._payload = convert_to_dict(value)


class uuResponse:
    """
    class containing all important http, https response properties
    """
    def __init__(self, command):
        self._command: uuCommand = command
        self._payload = None
        self.http_status_code = 0
        self.content_type: uuContentType = ""

    @property
    def payload_json(self) -> uuDict:
        return self._payload

    @payload_json.setter
    def payload_json(self, value):
        self._payload = convert_to_dict(value)


class uuCommand:
    """

    """
    def __init__(self, rest, url: str, payload: dict or json or str, method: uuRestMethod,
                 content_type: uuContentType = uuContentType.APPLICATION_JSON, raise_exception_on_error: bool = False):
        # save the reference to the uuRest instance
        self.rest = rest
        # create a request
        self._initial_request = uuRequest(self, url, payload, method, content_type, raise_exception_on_error)
        self.requests: List[uuRequest] = []
        self.responses: List[uuResponse] = []
        self._http_code: int = 0
        self._url: str = url
        self._method = method
        self._content_type = uuContentType.APPLICATION_JSON
        self._call()

    # @property
    # def url(self) -> str:
    #     return self._url
    #
    # @property
    # def method(self) -> str:
    #     return str(self._method)

    @property
    def content_type(self) -> str:
        if len(self.responses) > 0:
            return self.responses[-1].content_type
        return ""

    @property
    def http_status_code(self) -> int:
        if len(self.responses) > 0:
            return self.responses[-1].http_status_code
        return 0

    @property
    def json(self) -> dict or None:
        if len(self.responses) > 0:
            result = self.responses[-1].payload_json
            return result
        else:
            result = None
        return result

    @property
    def raw_content(self) -> dict:
        if len(self.responses) > 0:
            result = self.responses[-1].payload_json
        else:
            result = None
        return result

    def save_raw_content(self, filename: str):
        save_binary(self.raw_content, filename)
        return

    def save_json(self, filename: str, encoding):
        save_json(self.json, filename, encoding=encoding)
        return

    def _call(self, new_page_info: dict or None = None):
        # if len(self.requests) > 0 and not self.is_paged_call:
        #     raise Exception(f'This is not a paged call (list call), but there is an attempt to load next page.')
        request = self._initial_request.create_copy()
        if new_page_info is not None:
            request.payload_json.update({f'pageInfo': new_page_info})
        self.requests.append(request)
        # call api
        result = self.rest.call_raw(api_call_url=request.url, request_payload=request.payload_json, method=request.method,
                                    raise_exception_on_error=request.raise_exception_on_error)
        # process the result
        response = uuResponse(self)
        response.http_status_code = result[f'http_code']
        response.content_type = result[f'content_type']
        response.payload_json = result[f'payload']
        self.responses.append(response)

    def _page_info_list_items_on_a_page(self, list_name) -> int:
        result = 0
        # take the very last response
        if len(self.responses) > 0:
            payload = self.responses[-1].payload_json
            # check if element exists in the response payload
            if list_name in payload.keys():
                if isinstance(payload[list_name], list):
                    # get count of elements on currently displayed page
                    result = len(payload[list_name])
        return result

    def _page_info(self, list_name) -> dict or None:
        """
        Gets a page infor from the response
        :return:
        """
        result = None
        # take the very last response
        if len(self.responses) > 0:
            payload = self.responses[-1].payload_json
            # test if pageInfo exists
            if "pageInfo" in payload.keys():
                result = payload["pageInfo"]
                # check pageSize
                if "pageSize" not in result.keys():
                    raise Exception(f'PageInfo should contain "pageSize". Received following pageInfo: {result}')
                if not isinstance(result["pageSize"], int):
                    raise Exception(f'pageSize located in the pageInfo element must be integer, but it is type of {str(type(result["pageSize"]))}.')
                if result["pageSize"] < 1:
                    raise Exception(f'pageSize located in the pageInfo element must be must be higher than 0. Received following pageInfo: {result}')
                # if there are more items on a page then pageSize - update pageSize
                list_items_count = self._page_info_list_items_on_a_page(list_name)
                # if there is no item with list_name then return none
                if list_items_count < 1:
                    return None
                if result["pageSize"] < list_items_count:
                    result["pageSize"] = list_items_count
                # setup pageIndex
                if "pageIndex" not in result.keys():
                    result.update({"pageIndex": 0})
                # create total if it does not exist
                if "total" not in result.keys():
                    result.update({"total": min(result["pageSize"]-1, list_items_count)})
        return result

    def _items_on_page(self, page_index, start_index_on_page, stop_index_on_page, list_name):
        page_info = self._page_info(list_name=list_name)
        # check if already loaded page is the requested one
        current_page_index = page_info["pageIndex"]
        current_page_size = page_info["pageSize"]
        # if it is not, call the api and download requested page
        if page_index != current_page_index:
            new_page_info = {
                f'pageIndex': page_index,
                f'pageSize': current_page_size
            }
            self._call(new_page_info=new_page_info)
            # verify that requested page was downloaded
            page_info = self._page_info(list_name=list_name)
            current_page_index = page_info["pageIndex"]
            if current_page_index != page_index:
                raise Exception(f'Cannot download page "{page_index}" in _items_on_page.')
        # check that item list is not empty
        if list_name not in self.json:
            return None
        item_list = self.json[list_name]
        # check that start and stop index is in the boundaries
        stop_index_on_page = min(stop_index_on_page, len(item_list))
        if start_index_on_page < 0 or stop_index_on_page < 0 or start_index_on_page >= len(item_list) or start_index_on_page > stop_index_on_page:
            return None
        # yield items
        for i in range(start_index_on_page, stop_index_on_page):
            yield item_list[i]

    def items(self, start_index: int or None = None, stop_index: int or None = None, list_name: str = "itemList"):
        # get page info
        page_info = self._page_info(list_name=list_name)
        # if there are no items on the page then exit immediately
        if page_info is None:
            return
        # get pageSize and total
        page_size = page_info["pageSize"]
        total = page_info["total"]
        # setup start index and stop index
        start_index = 0 if start_index is None else start_index
        stop_index = total if stop_index is None else stop_index
        start_index = total - (-start_index % total) if start_index < 0 else start_index
        stop_index = total - (-stop_index % total) if stop_index < 0 else stop_index
        if start_index > stop_index:
            raise Exception(f'Cannot iterate through items. Start index "{start_index}" is higher than stop index "{stop_index}".')
        # setup start page and stop page
        start_page = math.floor(start_index / page_size)
        stop_page = math.floor(stop_index / page_size)
        # yield values
        for page_index in range(start_page, stop_page + 1):
            start_index_on_page = 0 if page_index != start_page else start_index % page_size
            stop_index_on_page = page_size if page_index != stop_page else stop_index % page_size
            # get items
            items = self._items_on_page(page_index, start_index_on_page, stop_index_on_page, list_name=list_name)
            if items is None:
                return
            # return item
            for item in self._items_on_page(page_index, start_index_on_page, stop_index_on_page, list_name=list_name):
                yield item

    def items_count(self, list_name="itemList") -> int:
        page_info = self._page_info(list_name=list_name)
        if page_info is None:
            return -1
            # raise Exception(f'Cannot resolve items_count. This is not a paged call.')
        total = page_info["total"]
        return total

    def __str__(self):
        result = self.json
        if result is not None:
            result = convert_to_dict(result)
            return json.dumps(result, indent=4, ensure_ascii=False)
        return result
