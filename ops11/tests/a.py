import time

# def run():
#     a = "123"
#     print(a)
#
# # print(a)
#
# c = 100
#
# def f1():
#     # 嵌套变量
#     a = 1
#
#     def f2():
#         b = 2
#         print(a)
#
#     f2()
#
#
# f1()

timer = time.time


def decorateMsg(msg):
    def decorate(func):

        def wrapperxxxx(*args, **kwargs):
            start = timer()

            func(*args, **kwargs)

            stop = timer()
            print(f"time interval {stop-start}", msg)

        return wrapperxxxx
    return decorate


@decorateMsg(msg="hello world")
def f1(x, y, z):
    print("hello world")
    time.sleep(5)


print(f1(1, 2, 3))