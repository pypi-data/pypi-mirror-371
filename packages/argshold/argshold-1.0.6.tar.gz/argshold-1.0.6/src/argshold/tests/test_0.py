import unittest
from functools import partialmethod
from typing import *

from frozendict import frozendict

from argshold.core import FrozenArgumentHolder as FAH


class TestFrozenArgumentHolder(unittest.TestCase):

    def test_initialization(self: Self) -> None:
        holder: FAH = FAH(1, 2, a=3, b=4)
        self.assertEqual(holder.args, (1, 2))
        self.assertEqual(holder.kwargs, frozendict(a=3, b=4))

    def test_equality(self: Self) -> None:
        holder1: FAH = FAH(1, 2, a=3, b=4)
        holder2: FAH = FAH(1, 2, a=3, b=4)
        holder3: FAH = FAH(1, 2, a=3)
        self.assertEqual(holder1, holder2)
        self.assertNotEqual(holder1, holder3)

    def test_hash(self: Self) -> None:
        holder1: FAH = FAH(1, 2, a=3, b=4)
        holder2: FAH = FAH(1, 2, a=3, b=4)
        self.assertEqual(hash(holder1), hash(holder2))

    def test_len(self: Self) -> None:
        holder: FAH = FAH(1, 2, a=3, b=4)
        self.assertEqual(len(holder), 4)

    def test_repr(self: Self) -> None:
        holder: FAH = FAH(1, 2, a=3, b=4)
        self.assertEqual(repr(holder), "FrozenArgumentHolder(1, 2, a=3, b=4)")

    def test_immutable_attributes(self: Self) -> None:
        holder: FAH = FAH(1, 2, a=3, b=4)
        with self.assertRaises(AttributeError):
            holder.args = (3, 4)
        with self.assertRaises(AttributeError):
            holder.kwargs = frozendict(c=5)

    def test_call(self: Self) -> None:
        def sample_function(x: Any, y: Any, a: Any = 0, b: Any = 0) -> Any:
            return x + y + a + b

        holder: FAH = FAH(1, 2, a=3, b=4)
        result: Any = holder.call(sample_function)
        self.assertEqual(result, 10)

    def test_copy(self: Self) -> None:
        holder: FAH = FAH(1, 2, a=3, b=4)
        copied: FAH = holder.copy()
        self.assertEqual(holder, copied)
        self.assertIsNot(holder, copied)

    def test_partialmethod(self: Self) -> None:
        trueHolder: FAH = FAH(True)
        falseHolder: FAH = FAH(False)

        class Cell:
            def __init__(self: Self) -> None:
                self._alive = False

            @property
            def alive(self: Self) -> Any:
                return self._alive

            def set_state(self: Self, state: Any) -> None:
                self._alive = bool(state)

            set_alive: partialmethod = trueHolder.partialmethod(set_state)
            set_dead: partialmethod = falseHolder.partialmethod(set_state)

        cell: Cell = Cell()
        self.assertFalse(cell.alive)
        cell.set_alive()
        self.assertTrue(cell.alive)
        cell.set_dead()
        self.assertFalse(cell.alive)


if __name__ == "__main__":
    unittest.main()
