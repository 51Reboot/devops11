from faker import Faker
from xpinyin import Pinyin

faker = Faker(locale="zh_CN")
p = Pinyin()

for i in range(100):
    gen_cn_name = faker.name_male()
    phone = faker.phone_number()
    yp_name = p.get_pinyin(gen_cn_name)
    yp_name = yp_name.replace("-", "")
    print(f"{gen_cn_name} {yp_name} {phone}")

