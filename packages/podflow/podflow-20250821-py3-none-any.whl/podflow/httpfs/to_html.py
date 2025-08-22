# podflow/httpfs/to_html.py
# coding: utf-8

import re
import html


def ansi_to_html(ansi_text):
    html_output = ""
    ansi_codes = {
        "\033[30m": "ansi-30m",  # 黑色
        "\033[31m": "ansi-31m",  # 红色
        "\033[32m": "ansi-32m",  # 绿色
        "\033[33m": "ansi-33m",  # 黄色
        "\033[34m": "ansi-34m",  # 蓝色
        "\033[35m": "ansi-35m",  # 品红
        "\033[36m": "ansi-36m",  # 青色
        "\033[37m": "ansi-37m",  # 白色
        "\033[90m": "ansi-90m",  # 亮黑色
        "\033[91m": "ansi-91m",  # 亮红色 
        "\033[92m": "ansi-92m",  # 亮绿色
        "\033[93m": "ansi-93m",  # 亮黄色
        "\033[94m": "ansi-94m",  # 亮蓝色
        "\033[95m": "ansi-95m",  # 亮品红
        "\033[96m": "ansi-96m",  # 亮青色
        "\033[97m": "ansi-97m",  # 亮白色
        "\033[0m": "",  # 重置
    }
    inside_span = False

    parts = re.split(r"(\033\[\d+m)", ansi_text)

    for part in parts:
        if part in ansi_codes:
            if style := ansi_codes[part]:
                if inside_span:
                    html_output += "</span>"
                html_output += f'<span class="{style}">'
                inside_span = True
            elif inside_span:  # Reset code
                html_output += "</span>"
                inside_span = False
        else:
            escaped_part = html.escape(part)
            html_output += escaped_part

    if inside_span:
        html_output += "</span>"
    html_output = re.sub(r'^\s', '', html_output)
    html_output = re.sub(r'\s+$', '', html_output)
    return html_output


def qrcode_to_html(url):
    return f'<span class="qrcode-container" data-url="{url}"></span>'
