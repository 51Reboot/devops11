

class A(object):

    @classmethod
    def as_view(cls):
        print("C")

    def dispath(self):
        print("dispath A")


class B(object):

    @classmethod
    def as_view(cls):
        cls().dispath()
        print("C")

    def dispath(self):
        print("dispath B")


class C(A, B):

    @classmethod
    def as_view(cls):
        super(C, cls).as_view()
        print("C")

    def dispath(self):
        print("dispath C")


C.as_view()