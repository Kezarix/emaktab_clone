import re

text_data = """
Иван: +79991112233, Анна: +79992223344.
Заказ №45892 был успешно отправлен.
Цена товара: 1 500 руб. Скидка: 300 руб.
"""

print("--- ИСХОДНЫЙ ТЕКСТ ---")
print(text_data.strip())
print("-" * 30)

match = re.search(r"Заказ №(\d+)", text_data)

print("[1. re.search]")
if match:
    print("Полное совпадение:", match.group(0))
    print("Извлеченный номер заказа:", match.group(1))
print("-" * 30)

phones = re.findall(r"\+?\d{11}", text_data)

print("[2. re.findall]")
print("Найденные телефоны:", phones)
print("-" * 30)

clean_text = re.sub(r"(?<=\d)\s(?=\d)", "", text_data)

print("[3. re.sub]")
print("Текст после удаления пробелов в числах:")
print(clean_text.strip())
print("-" * 30)


#split разбивает по шаблонам
#re.finditer — находит все совпадения, но возвращает подробные объекты
#re.compile — собирает шаблон заранее.