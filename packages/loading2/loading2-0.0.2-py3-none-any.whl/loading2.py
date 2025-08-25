import itertools
from threading import Event, Thread


def loading(
    msg: str | None = "Loading...", ok: str | None = "OK", err: str | None = "Failed:"
):
    """add loading anime easily
    e.g.

        >>> @loading()
        >>> def long_time_task():
        >>>     time.sleep(2)
    """

    def decorator(func):
        def decorated(*args, **kwargs):
            done = Event()
            spinner = Thread(target=spin, args=(msg, done))
            spinner.start()
            interrupt = False
            is_err = False
            try:
                res = func(*args, **kwargs)
            except KeyboardInterrupt:
                print("\nabort!")
                interrupt = True
            except Exception as e:
                print(err, e)
                is_err = True
            done.set()
            spinner.join()
            if not is_err and not interrupt:
                print(ok)
                return res

        return decorated

    return decorator


def spin(msg: str, done: Event) -> None:
    """from fluent python"""
    for char in itertools.cycle(r"\|/-"):
        status = f"\r{char} {msg}"
        print(status, end="", flush=True)
        if done.wait(0.1):
            break

    blanks = " " * len(status)
    print(f"\r{blanks}\r", end="")
