import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import arknights_toolkit as arkkit
from arclet.alconna import Alconna, Args, CommandMeta, Option
from arclet.entari.command import Match
from arknights_toolkit.update.main import fetch
from arknights_toolkit.gacha import ArknightsGacha, GachaUser

from arclet.entari import BasicConfModel, plugin_config, collect_disposes, command, Plugin, metadata, Session, Image
from arclet.entari.logger import log
from arclet.entari.localdata import local_data


__version__ = "0.2.0"


class Config(BasicConfModel):
    gacha_max: int = 300
    """单次抽卡最大次数，防止刷屏"""
    pure_text: bool = False
    """是否只使用纯文本输出，关闭图片输出以节省资源"""
    pool_file: str = ""
    """卡池文件路径，留空则使用默认路径"""
    proxy: Optional[str] = None
    """HTTP代理"""


metadata(
    "明日方舟抽卡模拟",
    [{"name": "RF-Tar-Railt", "email": "rf_tar_railt@qq.com"}],
    __version__,
    description="明模拟日方舟抽卡功能，支持模拟十连",
    urls={
        "homepage": "https://github.com/ArcletProject/entari-plugin-arkgacha",
    },
    config=Config,
)

_config = plugin_config(Config)

if _config.pool_file:
    pool_file = Path(_config.pool_file)
else:
    pool_file = local_data.get_data_file("arkgacha", "pool.json")


gacha = ArknightsGacha(
    pool_file,
    proxy=_config.proxy
)
user_cache_file = local_data.get_cache_file("arkgacha", "user.json")
if not user_cache_file.exists():
    userdata = {}
else:
    with user_cache_file.open("r", encoding="utf-8") as f:
        userdata = json.load(f)


gacha_cmd = Alconna(
    "方舟抽卡", Args["count", int, 10],
    Option("更新", help_text="更新抽卡卡池数据"),
    Option("帮助", help_text="显示帮助信息"),
    Option("模拟", help_text="模拟十连"),
    meta=CommandMeta(
        description="文字版抽卡，可以转图片发送",
        usage=f"方舟抽卡 [count = 10], count不会超过{_config.gacha_max}",
        example="方舟抽卡 10",
        compact=True
    )
)

gacha_cmd.shortcut("方舟十连", arguments=["模拟"])
gacha_cmd.shortcut("方舟卡池更新", arguments=["更新"])

logger = log.wrapper("[Arkgacha]")
plug = Plugin.current()


@plug.use("::startup")
async def _():
    if arkkit.need_init():
        await fetch(2, True, proxy=_config.proxy)
        base_path = Path(arkkit.__file__).parent / "resource"
        with (base_path / "ops_initialized").open("w+", encoding="utf-8") as _f:
            _f.write(arkkit.__version__)
        logger.info("初始化明日方舟抽卡模块完成")
    else:
        await fetch(2, False, proxy=_config.proxy)


@collect_disposes
def _save_user_data():
    with user_cache_file.open("w+", encoding="utf-8") as _f:
        json.dump(userdata, _f, ensure_ascii=False, indent=2)


disp = command.mount(gacha_cmd)


@disp.assign("帮助")
async def help_(session: Session):
    await session.send(
        "可用命令：\n"
        "方舟抽卡 [count = 10]\n"
        "方舟十连\n"
        "方舟抽卡帮助\n"
        "方舟卡池更新\n"
    )


@disp.assign("更新")
async def update_pool(session: Session):
    if new := (await gacha.update()):
        text = (
            f"更新成功，卡池已更新至{new.title}\n"
            "六星角色：\n" +
            "\n".join(f"{i.name} {'【限定】' if i.limit else '【常驻】'}" for i in new.six_chars) +
            "\n五星角色：\n" +
            "\n".join(f"{i.name} {'【限定】' if i.limit else '【常驻】'}" for i in new.five_chars)
        )
        if _config.pure_text:
            await session.send(text)
        else:
            await session.send([Image(new.pool)(text)])
    else:
        await session.send("卡池已是最新")


@disp.assign("模拟")
async def simulate(session: Session):
    from arknights_toolkit.gacha.simulate import simulate_image

    user_id = session.user.id
    if user_id not in userdata:
        user = GachaUser()
        userdata[user_id] = asdict(user)
    else:
        user = GachaUser(**userdata[user_id])
    res = gacha.gacha(user, 10)
    img = await simulate_image(res[0], proxy=_config.proxy)
    await session.send([Image.of(raw=img, mime="image/jpeg")("模拟十连")])
    userdata[user_id] = asdict(user)
    return


@disp.assign("$main")
async def _(session: Session, count: Match[int]):
    user_id = session.user.id
    if user_id not in userdata:
        user = GachaUser()
        userdata[user_id] = asdict(user)
    else:
        user = GachaUser(**userdata[user_id])
    _count = min(max(int(count.result), 1), _config.gacha_max)
    data = gacha.gacha(user, _count)
    get_six = {}
    get_five = {}
    four_count = 0
    for ten in data:
        for res in ten:
            if res.rarity == 6:
                get_six[res.name] = get_six.get(res.name, 0) + 1
            elif res.rarity == 5:
                get_five[res.name] = get_five.get(res.name, 0) + 1
            elif res.rarity == 4:
                four_count += 1
    text = (
        f"抽卡次数: {count.result}\n"
        f"六星角色：\n" +
        "\n".join(f"{i} x{get_six[i]}" for i in get_six) +
        "\n五星角色：\n" +
        "\n".join(f"{i} x{get_five[i]}" for i in get_five) +
        "\n四星角色：\n" +
        f"共{four_count}个四星"
    )
    if _config.pure_text:
        await session.send(text)
    else:
        img = gacha.create_image(user, data, _count, True)
        await session.send([Image.of(raw=img, mime="image/jpeg")(text)])
    userdata[user_id] = asdict(user)
    return
