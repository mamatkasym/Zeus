import hashlib
import hmac
import subprocess
import urllib.parse
import uuid

try:
    from constants import Constants
except ImportError:
    from .constants import Constants


class Signature:
    @staticmethod
    def get_enc_password(password, public_key, public_key_id):
        proc = subprocess.Popen(["php", "-f", "encrypt.php", password, public_key_id, public_key],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out = proc.communicate()[0]
        return out.decode()

    @staticmethod
    def generate_UUID(uuid_type):
        generated_uuid = str(uuid.uuid4())
        if uuid_type:
            return generated_uuid
        else:
            return generated_uuid.replace("-", "")

    @staticmethod
    def generate_signature_data(data):
        hash = hmac.new(Constants.IG_SIG_KEY.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()

        return 'signed_body=' + hash + '.' + urllib.parse.quote_plus(data) + '&ig_sig_key_version=4'

    @staticmethod
    def generate_signature(data):
        return hmac.new(Constants.IG_SIG_KEY.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()

    @staticmethod
    def generate_jazoest(phone_id):
        jazoest_prefix = '2'
        array = list(phone_id)
        i = 0
        for a in array:
            i += ord(str(a))

        return jazoest_prefix + str(i)

    @staticmethod
    def get_seed(*args):
        m = hashlib.md5()
        m.update(b"".join([arg.encode("utf-8") for arg in args]))
        return m.hexdigest()

    @staticmethod
    def generate_device_id(seed):
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode("utf-8") + volatile_seed.encode("utf-8"))
        return "android-" + m.hexdigest()[:16]

    @staticmethod
    def generate_all():
        print("Please enter username and password")
        username, password = input().split()

        phone_id = Signature.generate_UUID(True)
        print("Phone id is --> ", phone_id )
        print("uuid is --> ", Signature.generate_UUID(True))
        print("session id is --> ", Signature.generate_UUID(True))
        print('device id is --> ', Signature.generate_UUID(Signature.get_seed(username,password)))
        print("android device id is --> ", Signature.generate_device_id(phone_id))
        print("jazoest is --> ", Signature.generate_jazoest(phone_id))



# print(Signature.generate_all())
