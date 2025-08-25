# wai-logging
Simple helper library for logging.


## Installation

From PyPI:

```bash
pip install wai_logging
```

From Github:

```bash
pip install git+https://github.com/waikato-datamining/wai-logging.git
```


## Methods

The following helper methods are available:

* `init_logging` - initializes the logging with a default level, which can be overridden with an environment variable
* `set_logging_level` - sets the logging level of a `logging.Logger` instance
* `str_to_logging_level` - turns a string logging level into a `logging` module one, used by `init_logging` and `set_logging_level`
* `add_logging_level` - adds an option for the logging level to an `argparse.ArgumentParser` instance
* `add_logger_name` - adds an option for a custom name for a logger to an `argparse.ArgumentParser` instance


## Usage

Below are some examples on how to use the aforementioned methods and what the 
output may look like. 

### Example 1

The following logging setup only outputs on stderr using a simple format without timestamps: 

```python
from wai.logging import init_logging, LOGGING_INFO, set_logging_level
import logging

init_logging(LOGGING_INFO)
logger = logging.getLogger("my.test")
set_logging_level(logger, LOGGING_INFO)
logger.debug("debugging output")
logger.info("info output")
logger.warning("warning output")
```

The output:

```
INFO:my.test:info output
WARNING:my.test:warning output
```

### Example 2

This configuration uses timestamps in its output (`log_format`; see [format strings](https://docs.python.org/3/library/logging.html#logrecord-attributes)) 
and logs to a file as well (`filename`):

```python
from wai.logging import init_logging, LOGGING_INFO, set_logging_level, TIMESTAMP_LOG_FORMAT
import logging

init_logging(LOGGING_INFO, filename="./out.log", log_format=TIMESTAMP_LOG_FORMAT)
logger = logging.getLogger("my.test")
set_logging_level(logger, LOGGING_INFO)
logger.debug("debugging output")
logger.info("info output")
logger.warning("warning output")
```

The output:

```
2025-01-14 09:25:22,837 - INFO - my.test - info output
2025-01-14 09:25:22,837 - WARNING - my.test - warning output
```

### Example 3

The following setup uses a [rotating file handler](https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler) 
and keeps a maximum of three backups (`backupCount`; log files get a numeric suffix like `.1`). 
A rotation is initiated when the process is restarted and the log file exceeds 100 bytes (`maxBytes`).

```python
from wai.logging import init_logging, LOGGING_INFO, set_logging_level
import logging.handlers

init_logging(LOGGING_INFO, handlers=[
    logging.StreamHandler(), 
    logging.handlers.RotatingFileHandler(filename="./out.log", backupCount=3, maxBytes=100)])
logger = logging.getLogger("my.test")
set_logging_level(logger, LOGGING_INFO)
logger.debug("debugging output")
logger.info("info output")
logger.warning("warning output")
```

The output:

```
INFO:my.test:info output
WARNING:my.test:warning output
```
