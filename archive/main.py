import argparse
import time

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cookie': 'PHPSESSID=hao15657qndu9kbguslnb79ne6',
    'Host': '163.20.160.14',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://163.20.160.14/~word/modules/myalbum/viewcat.php?pos=0&cid=38&num=50&orderby=titleA',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
}


def fetch_image_info(args):
    failed_url = []
    image_info = []
    for pos in range(args.start_pos, args.total_num, args.step):
        url = f"http://163.20.160.14/~word/modules/myalbum/viewcat.php?pos={pos}&cid={args.cid}&num={args.step}&orderby=titleA"
        print(f"Processing [pos={pos}&cid={args.cid}]...", end=' ')
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            failed_url.append(url)
            print("Failed!")
        else:
            html = res.text
            soup = BeautifulSoup(html)
            content = soup.find_all(id='content')[0]
            image_table = content.find_all("table")[1]
            print("Done.")
        time.sleep(args.wait_time)


def main(args):
    fetch_image_info(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wait_time', type=float, default=5)
    parser.add_argument('--start_pos', type=int, default=0)
    parser.add_argument('--cid', type=int, required=True, help="each album has a unique cid")
    parser.add_argument('--step', type=int, default=50)
    parser.add_argument('--total_num', type=int, required=True)
    parser.add_argument('--save_path', type=str)
    cfg = parser.parse_args()
    main(cfg)
