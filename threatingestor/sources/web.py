import requests

from threatingestor.sources import Source


class Plugin(Source):

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def run(self, saved_state):
        # read saved state and set HTTP headers
        headers = {}
        if saved_state:
            # if both last modified and etag, set both
            # otherwise just interpret the whole field as last modified
            last_modified = saved_state

            if len(saved_state.split(';')) == 2:
                last_modified, etag = saved_state.split(';')
                headers['If-None-Match'] = etag

            headers['If-Modified-Since'] = last_modified

        # send head first to check 304
        response = requests.head(self.url, headers=headers)

        # if not modified, return immediately
        if response.status_code == 304:
            return saved_state, []

        # otherwise, do the full request
        response = requests.get(self.url, headers=headers)

        # form saved state
        last_modified = response.headers.get('Last-Modified')
        etag = response.headers.get('Etag')

        if etag:
            saved_state = ';'.join([last_modified, etag])
        else:
            saved_state = last_modified

        # process text
        artifact_list = self.process_element(response.text, self.url, include_nonobfuscated=True)

        return saved_state, artifact_list