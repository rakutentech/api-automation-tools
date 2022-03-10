import re
import json
import itertools as it


def generate_batch(method, headers, url, fr_pairs=None, cr_pairs=None, bad_header_count=1, include_query_params=False,
                   description='', body=None, api_tag='v1'):
    """
    This generates url batches to feed into the async_requests.request loader.

    Args:
        method (str): The method of the request.
        headers (dict): The headers of the request.
        url (str): A 200 type url(a passing request).
        fr_pairs (None|list|list<list>): Forbidden swap out pairs e.g. [id, forbidden_id].
        cr_pairs (None|list|list<list>): Expected codes to update/replace [old code, new code].
        bad_header_count (int): The amount of bad header possibilities used.
        include_query_params (bool): Whether to include query params in the bad url generation.
        description (str): A description of the request.
        body (dict): A json(dict) body of the request.
        api_tag (None|str): The tag or version of the api. The endpoint usually begins right after
                            e.g. /api/v1/ENDPOINT-START.
    Returns:
        batch (list<dict>): The list of 200-500 url combinations.
    """
    method = method.lower()
    good_code = {'get': '200', 'patch': '200', 'post': '201', 'put': '204', 'delete': '204'}[method]

    bad_headers = generate_bad_headers(headers)[:bad_header_count]

    query_params = ''
    if not include_query_params:
        if '?' in url:
            url_query_split = url.split('?')
            url = url_query_split[0]
            query_params = f'?{url_query_split[-1]}'

    invalid_urls = generate_bad_urls(url, '999', api_tag=api_tag)
    forbidden_urls = generate_bad_urls(url, replacements=fr_pairs, api_tag=api_tag)
    not_found_urls = generate_bad_urls(url, '0', api_tag=api_tag)

    if description:
        description += ' '
    batch = {
        good_code: [{'code': good_code, 'description': f'{description}good',
                     'method': method, 'headers': headers, 'url': url}],
        '400': [{'code': '400', 'description': f'{description}invalid', 'method': method, 'headers': headers, 'url': u}
                for u in invalid_urls],
        '401': [{'code': '401', 'description': f'{description}not auth', 'method': method, 'headers': h, 'url': url}
                for h in bad_headers],
        '403': [{'code': '403', 'description': f'{description}forbidden',
                 'method': method, 'headers': headers, 'url': u} for u in forbidden_urls],
        '404': [{'code': '404', 'description': f'{description}not found',
                 'method': method, 'headers': headers, 'url': u} for u in not_found_urls],
    }

    if cr_pairs:
        if type(cr_pairs[0]) is not list:
            cr_pairs = [cr_pairs]

        for crp in cr_pairs:
            matching_code = batch.get(str(crp[0])) or []
            for b in matching_code:
                b['code'] = f'{crp[1]}|{str(crp[0])}'

    batch = [i for b in batch.values() for i in b]
    for b in batch:
        url_split = b['url'].split('|')
        if url_split[-1].isdigit():
            b['url'] = url_split[0]
            b['code'] = f"{url_split[-1]}|{b['code']}"
        b['url'] += query_params

    if body:
        for b in batch:
            b['json'] = body

        json_body = json.dumps(body)
        good_batch = {'code': good_code, 'description': f'{description}good',
                      'method': method, 'headers': headers, 'url': url}
        batch += [{**good_batch, **{'json': json.loads(b), 'description': f'{description}invalid'},
                   'code': '400'} for b in generate_bad_urls(json_body, '999')]
        batch += [{**good_batch, **{'json': json.loads(b), 'description': f'{description}not found'},
                   'code': '404'} for b in generate_bad_urls(json_body, '0')]

    return [batch[0]] + sorted(batch[1:], key=lambda k: k['code'].split('|')[0])


def generate_unsafe_batch(method, headers, url, **kwargs):
    """
    This generates unsafe url batches to feed into the async_requests.request loader.

    Args:
        method (str): The method of the request.
        headers (dict): The headers of the request.
        url (str): A 200 type url(a passing request).
        kwargs (dict): See the below.
            json (dict): A body to send as json.
            data (data): A body to send as multi-part.
    Returns:
        batch (list<dict>): The list of 200-500 url combinations.
    """
    method = method.lower()
    batch_template = {'code': '', 'method': method, 'headers': headers, 'url': url}

    batch_bad_qp = []
    if '?' in url:
        url_query_split = url.split('?')
        url_no_qp = url_query_split[0]
        qp_json = {'?': {q.split('=')[0]: q.split('=')[1] for q in url_query_split[-1].split('&')}}
        bad_qp_json = generate_unsafe_bodies(qp_json)
        bad_qp = [f"?{'&'.join([f'{p[0]}={p[1]}' for p in b['?'].items()])}" for b in bad_qp_json]
        batch_bad_qp = [{**batch_template, **{'url': f'{url_no_qp}{b}'}, **kwargs} for b in bad_qp]

    batch_bad_bodies = []
    if kwargs:
        bad_bodies = generate_unsafe_bodies(kwargs)
        batch_bad_bodies = [{**batch_template, **b} for b in bad_bodies]

    return batch_bad_qp + batch_bad_bodies


def generate_bad_headers(headers):
    """
    This generates a list of bad headers.

    Args:
        headers (dict): The headers of the request.

    Returns:
        bad_headers (list<dict>): The list of bad headers of the request.
    """
    headers = headers.copy()

    bad_headers = [{**headers.copy(), **{key: re.sub(r'[a-zA-Z]', 'a', re.sub(r'\d', '0', value))}}
                   for key, value in headers.items() if 'Content-Type' not in key]

    if len(bad_headers) > 1:
        bad_headers += [{key: re.sub(r'\d', '0', value) if 'Content-Type' not in key else value
                         for key, value in headers.items()}]

    return bad_headers


def generate_bad_urls(url, sub_value=None, replacements=None, api_tag='v1'):
    """
    This generates a list of bad urls.

    Args:
        url (str): A 200 type url(a passing request).
        sub_value (str): A numerical substitute value for invalidating(i.e. '999') or converting to not found(i.e. '0').
        replacements (None|list|list<list>): Forbidden swap out pairs e.g. [id, forbidden_id].
        api_tag (None|str): The tag or version of the api. The endpoint usually begins right after
                            e.g. /api/v1/ENDPOINT-START.

    Returns:
        bad_urls (list): The list of bad urls for the request.
    """
    if not sub_value and not replacements:
        return []
    
    url = url[:]
    url_parts = url.split('/')

    tag_index = 0
    if api_tag in url_parts:
        tag_index = url_parts.index(api_tag)

    if sub_value:
        replacements = [[p, re.sub(r'[a-z]', 'a', re.sub(rf'\d(?<!{api_tag})', sub_value, p))]
                        for p in url_parts[tag_index + 1:] if re.findall(r'\d+', p)]
        if not replacements:
            return []
    elif replacements and type(replacements[0]) is not list:
        replacements = [replacements]

    root = '/'.join(url[:].split('/')[:tag_index + 1]) + '/'
    back = '/'.join(url[:].split('/')[tag_index + 1:])

    num_combinations = len(set([r[0] for r in replacements]))
    combinations = [c for c in it.combinations(replacements, num_combinations)
                    if len(set([i[0] for i in c])) > num_combinations - 1]

    bad_urls = []
    for comb in combinations:
        bad_url = root + back[:]
        if bad_url[-1] == '/':
            bad_url = bad_url[:-1]
        codes = []

        for c in comb:
            bad_url = bad_url.replace(c[0], c[1])

            _code = ''
            if len(c) > 2:
                codes.append(c[2])
                _code = f'|{c[2]}'

            if sub_value:
                _bad_url = root + back[:]
                if _bad_url[-1] == '/':
                    _bad_url = _bad_url[:-1]

                _bad_url = _bad_url.replace(c[0], c[1])
                _bad_url = f'{_bad_url}{_code}'
                if _bad_url not in bad_urls:
                    bad_urls.append(_bad_url)

        code = ''
        if codes:
            code = f'|{sorted(codes)[-1]}'

        bad_url += code
        if bad_url not in bad_urls:
            bad_urls.append(bad_url)

    return bad_urls


def generate_unsafe_bodies(body):
    """
    This creates a bad body from a good one.

    Args:
        body (dict): The body to be sent.

    Returns:
        bad_bodies (list): Bad bodies.
    """
    conditions = [" '--", "'+OR+1=1--", "' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK"]
    queries = ["SELECT version() --", "select database_to_xml(true,true,'');",
               "UNION SELECT * FROM information_schema.tables --"]
    germs = conditions + queries

    body_type = list(body.keys())[0]
    bad_values = [{key: f'{value} {g}'} for g in germs for key, value in body[body_type].items() if 'file' not in key]
    return [{body_type: {**body[body_type], **b}} for b in bad_values]
