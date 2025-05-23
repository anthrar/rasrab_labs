class IncorrectTriangleSides(Exception):
    pass

class Triangle():
    def __init__(self, a, b, c):
        try:    
            a = float(a)
            b = float(b)
            c = float(c)
        except:
            raise IncorrectTriangleSides
        if a+b<c or a+c<b or b+c<a:
            raise IncorrectTriangleSides
        if a<0 or b<0 or c<0:
            raise IncorrectTriangleSides
        self.a = a
        self.b = b
        self.c = c
    def triangle_type(self):
        if self.a==self.b==self.c:
            return 'equilateral'
        elif self.a==self.b or self.b==self.c or self.a==self.c:
            return 'isosceles'
        else:
            return 'nonequilateral'
    def perimeter(self):
        perm = self.a+self.b+self.c
        return perm

