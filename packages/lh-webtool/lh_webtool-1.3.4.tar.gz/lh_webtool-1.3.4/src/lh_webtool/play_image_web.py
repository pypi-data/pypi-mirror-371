# -*- encoding: utf-8 -*-
"""
@File    :   play_image_web.py
@Time    :   2024/03/23 10:41:16
@Author  :   lihao57
@Version :   1.0
@Contact :   lihao57@baidu.com
"""


import os
import shutil
import json
import glob
import pywebio
import pywebio.output as output
import pywebio.pin as pin
import pywebio.session as session
from pywebio.platform.flask import webio_view
import logging
import time
import argparse
import socket
from flask import Flask, render_template, send_from_directory
from lh_webtool.crawler import Crawler

app = Flask(__name__)
image_urls = []
local_path = ""


def get_local_ip():
    """get local ip"""
    # 获取本机主机名
    hostname = socket.gethostname()
    # 获取本机 IP 地址
    local_ip = socket.gethostbyname(hostname)
    return local_ip


@app.route("/images")
def index():
    """index"""
    global image_urls
    return render_template("play_image.html", image_urls=image_urls)


@app.route("/image/<path:filename>")
def serve_image(filename):
    """serve image"""
    global local_path
    return send_from_directory(local_path, filename)


class TaskManager:
    """
    TaskManager

    Parameterars:
        title (str): web title
        host (str): web host
        port (int): web port
    """

    def __init__(
        self,
        title,
        host,
        port,
    ):
        self.title = title
        self.host = host
        self.port = port

        # 获取当前执行脚本的绝对路径
        current_file = os.path.abspath(__file__)
        self.cache_path = os.path.join(os.path.dirname(current_file), "static")
        logging.info("cache path: {}".format(self.cache_path))
        self.crawler = Crawler()

        pywebio.config(title=self.title)
        app.add_url_rule(
            "/",
            "webio_view",
            webio_view(self.display_task),
            methods=["GET", "POST"],
        )
        app.run(debug=False, host=self.host, port=self.port)

    def display_task(self):
        """display task"""
        session.set_env(title=self.title)
        output.put_row(
            [
                pin.put_input(name="url_or_path", value=pin.pin["url_or_path"], placeholder="图像数据url/本地路径"),
                output.put_button(label="确认", onclick=self.confirm_callback, disabled=False),
            ],
            size="auto",
        )
        pin.put_checkbox(
            name="cache",
            options=[{"label": "开启缓存", "value": "开启缓存", "selected": False}],
        )
        default_config = """
{
    "name": "a",
    "url_key": "href",
    "pattern": ".*?.(?:jpg|png)",
    "attrs": {},
    "ext": "jpg|png"
}
"""
        pin.put_textarea(
            name="config",
            label="配置",
            value=default_config,
            rows=8,
            code={"mode": "json", "theme": "darcula"},
        )

    def confirm_callback(self):
        """confirm callback"""
        global image_urls
        url_or_path = pin.pin["url_or_path"]
        cache = pin.pin["cache"]
        config = pin.pin["config"]
        logging.info("url_or_path: {}".format(url_or_path))
        logging.info("config: {}".format(config))

        # parse config
        try:
            config = json.loads(config)
        except Exception as e:
            logging.error(e)
            output.toast(content="配置不是一个合法的json字典", duration=1)
            return

        name = config.get("name", None)
        url_key = config.get("url_key", None)
        pattern = config.get("pattern", None)
        attrs = config.get("attrs", {})
        ext = config.get("ext", None)

        if url_or_path.startswith("http://") or url_or_path.startswith("https://"):  # 网络图像
            if name is None:
                output.toast(content="配置必须包含`name`", duration=1)
                return
            elif url_key is None:
                output.toast(content="配置必须包含`url_key`", duration=1)
                return
            elif pattern is None:
                output.toast(content="配置必须包含`pattern`", duration=1)
                return
            elif not isinstance(attrs, dict):
                output.toast(content="`attrs`必须是一个字典", duration=1)
                return

            try:
                url_links = self.crawler.crawl(url_or_path, name, url_key, pattern, attrs)
                if len(url_links) == 0:
                    output.toast(content="图像链接获取失败，请重新设置`url`", duration=1)
                    return
                logging.info("url_links: {}".format("\n".join(url_links)))

                if cache:
                    if os.path.exists(self.cache_path):
                        shutil.rmtree(self.cache_path)
                    image_urls = self.crawler.download(url_links, self.cache_path)
                    logging.info("image number: {}".format(len(image_urls)))
                    if len(image_urls) == 0:
                        output.toast(content="图像下载失败，请重试", duration=1)
                        return
                    image_urls = ["static/" + os.path.basename(image_url) for image_url in image_urls]
                else:
                    image_urls = url_links
            except ValueError as e:
                logging.error(e)
                output.toast(content="url无效，请重新设置", duration=1)
        else:  # 本地图像
            global local_path
            local_path = os.path.abspath(url_or_path)
            if ext is None:
                output.toast(content="配置必须包含`ext`", duration=1)
                return

            exts = ext.split("|")
            image_urls = []
            for ext in exts:
                image_urls += glob.glob(os.path.join(local_path, f"*.{ext}"))
            image_urls = [os.path.basename(image_url) for image_url in image_urls]

        image_urls = sorted(image_urls)
        output.toast(content="图像数量：{}".format(len(image_urls)), duration=1)
        time.sleep(0.2)
        if not image_urls:
            return

        # 在新窗口中打开 Flask 页面
        session.run_js(f'window.open("http://{self.host}:{self.port}/images", name="play image")')


def main():
    """main"""
    # set base logging config
    fmt = "[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s] %(message)s"
    logging.basicConfig(format=fmt, level=logging.INFO)

    # arg
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, help="title", default="在线图像播放器")
    parser.add_argument("--host", type=str, help="host", default=get_local_ip())
    parser.add_argument("--port", type=int, help="port", default=8082)
    args = parser.parse_args()
    print(args)

    t1 = time.time()
    TaskManager(**vars(args))

    t2 = time.time()
    logging.info("total time: {}".format(t2 - t1))


if __name__ == "__main__":
    main()
