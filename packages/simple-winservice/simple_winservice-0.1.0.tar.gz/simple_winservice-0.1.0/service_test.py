import os
from threading import Event

from simple_winservice import ServiceHandle, register_service, run_service

tok = Event()


def cancel_service() -> None:
    tok.set()


def service_main(handle: ServiceHandle, args: list[str]) -> None:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    handle.event_log_info("Successfully started service thingy!")
    with open("output_test.txt", "w") as f:
        f.write("Hello from service start\n")
        for arg in args:
            f.write(f"Service arg: {arg}\n")
    handle.set_service_running()
    handle.event_log_info("Service is now running yay")
    while not tok.wait(1):
        with open("output_test.txt", "a") as f:
            f.write("Hello from service running\n")
    with open("output_test.txt", "a") as f:
        f.write("Hello from service end\n")
    handle.event_log_info("Service was asked to shut down and is complying")


def main() -> None:
    register_service(service_main, "MyTestService4", cancel_service)
    run_service()


if __name__ == "__main__":
    main()
