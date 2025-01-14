import serial
import struct


class SerialHandler:
    def __init__(self, port_name, baud_rate=38400):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.serial_port = None

    def open(self):
        try:
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baud_rate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            return True
        except Exception as e:
            print(f"Failed to open port {self.port_name}: {e}")
            return False

    def close(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def calculate_crc(self, data):
        """
        Calculate CRC16 for Modbus RTU.
        """
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def send_request(self, slave_id, function_code, start_address, data=None):
        """
        Send Modbus RTU request.
        """
        request = [slave_id, function_code, start_address >> 8, start_address & 0xFF]
        if data:
            if isinstance(data, int):  # Single value
                request += [data >> 8, data & 0xFF]
            elif isinstance(data, list):  # Multiple values
                request += [len(data) >> 8, len(data) & 0xFF]
                request += [len(data) * 2]  # Byte count
                for value in data:
                    request += [value >> 8, value & 0xFF]

        # Calculate and append CRC
        crc = self.calculate_crc(request)
        request += [crc & 0xFF, (crc >> 8) & 0xFF]
        self.serial_port.write(bytearray(request))

    def read_response(self, expected_length):
        """
        Read and validate response.
        """
        response = self.serial_port.read(expected_length)
        if len(response) < expected_length:
            print("Incomplete response")
            return None

        # Verify CRC
        data = response[:-2]
        received_crc = struct.unpack("<H", response[-2:])[0]
        calculated_crc = self.calculate_crc(data)

        if received_crc != calculated_crc:
            print("CRC validation failed")
            return None

        return response

    def write_single(self, slave_id, address, value):
        """
        Write a single register (Function 0x06).
        """
        self.send_request(slave_id, 0x06, address, value)
        return self.read_response(8)

    def write_multiple(self, slave_id, address, values):
        """
        Write multiple registers (Function 0x10).
        """
        self.send_request(slave_id, 0x10, address, values)
        return self.read_response(8)

    def read_holding_registers(self, slave_id, address, count):
        """
        Read holding registers (Function 0x03).
        """
        self.send_request(slave_id, 0x03, address, count)
        response_length = 5 + count * 2  # Modbus RTU framing
        return self.read_response(response_length)
