import itertools as it
import re
from copy import deepcopy
from urllib.parse import urlparse

import orjson


def generate_batch(
    method: str,
    headers: dict,
    url: str,
    description: str = "",
    fr_pairs: None | list | list[list] = None,
    bad_header_count: int = 1,
    include_query_params: bool = True,
    full: bool = False,
    json: None | dict = None,
    data: None | dict = None,
    unsafe_bodies: bool = False,
) -> list[dict]:
    """
    This generates url batches to feed into the async_requests.request loader.

    Args:
        method: The method of the request.
        headers: The headers of the request.
        url: A 200 type url(a passing request).
        description: A description of the request.
        fr_pairs: Forbidden swap out pairs e.g. [id, forbidden_id].
        bad_header_count: The amount of bad header possibilities used.
        include_query_params: Whether to include query params in the bad url generation.
        full: Whether to generate bad values on all strings instead of strings with numbers.
        json: A json (dict) body of the request.
        data: A data (dict) body of the request.
        unsafe_bodies: Whether to include unsafe bodies in the batch.
    Returns:
        batch: The list of 200-500 url combinations.
    """
    method = method.lower()
    good_code = {
        "get": "200",
        "patch": "200",
        "post": "201",
        "put": "204",
        "delete": "204",
    }[method]

    bad_headers = generate_bad_bodies(headers, "0", original_keys=True)[
        :bad_header_count
    ]

    invalid_urls = generate_bad_urls(
        url, "999", include_query_params=include_query_params, full=full
    )
    forbidden_urls = generate_bad_urls(
        url, replacements=fr_pairs, include_query_params=include_query_params, full=full
    )
    not_found_urls = generate_bad_urls(
        url, "0", include_query_params=include_query_params, full=full
    )
    clean_url = url.replace(";", "")
    if description:
        description += " "

    batch = [
        [
            {
                "code": good_code,
                "description": f"{description}good",
                "method": method,
                "headers": headers,
                "url": clean_url,
            }
        ],
        [
            {
                "code": "400",
                "description": f"{description}invalid",
                "method": method,
                "headers": headers,
                "url": u,
            }
            for u in invalid_urls
        ],
        [
            {
                "code": "401",
                "description": f"{description}not auth",
                "method": method,
                "headers": h,
                "url": clean_url,
            }
            for h in bad_headers
        ],
        [
            {
                "code": "403",
                "description": f"{description}forbidden",
                "method": method,
                "headers": headers,
                "url": u,
            }
            for u in forbidden_urls
        ],
        [
            {
                "code": "404",
                "description": f"{description}not found",
                "method": method,
                "headers": headers,
                "url": u,
            }
            for u in not_found_urls
        ],
    ]
    batch = [i for b in batch for i in b]

    if json or data:
        body = json
        key = "json"
        if data:
            body = data
            key = "data"

        for b in batch:
            b[key] = body

        good_batch = {
            "code": good_code,
            "description": f"{description}good",
            "method": method,
            "headers": headers,
            "url": clean_url,
        }
        batch += [
            {
                **good_batch,
                **{key: b, "description": f"{description}invalid"},
                "code": "400",
            }
            for b in generate_bad_bodies(body, "999")
        ]
        batch += [
            {
                **good_batch,
                **{key: b, "description": f"{description}not found"},
                "code": "404",
            }
            for b in generate_bad_bodies(body, "0")
        ]

        if unsafe_bodies:
            batch += [
                {
                    **good_batch,
                    **{key: b, "description": f"{description}unsafe bodies"},
                    "code": "???",
                }
                for b in generate_unsafe_bodies(body)
            ]

    return [batch[0]] + sorted(batch[1:], key=lambda k: k["code"].split("|")[0])


def generate_bad_urls(
    data: str,
    sub_value: None | str = None,
    replacements: None | list | list[list] = None,
    include_query_params: bool = True,
    full: bool = False,
) -> list:
    """
    This generates a list of bad urls e.g. path params and query params.

    Args:
        data: A 200 type url.
        sub_value: A numerical substitute value for invalidating(i.e. '999')
                   or converting to not found(i.e. '0').
        replacements: Forbidden swap out pairs e.g. [id, forbidden_id].
        include_query_params: Whether to include bad generations of query params.
        full: Whether to generate bad values on all strings instead of strings with numbers.

    Returns:
        bad_datas: The list of bad datas for the request.
    """
    if not sub_value and not replacements:
        return []

    _data = data[:]
    parsed = urlparse(_data)
    _data = _data.replace(";", "")

    query = parsed.query
    if not include_query_params:
        query = ""

    path = parsed.path
    if ";" not in parsed.path:
        path = f";{path}"
    path, params = path.split(";")
    params += "/" + re.sub(r"[?=&]", "/", query)

    return generate_bad_data(sub_value, replacements, full, _data, params)


def generate_bad_bodies(
    data: dict,
    sub_value: None | str = None,
    replacements: None | list | list[list] = None,
    full: bool = False,
    original_keys: bool = False,
) -> list:
    """
    This generates a list of bad bodies.

    Args:
        data: A 200 type body.
        sub_value: A numerical substitute value for invalidating(i.e. '999')
                   or converting to not found(i.e. '0').
        replacements: Forbidden swap out pairs e.g. [id, forbidden_id].
        full: Whether to generate bad values on all strings instead of strings with numbers.
        original_keys: Whether to keep the bad bodies with their original keys.

    Returns:
        bad_data: The list of bad datas for the request.
    """
    if not sub_value and not replacements:
        return []

    _data = deepcopy(data)

    incorruptible_fields = {}
    for key, value in data.items():
        if "file" in key or not isinstance(value, (int, float, str, dict)):
            incorruptible_fields[key] = _data.pop(key)

    _data = orjson.dumps(_data).decode()
    params = "/".join(f"{k}/{v}" for k, v in data.items())

    bad_data = generate_bad_data(sub_value, replacements, full, _data, params)
    bad_data = [orjson.loads(b) for b in bad_data]
    if original_keys:
        bad_data = [b for b in bad_data if all(k in data for k in b)]
    for b in bad_data:
        b.update(incorruptible_fields)
    return bad_data


def generate_bad_data(
    sub_value: str, replacements: list | list[list], full: bool, data: str, params: str
):
    """
    This generates a list of bad data.

    Args:
        sub_value: A numerical substitute value for invalidating(i.e. '999')
                   or converting to not found(i.e. '0').
        replacements: Forbidden swap out pairs e.g. [id, forbidden_id].
        full: Whether to generate bad values on all strings instead of strings with numbers.
        data: The original 200 type data object (str url or json).
        params: The parameters to corrupt.

    Returns:
        bad_datas: The list of bad datas for the request.
    """

    if sub_value:
        replacements = [
            [p, re.sub(r"[a-zA-Z]", "a", re.sub(r"\d", sub_value, p))]
            for p in params.split("/")
            if full or re.findall(r"\d+", p)
        ]
        if not replacements:
            return []
    elif replacements and type(replacements[0]) is not list:
        replacements = [replacements]

    num_combinations = len(set([r[0] for r in replacements]))
    combinations = [
        c
        for c in it.combinations(replacements, num_combinations)
        if len(set([i[0] for i in c])) > num_combinations - 1
    ]

    bad_datas = []
    for comb in combinations:
        bad_data = data[:]
        if bad_data[-1] == "/":
            bad_data = bad_data[:-1]

        for c in comb:
            bad_data = bad_data.replace(c[0], c[1])

            if sub_value:
                _bad_data = data[:]
                if _bad_data[-1] == "/":
                    _bad_data = _bad_data[:-1]

                _bad_data = re.sub(rf"\b{c[0]}\b", c[1], _bad_data)
                if _bad_data not in bad_datas:
                    bad_datas.append(_bad_data)

        if bad_data not in bad_datas:
            bad_datas.append(bad_data)

    return bad_datas


def generate_unsafe_bodies(body: dict) -> list[dict]:
    """
    This creates an unsafe body from a good one.

    Args:
        body: The body to be corrupted.

    Returns:
        bad_bodies: The unsafe bodies.
    """
    conditions = [
        " '--",
        "'+OR+1=1--",
        "' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
    ]
    queries = [
        "SELECT version() --",
        "select database_to_xml(true,true,'');",
        "UNION SELECT * FROM information_schema.tables --",
    ]
    germs = conditions + queries

    num_combinations = len(body)
    combinations = [
        c
        for c in it.combinations(germs, num_combinations)
        if len(set([i[0] for i in c])) > num_combinations - 1
    ]

    return [
        {k: f"{v} {p}" for k, v in body.items() if "file" not in k}
        for c in combinations
        for p in c
    ]
