#!/usr/bin/env python3
"""DB module.
The Base is what all classes inherit from and this helps to
create all the tables defined in them.
Engine - Helps us connect to the db and gives Base access to
crete all tables or delete them.
Session - Gives us the platform to interact with the db.
It is used with the sessionmaker that binds with Engine
"""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from user import Base, User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError


class DB:
    """DB class
    """
    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db")
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add / save new user to the database"""
        newUser = User(email=email, hashed_password=hashed_password)
        session = self._session
        session.add(newUser)
        session.commit()
        return newUser

    def find_user_by(self, **kwargs) -> User:
        """returns the first row found in the users table as
        filtered by the method’s input arguments"""
        columns, values = [], []
        for key, val in kwargs.items():
            # if the column exist as a field/attributes in User instance
            if hasattr(User, key):
                columns.append(getattr(User, key))
                values.append(val)
            else:
                raise InvalidRequestError
        session = self._session
        # filter table user such that all the specified columns match the
        # corresponding values
        # use tuple_() for composite (multi-column) queries
        user_row = session.query(User).filter(
                tuple_(*columns).in_([tuple(values)])).first()
        if not user_row:
            raise NoResultFound
        else:
            return user_row

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update user in the databse"""
        found_user_row = self.find_user_by(id=user_id)
        if found_user_row is None:
            return None

        update_dict = {}
        for key, val in kwargs.items():
            if hasattr(User, key):
                update_dict[getattr(User, key)] = val
            else:
                raise ValueError
        session = self._session
        session.query(User).filter(User.id == user_id).update(
                update_dict,
                synchronize_session=False,
            )
        session.commit()
