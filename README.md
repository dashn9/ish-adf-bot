#Ish Web Bot
This Software Technology Is Used For Simulating Human Like Behaviour On. WebSites/WebPages.
Still In Progress, But Can Be Utilized If The System Is Thoroughly Understood.


Insert webdriver In Respective Browser Directory In ./SeleniumWebDrivers

iptables -A INPUT -p tcp --dport 10000 -j DROP #Execute this intruction on terminal. I noticed a lot of traffic were
sent to port 10000 on multiple ips with hostnames matching *.client.de

#216.58.223.227

    # don't use
    def save_cache(self):
        # Serialize the dictionary using pickle and write it to a file
        with open(bot_constants.FULL_DIRECTORY_PATH + '/web_cache.pickle', 'wb') as f:
            pickle.dump(self.web_cache, f)

    # don't use
    def web_cacher(self, request: request.Request, response: request.Response):
        if not isinstance(self.web_cache, dict):
            print(f"Bot Process Id {self.bot_process_id} <:::> Warning: You are attempting to cache a web resource, but"
                  f" you haven't initiated web caching yet")
            return False
        key = request.url
        # list of file types to cache
        file_types_to_cache = ["image/", "font/", "text/css"]
        if request.method == 'GET' and (any(resource_type in response.headers.get("content-type", "")
                                           for resource_type in file_types_to_cache)
                or "text/javscript" in response.headers.get("content-type", "") and bot_constants.WORKING_HOST in request.host):
            if key not in self.web_cache.keys():
                print(f"Bot Process Id {self.bot_process_id} <:::> caching url: {key}")
                response.request = request
                response.is_cache_copy = True
                self.web_cache[key] = response
                self.save_cache()
            else:
                print(f"Bot Process Id {self.bot_process_id} <:::> {key} is already in cache")

    def fetch_from_cache(self, key):
        if not isinstance(self.web_cache, dict):
            print(f"Bot Process Id {self.bot_process_id} <:::> Warning: You are attempting to fetch a web resource"
                  f" from cache but you haven't initiated web caching yet")
            return False
        return self.web_cache.get(key, False)

    def generate_response_if_cached(self, key, request: request.Request):
        cached_response = self.fetch_from_cache(key)
        if cached_response and cached_response.request.method == "GET":
            print(f"attempting to fetch {request.url}, type: {cached_response.headers.get('content-encoding')}")
            if "text/" in cached_response.headers.get("content-type", ""):
                cached_response.body = decode(cached_response.body, cached_response.headers.get('identity'))
                print("cached response body: ", cached_response.body)
                cached_response.body = cached_response.body.decode('utf-8')
            print(f"Bot Process Id {self.bot_process_id} <:::> {key} is cached, generating response")
            request.response = cached_response
