try:
    from signature import Signature
except ImportError:
    from ..signature import Signature


class DeviceInfo:

    def __init__(self):
        self.uuid = Signature.generate_UUID(True)
        self.phone_id = Signature.generate_UUID(True)
        self.x_pigeon = Signature.generate_UUID(True)
        self.android_device_id = Signature.generate_device_id(self.phone_id)
        self.jazoest = Signature.generate_jazoest(self.phone_id)
        self.waterfall_id = Signature.generate_UUID(True)
        self.advertising_id = Signature.generate_UUID(True)
        self.attribution_id = Signature.generate_UUID(True)

    def get_device_info(self):
        device = {
            'uuid': self.uuid,
            'phone_id': self.phone_id,
            'x_pigeon': self.x_pigeon,
            'android_device_id': self.android_device_id,
            'jazoest': self.jazoest,
            'waterfall_id': self.waterfall_id,
            'advertising_ud': self.advertising_id,
            'attribution_id': self.attribution_id
        }
        return device


if __name__ == "__main__":
    pass
