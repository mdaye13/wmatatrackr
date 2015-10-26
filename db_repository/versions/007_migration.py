from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
time_between_stations = Table('time_between_stations', post_meta,
    Column('station', String, primary_key=True, nullable=False),
    Column('previous_station', String, primary_key=True, nullable=False),
    Column('distance', Float),
    Column('time', Float),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['time_between_stations'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['time_between_stations'].drop()
