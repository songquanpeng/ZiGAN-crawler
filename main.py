import argparse
import asyncio
import os
import shutil
import time

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from tqdm import tqdm

save_path = "None"
tmp_path = os.path.join('archive', 'tmp')
os.makedirs(tmp_path, exist_ok=True)


async def handle_response(response):
    if response.ok and response.request.resource_type == "image":
        filename = response.url.split('/')[-1]
        with open(os.path.join(tmp_path, f"{filename}"), 'wb') as f:
            content = await response.body()
            f.write(content)


async def main(args):
    if args.save_name is None:
        args.save_name = f"cid_{args.cid}"
    global save_path
    save_path = os.path.join('data', args.save_name)
    os.makedirs(save_path, exist_ok=True)
    async with async_playwright() as p:
        if args.debug:
            browser = await p.webkit.launch(headless=False, slow_mo=50)
        else:
            browser = await p.webkit.launch()
        page = await browser.new_page()
        page.on('response', handle_response)
        pbar = tqdm(range(args.start_pos, args.total_num, args.step), total=args.total_num // args.step)
        for pos in pbar:
            pbar.set_description(f"Pos: {pos}")
            url = f"http://163.20.160.14/~word/modules/myalbum/viewcat.php?pos={pos}&cid={args.cid}&num={args.step}&orderby=titleA"
            await page.goto(url)
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            content = soup.find_all(id='content')[0]
            image_table = content.find_all("table")[2]
            images = image_table.find_all("img")
            old2new = {}
            for image in images:
                if image.has_attr('alt') and image['alt'] != "":
                    alt = image['alt']
                    src = image['src']
                    ext = src.split('.')[-1]
                    old_filename = src.split('/')[-1]
                    old2new[old_filename] = f"{alt}.{ext}"
            for image in os.listdir(tmp_path):
                if image in old2new:
                    shutil.copy(os.path.join(tmp_path, image), os.path.join(save_path, old2new[image]))
                os.remove(os.path.join(tmp_path, image))
            time.sleep(args.wait_time)
        await browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wait_time', type=float, default=5)
    parser.add_argument('--start_pos', type=int, default=0)
    parser.add_argument('--cid', type=int, required=True, help="each album has a unique cid")
    parser.add_argument('--step', type=int, default=50)
    parser.add_argument('--total_num', type=int, required=True)
    parser.add_argument('--save_name', type=str)
    parser.add_argument('--debug', action='store_true')
    cfg = parser.parse_args()
    asyncio.run(main(cfg))
