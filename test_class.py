import unittest
from triangle_class import Triangle, IncorrectTriangleSides

class TestTriangle(unittest.TestCase):
    def test_equilateral(self):
        triangle = Triangle(10, 10, 10)
        self.assertEqual(triangle.triangle_type(), 'equilateral')
    
    def test_isosceles(self):
        triangle = Triangle(10, 10, 15)
        self.assertEqual(triangle.triangle_type(), 'isosceles')

    def test_nonequilateral(self):
        triangle = Triangle(3, 4, 5)
        self.assertEqual(triangle.triangle_type(), 'nonequilateral')

    def test_perimeter(self):
        triangle = Triangle(5, 7, 12)
        self.assertEqual(triangle.perimeter(), 24)

    # Отрицательные тесты
    def test_nonnumbers(self):
        with self.assertRaises(IncorrectTriangleSides, msg='Ошибка не произошла'):
            triangle = Triangle('a', 'b', 'c')
    
    def test_minus(self):
        with self.assertRaises(IncorrectTriangleSides, msg='Ошибка не произошла'):
            triangle = Triangle(-3, -4, -5)

    # Тест на треугольника, который не собирается (одна из его сторон слишком длинная)
    def test_broken(self):
        with self.assertRaises(IncorrectTriangleSides, msg='Ошибка не произошла'):
            triangle = Triangle(5, 5, 30)

            
if __name__ == '__main__':
    unittest.main()