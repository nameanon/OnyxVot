from tortoise.models import Model
from tortoise import fields, Tortoise
import os
import datetime
import pytz


class Reminder(Model):

    rem_id = fields.IntField(pk=True)
    desc = fields.TextField()
    time_due_col = fields.DatetimeField()
    user_bind = fields.IntField()
    time_differential = fields.TimeDeltaField()

    def __str__(self):
        ct = datetime.datetime.utcnow()
        ct = pytz.utc.localize(ct)
        ct = ct - datetime.timedelta(microseconds=ct.microsecond)
        due = self.time_due_col - ct
        due = due - datetime.timedelta(microseconds=due.microseconds)
        return f"{self.desc} due in {due}"


ap = os.path.abspath(__file__)
ap = ap[:len(ap) - 28]


async def db_init(db_name):
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await Tortoise.init(
        db_url=f'sqlite:///{ap}db_files/{db_name}',
        modules={'models': ['Cogs.reminderRewrite']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()


