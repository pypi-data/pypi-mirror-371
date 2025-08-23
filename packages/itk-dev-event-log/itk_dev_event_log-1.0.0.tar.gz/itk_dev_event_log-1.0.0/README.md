# itk_dev_event_log

## Intro

This library is a simple MSSQL-based event logging system.

It allows one to log events to a database consisting of a process name, message and count.
The log is automatically stamped with the current time.

## Usage

```python
import itk_dev_event_log

itk_dev_event_log.setup_logging(
    "Server=localhost\SQLEXPRESS;Database=MyDatabase;Trusted_Connection=yes;Driver={ODBC Driver 17 for SQL Server}"
)

itk_dev_event_log.emit("process", "message", 1)
itk_dev_event_log.emit("process", "message", 1)
itk_dev_event_log.emit("process", "message", 1)
```
