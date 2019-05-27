import time

resources = []
current_milli_time = lambda: int(round(time.time() * 1000))


def check(url):
    """Check if a url is in cache, returning the content
    :param url: The url from browser
    """
    resource = is_in_cache(url)
    if resource != None:
        return resource['content']
    return None


def update(url, content):
    """update the content of a url if exists, create a new entry in opossite, and increase the counter
    :param url: The url from browser
    :param content: HTML page to storage
    """
    resource = is_in_cache(url)
    if resource == None:
        resource = {
            'url': url,
            'content': content,
            'counter': 0,
            'lastUsed': current_milli_time()
        }
        resources.append(resource)
    else:
        resource['content'] = content

    add_to_counter(resource)


def add_to_counter(resource):
    """increase the counter of a resource and order the list of resources
    :param resource: The concrete html page
    """
    resource['counter'] = resource['counter'] + 1
    order_list(resources)


def order_list(resources):
    """Order the list of resources per number of the counter and for the tiebreaker last used resource
    :param resource: The concrete html page
    """
    sort = sorted(resources, key=lambda x: (x['counter'], x['lastUsed']), reverse=True)
    for i in range(2, len(sort)):
        sort[i]['content'] = None
    resources = sort


def is_in_cache(url):
    """Verify if the uri is in cache, returning the resource dicionary
    :param content: HTML page to storage
    """
    for resource in resources:
        if resource['url'] == url:
            return resource
    return None

# def fetch_from_server(filename):
#     url = 'http://localhost:8000' + filename
#
#     try:
#         response = webbrowser.open(url, new=1)
#         # Grab the header and content from the server req
#         # response_headers = response.info()
#         content = response.read().decode('utf-8')
#         return content
#     except HTTPError:
#         return None
#
#
# def fetch_from_cache(filename):
#     try:
#         # Check if we have this file locally
#         fin = open('cache' + filename)
#         content = fin.read()
#         fin.close()
#         # If we have it, let's send it
#         return content
#     except IOError:
#         return None
#
#
# def save_in_cache(filename, content):
#     print('Saving a copy of {} in the cache'.format(filename))
#     cached_file = open('cache' + filename, 'w')
#     cached_file.write(content)
#     cached_file.close()
#
#
# def fetch_file(filename):
#
#     # Let's try to read the file locally first
#     file_from_cache = fetch_from_cache(filename)
#
#     if file_from_cache:
#         print('Fetched successfully from cache.')
#         return file_from_cache
#     else:
#         print('Not in cache. Fetching from server.')
#         file_from_server = fetch_from_server(filename)
#
#         if file_from_server:
#             save_in_cache(filename, file_from_server)
#             return file_from_server
#         else:
#             return None
