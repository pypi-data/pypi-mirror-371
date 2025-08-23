from collections.abc import Callable

class ServiceHandle:
    """
    A handle for manipulating the active windows service.
    """
    def event_log_info(self, s: str) -> None:
        """
        Log an informational event to the registered event log.
        """
        ...
    def event_log_warn(self, s: str) -> None:
        """
        Log a warning event to the registered event log.
        """
        ...
    def event_log_error(self, s: str) -> None:
        """
        Log an error event to the registered event log.
        """
        ...
    def set_service_running(self) -> None:
        """
        Report that the service is now running to windows.
        If this is never called, attempts to start the service will time out.
        """
        ...

def register_service(
    callback: Callable[[ServiceHandle, list[str]], None],
    service_name: str,
    stop_callback: Callable[[], None],
) -> None:
    """
    Create a python service, and register a logger for windows event log.
    This must be called before the service can be started.

     * `callback` - a python function that is called when the service is started.
       this is the main entrypoint to the service.
     * `event_log_name` - name of the event log source to use. This source must be created,
       and is expected to have an EventMessageFile entry pointing to `EventLogMessages.dll`,
       which should be present on all windows machines in some form.
     * `stop_callback` - a python function that is called when the service is asked to stop.
       This should gracefully shut down the service.
    """
    ...

def run_service() -> None:
    """
    Run the registered windows service. This method will block until the service terminates.
    """
    ...
