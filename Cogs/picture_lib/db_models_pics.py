import datetime

import pytz
from tortoise.models import Model
from tortoise import fields, Tortoise
import os


class PicUpload(Model):
    # rem_id = fields.IntField(pk=True)
    # desc = fields.TextField()
    # time_due_col = fields.DatetimeField()
    # user_bind = fields.IntField()
    # time_differential = fields.TimeDeltaField()

    send_task_id = fields.IntField(pk=True)
    guild_id = fields.IntField()
    channel_id = fields.IntField()
    func_to_use = fields.TextField()
    params_of_func = fields.TextField(null=True)
    time_to_send = fields.DatetimeField()

    def __str__(self):

        ct = datetime.datetime.utcnow()
        ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        ct = pytz.utc.localize(ct)

        time_dif = self.time_to_send - ct
        if self.params_of_func:
            func = self.func_to_use + " " + self.params_of_func
        else:
            func = self.func_to_use

        return f"ID: {self.send_task_id} - Channel: <#{self.channel_id}> " \
               f"- Func: {func} - Run in:{time_dif}"


ap = os.path.abspath(__file__)
ap = ap[:len(ap) - 29]



async def db_init(db_name):
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await Tortoise.init(
        db_url=f'sqlite:///{ap}db_files/{db_name}',
        modules={'models': ['Cogs.picture_lib']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()
