"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path
from time import sleep

from pytest import fixture
from pytest import raises

from ..params import TimerParams
from ..time import Time
from ..timers import Timers
from ...types import DictStrAny
from ...types import inrepr
from ...types import instr
from ...types import lattrs



@fixture
def timers(
    tmp_path: Path,
) -> Timers:
    """
    Construct the instance for use in the downstream tests.

    :param tmp_path: pytest object for temporal filesystem.
    :returns: Newly constructed instance of related class.
    """

    model = TimerParams

    source: DictStrAny = {
        'one': model(timer=1),
        'two': model(timer=1)}


    store = (
        f'sqlite:///{tmp_path}'
        '/cache.db')

    timers = Timers(
        store=store)

    table = (
        timers
        .store_table)

    session = (
        timers
        .store_session)


    record = table(
        group='default',
        unique='two',
        last='1970-01-01T00:00:00Z',
        update='1970-01-01T00:00:00Z')

    session.merge(record)

    record = table(
        group='default',
        unique='tre',
        last='1970-01-01T00:00:00Z',
        update='1970-01-01T00:00:00Z')

    session.merge(record)

    session.commit()


    timers.create(
        'one', source['one'])

    timers.create(
        'two', source['two'])


    return timers



def test_Timers(
    timers: Timers,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param timers: Primary class instance for timers object.
    """


    attrs = lattrs(timers)

    assert attrs == [
        '_Timers__params',
        '_Timers__store',
        '_Timers__group',
        '_Timers__table',
        '_Timers__locker',
        '_Timers__sengine',
        '_Timers__session',
        '_Timers__childs']


    assert inrepr(
        'timers.Timers object',
        timers)

    assert isinstance(
        hash(timers), int)

    assert instr(
        'timers.Timers object',
        timers)


    assert timers.params

    assert timers.store[:6] == 'sqlite'

    assert timers.group == 'default'

    assert timers.store_table

    assert timers.store_engine

    assert timers.store_session

    assert len(timers.children) == 2


    timer = timers.children['one']

    assert timer.time >= Time('-1s')


    timer = timers.children['two']

    assert timer.time == '1970-01-01'



def test_Timers_cover(
    timers: Timers,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param timers: Primary class instance for timers object.
    """


    assert timers.ready('two')
    assert timers.pause('two')

    timers.update('two', 'now')

    assert not timers.ready('two')
    assert timers.pause('two')


    timers = Timers()


    params = TimerParams(timer=1)

    timers.create('fur', params)

    assert not timers.ready('fur')
    assert timers.pause('fur')

    sleep(1)

    assert timers.ready('fur')
    assert timers.pause('fur')

    timers.delete('fur')



def test_Timers_raises(
    timers: Timers,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param timers: Primary class instance for timers object.
    """


    _raises = raises(ValueError)

    with _raises as reason:
        timers.ready('dne')

    _reason = str(reason.value)

    assert _reason == 'unique'


    _raises = raises(ValueError)

    params = TimerParams(timer=1)

    with _raises as reason:
        timers.create('one', params)

    _reason = str(reason.value)

    assert _reason == 'unique'


    _raises = raises(ValueError)

    with _raises as reason:
        timers.update('dne', 'now')

    _reason = str(reason.value)

    assert _reason == 'unique'
