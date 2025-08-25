import pytest
import time
from loading2 import loading, spin
from threading import Event, Thread


def test_loading_decorator_basic():
    @loading()
    def dummy():
        return "ok"

    assert dummy() == "ok"


def test_loading_decorator_with_args():
    @loading()
    def add(a, b):
        return a + b

    assert add(3, 5) == 8

def test_loading_decorator_success(capsys):
    @loading()
    def task():
        time.sleep(0.2)
        return "finished"

    result = task()
    captured = capsys.readouterr()
    assert "Loading..." in captured.out
    assert "OK" in captured.out
    assert result == "finished"

def test_loading_decorator_exception(capsys):
    @loading()
    def error_task():
        time.sleep(0.1)
        raise ValueError("fail")

    error_task()
    captured = capsys.readouterr()
    assert "Failed:" in captured.out

def test_loading_decorator_custom_params(capsys):
    @loading(msg="Working...", ok="Done!", err="Oops:")
    def custom_task():
        time.sleep(0.1)
        return 123

    result = custom_task()
    captured = capsys.readouterr()
    assert "Working..." in captured.out
    assert "Done!" in captured.out
    assert result == 123

def test_spin_outputs(monkeypatch):
    # Patch print to collect output
    output = []
    def fake_print(*args, **kwargs):
        output.append(args[0])

    monkeypatch.setattr("builtins.print", fake_print)
    done = Event()
    t = Thread(target=spin, args=("TestMsg", done))
    t.start()
    time.sleep(0.3)
    done.set()
    t.join()
    # Should have output at least once
    assert any("TestMsg" in line for line in output)

def test_loading_keyboard_interrupt(capsys):
    @loading()
    def interrupt_task():
        raise KeyboardInterrupt()
    interrupt_task()
    captured = capsys.readouterr()
    assert "abort!" in captured.out
