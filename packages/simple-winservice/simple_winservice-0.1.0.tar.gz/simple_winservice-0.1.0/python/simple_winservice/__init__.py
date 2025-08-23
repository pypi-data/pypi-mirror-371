"""
This is a simple rust-based python library for creating basic windows services.

It supports basic event logging, as well as setting up and running a service. Note that
you must provide the event message source for event logging yourself.

.. code-block:: python

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
"""

from .simple_winservice import *
