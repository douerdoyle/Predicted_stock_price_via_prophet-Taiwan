import os, time, requests, traceback

class RequestsRetryer():
    def __init__(self, use_tor=True, tor_req_limit=20):
        self.tor_req_limit = tor_req_limit
        self.tor_req_count = 0
        self.tor_pause_s = 5
        self.retry_limit = 5
        self.session = requests.session()
        self.use_tor = use_tor
        self.sleep_status = not self.use_tor
        if self.use_tor:
            self.session.proxies = {x: 'socks5://127.0.0.1:9050' for x in ['http', 'https']}

    # def restart_tor(self):
    #     os.system("killall tor")
    #     time.sleep(self.tor_pause_s)

    # def before_req(self):
    #     self.tor_req_count+=1
    #     if self.tor_req_count>=self.tor_req_limit:
    #         self.restart_tor()
    #         self.tor_req_count = 0

    def requests_retryer(self, method, *args, **kwargs):
        err_msg = None
        nnn = 0
        while True:
            nnn+=1
            # if self.use_tor:
            #     self.before_req()
            try:
                rsp = getattr(self.session, method)(*args, **kwargs)
            except:
                err_msg = traceback.format_exc()
                continue
            if nnn>=self.retry_limit:
                raise Exception(err_msg)
            if self.sleep_status:
                freeze()
            return rsp
