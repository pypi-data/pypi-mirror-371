//! Logic based on winlog2, which is forked from winlog,
//! https://github.com/Berrysoft/winlog
//! Unlike winlog we send only a single event ID, 0, and use
//! the .NET 4 built-in EventMessageFile, since this is shipped bundled with a python
//! executable, and has no easy way to expose its own string table.

use log::{Level, LevelFilter, Metadata, Record};
use widestring::U16CString;
use windows_sys::Win32::{
    Foundation::HANDLE,
    System::EventLog::{
        DeregisterEventSource, RegisterEventSourceW, ReportEventW, EVENTLOG_ERROR_TYPE,
        EVENTLOG_INFORMATION_TYPE, EVENTLOG_WARNING_TYPE,
    },
};

/// Initialize the event log logger, registering it with `log`
pub fn init(name: &str) -> Result<(), String> {
    log::set_boxed_logger(Box::new(WinLogger::new(name)?))
        .map_err(|e| format!("Failed to set logger: {e}"))?;
    log::set_max_level(LevelFilter::Trace);
    Ok(())
}

struct WinLogger {
    handle: HANDLE,
}

impl WinLogger {
    pub fn new(name: &str) -> Result<WinLogger, String> {
        let name = U16CString::from_str(name)
            .map_err(|e| format!("Failed to convert event log name to UTF-16 string: {e}"))?;
        // SAFETY: So long as we pass a valid utf-16 string, this should be fine.
        // The server name is allowed to be null.
        let handle = unsafe { RegisterEventSourceW(std::ptr::null_mut(), name.as_ptr()) };

        if handle.is_null() {
            Err(format!(
                "Failed to register event source: {}",
                std::io::Error::last_os_error()
            ))
        } else {
            Ok(WinLogger { handle })
        }
    }
}

impl Drop for WinLogger {
    fn drop(&mut self) {
        unsafe { DeregisterEventSource(self.handle) };
    }
}

// SAFETY: event source should be thread safe
unsafe impl Send for WinLogger {}
unsafe impl Sync for WinLogger {}

impl log::Log for WinLogger {
    fn enabled(&self, _: &Metadata) -> bool {
        true
    }

    fn log(&self, record: &Record) {
        let level = record.level();
        // Event log only has information, warning, and error.
        let wtype = match level {
            Level::Error => EVENTLOG_ERROR_TYPE,
            Level::Warn => EVENTLOG_WARNING_TYPE,
            Level::Info => EVENTLOG_INFORMATION_TYPE,
            Level::Debug => EVENTLOG_INFORMATION_TYPE,
            Level::Trace => EVENTLOG_INFORMATION_TYPE,
        };

        let msg = U16CString::from_str_truncate(format!("{}", record.args()));
        let msg_ptr = msg.as_ptr();

        // SAFETY: `handle` is a valid event log handle, verified to be non-null in `new`.
        // The string array must be a valid pointer to one or more UTF-16 strings, in this case
        // just the message itself.
        unsafe {
            ReportEventW(
                self.handle,
                wtype, // type, inferred from log level.
                0,     // category
                0,     // Event ID is 0, which gives clean and error-free event logs.
                std::ptr::null_mut(),
                1, // Number of strings in lpstrings array.
                0,
                &msg_ptr,
                std::ptr::null_mut(),
            )
        };
    }

    fn flush(&self) {}
}
