# podflow/message/update_information_display.py
# coding: utf-8

import re
import os
from podflow import gVar
from podflow.basic.write_log import write_log
from podflow.message.want_retry import want_retry


def skip_display(name, channelid_key, channelid_value, id_update):
    if name == "YouTube":
        failed_count = gVar.channelid_youtube[channelid_value]["want_retry_count"]
    elif name == "BiliBili":
        failed_count = gVar.channelid_bilibili[channelid_value]["want_retry_count"]
    else:
        failed_count = 0
    for video_id in id_update[channelid_key]:
        if want_retry(video_id, failed_count):
            return False
    return True


# 输出需要更新的信息模块
def update_information_display(
    channelid_ids_update, content_id_update, content_id_backward_update, name
):
    if not channelid_ids_update:
        return
    print_channelid_ids_update = f"需更新的{name}频道:\n"
    # 获取命令行字节宽度
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 47
    # 尝试拆分输出
    try:
        for channelid_key, channelid_value in channelid_ids_update.items():
            if len(print_channelid_ids_update) != len(name) + 8:
                if (
                    len(
                        re.sub(
                            r"\033\[[0-9;]+m",
                            "",
                            print_channelid_ids_update.split("\n")[-1],
                        ).encode("GBK")
                    )
                    + len(f" | {channelid_value}".encode("utf-8"))
                    <= terminal_width
                ):
                    print_channelid_ids_update += " | "
                else:
                    print_channelid_ids_update += "\n"
            if (
                channelid_key in content_id_update
                and channelid_key in content_id_backward_update
            ):
                if skip_display(
                    name, channelid_key, channelid_value, content_id_update
                ) and skip_display(
                    name, channelid_key, channelid_value, content_id_backward_update
                ):
                    print_channelid_ids_update += f"\033[97m{channelid_value}\033[0m"
                else:
                    print_channelid_ids_update += f"\033[34m{channelid_value}\033[0m"
            elif channelid_key in content_id_update:
                if skip_display(
                    name, channelid_key, channelid_value, content_id_update
                ):
                    print_channelid_ids_update += f"\033[97m{channelid_value}\033[0m"
                else:
                    print_channelid_ids_update += f"\033[32m{channelid_value}\033[0m"
            elif channelid_key in content_id_backward_update:
                if skip_display(
                    name, channelid_key, channelid_value, content_id_backward_update
                ):
                    print_channelid_ids_update += f"\033[97m{channelid_value}\033[0m"
                else:
                    print_channelid_ids_update += f"\033[36m{channelid_value}\033[0m"
            else:
                print_channelid_ids_update += f"\033[33m{channelid_value}\033[0m"
    # 如果含有特殊字符将使用此输出
    except Exception:
        len_channelid_ids_update = len(channelid_ids_update)
        count_channelid_ids_update = 1
        for channelid_key, channelid_value in channelid_ids_update.items():
            if (
                channelid_key in content_id_update
                and channelid_key in content_id_backward_update
            ):
                print_channelid_ids_update += f"\033[34m{channelid_value}\033[0m"
            elif channelid_key in content_id_update:
                print_channelid_ids_update += f"\033[32m{channelid_value}\033[0m"
            elif channelid_key in content_id_backward_update:
                print_channelid_ids_update += f"\033[36m{channelid_value}\033[0m"
            else:
                print_channelid_ids_update += f"\033[33m{channelid_value}\033[0m"
            if count_channelid_ids_update != len_channelid_ids_update:
                if count_channelid_ids_update % 2 != 0:
                    print_channelid_ids_update += " | "
                else:
                    print_channelid_ids_update += "\n"
                count_channelid_ids_update += 1
    write_log(print_channelid_ids_update)
