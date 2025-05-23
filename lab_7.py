import numbers
class IncorrectTriangleSides(Exception):
    pass


def get_triangle_type(a, b, c):
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
    if a==b==c:
        return 'equilateral'
    elif a==b or b==c or a==c:
        return 'isosceles'
    else:
        return 'nonequilateral'
    

    