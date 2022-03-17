from collections import OrderedDict
opendata_url = 'https://quality.data.gov.tw/dq_download_json.php'
opendata_params_dict = OrderedDict()
opendata_params_dict['上市公司基本資料'] = {
    'nid':'18419',
    'md5_url':'04541d53fd5cbeb2803e0fe4becc4b97'
}
opendata_params_dict['上櫃股票基本資料'] = {
    'nid':'25036',
    'md5_url':'1aae8254db1d14b0d113dd93f2265d06'
}

prefix_dict = OrderedDict()
prefix_dict['上市公司基本資料'] = 'tse'
prefix_dict['上櫃股票基本資料'] = 'otc'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
    'origin': 'https://invest.cnyes.com',
    'Referer': 'https://invest.cnyes.com/',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'x-cnyes-app': 'unknown',
    'x-platform': 'WEB, WEB',
    'x-system-kind': 'FUND_OLD_DRIVER',
}

opendata_folder_dir = f"/app/opendata/"

cnyes_history_api_url = 'https://ws.api.cnyes.com/ws/api/v1/charting/history?'
sh_params_template = {
    'resolution': 'D',
    'quote': '1',
}
key_mapping_dict = {
    'c': 'close',
    'h': 'high',
    'l': 'low',
    'o': 'open',
    'v': 'trade_count',
    't': 'date',
}
################################
stock_api_url = 'http://stock_api/'
stock_api_prophet_url = f'{stock_api_url}predict/prophet'
################################
result_folder_dir = '/app/result/'
################################
cnyes_buysell_api_url = 'https://marketinfo.api.cnyes.com/mi/api/v1/investors/buysell/'
