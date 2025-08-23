use std::{
    ffi::OsString,
    sync::{LazyLock, Mutex},
    time::Duration,
};

mod eventlog;

use ::windows_service::{
    define_windows_service,
    service::{
        ServiceControl, ServiceControlAccept, ServiceExitCode, ServiceState, ServiceStatus,
        ServiceType,
    },
    service_control_handler::{self, ServiceControlHandlerResult, ServiceStatusHandle},
    service_dispatcher,
};
use pyo3::{
    exceptions::{PyException, PyValueError},
    prelude::*,
    types::PyFunction,
};

struct ServiceInfo {
    callback: Py<PyFunction>,
    on_stop_cb: Py<PyFunction>,
    name: String,
}

static SERVICE_START_CB: LazyLock<Mutex<Option<ServiceInfo>>> = LazyLock::new(Mutex::default);

define_windows_service!(ffi_service_main, safe_service_main);

#[pyclass]
#[derive(Clone)]
struct ServiceHandle {
    handle: ServiceStatusHandle,
}

#[pymethods]
impl ServiceHandle {
    /// Log an informational event to the registered event log.
    fn event_log_info(&self, s: &str) {
        log::info!("{s}");
    }

    /// Log a warning event to the registered event log.
    fn event_log_warn(&self, s: &str) {
        log::warn!("{s}");
    }

    /// Log an error event to the registered event log.
    fn event_log_error(&self, s: &str) {
        log::error!("{s}");
    }

    /// Report that the service is now running to windows.
    /// If this is never called, attempts to start the service will time out.
    fn set_service_running(&self) -> PyResult<()> {
        self.handle
            .set_service_status(ServiceStatus {
                service_type: ServiceType::OWN_PROCESS,
                current_state: ServiceState::Running,
                controls_accepted: ServiceControlAccept::STOP,
                exit_code: ServiceExitCode::Win32(0),
                checkpoint: 0,
                wait_hint: Duration::default(),
                process_id: None,
            })
            .map_err(|e| {
                PyErr::new::<PyException, _>(format!("Failed to set service status: {e}"))
            })?;
        Ok(())
    }
}

fn setup_service_internal(
    info: &ServiceInfo,
    name: &str,
    py: Python<'_>,
) -> Result<ServiceHandle, ::windows_service::Error> {
    // We do need to register a service control event handler. For now, all we really care about
    // is the stop event, which we follow up on by calling the python stop callback.
    let stop_cb = info.on_stop_cb.clone_ref(py);
    let event_handler = move |control_event| match control_event {
        ServiceControl::Stop => {
            Python::with_gil(|py2| {
                log::info!("Service stop was requested, shutting down");
                if let Err(e) = stop_cb.call(py2, (), None) {
                    log::error!("Failed to call python stop callback: {e}");
                }
            });
            ServiceControlHandlerResult::NoError
        }
        ServiceControl::Interrogate => ServiceControlHandlerResult::NoError,
        _ => ServiceControlHandlerResult::NotImplemented,
    };
    let status_handle = service_control_handler::register(name, event_handler)?;
    Ok(ServiceHandle {
        handle: status_handle,
    })
}

const PYTHON_FAILED_EXIT_CODE: u32 = 1;

fn safe_service_main(arguments: Vec<OsString>) {
    // Try to get the callback, otherwise there really isn't anything we can do here.

    // We hold the lock while the service is running. You _really_ cannot run multiple services
    // in the same process, so this is required for this API to be sound.
    let lck = SERVICE_START_CB.lock().unwrap();
    let Some(svc) = lck.as_ref() else {
        return;
    };
    // Grab the GIL. That does mean we need to release the GIL before this method is called.
    // From here we get a service handle, and an exit code. We may not get a service handle,
    // if something goes disastrously wrong, but it should not be possible to cause that to happen
    // from faulty python code, and it would indicate a bug in this library.
    let handle = Python::with_gil(|py| {
        // Parse the arguments from the service call.
        let args_str: Result<Vec<_>, _> = arguments.into_iter().map(|a| a.into_string()).collect();
        let args_str = match args_str {
            Ok(v) => v,
            Err(e) => {
                log::error!("Failed to convert argument to string: {:?}", e);
                pyo3::exceptions::PyValueError::new_err("Service arguments are not valid strings")
                    .restore(py);
                return None;
            }
        };

        // The service name is always the first argument.
        let Some(svc_name) = args_str.first().cloned() else {
            pyo3::exceptions::PyValueError::new_err(
                "The service name is not present in the argument list. Is the entry point not called by windows?"
            ).restore(py);
            return None;
        };

        let handle = match setup_service_internal(svc, &svc_name, py) {
            Ok(v) => v,
            Err(e) => {
                log::error!("Failed to setup service: {:?}", e);
                pyo3::exceptions::PyException::new_err(format!("Failed to setup service: {e:?}"))
                    .restore(py);
                return None;
            }
        };

        let mut exit_code = 0;

        // Call the python callback. This is the entry point to the service, and will block.
        // Most services will never return from here, unless cancelled externally.
        // Those that do return may be restarted automatically by windows.
        if let Err(e) = svc.callback.call(py, (handle.clone(), args_str), None) {
            log::error!("Python callback failed fatally: {e:?}");
            e.restore(py);
            // When the python program fails fatally, we still want to report that the service
            // stopped, so return the handle.
            // We do need to set a non-zero exit code.
            exit_code = PYTHON_FAILED_EXIT_CODE;
        }

        Some((handle, exit_code))
    });

    if let Some((handle, exit_code)) = handle {
        let _ = handle.handle.set_service_status(ServiceStatus {
            service_type: ServiceType::OWN_PROCESS,
            current_state: ServiceState::Stopped,
            controls_accepted: ServiceControlAccept::STOP,
            exit_code: if exit_code != 0 {
                // This exit code can be completely arbitrary. L
                ServiceExitCode::ServiceSpecific(exit_code)
            } else {
                ServiceExitCode::Win32(0)
            },
            checkpoint: 0,
            wait_hint: Duration::default(),
            process_id: None,
        });
    }
}

#[pyfunction]
/// Create a python service, and register a logger for windows event log.
/// This must be called before the service can be started.
///
/// # Arguments
///
///  * `callback` - a python function that is called when the service is started.
///    this is the main entrypoint to the service.
///  * `event_log_name` - name of the event log source to use. This source must be created,
///    and is expected to have an EventMessageFile entry pointing to `EventLogMessages.dll`,
///    which should be present on all windows machines in some form.
///  * `stop_callback` - a python function that is called when the service is asked to stop.
///    This should gracefully shut down the service.
fn register_service(
    py: Python<'_>,
    callback: Py<PyFunction>,
    event_log_name: String,
    stop_callback: Py<PyFunction>,
) -> PyResult<()> {
    py.allow_threads(|| {
        eventlog::init(&event_log_name)
            .map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))?;
        *SERVICE_START_CB.lock().unwrap() = Some(ServiceInfo {
            callback,
            name: event_log_name,
            on_stop_cb: stop_callback,
        });
        Ok(())
    })
}

#[pyfunction]
/// Run the service. This will block until the service terminates.
fn run_service(py: Python<'_>) -> PyResult<()> {
    py.allow_threads(|| {
        let Some(name) = SERVICE_START_CB
            .lock()
            .unwrap()
            .as_ref()
            .map(|m| m.name.clone())
        else {
            return Err(PyErr::new::<PyException, _>(
                "Attempted to start service that has not yet been registered",
            ));
        };

        service_dispatcher::start(&name, ffi_service_main).map_err(|e| {
            PyErr::new::<PyException, _>(format!("Unexpected error starting service: {e}"))
        })?;

        Ok(())
    })
}

/// A rust library for running windows services from python with logging through
/// event log.
#[pymodule(name = "simple_winservice")]
fn service(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(register_service, m)?)?;
    m.add_function(wrap_pyfunction!(run_service, m)?)?;
    m.add_class::<ServiceHandle>()?;
    Ok(())
}
