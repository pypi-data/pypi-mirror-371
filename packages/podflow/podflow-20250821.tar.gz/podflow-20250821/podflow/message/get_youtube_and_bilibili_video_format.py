# podflow/message/get_youtube_and_bilibili_video_format.py
# coding: utf-8

from podflow import gVar
from podflow.basic.write_log import write_log
from podflow.bilibili.get import get_bilibili_cid
from podflow.httpfs.progress_bar import progress_bar
from podflow.message.media_format import media_format


def one_format(id_update_format, id_num):
    entry_id_update_format = id_update_format[0]
    gVar.video_id_update_format[id_num]["url"] = entry_id_update_format["url"]
    gVar.video_id_update_format[id_num]["format"] = entry_id_update_format[
        "duration_and_id"
    ]
    gVar.video_id_update_format[id_num]["title"] = entry_id_update_format["title"]
    gVar.video_id_update_format[id_num]["timestamp"] = entry_id_update_format[
        "timestamp"
    ]
    gVar.video_id_update_format[id_num]["description"] = entry_id_update_format[
        "description"
    ]
    gVar.video_id_update_format[id_num]["main"] = id_num
    gVar.video_id_update_format[id_num]["image"] = entry_id_update_format["image"]
    gVar.video_id_update_format[id_num]["download"] = entry_id_update_format["download"]


# YouTube&哔哩哔哩视频信息模块
def get_youtube_and_bilibili_video_format(
    id_num, stop_flag,
    video_format_lock,
    prepare_animation,
    ratio_part,
    ratio_part_lock,
):
    url = gVar.video_id_update_format[id_num]["url"]
    media = gVar.video_id_update_format[id_num]["media"]
    quality = gVar.video_id_update_format[id_num]["quality"]
    id_update_format = media_format(
        url,
        id_num,
        media,
        quality,
        gVar.video_id_update_format[id_num]["cookie"],
    )
    if "youtube" in url:
        for fail_info in ["年龄限制", "需登录", "请求拒绝", "无法获取音频ID"]:
            if fail_info in id_update_format:
                if gVar.youtube_cookie:
                    gVar.video_id_update_format[id_num][
                        "cookie"
                    ] = "channel_data/yt_dlp_youtube.txt"
                    id_update_format = media_format(
                        url,
                        id_num,
                        media,
                        quality,
                        gVar.video_id_update_format[id_num]["cookie"],
                    )
                    if fail_info in id_update_format:
                        id_update_format = f"\033[31m{fail_info}\033[0m(Cookies错误)"
                else:
                    id_update_format = f"\033[31m{fail_info}\033[0m(需要Cookies)"
                break
    else:
        if gVar.channelid_bilibili[gVar.video_id_update_format[id_num]["name"]]["AllPartGet"]:
            power = gVar.video_id_update_format[id_num]["power"]
        else:
            power = get_bilibili_cid(id_num, gVar.video_id_update_format[id_num]["name"])[2]
        if power is True and (
            "试看" in id_update_format
            or "提取器错误" in id_update_format
            or id_update_format == "无法获取音频ID"
        ):
            id_update_format = "\033[31m充电专属\033[0m"
    if isinstance(id_update_format, list):
        if len(id_update_format) == 1:
            one_format(id_update_format, id_num)
        else:
            entrys_id = []
            for entry_id_update_format in id_update_format:
                entry_id = entry_id_update_format["id"]
                entrys_id.append(entry_id)
                gVar.video_id_update_format[entry_id] = {
                    "id": gVar.video_id_update_format[id_num]["id"],
                    "media": media,
                    "quality": quality,
                    "url": entry_id_update_format["url"],
                    "name": gVar.video_id_update_format[id_num]["name"],
                    "cookie": gVar.video_id_update_format[id_num]["cookie"],
                    "format": entry_id_update_format["duration_and_id"],
                    "title": entry_id_update_format["title"],
                    "timestamp": entry_id_update_format["timestamp"],
                    "description": entry_id_update_format["description"],
                    "main": id_num,
                    "image": entry_id_update_format["image"],
                    "download": entry_id_update_format["download"],
                    "backward_update": gVar.video_id_update_format[id_num][
                        "backward_update"
                    ],
                }
            gVar.video_id_update_format[id_num] = entrys_id
    else:
        with video_format_lock:
            stop_flag[0] = "error"
            prepare_animation.join()
            gVar.video_id_failed.append(id_num)
            write_log(
                f"{gVar.video_id_update_format[id_num]['name']}|{id_num}|{id_update_format}",
                None,
                True,
                False,
            )
            del gVar.video_id_update_format[id_num]
    with ratio_part_lock:
        # 主进度条更新
        progress_bar(ratio_part, 0.199)
