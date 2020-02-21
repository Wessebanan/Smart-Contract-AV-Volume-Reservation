import vehicle
from graphics import *

path = [Point(0,1), Point(1,1), Point(1,2)]
car = vehicle.Vehicle(110, 190, 100, 100, "blue")

bl = Point(car.pos_x - car.circle.getRadius(), car.pos_y - car.circle.getRadius())
br = Point(car.pos_x + car.circle.getRadius(), car.pos_y - car.circle.getRadius())
tl = Point(car.pos_x - car.circle.getRadius(), car.pos_y + car.circle.getRadius())
tr = Point(car.pos_x + car.circle.getRadius(), car.pos_y + car.circle.getRadius())

car.set_path(path)

print(car.path)

print(car.cell_in_pathP(car.get_cellP(bl)))
print(car.cell_in_pathP(car.get_cellP(br)))
print(car.cell_in_pathP(car.get_cellP(tl)))
print(car.cell_in_pathP(car.get_cellP(tr)))