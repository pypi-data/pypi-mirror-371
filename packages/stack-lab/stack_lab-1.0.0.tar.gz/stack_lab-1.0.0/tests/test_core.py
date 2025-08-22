# tests/test_core.py

import pytest
from stack_lab import Stack

def test_stack_initialization():
    s = Stack()
    assert s.is_empty()
    assert len(s) == 0

def test_push_and_peek():
    s = Stack()
    s.push(10)
    assert s.peek() == 10
    s.push(20)
    assert s.peek() == 20

def test_pop():
    s = Stack()
    s.push("a")
    s.push("b")
    assert s.pop() == "b"
    assert s.pop() == "a"
    assert s.is_empty()

def test_pop_empty():
    s = Stack()
    with pytest.raises(IndexError, match="pop from empty stack"):
        s.pop()

def test_peek_empty():
    s = Stack()
    with pytest.raises(IndexError, match="peek from empty stack"):
        s.peek()

def test_len():
    s = Stack()
    for i in range(5):
        s.push(i)
    assert len(s) == 5

def test_repr_and_str():
    s = Stack()
    s.push(1)
    s.push(2)
    assert "Stack" in repr(s)
    assert str(s) == "[1, 2]"
