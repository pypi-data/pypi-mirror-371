"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from copy import deepcopy
from threading import Lock
from typing import Annotated
from typing import Optional
from typing import TYPE_CHECKING
from typing import Type

from pydantic import Field

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from .common import PARSABLE
from .params import WindowsParams
from .time import Time
from .window import Window
from ..types import BaseModel
from ..types import DictStrAny
from ..types import LDictStrAny

if TYPE_CHECKING:
    from .params import WindowParams



WINDOWS = dict[str, Window]



class WindowsTable(DeclarativeBase):
    """
    Schematic for the database operations using SQLAlchemy.

    .. note::
       Fields are not completely documented for this model.
    """

    group = Column(
        String,
        primary_key=True,
        nullable=False)

    unique = Column(
        String,
        primary_key=True,
        nullable=False)

    last = Column(
        String,
        nullable=False)

    next = Column(
        String,
        nullable=False)

    update = Column(
        String,
        nullable=False)



class WindowsRecord(BaseModel):
    """
    Contain the information of the record from the database.

    :param record: Record from the SQLAlchemy query routine.
    """

    group: Annotated[
        str,
        Field(...,
              description='Group the children by category',
              min_length=1)]

    unique: Annotated[
        str,
        Field(...,
              description='Unique identifier for the child',
              min_length=1)]

    last: Annotated[
        str,
        Field(...,
              description='Last schedule for the period',
              min_length=20,
              max_length=32)]

    next: Annotated[
        str,
        Field(...,
              description='Next schedule for the period',
              min_length=20,
              max_length=32)]

    update: Annotated[
        str,
        Field(...,
              description='When the record was updated',
              min_length=20,
              max_length=32)]


    def __init__(
        self,
        record: Optional[DeclarativeBase] = None,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        fields = [
            'group',
            'unique',
            'last',
            'next',
            'update']

        params = {
            x: getattr(record, x)
            for x in fields}


        timefs = [
            'last',
            'next',
            'update']

        params |= {
            k: (Time(v).simple
                if v else None)
            for k, v in
            params.items()
            if k in timefs}


        super().__init__(**params)



class Windows:
    """
    Track windows on unique key determining when to proceed.

    .. warning::
       This class will use an in-memory database for cache,
       unless a cache file is explicity defined.

    .. testsetup::
       >>> from .params import WindowParams
       >>> from .params import WindowsParams

    Example
    -------
    >>> source = {'one': WindowParams(window=1)}
    >>> params = WindowsParams(windows=source)
    >>> windows = Windows(params, '-2s', 'now')
    >>> [windows.ready('one') for x in range(4)]
    [True, True, True, False]

    :param params: Parameters used to instantiate the class.
    :param start: Determine the start for scheduling window.
    :param stop: Determine the ending for scheduling window.
    :param store: Optional database path for keeping state.
    :param group: Optional override for default group name.
    """

    __params: 'WindowsParams'

    __store: str
    __group: str
    __table: Type[WindowsTable]
    __locker: Lock

    __sengine: Engine
    __session: (
        # pylint: disable=unsubscriptable-object
        sessionmaker[Session])

    __start: Time
    __stop: Time

    __childs: WINDOWS


    def __init__(  # noqa: CFQ002
        self,
        params: Optional['WindowsParams'] = None,
        start: PARSABLE = 'now',
        stop: PARSABLE = '3000-01-01',
        *,
        store: str = 'sqlite:///:memory:',
        table: str = 'windows',
        group: str = 'default',
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        params = deepcopy(params)

        if params is None:
            params = WindowsParams()

        self.__params = params


        self.__store = store
        self.__group = group

        class SQLBase(DeclarativeBase):
            pass

        self.__table = type(
            f'encommon_windows_{table}',
            (SQLBase, WindowsTable),
            {'__tablename__': table})

        self.__locker = Lock()

        self.__build_engine()


        start = Time(start)
        stop = Time(stop)

        assert stop > start

        self.__start = start
        self.__stop = stop


        self.__childs = {}

        self.__build_objects()


    def __build_engine(
        self,
    ) -> None:
        """
        Construct instances using the configuration parameters.
        """

        sengine = create_engine(
            self.__store,
            pool_pre_ping=True)

        (self.__table.metadata
         .create_all(sengine))

        session = (
            sessionmaker(sengine))

        self.__sengine = sengine
        self.__session = session


    def __build_objects(
        self,
    ) -> None:
        """
        Construct instances using the configuration parameters.
        """

        params = self.__params

        items = (
            params.windows
            .items())

        for name, item in items:
            self.create(name, item)


    @property
    def params(
        self,
    ) -> 'WindowsParams':
        """
        Return the Pydantic model containing the configuration.

        :returns: Pydantic model containing the configuration.
        """

        return self.__params


    @property
    def store(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__store


    @property
    def group(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__group


    @property
    def store_table(
        self,
    ) -> Type[WindowsTable]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__table


    @property
    def store_engine(
        self,
    ) -> Engine:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__sengine


    @property
    def store_session(
        self,
    ) -> Session:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__session()


    @property
    def start(
        self,
    ) -> Time:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return Time(self.__start)


    @property
    def stop(
        self,
    ) -> Time:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return Time(self.__stop)


    @property
    def children(
        self,
    ) -> dict[str, Window]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return dict(self.__childs)


    def save_children(
        self,
    ) -> None:
        """
        Save the child caches from the attribute into database.
        """

        sess = self.__session()
        lock = self.__locker

        table = self.__table
        group = self.__group
        childs = self.__childs


        inserts: LDictStrAny = []

        update = Time('now')


        items = childs.items()

        for unique, cache in items:

            _last = cache.last.subsec
            _next = cache.next.subsec
            _update = update.subsec

            inputs: DictStrAny = {
                'group': group,
                'unique': unique,
                'last': _last,
                'next': _next,
                'update': _update}

            inserts.append(inputs)


        with lock, sess as session:

            for insert in inserts:

                session.merge(
                    table(**insert))

            session.commit()


    def ready(
        self,
        unique: str,
        update: bool = True,
    ) -> bool:
        """
        Determine whether or not the appropriate time has passed.

        :param unique: Unique identifier for the related child.
        :param update: Determines whether or not time is updated.
        :returns: Boolean indicating whether enough time passed.
        """

        childs = self.__childs

        if unique not in childs:
            raise ValueError('unique')

        child = childs[unique]

        ready = child.ready(update)

        if ready is True:
            self.save_children()

        return ready


    def pause(
        self,
        unique: str,
        update: bool = True,
    ) -> bool:
        """
        Determine whether or not the appropriate time has passed.

        :param unique: Unique identifier for the related child.
        :param update: Determines whether or not time is updated.
        :returns: Boolean indicating whether enough time passed.
        """

        return not self.ready(
            unique, update)


    def select(
        self,
        unique: str,
    ) -> Optional[WindowsRecord]:
        """
        Return the record from within the table in the database.

        :returns: Record from within the table in the database.
        """

        sess = self.__session()
        lock = self.__locker

        table = self.__table
        model = WindowsRecord

        table = self.__table
        group = self.__group

        _unique = table.unique
        _group = table.group


        with lock, sess as session:

            query = (
                session.query(table)
                .filter(_unique == unique)
                .filter(_group == group))

            _records = list(query.all())


        records = [
            model(x)
            for x in _records]


        if len(records) == 0:
            return None

        assert len(records) == 1

        return records[0]


    def create(
        self,
        unique: str,
        params: 'WindowParams',
    ) -> Window:
        """
        Create a new window using the provided input parameters.

        :param unique: Unique identifier for the related child.
        :param params: Parameters used to instantiate the class.
        :returns: Newly constructed instance of related class.
        """

        childs = self.__childs
        _start = self.__start
        _stop = self.__stop

        if unique in childs:
            raise ValueError('unique')

        window = params.window
        start = params.start
        stop = params.stop
        anchor = params.anchor
        delay = params.delay


        select = self.select(unique)

        if select is not None:
            start = select.next
            anchor = select.next


        child_start = Time(
            start if start
            else _start)

        child_stop = Time(
            stop if stop
            else _stop)

        anchor = anchor or start


        if child_start < _start:
            child_start = _start

        if child_stop > _stop:
            child_stop = _stop


        child = Window(
            window=window,
            start=child_start,
            stop=child_stop,
            anchor=anchor,
            delay=delay)

        childs[unique] = child


        self.save_children()

        return child


    def update(
        self,
        unique: str,
        value: Optional[PARSABLE] = None,
    ) -> None:
        """
        Update the window from the provided parasable time value.

        :param unique: Unique identifier for the related child.
        :param value: Override the time updated for window value.
        """

        childs = self.__childs

        if unique not in childs:
            raise ValueError('unique')

        child = childs[unique]

        child.update(value)

        self.save_children()


    def delete(
        self,
        unique: str,
    ) -> None:
        """
        Delete the window from the internal dictionary reference.

        .. note::
           This is a graceful method, will not raise exception
           when the provided unique value does not exist.

        :param unique: Unique identifier for the related child.
        """

        sess = self.__session()
        lock = self.__locker
        childs = self.__childs

        table = self.__table
        group = self.__group

        _unique = table.unique
        _group = table.group


        with lock, sess as session:

            (session.query(table)
             .filter(_unique == unique)
             .filter(_group == group)
             .delete())

            session.commit()


        if unique in childs:
            del childs[unique]
