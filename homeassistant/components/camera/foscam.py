"""
This component provides basic support for Foscam IP cameras.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/camera.foscam/
"""
import logging

import voluptuous as vol

from homeassistant.components.camera import (Camera, PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_NAME, CONF_USERNAME, CONF_PASSWORD, CONF_PORT)
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['libpyfoscam==1.0']

CONF_IP = 'ip'

DEFAULT_NAME = 'Foscam Camera'
DEFAULT_PORT = 88

FOSCAM_COMM_ERROR = -8

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up a Foscam IP Camera."""
    add_entities([FoscamCam(config)])


class FoscamCam(Camera):
    """An implementation of a Foscam IP camera."""

    def __init__(self, device_info):
        """Initialize a Foscam camera."""
        from libpyfoscam import FoscamCamera

        super(FoscamCam, self).__init__()

        ip_address = device_info.get(CONF_IP)
        port = device_info.get(CONF_PORT)
        self._username = device_info.get(CONF_USERNAME)
        self._password = device_info.get(CONF_PASSWORD)
        self._name = device_info.get(CONF_NAME)
        self._motion_status = False

        self._foscam_session = FoscamCamera(
            ip_address, port, self._username, self._password, verbose=False)

        t = time.localtime(time.time())
        self._foscam_session.set_system_time(1, 'time.nist.gov', 0,
            1, 0, 0, 1, t[0],
            t[1], t[2], t[3], t[4], t[5], callback=None)

    def camera_image(self):
        """Return a still image response from the camera."""
        # Send the request to snap a picture and return raw jpg data
        # Handle exception if host is not reachable or url failed
        result, response = self._foscam_session.snap_picture_2()
        if result == FOSCAM_COMM_ERROR:
            return None

        return response

    @property
    def motion_detection_enabled(self):
        """Camera Motion Detection Status."""
        return self._motion_status

    def enable_motion_detection(self):
        """Enable motion detection in camera."""
        try:
            ret = self._foscam_session.enable_motion_detection()
            self._motion_status = ret == FOSCAM_COMM_ERROR
        except TypeError:
            _LOGGER.debug("Communication problem")
            self._motion_status = False

    def disable_motion_detection(self):
        """Disable motion detection."""
        try:
            ret = self._foscam_session.disable_motion_detection()
            self._motion_status = ret == FOSCAM_COMM_ERROR
        except TypeError:
            _LOGGER.debug("Communication problem")
            self._motion_status = False

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name
