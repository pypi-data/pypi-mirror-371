# OzOptics ODL module driver

import logging
import time

import serial.tools.list_ports
from serial import Serial

from pnpq.errors import OdlGetPosNotCompleted


class OpticalDelayLine:
    """Base class for the OzOptics ODL driver."""

    name: str
    conn: Serial
    """represents a Serial connection"""

    device_sn: str | None
    """device's serial number"""

    port: str | None
    """initialize ODL class"""

    def __init__(
        self,
        port: str | None = None,
        serial_number: str | None = None,
    ):
        if serial_number is None and port is None:
            raise RuntimeError("Not port name nor serial_number are specified!")

        self.name = "Optical Delay Line"
        self.default_interface = "Serial Interface"
        self.device_sn = serial_number
        self.port = port
        self.conn = Serial()

        available_ports = serial.tools.list_ports.comports()
        for ports in available_ports:
            if ports.serial_number == self.device_sn or ports.device == self.port:
                self.conn.port = ports.device
                break

        if self.conn.port is None:
            raise RuntimeError("Can not find ODL by serial_number (FTDI_SN) or port!")


class OdlOzOptics(OpticalDelayLine):
    def __init__(
        self,
        serial_port: str | None = None,
        serial_number: str | None = None,
    ):
        super().__init__(serial_port, serial_number)
        self.conn.baudrate = 9600
        """Basic Communication BaudRate"""
        self.resolution = 32768 / 5.08
        """32768 steps per motor revolution(5.08 mm = 2xDistance Travel or mirror travel per pitch 0.1 inch)"""
        self.conn.timeout = 10

        self.command_terminate = "\r\n"

        self.logger = logging.getLogger(f"{self}")
        self.conn.open()

    def connect(self) -> None:
        if self.conn.is_open == 0:
            self.conn.open()

    def move(self, dist: float) -> None:
        if not self.conn.is_open:
            raise RuntimeError("Moving ODL failed: can not connect to ODL device")
        if dist > 200 or dist < 0:
            raise ValueError("Invalid Move Parameter")
        self.set_step(int(dist * self.resolution))

    def set_step(self, value: int) -> str:
        cmd = "S" + str(value)
        response = self.serial_command(cmd)
        return response

    def get_step(self) -> int:
        response = self.serial_command("S?")
        if "UNKNOWN" in response:
            raise OdlGetPosNotCompleted(
                f"Unknown position for ODL({self}): run find_home() first and then change or get the position"
            )
        step = response.split("Done")[0].split(":")[1]
        return int(step)

    def home(self) -> str:
        cmd = "FH"
        response = self.serial_command(cmd)
        return response

    def get_serial(self) -> str:
        cmd = "V2"
        response = self.serial_command(cmd)
        return response.split("Done")[0].split("\r\n")[1]

    def get_device_info(self) -> tuple[str, str]:
        cmd = "V1"
        response = self.serial_command(cmd)
        response = response.split("\r\n")[1]
        device_name = response.split("V")[0]
        hwd_version = response.split("V")[1].split("_")[0]
        return device_name, hwd_version

    def get_mfg_date(self) -> str:
        cmd = "d?"
        response = self.serial_command(cmd)
        date = response.split("\r\n")[1]
        return date

    def echo(self, on_off: int) -> str:
        cmd = "e" + str(on_off)
        response = self.serial_command(cmd)
        return response

    def reset(self) -> str:
        cmd = "RESET"
        response = self.serial_command(cmd)
        return response

    def oz_mode(self, on_off: int) -> str:  # on_off -> 0: OZ mode OFF | 1: OZ mode ON
        cmd = "OZ-SHS" + str(on_off)
        # cmd = '?'
        response = self.serial_command(cmd)
        return response

    def forward(self) -> str:
        cmd = "GF"
        response = self.serial_command(cmd)
        return response

    def reverse(self) -> str:
        cmd = "GR"
        response = self.serial_command(cmd)
        return response

    def stop(self) -> str:
        cmd = "G0"
        response = self.serial_command(cmd)
        return response

    def write_to_flash(self) -> str:
        cmd = "OW"
        response = self.serial_command(cmd)
        return response

    def start_burn_in(self, parameter: int) -> str:
        cmd = "OZBI" + str(parameter)
        response = self.serial_command(cmd)
        return response

    def write_name(self, parameter: int) -> str:
        cmd = "ODN" + str(parameter)
        response = self.serial_command(cmd)
        return response

    def write_serial(self, parameter: int) -> str:
        cmd = "ODS" + str(parameter)
        response = self.serial_command(cmd)
        return response

    def write_mfg_date(self, parameter: int) -> str:
        cmd = "ODM" + str(parameter)
        response = self.serial_command(cmd)
        return response

    def write_hw_version(self, parameter: int) -> str:
        cmd = "OHW" + str(parameter)
        response = self.serial_command(cmd)
        return response

    def serial_close(self) -> None:
        self.conn.close()

    def serial_send(self, serial_cmd: str) -> None:
        # Encode and send the command to the serial device.
        self.conn.reset_input_buffer()  # flush input buffer, discarding all its contents
        self.conn.reset_output_buffer()  # flush output buffer, aborting current output and discard all that is in buffer
        self.conn.write(serial_cmd.encode())

    def serial_read(self) -> str:
        device_output = (self.conn.read_until(expected=b"Done")).decode("iso-8859-1")
        self.logger.debug("Device read successful: %s", device_output)
        if "Done" not in device_output:
            raise RuntimeError("Reading from the device failed (Timeout)!")
        return device_output

    def serial_command(self, serial_cmd: str) -> str:
        self.serial_send(serial_cmd + self.command_terminate)
        device_output = self.serial_read()
        return device_output

    def read_key(self, key: str, retries: int = 5) -> str:
        device_output = ""
        got_ok = False
        while self.conn.in_waiting > 0 or (got_ok is False and retries > 0):
            device_output += (self.conn.read(self.conn.in_waiting)).decode("iso-8859-1")
            # command output is complete.
            if device_output.find(key) >= 0:
                got_ok = True
            time.sleep(0.05)
            retries -= 1
        return device_output

    def readall(self) -> tuple[bool, str]:
        ok = False
        read_bytes = self.conn.read(1)
        while self.conn.in_waiting > 0:
            read_bytes += self.conn.read(1)
        msg = read_bytes.decode("UTF-8")
        ok = True
        return ok, msg


if __name__ == "__main__":
    dev = OdlOzOptics("/dev/ttyUSB0")
    print("Module Under Test")
