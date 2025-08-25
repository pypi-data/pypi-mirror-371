"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from ..funcs import funcname



def test_funcname() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    assert funcname() == 'test_funcname'


    class Test:

        def test1(self) -> str:
            return funcname()

        @classmethod
        def test2(cls) -> str:
            return funcname()


    method1 = Test().test1()
    method2 = Test.test2()

    assert method1 == 'Test.test1'
    assert method2 == 'Test.test2'
