import time, psutil, requests, traceback

def freeze(sleep_seconds=5):
    time.sleep(sleep_seconds)

def format_num_string(input_string):
    return(input_string.replace(',', '').replace('X', ''))

def check_duplicate_process(script_name_func):
    pid_list = []
    for process in psutil.process_iter():
        # 檢查pid是否存在、是否以python執行、python執行的檔案是否為該排程
        try:
            process_command = ' '.join(process.cmdline())
        except:
            continue
        if psutil.pid_exists(process.pid) \
        and 'python' in process_command.lower() \
        and script_name_func in process_command \
        and '/bin/bash -c ' not in process_command:
            pid_list.append(process.pid)
    # 代表包含這個程式在內，有兩個以上相同的排程正在運行
    return(True if len(pid_list)>=2 else False)

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
