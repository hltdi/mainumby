#   
#   Mainumby Database helpef functions.
#   Uses the Object Relational Mapper implementation of SQLAlchemy.
#
########################################################################
#
#   This file is part of the PloGs project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2015, 2016, 2019 PLoGS <gasser@indiana.edu>
#   
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# =========================================================================

# 2015.07.11
# -- Created (but not used for anything)

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask import _app_ctx_stack
import datetime
from .text import *

TEXT_DATABASE = 'sqlite:///text.db'
LEX_DATABASE = 'sqlite:///lex.db'

class DB:
    """Container for Database functions since we'll need at least 2 of them."""

    def __init__(self, file, engine=None, session=None):
        self.file = file
        self.engine = None
        self.session = None

    def make_engine(self, echo=False):
        self.engine = create_engine(self.file, echo=echo)

    def make_session(self, echo=False):
        """Opens a new database connection if there is none yet for the
        current application context."""
        top = _app_ctx_stack.top
        if top:
            if not hasattr(top, 'db_session'):
                self.make_engine(echo=echo)
                Session = sessionmaker(bind=self.engine)
                top.db_session = Session()
            self.session = top.db_session
        self.make_engine(echo=echo)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def initialize(self, echo=False):
        if not self.engine:
            self.make_engine(echo=echo)
        Base.metadata.create_all(self.engine)

    def clear_db(self):
        if self.engine:
            Base.metadata.drop_all(self.engine)

