from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from server.database import Base

from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound

from werkzeug import security

import random
import string


def gen_secret(set, n):
    return "".join(random.choice(set) for x in range(n))


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    lattitude = Column(Float)
    longitude = Column(Float)

    owner = Column(String(length=3))

    path_id = Column(Integer, ForeignKey("paths.id"))
    path = relationship("Path", back_populates="hops", uselist=False,
                        foreign_keys=[path_id])

    head_of_id = Column(Integer, ForeignKey("paths.id"))
    head_of = relationship("Path", back_populates="head_node", uselist=False,
                           foreign_keys=[head_of_id])

    next_id = Column(Integer, ForeignKey("nodes.id"))
    prev = relationship("Node", remote_side=[id],
                        foreign_keys=[next_id])

    def __repr__(self):
        return "<Node %r %r %r>" % (self.id, self.owner, self.path)


class Path(Base):
    __tablename__ = "paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    message = Column(Text())
    # next_code len is twice as much as initial code_len. For future.
    next_code = Column(String(length=16))

    head_node_id = Column(Integer, ForeignKey("nodes.id"))
    head_node = relationship("Node", back_populates="head_of",
                             uselist=False,
                             foreign_keys=[Node.head_of_id])

    hops = relationship("Node", back_populates="path",
                        foreign_keys=[Node.path_id])

    def __init__(self, message):
        self.message = message
        self.next_code = gen_secret(string.ascii_lowercase + string.digits, 8)
        self.head_node = None

    def __repr__(self):
        return "<Path %r %r>" % (self.id, self.message)


def add_node(uname, lat, lon, code):
    try:
        path = Path.query.filter_by(next_code=code).one()
    except NoResultFound:
        return None

    node = Node(owner=uname, lattitude=lat, longitude=lon,
                path=path, prev=path.head_node)
    path.head_node = node
    path.next_code = gen_secret(string.ascii_lowercase + string.digits, 8)
    return path
