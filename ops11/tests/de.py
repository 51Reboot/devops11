import signal
import time


class TimeoutError(Exception):
    pass


def timeout(seconds, error_message='Function call timed out'):
    def decorate(func):
        def wrapper(*args, **kwargs):
            def _handle_timeout(signum, frame):
                raise TimeoutError(error_message)

            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)

            print("---> wrapper start")
            try:
                return func(*args, **kwargs)
            except TimeoutError:
                print("timeout err")
            finally:
                signal.alarm(0)
            print("---> wrapper stop")

        return wrapper

    return decorate


@timeout(3)
def pprint(*args, **kwargs):
    time.sleep(5)
    print(f"args: {args}, \nkwargs: {kwargs}")


pprint()
