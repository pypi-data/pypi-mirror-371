from math import sqrt, ceil, floor
from typing import Union, Tuple


# 2D
class Vector:
    def __init__(self, x, y):
        if isinstance(x, complex) and isinstance(y, complex):
            raise FloatingPointError('复数……向量?!?!?!')
        elif not (isinstance(x, (float, int)) and isinstance(x, (float, int))):
            raise FloatingPointError('填个数字不行吗?!?!?!')
        self.x = x
        self.y = y

    def __add__(self, other: "Vector") -> "Vector":
        if not isinstance(other, Vector):
            raise FloatingPointError('填向量！！！！！！')
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        if not isinstance(other, Vector):
            raise FloatingPointError('填向量！！！！！！')
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Union[float, int]) -> "Vector":
        if not isinstance(scalar, (float, int)):
            raise FloatingPointError('填向量！！！！！！')
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: Union[float, int]) -> "Vector":
        if not isinstance(scalar, (float, int)):
            raise FloatingPointError('填数！！！！！！')
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Union[float, int]) -> "Vector":
        if not isinstance(scalar, (float, int)):
            raise FloatingPointError('填数！！！！！！')
        if scalar == 0:
            raise FloatingPointError('你的数学老师没教过你除数不能为0吗? Tell me!!!!! Look at my eyes!!!!!!')
        return Vector(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar: Union[float, int]) -> "Vector":
        if not isinstance(scalar, (float, int)):
            raise FloatingPointError('填数！！！！！！')
        if scalar == 0:
            raise FloatingPointError('你的数学老师没教过你除数不能为0吗? Tell me!!!!! Look at my eyes!!!!!!')
        return Vector(self.x // scalar, self.y // scalar)

    def __mod__(self, scalar: Union[float, int]) -> "Vector":
        if not isinstance(scalar, (float, int)):
            raise FloatingPointError('填数！！！！！！')
        if scalar == 0:
            raise FloatingPointError('你的数学老师没教过你除数不能为0吗? Tell me!!!!! Look at my eyes!!!!!!')
        return Vector(self.x % scalar, self.y % scalar)

    def mode(self) -> Union[float, int]:
        return sqrt(self.x ** 2 + self.y ** 2)

    def __pow__(self, scalar: Union[float, int]) -> "Vector":
        if not isinstance(scalar, (float, int)):
            raise FloatingPointError('填数！！！！！！！')
        return Vector(self.x ** scalar, self.y ** scalar)

    def __str__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Vector2D(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector):
            return self.mode() == other.mode()
        else:
            return self.mode() == other

    def __ne__(self, other: object) -> bool:
        return self.mode() != other.mode()

    def __lt__(self, other: object) -> bool:
        return self.mode < other.mode()

    def __le__(self, other: object) -> bool:
        return self.mode <= other.mode()

    def __gt__(self, other: object) -> bool:
        return self.mode > other.mode()

    def __ge__(self, other: object) -> bool:
        return self.mode >= other.mode()

    def __len__(self) -> int:
        return 2

    def __abs__(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2)

    def __bool__(self) -> bool:
        return self.x != 0 and self.y != 0

    def ceil(self) -> "Vector":
        return Vector(ceil(self.x), ceil(self.y))

    def floor(self) -> "Vector":
        return Vector(floor(self.x), floor(self.y))

    def normalize(self) -> "Vector":
        mod = self.mode()
        if mod == 0:
            raise FloatingPointError("零向量无法归一化")
        return self / mod

    def __iter__(self):
        yield self.x
        yield self.y


base_vector_2D_i = Vector(1, 0)
base_vector_2D_j = Vector(0, 1)


def dot_2D(self: Vector, other: Vector) -> Union[float, int]:
    if not (isinstance(self, Vector) and isinstance(other, Vector)):
        raise FloatingPointError('填向量！！！！！！')
    return self.x * other.x + self.y * other.y


def cross_2D(self: Vector, other: Vector) -> Union[float, int]:
    if not (isinstance(self, Vector) and isinstance(other, Vector)):
        raise FloatingPointError('填向量！！！！！！')
    return self.x * other.y - self.y * other.x


def vector_2D(self: Union[float, int], other: Union[float, int]):
    if not (isinstance(self, (float, int)) and isinstance(other, (float, int))):
        raise FloatingPointError('填向量！！！！！！')
    return Vector(self, other)


class Matrix:
    def __init__(self, data=None):
        if data is None:
            data = (Vector(1, 0), Vector(0, 1))
        else:
            if not all(isinstance(v, Vector) for v in data) or len(data) != 2:
                raise FloatingPointError('data 必须是由两个 Vector 实例组成的可迭代对象!')
        self.i = data[0]
        self.j = data[1]

    def det(self):
        return self.i.x * self.j.y - self.i.y * self.j.x

    def __mul__(self, other: "Matrix") -> "Matrix":
        if not isinstance(other, Matrix):
            raise FloatingPointError("填矩阵!!!!!!")
        row1 = Vector(self.i.x * other.i.x + self.i.y * other.j.x, self.i.x * other.i.y + self.i.y * other.j.y)
        row2 = Vector(self.j.x * other.i.x + self.j.y * other.j.x, self.j.x * other.i.y + self.j.y * other.j.y)
        return Matrix(row1, row2)

    def __str__(self) -> str:
        return f"Matrix({self.i}, {self.j})"

    def __repr__(self) -> str:
        return f"Matrix2D(i = {self.i!r}, j = {self.j!r})"

    def __eq__(self, other: "Matrix") -> bool:
        return self.det() == other.det()

    def __ne__(self, other: "Matrix") -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: "Matrix") -> bool:
        return self.det() < other.det()

    def __le__(self, other: "Matrix") -> bool:
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other: "Matrix") -> bool:
        return not self.__le__(other)

    def __ge__(self, other: "Matrix") -> bool:
        return not self.__lt__(other)

    def transpose(self) -> "Matrix":
        return Matrix([Vector(self.i.x, self.j.x), Vector(self.i.y, self.j.y)])

    def __iter__(self):
        yield self.i
        yield self.j


base_Matrix_2D = Matrix((Vector(1, 0), Vector(0, 1)))


def change_vector_2D(vec: Vector, mat: Matrix) -> Vector:
    return Vector(vec.x * mat.i.x + vec.y * mat.j.x, vec.x * mat.i.y + vec.y * mat.j.y)


def matrix_2D(rows: Union[Tuple[Vector, Vector], Tuple[
    Union[float, int], Union[float, int], Union[float, int], Union[float, int]]]) -> Matrix:
    if isinstance(rows[0], Vector) and isinstance(rows[1], Vector):
        return Matrix(list(rows))
    elif all(isinstance(x, (int, float)) for x in rows) and len(rows) == 4:
        return Matrix([Vector(rows[0], rows[1]), Vector(rows[2], rows[3])])
    else:
        raise FloatingPointError("输入必须是两个Vector或四个数字的元组")


# 3D
class Vectors:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __add__(self, other: "Vectors") -> "Vectors":
        return Vectors(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vectors") -> "Vectors":
        return Vectors(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: Union[int, float]) -> "Vectors":
        return Vectors(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: Union[int, float]) -> "Vectors":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Union[int, float]) -> "Vectors":
        return Vectors(self.x / scalar, self.y / scalar, self.z / scalar)

    def __floordiv__(self, scalar: Union[int, float]) -> "Vectors":
        return Vectors(self.x // scalar, self.y // scalar, self.z // scalar)

    def __mod__(self, scalar: Union[int, float]) -> "Vectors":
        return Vectors(self.x % scalar, self.y % scalar, self.z % scalar)

    def mode(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def __pow__(self, scalar: Union[int, float]) -> "Vectors":
        return Vectors(self.x ** scalar, self.y ** scalar, self.z ** scalar)

    def __str__(self) -> str:
        return f"Vectors({self.x}, {self.y}, {self.z})"

    def __repr__(self) -> str:
        return f"Vector3D(x = {self.x}, y = {self.y}, z = {self.z})"

    def __eq__(self, other: object) -> bool:
        return self.mode() == other.mode()

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        return self.mode() < other.mode()

    def __le__(self, other: object) -> bool:
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other: object) -> bool:
        return not self.__le__(other)

    def __ge__(self, other: object) -> bool:
        return not self.__lt__(other)

    def __len__(self) -> int:
        return 3

    def __abs__(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def __bool__(self) -> bool:
        if self.mode() == 0:
            return False
        return True

    def ceil(self) -> "Vectors":
        return Vectors(ceil(self.x), ceil(self.y), ceil(self.z))

    def floor(self) -> "Vectors":
        return Vectors(floor(self.x), floor(self.y), floor(self.z))

    def normalize(self) -> "Vectors":
        mod = self.mode()
        if mod == 0:
            raise FloatingPointError("零向量无法归一化！")
        return self / mod

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z


base_vector_3D_i = Vectors(1, 0, 0)
base_vector_3D_j = Vectors(0, 1, 0)
base_vector_3D_k = Vectors(0, 0, 1)


def dot_3D(self: Vectors, other: Vectors) -> float:
    return self.x * other.x + self.y * other.y + self.z * other.z


def cross_3D(self: Vectors, other: Vectors) -> Vectors:
    row1 = self.y * other.z - self.z * other.y
    row2 = self.z * other.x - self.x * other.z
    row3 = self.x * other.y - self.y * other.x
    return Vectors(row1, row2, row3)


def vector_3D(a, b, c):
    return Vectors(a, b, c)


class Matrixes:
    def __init__(self, data=None):
        if data is None:
            data = (Vectors(1, 0, 0), Vectors(0, 1, 0), Vectors(0, 0, 1))
        else:
            if not all(isinstance(v, Vectors) for v in data) or len(data) != 3:
                raise FloatingPointError("data 必须是由三个 Vectors 实例组成的可迭代对象!")
        self.i = data[0]
        self.j = data[1]
        self.k = data[2]

    def __mul__(self, other: "Matrixes") -> "Matrixes":
        row1 = Vectors(
            dot_3D(self.i, Vectors(other.i.x, other.j.x, other.k.x)),
            dot_3D(self.i, Vectors(other.i.y, other.j.y, other.k.y)),
            dot_3D(self.i, Vectors(other.i.z, other.j.z, other.k.z))
        )
        row2 = Vectors(
            dot_3D(self.j, Vectors(other.i.x, other.j.x, other.k.x)),
            dot_3D(self.j, Vectors(other.i.y, other.j.y, other.k.y)),
            dot_3D(self.j, Vectors(other.i.z, other.j.z, other.k.z))
        )
        row3 = Vectors(
            dot_3D(self.k, Vectors(other.i.x, other.j.x, other.k.x)),
            dot_3D(self.k, Vectors(other.i.y, other.j.y, other.k.y)),
            dot_3D(self.k, Vectors(other.i.z, other.j.z, other.k.z))
        )
        return Matrixes(row1, row2, row3)

    def det(self) -> float:
        ip = self.i.x * self.j.y * self.k.z + self.i.z * self.j.x * self.k.y + self.i.y * self.j.z * self.k.x
        pt = self.i.z * self.j.y * self.k.x + self.i.x * self.j.z * self.k.y + self.i.y * self.j.x * self.k.z
        return ip - pt

    def __str__(self) -> str:
        return f"Matrixes({self.i}, {self.j}, {self.k})"

    def __repr__(self) -> str:
        return f"Matrix3D(i = {self.i!r}, j = {self.j!r}, k = {self.k!r})"

    def __eq__(self, other: object) -> bool:
        return self.det() == other.det()

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: "Matrix") -> bool:
        return self.det() < other.det()

    def __le__(self, other: "Matrix") -> bool:
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other: "Matrix") -> bool:
        return not self.__le__(other)

    def __ge__(self, other: "Matrix") -> bool:
        return not self.__lt__(other)

    def transpose(self) -> "Matrixes":
        row1 = Vectors(self.i.x, self.j.x, self.k.x)
        row2 = Vectors(self.i.y, self.j.y, self.k.y)
        row3 = Vectors(self.i.z, self.j.z, self.k.z)
        return Matrixes(row1, row2, row3)

    def __iter__(self):
        yield self.i
        yield self.j
        yield self.k


base_Matrix_3D = Matrixes((base_vector_3D_i, base_vector_3D_j, base_vector_3D_k))


def change_vector_3D(vec: Vectors, mat: Matrixes) -> Vectors:
    return Vectors(vec.x * mat.i.x + vec.y * mat.j.x + vec.z * mat.k.x, vec.x * mat.i.y + vec.y * mat.j.y + vec.z * mat.k.y, vec.x * mat.i.z + vec.y * mat.j.z + vec.z * mat.k.z)


def matrix_3D(rows: Union[Tuple[Vectors, Vectors, Vectors], Tuple[
    Union[float, int], Union[float, int], Union[float, int], Union[float, int], Union[float, int],
    Union[float, int], Union[float, int], Union[float, int], Union[float, int]]]) -> Matrix:
    if isinstance(rows[0], Vectors) and isinstance(rows[1], Vectors) and isinstance(rows[2], Vectors):
        return Matrix(list(rows))
    elif all(isinstance(x, (int, float)) for x in rows) and len(rows) == 4:
        return Matrix([Vectors(rows[0], rows[1], rows[2]), Vectors(rows[3], rows[4], rows[5]), Vectors(rows[6], rows[7], rows[8])])
    else:
        raise FloatingPointError("输入必须是三个Vector或九个数字的元组")