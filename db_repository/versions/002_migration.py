from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
station_together = Table('station_together', post_meta,
    Column('station1', String, primary_key=True, nullable=False),
    Column('station2', String, primary_key=True, nullable=False),
)

station = Table('station', pre_meta,
    Column('code', VARCHAR, primary_key=True, nullable=False),
    Column('name', VARCHAR),
    Column('address', INTEGER),
    Column('lat', FLOAT),
    Column('lon', FLOAT),
    Column('line_code_1', VARCHAR),
    Column('line_code_2', VARCHAR),
    Column('line_code_3', VARCHAR),
    Column('line_code_4', VARCHAR),
    Column('station_together_1', VARCHAR),
    Column('station_together_2', VARCHAR),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['station_together'].create()
    pre_meta.tables['station'].columns['station_together_1'].drop()
    pre_meta.tables['station'].columns['station_together_2'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['station_together'].drop()
    pre_meta.tables['station'].columns['station_together_1'].create()
    pre_meta.tables['station'].columns['station_together_2'].create()
