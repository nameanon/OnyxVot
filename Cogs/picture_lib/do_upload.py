from .db_models_pics import PicUpload
import datetime
from ..reminderRewrite import schedule
from .met_query_handler import parse_query_input
from .get_met_embed import get_met_embed

async def do_upload(cog, dest_hook: PicUpload):
    channel = cog.bot.get_guild(dest_hook.guild_id).get_channel(dest_hook.channel_id)

    e = None

    if dest_hook.func_to_use == "cute":
        e = cog.cute_embed

    elif dest_hook.func_to_use == "met" and dest_hook.params_of_func is None:
        e = cog.met_embed

    elif dest_hook.func_to_use == "met" and dest_hook.params_of_func is not None:
        params = parse_query_input(dest_hook.params_of_func)
        e = get_met_embed(cog, params)

    await PicUpload.filter(send_task_id=dest_hook.send_task_id) \
        .update(time_to_send=cog.ct + datetime.timedelta(hours=2))

    await channel.send(embed=e)

    hook = await PicUpload.filter(send_task_id=dest_hook.send_task_id).first()

    cog.bot.loop.create_task(schedule(hook.time_to_send, do_upload, cog, dest_hook),
                             name=f"SEND_TASK - {dest_hook.send_task_id}")
