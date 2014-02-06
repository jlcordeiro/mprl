from objects import ObjectController
from messages import *
import views.objects
import models.weapons


class Weapon(ObjectController):
    def __init__(self, x, y):
        self._model = None
        self._views = None
        raise NotImplementedError("not_implemented")

    @property
    def min_damage(self):
        return self._model.min_damage

    @property
    def max_damage(self):
        return self._model.max_damage


class Stick(Weapon):
    def __init__(self, x, y):
        self._model = models.weapons.Stick(x, y)
        self._view = views.objects.Weapon()


class Crowbar(Weapon):
    def __init__(self, x, y):
        self._model = models.weapons.Crowbar(x, y)
        self._view = views.objects.Weapon()


def WeaponFactory(x, y):
    dice = libtcod.random_get_int(0, 0, 100)
    if dice < 50:
        return Stick(x, y)
    else:
        return Crowbar(x, y)
