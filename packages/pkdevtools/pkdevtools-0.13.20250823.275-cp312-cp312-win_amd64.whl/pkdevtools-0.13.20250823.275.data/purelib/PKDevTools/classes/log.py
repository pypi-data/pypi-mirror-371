# -*- coding: utf-8 -*-
"""
    The MIT License (MIT)

    Copyright (c) 2023 pkjmesra

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

"""
import inspect
import logging
import os
import sys
import tempfile
import time
import warnings
import atexit
from collections import OrderedDict
from functools import wraps
from threading import get_ident, Lock
import threading

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

from itertools import *

__all__ = [
    "redForegroundText",
    "greenForegroundText",
    "line_break",
    "clear_screen",
    "set_cursor",
    "setup_custom_logger",
    "default_logger",
    "log_to",
    "tracelog",
    "suppress_stdout_stderr",
]
__trace__ = False
__filter__ = None
__DEBUG__ = False

# Global lock for thread-safe operations
_logger_lock = Lock()
_handlers_configured = False
_console_handler = None
_file_handler = None

class colors:
    """Colors class:
    Reset all colors with colors.reset
    Two subclasses fg for foreground and bg for background.
    Use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.green
    Also, the generic bold, disable, underline, reverse, strikethrough,
    and invisible work with the main class
    i.e. colors.bold
    """

    reset = "\033[0m"
    bold = "\033[01m"
    disable = "\033[02m"
    underline = "\033[04m"
    reverse = "\033[07m"
    strikethrough = "\033[09m"
    invisible = "\033[08m"

    class fg:
        black = "\033[30m"
        red = "\033[31m"
        green = "\033[32m"
        orange = "\033[33m"
        blue = "\033[34m"
        purple = "\033[35m"
        cyan = "\033[36m"
        lightgrey = "\033[37m"
        darkgrey = "\033[90m"
        lightred = "\033[91m"
        lightgreen = "\033[92m"
        yellow = "\033[93m"
        lightblue = "\033[94m"
        pink = "\033[95m"
        lightcyan = "\033[96m"

    class bg:
        black = "\033[40m"
        red = "\033[41m"
        green = "\033[42m"
        orange = "\033[43m"
        blue = "\033[44m"
        purple = "\033[45m"
        cyan = "\033[46m"
        lightgrey = "\033[47m"

class emptylogger():
    """Null logger that does nothing when PKDevTools_Default_Log_Level is not set"""
    
    @property
    def logger(self):
        return None

    @property
    def level(self):
        return logging.NOTSET

    @property
    def isDebugging(self):
        return False

    @level.setter
    def level(self, level):
        return

    @staticmethod
    def getlogger(logger):
        return emptylogger()
    
    def flush(self):
        return

    def addHandlers(self, log_file_path=None, levelname=logging.NOTSET):
        return None, None

    def debug(self, e, exc_info=False):
        return

    def info(self, line):
        return

    def warn(self, line):
        return

    def error(self, line):
        return

    def setLevel(self, level):
        return

    def critical(self, line):
        return

    def addHandler(self, hdl):
        return

    def removeHandler(self, hdl):
        return

class filterlogger:
    """Thread-safe logger that handles multi-process environments"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, logger=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, logger=None):
        if getattr(self, '_initialized', False):
            return
            
        with self._lock:
            if getattr(self, '_initialized', False):
                return
                
            self._logger = logger or logging.getLogger("PKDevTools")
            self._initialized = True
            # Ensure we have a unique logger name for multi-process safety
            self._logger.name = f"PKDevTools_{os.getpid()}_{get_ident()}"

    def __repr__(self):
        return f"LogLevel: {self.level}, isDebugging: {self.isDebugging}"
    
    @property
    def logger(self):
        return self._logger

    @property
    def level(self):
        return self.logger.level

    @property
    def isDebugging(self):
        return self.level == logging.DEBUG

    @level.setter
    def level(self, level):
        with self._lock:
            if level != self.level:
                self.logger.setLevel(level)

    @staticmethod
    def getlogger(logger):
        # Check if logging should be enabled
        if 'PKDevTools_Default_Log_Level' not in os.environ:
            return emptylogger()
        
        return filterlogger(logger=logger)

    def flush(self):
        with self._lock:
            for h in self.logger.handlers:
                try:
                    h.flush()
                except:
                    pass

    def addHandlers(self, log_file_path=None, levelname=logging.NOTSET):
        global _handlers_configured, _console_handler, _file_handler
        
        with _logger_lock:
            if _handlers_configured:
                return _console_handler, _file_handler
                
            if log_file_path is None:
                log_file_path = os.path.join(tempfile.gettempdir(), f"PKDevTools-logs-{os.getpid()}.txt")
            
            trace_formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
            )

            # Remove existing handlers to avoid duplicates
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

            # Create file handler (always created if logging is enabled)
            _file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            _file_handler.setFormatter(trace_formatter)
            _file_handler.setLevel(levelname)
            self.logger.addHandler(_file_handler)

            # Create console handler only if explicitly enabled
            _console_handler = logging.StreamHandler()
            _console_handler.setFormatter(trace_formatter)
            _console_handler.setLevel(levelname)
            self.logger.addHandler(_console_handler)

            _handlers_configured = True
            
            return _console_handler, _file_handler

    def _should_log(self, message):
        """Check if message should be logged based on filter"""
        global __filter__
        if __filter__ is None:
            return True
        return __filter__ in message.upper()

    def debug(self, e, exc_info=False):
        if 'PKDevTools_Default_Log_Level' not in os.environ:
            return
            
        line = str(e)
        try:
            frame = inspect.stack()[1]
            filename = os.path.basename(frame.filename)
            line = f"{filename} - {frame.function} - {frame.lineno} - {line}"
        except Exception:
            pass
        
        if not self._should_log(line):
            return
            
        with self._lock:
            self.logger.debug(line, exc_info=exc_info)

    def info(self, line):
        if 'PKDevTools_Default_Log_Level' not in os.environ:
            return
            
        try:
            frame = inspect.stack()[1]
            filename = os.path.basename(frame.filename)
            line = f"{filename} - {frame.function} - {frame.lineno} - {line}"
        except Exception:
            pass
        
        if not self._should_log(line):
            return
            
        with self._lock:
            self.logger.info(line)

    def warn(self, line):
        if 'PKDevTools_Default_Log_Level' not in os.environ:
            return
            
        if not self._should_log(line):
            return
            
        with self._lock:
            self.logger.warning(line)

    def error(self, line):
        if 'PKDevTools_Default_Log_Level' not in os.environ:
            return
            
        if not self._should_log(line):
            return
            
        with self._lock:
            self.logger.error(line)

    def setLevel(self, level):
        with self._lock:
            self.logger.setLevel(level)

    def critical(self, line):
        if 'PKDevTools_Default_Log_Level' not in os.environ:
            return
            
        if not self._should_log(line):
            return
            
        with self._lock:
            self.logger.critical(line)

    def addHandler(self, hdl):
        with self._lock:
            self.logger.addHandler(hdl)

    def removeHandler(self, hdl):
        with self._lock:
            self.logger.removeHandler(hdl)

def setup_custom_logger(
    name,
    levelname=logging.DEBUG,
    trace=False,
    log_file_path="PKDevTools-logs.txt",
    filter=None,
):
    global __trace__, __filter__
    
    __trace__ = trace
    __filter__ = filter.upper() if filter else None
    
    # Only setup logging if environment variable is set
    if 'PKDevTools_Default_Log_Level' not in os.environ:
        return emptylogger()
    
    logger = filterlogger.getlogger(logging.getLogger(name))
    
    # Set the log level from environment variable
    try:
        env_level = int(os.environ['PKDevTools_Default_Log_Level'])
        logger.level = env_level
    except (ValueError, KeyError):
        logger.level = levelname
    
    # Configure handlers
    logger.addHandlers(log_file_path=log_file_path, levelname=logger.level)
    
    # Setup trace logger if tracing is enabled
    if trace:
        trace_logger = filterlogger.getlogger(logging.getLogger("PKDevTools_file_logger"))
        trace_logger.level = logging.DEBUG  # Tracing always uses DEBUG level
        trace_logger.addHandlers(log_file_path=log_file_path, levelname=logging.DEBUG)
        logger.info("Tracing started")
    
    # Turn off warnings
    warnings.simplefilter("ignore", DeprecationWarning)
    warnings.simplefilter("ignore", FutureWarning)

    return logger

def default_logger():
    if 'PKDevTools_Default_Log_Level' in os.environ:
        return filterlogger.getlogger(logging.getLogger("PKDevTools"))
    else:
        return emptylogger()

def file_logger():
    if 'PKDevTools_Default_Log_Level' in os.environ:
        return filterlogger.getlogger(logging.getLogger("PKDevTools_file_logger"))
    else:
        return emptylogger()

def trace_log(line):
    """Log tracing information - always works if tracing is enabled"""
    global __trace__
    if __trace__:
        file_logger().info(f"TRACE: {line}")

def flatten(line):
    """Flatten a list (or other iterable) recursively"""
    for el in line:
        if isinstance(el, Iterable) and not isinstance(el, str):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def getargnames(func):
    """Return an iterator over all arg names, including nested arg names and varargs.
    Goes in the order of the functions argspec, with varargs and
    keyword args last if present."""
    (
        args,
        varargs,
        varkw,
        defaults,
        kwonlyargs,
        kwonlydefaults,
        annotations,
    ) = inspect.getfullargspec(func)
    return chain(flatten(args), filter(None, [varargs, varkw]))

def getcallargs_ordered(func, *args, **kwargs):
    """Return an OrderedDict of all arguments to a function.
    Items are ordered by the function's argspec."""
    argdict = inspect.getcallargs(func, *args, **kwargs)
    return OrderedDict((name, argdict[name]) for name in getargnames(func))

def describe_call(func, *args, **kwargs):
    yield "Calling %s with args:" % func.__name__
    for argname, argvalue in getcallargs_ordered(func, *args, **kwargs).items():
        yield "\t%s = %s" % (argname, repr(argvalue))

def log_to(logger_func):
    """A decorator to log every call to function (function name and arg values).
    logger_func should be a function that accepts a string and logs it
    somewhere. The default is logging.debug.
    If logger_func is None, then the resulting decorator does nothing.
    This is much more efficient than providing a no-op logger
    function: @log_to(lambda x: None).
    """
    if logger_func is not None and 'PKDevTools_Default_Log_Level' in os.environ:

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if default_logger().level == logging.DEBUG or __trace__:
                    try:
                        frame = inspect.stack()[1]
                        filename = os.path.basename(frame.filename)
                        func_description = f"{filename} - {frame.function} - {frame.lineno}"
                        
                        description = f"Calling {func.__name__} with args:"
                        for argname, argvalue in inspect.getcallargs(func, *args, **kwargs).items():
                            description += f"\n\t{argname} = {repr(argvalue)}"
                            
                        logger_func(f"{func_description} - {description}")
                        startTime = time.time()
                        ret_val = func(*args, **kwargs)
                        time_spent = time.time() - startTime
                        logger_func(f"{func_description} - {func.__name__} completed: {time_spent:.3f}s (TIME_TAKEN)")
                        return ret_val
                    except Exception:
                        return func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            return wrapper
    else:
        def decorator(func):
            return func

    return decorator

def measure_time(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        # print('%r (%r, %r) %2.2f sec' % \
        #     (f.__name__, args, kw, te-ts))
        print('%r %2.2f sec' % \
            (f.__name__, te-ts))
        return result
    return timed if default_logger().level == logging.DEBUG else log_to(None)

tracelog = log_to(trace_log) if 'PKDevTools_Default_Log_Level' in os.environ and (default_logger().level == logging.DEBUG or __trace__) else log_to(None)

# def timeit(method):
#     def timed(*args, **kw):
#         ts = time.time()
#         result = method(*args, **kw)
#         te = time.time()
#         if 'log_time' in kw:
#             name = kw.get('log_name', method.__name__.upper())
#             kw['log_time'][name] = int((te - ts) * 1000)
#         else:
#             print ('%r  %2.2f ms' % \
#                   (method.__name__, (te - ts) * 1000))
#         return result
#     return timed


class suppress_stdout_stderr(object):
    """
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


def line_break():
    print("-" * 25)


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def set_cursor():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")


def redForegroundText(text):
    print("" + colors.fg.red + text + colors.reset)


def greenForegroundText(text):
    print("" + colors.fg.green + text + colors.reset)

# Register cleanup function
@atexit.register
def cleanup_logging():
    """Clean up logging handlers on exit"""
    if 'PKDevTools_Default_Log_Level' in os.environ:
        logger = default_logger()
        if hasattr(logger, 'flush'):
            logger.flush()
        logging.shutdown()
