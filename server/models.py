from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from server.database import Base

from sqlalchemy.orm import relationship, backref

from werkzeug import security

import random
import string


def gen_secret(set, n):
    return "".join(random.choice(set) for x in range(n))


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, autoincrement=True)

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    uname = Column(String, unique=True)
    secret = Column(String)

    created_paths = relationship("Path", back_populates="creator")

    def __init__(self, uname):
        uname = uname.lower()
        if Person.query.filter_by(uname=uname).count() > 0:
            raise ValueError("Username must be unique")
        self.uname = uname

    def make_secret(self):
        secret = gen_secret(string.ascii_letters + string.digits, 10)
        self.secret = security.generate_password_hash(secret)
        return secret

    def auth(self, secret):
        return security.check_password_hash(self.secret, secret)

    def __repr__(self):
        return "<Person %r>" % (self.uname)


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    lattitude = Column(Float)
    longitude = Column(Float)

    owner_id = Column(Integer, ForeignKey("people.id"))
    owner = relationship("Person", backref="owned_nodes",
                         foreign_keys=[owner_id])

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
        return "<Node %r %r %r>" % (self.id, self.owner.uname, self.path)


class Path(Base):
    __tablename__ = "paths"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    message = Column(Text())
    # next_code len is twice as much as initial code_len. For future.
    next_code = Column(String(length=16))

    creator_id = Column(Integer, ForeignKey("people.id"))
    creator = relationship("Person", back_populates="created_paths",
                           foreign_keys=[creator_id])

    head_node_id = Column(Integer, ForeignKey("nodes.id"))
    head_node = relationship("Node", back_populates="head_of",
                             uselist=False,
                             foreign_keys=[Node.head_of_id])

    hops = relationship("Node", back_populates="path",
                        foreign_keys=[Node.path_id])

    def __init__(self, uname, message):
        self.creator = Person.query.filter_by(uname=uname).one()
        self.message = message
        self.next_code = gen_secret(string.ascii_lowercase + string.digits, 8)
        self.head_node = None

    def add_node(self, uname, lat, lon, code):
        if not self.next_code == code.lower():
            return None

        user = Person.query.filter_by(uname=uname).one()
        node = Node(owner=user, lattitude=lat, longitude=lon,
                    path=self, prev=self.head_node)
        self.head_node = node
        self.next_code = gen_secret(string.ascii_lowercase + string.digits, 8)
        return self.next_code

    def __repr__(self):
        return "<Path %r %r %r>" % (self.id, self.creator.uname, self.message)
