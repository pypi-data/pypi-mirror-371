class Complex:
    '''Class to create a complex number'''
    def __init__(self, real: int, img: int):
        self.real = real
        self.img = img

    def __add__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real + other.real, self.img + other.img)
        return NotImplemented

    def __repr__(self):
        return f"Complex({self.real},{self.img})"
    
def sum(val1: Complex, val2: Complex):
    print(val1 + val2)

    