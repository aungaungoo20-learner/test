from pymodbus.client import ModbusSerialClient

# Configure the Modbus RTU client
client = ModbusSerialClient(
    method="rtu",
    port="/dev/ttyUSB0",  # on Windows something like "COM3"
    baudrate=9600,
    timeout=1,
    parity="N",
    stopbits=1,
    bytesize=8
)

if not client.connect():
    raise Exception("Could not connect to Modbus device")
