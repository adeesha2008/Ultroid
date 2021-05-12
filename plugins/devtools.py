# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}bash <cmds>`
    Run linux commands on telegram.

• `{i}eval <cmds>`
    Evaluate python commands on telegram.

• `{i}sysinfo`
    Shows System Info.
"""
import io
import sys
import traceback
from os import remove

from carbonnow import Carbon

from . import *


@ultroid_cmd(
    pattern="sysinfo$",
)
async def _(e):
    await eor(e, "`Sending...`")
    x, y = await bash("neofetch|sed 's/\x1B\\[[0-9;\\?]*[a-zA-Z]//g' >> neo.txt")
    with open("neo.txt", "r") as neo:
        p = (neo.read()).replace("\n\n", "")
    ok = Carbon(code=p)
    haa = await ok.save("neofetch")
    await e.client.send_file(e.chat_id, haa)
    remove("neofetch.jpg")
    remove("neo.txt")


@ultroid_cmd(
    pattern="bash",
)
async def _(event):
    if not event.out and not is_fullsudo(event.sender_id):
        return await eor(event, "`This Command Is Sudo Restricted.`")
    if Redis("I_DEV") != "True":
        await eor(
            event,
            f"Developer Restricted!\nIf you know what this does, and want to proceed\n\n `{HNDLR}setredis I_DEV True`\n\nThis Might Be Dangerous.",
        )
        return
    xx = await eor(event, "`Processing...`")
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eod(xx, "`No cmd given`", time=10)
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    stdout, stderr = await bash(cmd)
    OUT = f"**☞ BASH\n\n• COMMAND:**\n`{cmd}` \n\n"
    e = stderr
    if e:
        OUT += f"**• ERROR:** \n`{e}`\n"
    o = stdout
    if not o:
        o = "Success"
        OUT += f"**• OUTPUT:**\n`{o}`"
    else:
        _o = o.split("\n")
        o = "\n".join(_o)
        OUT += f"**• OUTPUT:**\n`{o}`"
    if len(OUT) > 4096:
        ultd = OUT.replace("`", "").replace("*", "").replace("_", "")
        with io.BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "bash.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb="resources/extras/ultroid.jpg",
                allow_cache=False,
                caption=f"`{cmd}`",
                reply_to=reply_to_id,
            )
            await xx.delete()
    else:
        await eor(xx, OUT)


@ultroid_cmd(
    pattern="eval",
)
async def _(event):
    if len(event.text) > 5:
        if not event.text[5] == " ":
            return
    if not event.out and not is_fullsudo(event.sender_id):
        return await eor(event, "`This Command Is Sudo Restricted.`")
    if Redis("I_DEV") != "True":
        await eor(
            event,
            f"Developer Restricted!\nIf you know what this does, and want to proceed\n\n {HNDLR}setredis I_DEV True\n\nThis Might Be Dangerous.",
        )
        return
    xx = await eor(event, "`Processing ...`")
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eod(xx, "`Give some python cmd`", time=5)
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    reply_to_id = event.message.id
    try:
        await aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = (
        "__►__ **EVALPy**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            cmd,
            evaluation,
        )
    )
    if len(final_output) > 4096:
        ultd = final_output.replace("`", "").replace("*", "").replace("_", "")
        with io.BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "eval.txt"
            await ultroid_bot.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb="resources/extras/ultroid.jpg",
                allow_cache=False,
                caption=f"```{cmd}```",
                reply_to=reply_to_id,
            )
            await xx.delete()
    else:
        await eor(xx, final_output)


async def aexec(code, event):
    e = message = event
    client = event.client
    p = print  # ignore: pylint
    exec(
        f"async def __aexec(e, client): "
        + "\n message = event = e"
        + "".join(f"\n {l}" for l in code.split("\n")),
    )

    return await locals()["__aexec"](e, e.client)


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})