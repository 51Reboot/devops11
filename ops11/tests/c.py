

class User(object):

    def __init__(self, id, name, address):
        self.id = id
        self.name = name
        self.address = address

    def serializer(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
        }


p = User(1, "reboot", 6)
print(p.serializer())
