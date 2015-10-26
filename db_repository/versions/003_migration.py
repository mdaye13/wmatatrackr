from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
train_prediction = Table('train_prediction', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('time', String),
    Column('cars', Integer),
    Column('destination', String),
    Column('destination_code', String),
    Column('destination_name', String),
    Column('group', String),
    Column('line', String),
    Column('location_code', String),
    Column('location_name', String),
    Column('minutes', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['train_prediction'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['train_prediction'].drop()
