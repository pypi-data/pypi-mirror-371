"""网络请求"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any, ClassVar, Generic, ParamSpec, TypedDict, TypeVar, cast

import httpx
import orjson as json
from typing_extensions import override

from ..exceptions import CredentialExpiredError, ResponseCodeError, SignInvalidError
from .common import calc_md5
from .credential import Credential
from .session import Session, get_session
from .sign import sign

_P = ParamSpec("_P")
_R = TypeVar("_R")

logger = logging.getLogger("qqmusicapi.network")


def _processor(data: dict[str, Any]) -> dict[str, Any]:
    return data


NO_PROCESSOR = _processor


def api_request(
    module: str,
    method: str,
    *,
    verify: bool = False,
    ignore_code: bool = False,
    process_bool: bool = True,
    cache_ttl: int | None = None,
    cacheable: bool = True,
    exclude_params: list[str] | None = None,
    catch_error_code: list[int] | None = None,
):
    """API请求"""

    def decorator(
        api_func: Callable[_P, Coroutine[None, None, tuple[dict[Any, Any], Callable[[dict[str, Any]], _R]]]],
    ):
        return ApiRequest[_P, _R](
            module,
            method,
            api_func=api_func,
            verify=verify,
            ignore_code=ignore_code,
            process_bool=process_bool,
            cacheable=cacheable,
            cache_ttl=cache_ttl,
            exclude_params=exclude_params,
            catch_error_code=catch_error_code,
        )

    return decorator


class BaseRequest(ABC):
    """请求基类"""

    # 公共参数默认值
    COMMON_DEFAULTS: ClassVar[dict[str, str]] = {
        "ct": "11",
        "tmeAppID": "qqmusic",
        "format": "json",
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "uid": "3931641530",
    }

    def __init__(
        self,
        common: dict[str, Any] | None = None,
        credential: Credential | None = None,
        verify: bool = False,
        ignore_code: bool = False,
    ) -> None:
        self._common = common or {}
        self._credential = credential
        self.verify = verify
        self.ignore_code = ignore_code
        self.cache = self.session._cache

    @property
    def session(self) -> Session:
        """获取请求会话"""
        return get_session()

    @property
    def credential(self) -> Credential:
        """获取请求凭证"""
        return self._credential or self.session.credential or Credential()

    @credential.setter
    def credential(self, value: Credential):
        """设置请求凭证"""
        self._credential = value

    @property
    def common(self) -> dict[str, Any]:
        """公共参数"""
        common = self._build_common_params(self.credential)
        common.update(self._common)
        return common

    @common.setter
    def common(self, value: dict[str, Any]):
        """设置公共参数"""
        self._common = value

    def _build_common_params(self, credential: Credential) -> dict[str, Any]:
        config = self.session.api_config
        common = {
            "cv": config["version_code"],
            "v": config["version_code"],
            "QIMEI36": self.session.qimei,
        }
        common.update(self.COMMON_DEFAULTS)
        if credential.has_musicid() and credential.has_musickey():
            common.update(
                {
                    "qq": str(credential.musicid),
                    "authst": credential.musickey,
                    "tmeLoginType": str(credential.login_type),
                }
            )
        return common

    def _set_cookies(self, credential: Credential):
        if credential.has_musicid() and credential.has_musickey():
            cookies = httpx.Cookies()
            cookies.set("uin", str(credential.musicid), domain=".qq.com")
            cookies.set("qqmusic_key", credential.musickey, domain=".qq.com")
            cookies.set("qm_keyst", credential.musickey, domain=".qq.com")
            cookies.set("tmeLoginType", str(credential.login_type), domain=".qq.com")
            self.session.cookies = cookies

    @abstractmethod
    def build_request_data(self) -> dict[str, Any]:
        """构建请求体数据"""
        pass

    def build_request(self) -> dict[str, Any]:
        """统一构建请求参数"""
        data = self.build_request_data()
        config = self.session.api_config
        request_params = {
            "url": config["enc_endpoint" if config["enable_sign"] else "endpoint"],
            "json": data,
        }
        if config["enable_sign"]:
            request_params["params"] = {"sign": sign(data)}
        return request_params

    async def request(self) -> httpx.Response:
        """执行请求"""
        if self.verify:
            self.credential.raise_for_invalid()
        request_data = self.build_request()
        logger.debug(f"发送请求: {request_data}")
        self._set_cookies(self.credential)
        resp = await self.session.post(**request_data)
        if not self.ignore_code:
            resp.raise_for_status()
        return resp

    @abstractmethod
    async def _process_response(self, resp: httpx.Response) -> Any:
        pass


class ApiRequest(BaseRequest, Generic[_P, _R]):
    """API 请求处理器"""

    def __init__(
        self,
        module: str,
        method: str,
        api_func: Callable[_P, Coroutine[None, None, tuple[dict[Any, Any], Callable[[dict[str, Any]], _R]]]]
        | None = None,
        *,
        params: dict[str, Any] | None = None,
        common: dict[str, Any] | None = None,
        credential: Credential | None = None,
        verify: bool = False,
        ignore_code: bool = False,
        process_bool: bool = True,
        cache_ttl: int | None = None,
        cacheable: bool = True,
        exclude_params: list[str] | None = None,
        catch_error_code: list[int] | None = None,
    ) -> None:
        super().__init__(common, credential, verify, ignore_code)
        self.module = module
        self.method = method
        self.params = params or {}
        self.api_func = api_func
        self.proceduce_bool = process_bool
        self.processor: Callable[[dict[str, Any]], Any] = NO_PROCESSOR
        self.cacheable = cacheable
        self.cache_ttl = cache_ttl
        self.exclude_params = exclude_params or []
        self.catch_error_code = catch_error_code or []

    def copy(self) -> "ApiRequest[_P, _R]":
        """创建当前 ApiRequest 实例的副本"""
        req = ApiRequest[_P, _R](
            module=self.module,
            method=self.method,
            api_func=self.api_func,
            params=self.params.copy(),
            common=self._common.copy(),
            credential=self.credential,
            verify=self.verify,
            ignore_code=self.ignore_code,
            process_bool=self.proceduce_bool,
            cacheable=self.cacheable,
            cache_ttl=self.cache_ttl,
            exclude_params=self.exclude_params.copy(),
            catch_error_code=self.catch_error_code,
        )
        req.processor = self.processor
        return req

    @override
    def build_request_data(self) -> dict[str, Any]:
        return {"comm": self.common, f"{self.module}.{self.method}": self.data}

    @property
    def data(self) -> dict[str, Any]:
        """API 请求数据"""
        if self.proceduce_bool:
            params = {k: int(v) if isinstance(v, bool) else v for k, v in self.params.items()}
        else:
            params = self.params

        return {
            "module": self.module,
            "method": self.method,
            "param": params,
        }

    def _generate_cache_key(self) -> str:
        params = self.params.copy()
        for key in self.exclude_params:
            params.pop(key, None)
        if self.credential:
            params["credential"] = f"{self.credential.musicid}{self.credential.musickey}"
        sorted_params = json.dumps(params, option=json.OPT_SORT_KEYS)
        return calc_md5(sorted_params)

    @override
    async def _process_response(self, resp: httpx.Response) -> dict[str, Any]:
        """处理响应数据"""
        if not resp.content:
            return {}
        try:
            data = json.loads(resp.content)
        except json.JSONDecodeError:
            return {"data": resp.text}
        req_data = data.get(f"{self.module}.{self.method}", {})
        if self.ignore_code:
            return req_data
        self._validate_response(req_data)
        return req_data.get("data", req_data)

    def _validate_response(self, data: dict[str, Any]) -> None:
        """验证响应状态码"""
        code = data.get("code", 0)
        logger.debug(
            "API %s.%s: %s",
            self.module,
            self.method,
            code,
        )

        if code == 0 or code in self.catch_error_code:
            return

        if code == 2000:
            raise SignInvalidError(data=data)
        if code == 1000:
            raise CredentialExpiredError(self.data, data)
        if code != 0:
            raise ResponseCodeError(code, self.data, data)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:  # noqa: D102
        if credential := kwargs.pop("credential", None):
            if isinstance(credential, Credential):
                self.credential = credential
        instance = self
        if instance.api_func:
            params, processor = await instance.api_func(*args, **kwargs)
            instance = self.copy()
            instance._common.update(params.pop("common", {}))
            instance.params.update(params)
            instance.processor = processor
        key = instance._generate_cache_key()
        if self.session.enable_cache and self.cacheable:
            if cache_data := await self.cache.get(key):
                return cache_data
        resp = await instance.request()
        resp = cast(_R, instance.processor(await instance._process_response(resp)))
        if self.session.enable_cache and self.cacheable:
            await self.cache.set(key, resp, ttl=self.cache_ttl)
        return resp

    def __repr__(self) -> str:
        return f"<ApiRequest {self.module}.{self.method}>"


class RequestItem(TypedDict):
    """请求 Item"""

    id: int
    key: str
    request: ApiRequest
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    processor: Callable[[dict[str, Any]], Any] | None


class RequestGroup(BaseRequest):
    """合并多个 API 请求,支持组级公共参数和重复模块方法处理"""

    def __init__(
        self,
        common: dict[str, Any] | None = None,
        credential: Credential | None = None,
        limit: int = 30,
    ):
        super().__init__(common, credential)
        self._requests: list[RequestItem] = []
        self.limit = limit
        self._key_counter = defaultdict(int)
        self._results = []

    def add_request(self, request: ApiRequest[_P, _R], *args: _P.args, **kwargs: _P.kwargs) -> None:
        """添加请求,自动生成唯一键"""
        base_key = f"{request.module}.{request.method}"
        self._key_counter[base_key] += 1
        count = self._key_counter[base_key]
        unique_key = f"{base_key}.{count}" if count > 1 else base_key
        request = request.copy()
        request.credential = self.credential

        self._requests.append(
            RequestItem(
                id=len(self._requests),
                key=unique_key,
                request=request,
                args=args,
                kwargs=kwargs,
                processor=request.processor,
            )
        )

    async def _process_response(self, resp: httpx.Response):
        try:
            if not resp.content:
                return []

            res_data = json.loads(resp.content)

            for req_item in self._requests:
                req = req_item["request"]
                req_data = res_data.get(req_item["key"], {})
                req._validate_response(req_data)
                if req_item["processor"]:
                    data = req_item["processor"](req_data.get("data", req_data))
                else:
                    data = req_data.get("data", req_data)
                if self.session.enable_cache and req.cacheable:
                    await self.cache.set(req._generate_cache_key(), data, ttl=req.cache_ttl)
                self._results[req_item["id"]] = data
        except json.JSONDecodeError:
            self._results = [{"data": resp.text}]

    async def _prepare_request(self):
        for req in self._requests:
            request = req["request"]
            if request.api_func:
                params, processor = await request.api_func(*req["args"], **req["kwargs"])
                self.common.update(params.pop("common", {}))
                request.params.update(params)
                req["processor"] = processor

    @override
    def build_request_data(self):
        """构建请求"""
        merged_data = {req["key"]: req["request"].data for req in self._requests}
        data = {"comm": self.common}
        data.update(merged_data)
        return data

    async def _get_cache(self):
        keys = [req["request"]._generate_cache_key() for req in self._requests if req["request"].cacheable]
        cache = self.cache
        cache_data = await cache.multi_get(keys)
        remove_index = []
        for idx, data in enumerate(cache_data):
            if data:
                self._results[idx] = data
                remove_index.append(idx)
        self._requests = [req for idx, req in enumerate(self._requests) if idx not in remove_index]

    async def _execute(self) -> list[Any]:
        """执行合并请求并返回各请求结果"""
        if not self._requests:
            return []
        self._results = [None] * len(self._requests)
        await self._prepare_request()
        if self.session.enable_cache:
            await self._get_cache()

        if not self._requests:
            return self._results
        resp = await self.request()
        await self._process_response(resp)
        return self._results

    async def execute(self) -> list[Any]:
        """执行合并请求"""
        if not self._requests:
            return []

        # 未设置 limit 或请求数未超过 limit 时直接处理
        if self.limit <= 0 or len(self._requests) <= self.limit:
            return await self._execute()

        # 分批次处理
        batches = [self._requests[i : i + self.limit] for i in range(0, len(self._requests), self.limit)]
        all_results = []

        for batch in batches:
            # 创建新 RequestGroup 处理当前批次
            batch_group = RequestGroup(
                common=self.common.copy(),
                credential=self.credential,
            )

            # 添加当前批次的请求
            for req_item in batch:
                batch_group.add_request(req_item["request"], *req_item["args"], **req_item["kwargs"])

            # 执行并收集结果
            batch_results = await batch_group._execute()
            all_results.extend(batch_results)

        return all_results
