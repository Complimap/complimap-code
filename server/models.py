from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from server.database import Base

from sqlalchemy.orm import relationship

class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now())
    fname = Column(String)
    lname = Column(String)

    def __repr__(self):
        return '<Node %r>' % (self.username)


class Path(Base):
    __tablename__ = "paths"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nodes = relationship('Node', backref='path', lazy='dynamic')

    def __repr__(self):
        return '<Path %r>' % (self.username)
