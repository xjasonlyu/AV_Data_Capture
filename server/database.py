from datetime import datetime

from peewee import *
from playhouse.db_url import connect

db_proxy = DatabaseProxy()


def database_init(url: str):
    db = connect(url,
                 field_types={'ARRAY': 'TEXT'})
    db_proxy.initialize(db)
    # create table if not exist
    db_proxy.create_tables([Metadata, Actress, Cover])


class ArrayField(Field):
    field_type = 'ARRAY'

    def db_value(self, value: list[str]) -> str:
        return ','.join(v for v in value)

    def python_value(self, value: str) -> list[str]:
        return value.split(',') if value else []


class BasicModel(Model):
    class Meta:
        database = db_proxy


class Metadata(BasicModel):
    vid = CharField(primary_key=True, unique=True)
    title = TextField()

    # info fields
    overview = TextField()
    genres = ArrayField()
    label = TextField()
    studio = TextField()
    series = TextField()
    runtime = IntegerField()

    # cast fields
    actresses = ArrayField()
    director = TextField()

    # image fields
    cover = TextField()
    images = ArrayField()

    # source fields
    sources = ArrayField()
    providers = ArrayField()

    # date fields
    release = DateField()

    # datetime fields
    last_modified = DateTimeField(default=datetime.now)


class Actress(BasicModel):
    name = CharField(primary_key=True, unique=True)
    images = ArrayField()

    # nullable fields
    measurements = TextField(null=True)
    cup_size = TextField(null=True)
    sign = TextField(null=True)
    blood_type = TextField(null=True)
    height = TextField(null=True)
    nationality = TextField(null=True)
    source = TextField(null=True)
    av_activity = DateField(null=True)
    birthday = DateField(null=True)


class Cover(BasicModel):
    vid = CharField(primary_key=True, unique=True)
    format = CharField()
    data = BlobField()
    pos = DoubleField(default=-1)


if __name__ == '__main__':
    database_init('sqlite:///:memory:')
