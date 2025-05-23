import unittest
from lab_7 import get_triangle_type, IncorrectTriangleSides

class TestTriangle(unittest.TestCase):
    positive = []
    negative = []

    def setUp(self):
        with open ('check.txt') as file:
            lines = file.readlines()

        negative = False # Флаг того, что мы обрабатываем негативные случаи
        for line in lines:
            if line.strip() == '---':
                negative = True
            elif negative:
                a, b, c = line.strip().split(', ') # Разделить строчку и каждый результат положить в соответствующую переменную
                self.negative.append([a,b,c])
            else:
                values, result = line.strip().split(': ')
                a, b, c = values.split(', ') # Разделить строчку и каждый результат положить в соответствующую переменную
                self.positive.append([a,b,c, result])
        
    def test_positive(self):
        for case in self.positive:
            a, b, c, result = case
            triangle_type = get_triangle_type(a,b,c)
            # Сравниваю результат функции и ожидаемый результат на одиннаковость. И если они разные, то считаю, что тест не пройден
            self.assertEqual(result, triangle_type, 'Неправильный тип треугольника: ' + result + ' ' + triangle_type) 

    def test_negative(self):
        for case in self.negative:
            a, b, c = case
            # Хочу, чтобы вылетела ошибка. Если она не вылетела, то тест считается непройденным.
            with self.assertRaises(IncorrectTriangleSides, msg='Ошибки не произошло'):
                get_triangle_type(a,b,c)
            

if __name__ == '__main__':
    unittest.main()