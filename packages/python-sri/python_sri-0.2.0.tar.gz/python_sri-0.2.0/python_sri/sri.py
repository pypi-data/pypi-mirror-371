"""Main class to implement SRI hashing

The class has many functions to simplify adding SRI hashes, from adding directly to
given HTML via a decorator all the way to computing a hash given some data.
"""

import base64
import functools
import hashlib
import io
import pathlib
import re
import socket
import ssl
import sys
from typing import Any, Callable, Literal, Optional, cast
from urllib import error as url_error
from urllib import parse as url_parse
from urllib import request as url_request

from . import parser


class SRI:
    """SubResource Integrity hash creation class

    When adding SRI hashes to HTML, this module only supports relative URLs for security
        reasons

    Parameters:
    domain: The domain that the application is served on. This is only used by functions
        that accept HTML. The protocol (or scheme) is always HTTPS, as this should
        already be implemented at a minimum, even though not explitly required for SRI
    Keyword only:
    static: Either None, disabling using the filesystem, or a dictionary with the keys
        "directory" and "url_path", the former being a path-like object and the latter a
        string, that is used to convert a URL into a filesystem path for reading files
    hash_alg: A string describing the desired hashing algorithm to choose. Defaults to
        "sha384". Currently limited to "sha256", "sha384", and "sha512"
    in_dev: A boolean value, defaulting to False, describing whether to, by default,
        clear method caches upon method completion. This is useful when developing a
        website, as it ensures fresh changes to files do not break the site. Can be
        overridden by the clear parameter on an individual method, which by default
        inherits the value of this parameter.

    Properties:
    available_algs: Tuple of available hashing algorithms
    hash_alg: Non editable property returning the selected hashing algorithm.
    in_dev: Non editable property returning the same value as provided by the in_dev
        parameter
    """

    __slots__ = (
        "__domain",
        "__url_overrides",
        "__static_dir",
        "__static_url",
        "__hash_alg",
        "__in_dev",
        "__sri_ptrn",
        "__parser",
    )
    available_algs: tuple[str, str, str] = ("sha256", "sha384", "sha512")

    def __init__(
        self,
        domain: str,
        *,
        static: Optional[dict[str, str | pathlib.Path]] = None,
        hash_alg: str = "sha384",
        in_dev: bool = False,
        **kwargs: Optional[float | dict[str, str] | ssl.SSLContext],
    ) -> None:
        self.__domain = domain
        self.__url_overrides: dict[str, dict[str, str] | ssl.SSLContext] = {}
        if "timeout" in kwargs and isinstance(kwargs["timeout"], int | float):
            socket.setdefaulttimeout(kwargs["timeout"])
        if "headers" in kwargs and isinstance(kwargs["headers"], dict):
            self.__url_overrides["headers"] = kwargs["headers"]
        if "timeout" in kwargs and isinstance(kwargs["context"], ssl.SSLContext):
            self.__url_overrides["context"] = kwargs["context"]
        if static is not None:
            if not isinstance(static, dict):
                raise TypeError("static must either be None or a dictionary")
            if "directory" not in static:
                raise ValueError("A directory must be given in the static dictionary")
            if isinstance(static["directory"], str):
                static["directory"] = pathlib.Path(static["directory"])
            if "url_path" not in static:
                raise ValueError("A url_path must be given in the static dictionary")
            if not isinstance(static["url_path"], pathlib.Path) and len(
                static["url_path"]
            ) - 1 != static["url_path"].rfind("/"):
                static["url_path"] += "/"
        self.__static_dir: Optional[pathlib.Path] = (
            None
            if static is None
            else (
                static["directory"]
                if isinstance(static["directory"], pathlib.Path)
                else None
            )
        )
        if self.__static_dir is not None and not self.__static_dir.is_dir():
            raise ValueError(
                "Provided static directory does not exist or is not a directory"
            )
        self.__static_url: Optional[str] = (
            None
            if static is None
            else (static["url_path"] if isinstance(static["url_path"], str) else None)
        )
        # Normalize string to best fit the three values
        # of sha256, sha384, sha512
        ptrn = re.compile("[\\W_]+")
        hash_alg = ptrn.sub("", hash_alg.casefold())
        if hash_alg not in self.available_algs:
            raise ValueError("Hash algorithm is not allowed to be used for SRI hashes")
        self.__hash_alg: Literal["sha256", "sha384", "sha512"] = cast(
            Literal["sha256", "sha384", "sha512"], hash_alg
        )
        # If in_dev is True, then the caches need clearing after each run for freshness
        self.__in_dev = in_dev
        self.__sri_ptrn = re.compile(
            "sha(256-[-A-Za-z0-9+/]{43}=?|"
            + "384-[-A-Za-z0-9+/]{64}|512-[-A-Za-z0-9+/]{86}(={2})?)"
        )
        self.__parser = parser.Parser()

    def __hash__(self) -> int:
        if self.__static_dir is None:
            return hash((self.__domain, None, self.__hash_alg, self.__in_dev))
        return hash(
            (
                self.__domain,
                self.__static_dir,
                self.__static_url,
                self.__hash_alg,
                self.__in_dev,
            )
        )

    @property
    def domain(self) -> str:
        return self.__domain

    @property
    def hash_alg(self) -> Literal["sha256", "sha384", "sha512"]:
        return self.__hash_alg

    @property
    def in_dev(self) -> bool:
        return self.__in_dev

    def clear_cache(self) -> None:
        self.hash_file_path.cache_clear()
        self.hash_file_object.cache_clear()
        self.hash_url.cache_clear()

    # Functions for creating/inserting SRI hashes
    # Starts with some decorators for ease, then each step has its own func
    # Ends with either the hash of a file descriptor or the content of some site
    # Hashing a URL has not been implemented yet

    def html_uses_sri(
        self, route: str, clear: Optional[bool] = None
    ) -> Callable[[Callable[..., str]], Callable[..., str]]:
        """A decorator to simplify adding SRI hashes to HTML

        @html_uses_sri(route, clear)
        route: The route that this function is defined for. Used to interpret relative
            URLs
        clear: An optional argument, that can override in_dev, controlling whether to
            clear caches after running.
        """

        def decorator(func: Callable[..., str]) -> Callable[..., str]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> str:
                nonlocal clear
                nonlocal route
                html: str = func(*args, **kwargs)
                return self.hash_html(route, html, clear)

            return wrapper

        return decorator

    def hash_html(self, route: str, html: str, clear: Optional[bool] = None) -> str:
        """Parse some HTML, adding in a SRI hash where applicable

        html: The HTML document to operate from
        clear: Whether to clear the cache after running. Defaults to the value of in_dev
            Use the in_dev property to control automatic clearing for freshness

        returns: New HTML with SRI hashes
        """
        if clear is None:
            clear = self.__in_dev
        self.__parser.empty()
        self.__parser.feed(html)
        sri_tags: list[parser.Element] = self.__parser.sri_tags
        base_url = url_parse.urljoin(self.__domain, route)
        for tag in sri_tags:
            integrity: Optional[str] = tag["integrity"]
            if integrity is None:
                integrity = ""
            # Check if integrity attribute already has a SRI hash (sha256-HASH,
            # sha384-HASH, sha512-HASH), where HASH could be 43 or 44 (sha256), 64
            # (sha384), or 79, 80 or 81 (sha512) chars in length
            if re.fullmatch(self.__sri_ptrn, integrity) is not None:
                # It is a SRI hash
                continue
            # Check if tag can actually utilise SRI, otherwise remove integrity attr and
            # add data-sri-error attribute with the error message
            if ("href" if tag.name == "link" else "src") not in tag:
                del tag["integrity"]
                tag["data-sri-error"] = "No URL to resource provided"
                continue
            if tag.name == "link" and (
                tag["rel"] not in ["stylesheet", "preload"]
                or (tag["rel"] == "preload" and tag["as"] not in ["script", "style"])
            ):
                del tag["integrity"]
                # In the <link> tag of this message, include the as="val" attribute if
                # rel="preload"
                as_attr = "" if tag["as"] is None else tag["as"]
                tag["data-sri-error"] = (
                    "Integrity attribute not supported with "
                    + f'<link rel="{tag["rel"]}"'
                    + ((' as="' + as_attr + '"') if tag["rel"] == "preload" else "")
                    + "> values"
                )
                continue
            # No checks for URL validity, except that it does not have a domain name
            # If the URL is not valid, then browsers will notify devs that it is not
            # Once the URL is valid, then it should just work here
            src: Optional[str] = tag[attr := "href" if tag.name == "link" else "src"]
            if src is None or len(src.strip()) == 0:
                del tag["integrity"]
                tag["data-sri-error"] = f"No URL found in {attr} attribute"
                continue
            src = src.strip()
            hash_str: str = ""
            parsed_url: url_parse.ParseResult = url_parse.urlparse(src)
            if parsed_url.netloc != "":
                # URL is an absolute URL which is currently not supported due to
                # difficulty proving the domain is owned by the app so that CDN content
                # is not hashed on page load, which would defeat the purpose of SRI
                del tag["integrity"]
                tag["data-sri-error"] = (
                    "python_sri does not currently support the addition of SRI hashes "
                    + "to absolute URLs. If this resource is owned by the website, use "
                    + "a relative URL instead for SRI hashes"
                )
                continue
            # Conversion to absolute URL is required for getting resources via network
            # and to match against a static path to find resources on the filesystem
            as_absolute_url: str = url_parse.urljoin(base_url, src)
            if self.__static_dir is not None and self.__static_url is not None:
                # Fetch via filesystem read
                url_path = url_parse.urlparse(as_absolute_url).path
                new_path: str = url_path.removeprefix(self.__static_url)
                if new_path == url_path:
                    # Absolute URL did not point to the configured static path
                    del tag["integrity"]
                    tag["data-sri-error"] = (
                        "Resource in URL not in configured static directory"
                    )
                    continue
                fs_path: pathlib.Path = self.__static_dir / pathlib.Path(new_path)
                try:
                    hash_str = self.hash_file_path(fs_path, False)
                except ValueError:
                    del tag["integrity"]
                    tag["data-sri-error"] = "File not found"
                    continue
            else:
                # Fetch via HTTP GET request
                try:
                    hash_str = self.hash_url(as_absolute_url)
                except ValueError as err:
                    if not str(err).startswith(
                        "Requested resource did not serve a Content-Type of text/"
                        + "javascript or text/css."
                    ):
                        raise err
                    del tag["integrity"]
                    tag["data-sri-error"] = (
                        "URL linked to in href/src attribute had an invalid "
                        + "Content-Type"
                    )
                    continue
                except url_error.HTTPError as err:
                    del tag["integrity"]
                    tag["data-sri-error"] = (
                        f"HTTP GET Failed. Status Code: {err.status}. Reason: "
                        + err.reason
                    )
                    continue
                except url_error.URLError as err:
                    del tag["integrity"]
                    tag["data-sri-error"] = (
                        f"Some other urllib error occured. Reason: {err.reason}"
                    )
                    continue
                except TimeoutError as err:
                    del tag["integrity"]
                    tag["data-sri-error"] = "Timeout exceeded"
                    continue
            # Should be valid hash in hash_str
            tag["integrity"] = hash_str
        if clear:
            self.clear_cache()
        return self.__parser.stringify()

    @functools.lru_cache(maxsize=64)
    def hash_file_path(
        self, path: str | pathlib.Path, clear: Optional[bool] = None
    ) -> str:
        """Hashes a file, using the file's path

        path: The path to the file to hash (a string or pathlib.Path)
        clear: Whether to clear the cache after running. Defaults to the value of in_dev
            Use the in_dev property to control automatic clearing for freshness

        returns: The SRI hash (eg sha256-HASH), or an empty string if the path does not
            exist or is not a file
        """
        if clear is None:
            clear = self.__in_dev
        if isinstance(path, pathlib.Path):
            if not path.is_file():
                raise ValueError(f"File not found at path {path}")
            with open(path, "rb") as f:
                if clear:
                    self.clear_cache()
                return self.hash_file_object(f, False)
        elif isinstance(path, str) and url_parse.urlparse(path).netloc == "":
            path_inst = pathlib.Path(path)
            if not path_inst.is_file():
                raise ValueError(f"File not found at path {path}")
            with open(path_inst, "rb") as f:
                if clear:
                    self.clear_cache()
                return self.hash_file_object(f, False)
        raise TypeError("Given file path does not seem like a usable file path")

    @functools.lru_cache(maxsize=64)
    def hash_file_object(
        self, file: io.BufferedIOBase, clear: Optional[bool] = None
    ) -> str:
        """Hashes a file, using a file object

        file: The file object, opened in binary mode (b)
        clear: Whether to clear the cache after running. Defaults to the value of in_dev
            Use the in_dev property to control automatic clearing for freshness

        returns: The SRI hash (eg sha256-HASH)
        """
        if clear is None:
            clear = self.__in_dev
        if sys.version_info.minor < 11:
            # hashlib.file_digest was added in Python 3.11
            with file:
                res = self.hash_data(file.read())
        else:
            alg = self.__hash_alg
            f_digest = hashlib.file_digest(  # type: ignore[attr-defined, unused-ignore]  # pylint: disable=no-member, line-too-long
                file, alg
            )
            digest: bytes = f_digest.digest()
            b64: str = base64.b64encode(digest).decode(encoding="ascii")
            res = f"{self.__hash_alg}-{b64}"
        if clear:
            self.clear_cache()
        return res

    @functools.lru_cache(maxsize=64)
    def hash_url(
        self,
        url: str,
        *,
        timeout: Optional[float] = None,
        headers: Optional[dict[str, str]] = None,
        context: Optional[ssl.SSLContext] = None,
        route: Optional[str] = None,
        clear: Optional[bool] = None,
    ) -> str:
        """Hashes the content of a URL

        url: The URL
        Keyword Arguments:
        timeout: How long to wait for a response from the server, in seconds. Can be set
            via socket.setdefaulttimeout(timeout)
        headers: A dictionary of HTTP request headers to send. Defaults to "{}"
        context: A ssl.SSLContext describing information relevant to creating a secure
            session using SSL/TLS. Defaults to whatever ssl.create_default_context()
            returns
        route: The route to whatever document is initiating the call. This could be
            "/index.html" etc. Required if the URL is not an absolute URL
        clear: Whether to clear the cache after running. Defaults to the value of in_dev
            Use the in_dev property to control automatic clearing for freshness

        returns: The SRI hash (eg sha256-HASH)
        """
        if clear is None:
            clear = self.__in_dev
        if timeout is None:
            timeout = socket.getdefaulttimeout()
        if headers is None:
            headers = (
                self.__url_overrides["headers"]
                if "headers" in self.__url_overrides
                and isinstance(self.__url_overrides["headers"], dict)
                else {}
            )
        if context is None:
            context = (
                self.__url_overrides["context"]
                if "context" in self.__url_overrides
                and isinstance(self.__url_overrides["context"], ssl.SSLContext)
                else ssl.create_default_context()
            )
        parts = url_parse.urlparse(url)
        if parts.netloc == "":
            if route is None:
                raise TypeError(
                    "Relative paths must include the route being used so that an "
                    + "absolute URL can be constructed"
                )
            base_url = url_parse.urljoin(self.domain, route)
            url = url_parse.urljoin(base_url, url)
            parts = url_parse.urlparse(url)
        if parts.scheme != "https":
            raise ValueError("URL scheme/protocol must be HTTPS")
        req = url_request.Request(url, data=None, headers=headers, method="GET")
        try:
            with url_request.urlopen(
                req, data=None, timeout=timeout, context=context
            ) as res:
                content_type = res.headers["Content-Type"].split(";")[0]
                if content_type not in [
                    "text/javascript",
                    "text/css",
                    "application/javascript",
                ]:
                    raise ValueError(
                        "Requested resource did not serve a Content-Type of "
                        + "text/javascript or text/css. Served Content-Type: "
                        + f"{content_type}. URL: {url}"
                    )
                if clear:
                    self.clear_cache()
                return self.hash_data(res.read())
        except url_error.HTTPError as err:
            print("URL:", url)
            print("HTTP GET Failed. Status Code:", err.status, ". Reason:", err.reason)
            raise err
        except url_error.URLError as err:
            print("URL:", url)
            print("Some other urllib error occured. Reason:", err.reason)
            raise err
        except TimeoutError as err:
            print("URL:", url)
            print(f"Timeout exceeded when GETting {url}")
            raise err

    def hash_data(self, data: bytes | bytearray | memoryview) -> str:
        """Create an SRI hash from some data

        data: A bytes-like object to hash

        returns: The SRI hash (eg sha256-HASH)
        """
        sha_hash = hashlib.new(self.__hash_alg)
        sha_hash.update(data)
        digest: bytes = sha_hash.digest()
        b64: str = base64.b64encode(digest).decode(encoding="ascii")
        return f"{self.__hash_alg}-{b64}"
