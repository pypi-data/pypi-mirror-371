# Cognite Windows Service Library

This is a python/rust library for running python programs as simple windows services. It supports basic event logging, though you will need to define the event message source yourself, typically through a windows installer or similar.

Unlike other windows service libraries, it does not have code to actually create the windows service, again assuming that this is done externally.

Event logging uses the user provided event log source name, and logs plain text to event ID 0.

## Usage

See the python interface. Simply install the library, call `register_service`, and once the extractor has come somewhat online, call `set_service_running` on the `ServiceHandle` passed to the startup callback. See method docs.

```python
from simple_winservice import register_service, run_service, ServiceHandle
from threading import Event

token = Event()

def cancel_service() -> None:
    token.set()

def service_main(handle: ServiceHandle, args: list[str]) -> None:
    handle.event_log_info("Service is now running!")

    while not token.wait(1):
        handle.event_log_info("Service is still running!")

    handle.event_log_info("Service is shutting down now")

def main() -> None:
    register_service(service_main, "MyTestService", cancel_service)
    run_service()

if __name__ == "__main__":
    main()
```

## Development

You will need `maturin`, and rust/cargo, installed using `rustup`. To build, activate a local venv, then just run `maturin develop`, after which the local venv will contain an installed version of the library you can use. There's a sample service in the `service_test.py` file, which is intended to be run as a windows service called with entry point `.../.env/Scripts/python.exe .../service_test.py more arguments here`.
