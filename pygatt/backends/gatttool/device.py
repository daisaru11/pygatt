import functools
import logging

from pygatt import BLEDevice, exceptions

log = logging.getLogger(__name__)


def connection_required(func):
    """Raise an exception before calling the actual function if the device is
    not connection.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._connected:
            raise exceptions.NotConnectedError()
        return func(self, *args, **kwargs)
    return wrapper


class GATTToolBLEDevice(BLEDevice):
    """A BLE device connection initiated by the GATTToolBackend.

    Since the GATTToolBackend can only support 1 device connection at at time,
    the device implementation defers to the backend for all functionality -
    every command has to synchronize around a the same interactive gatttool
    session, using the same connection.
    """
    def __init__(self, address, backend):
        super(GATTToolBLEDevice, self).__init__(address)
        self._primary_services = {}
        self._characteristics_by_service = {}
        self._descriptors_by_service = {}
        self._backend = backend
        self._connected = True

    @connection_required
    def bond(self, *args, **kwargs):
        self._backend.bond(self, *args, **kwargs)

    @connection_required
    def char_read(self, uuid, *args, **kwargs):
        return self._backend.char_read(self, uuid, *args, **kwargs)

    @connection_required
    def char_read_handle(self, handle, *args, **kwargs):
        return self._backend.char_read_handle(self, handle, *args, **kwargs)

    @connection_required
    def char_write_handle(self, handle, *args, **kwargs):
        self._backend.char_write_handle(self, handle, *args, **kwargs)

    @connection_required
    def disconnect(self):
        self._backend.disconnect(self)
        self._connected = False

    @connection_required
    def discover_characteristics(self):
        self._characteristics = self._backend.discover_characteristics(self)
        return self._characteristics

    @connection_required
    def discover_characteristics_by_service(self, service_uuid):
        self._characteristics_by_service[service_uuid] = self._backend.discover_characteristics_by_service(self, service_uuid)
        return self._characteristics_by_service[service_uuid]

    @connection_required
    def discover_descriptors_by_service(self, service_uuid):
        self._descriptors_by_service[service_uuid] = self._backend.discover_descriptors_by_service(self, service_uuid)
        return self._descriptors_by_service[service_uuid]

    @connection_required
    def primary_services(self):
        self._primary_services = self._backend.primary_services(self)
        return self._primary_services
