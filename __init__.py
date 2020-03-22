'''
Data sources:
https://nssdc.gsfc.nasa.gov/planetary/factsheet/

'''

import pyglet, ratcave as rc, math
from pyglet.window import key

# pyglet inits
window = pyglet.window.Window(width=1280, height=960, screen=0)
keys = key.KeyStateHandler()
window.push_handlers(keys)

# ratcave inits
default = rc.WavefrontReader(rc.resources.obj_primitives)
# star = default.get_mesh("Sphere", position=(0, 0, 0))

scene = rc.Scene(meshes=[], bgColor=(45 / 255, 45 / 255, 45 / 255))
scene.light.position.y = 10_000

scene.camera.rotation.x = -45
scene.camera.position.xyz = 0, 7, 7


class Planet:
	def __init__(self, diameter, pos=(0, 0, 0), rotationSpeed=0, period=None, name="", children=None):
		"""
		:param diameter:
			radius of planet (0-1, not to scale)
		:param pos:
			distance from the sun in 3 axis (AU)
		:param period:
			orbital period (days to encircle the parent-celestial-object), 365.2 in earth's case
		:param rotationSpeed:
			the amount of earth days needed to rotate the planet 360 degrees
		"""

		self.diameter = diameter
		self.position = pos  # this is accurate in IRL AU units, however it is rendered at 3x the scale
		self.period = period
		self.rotationSpeed = rotationSpeed
		self.name = name
		self.children = children
		# the default mesh diameter is 2, hence the halving in diameter below
		self.mesh = default.get_mesh("Sphere",
									position=[i * 3 for i in self.position],
									scale=0.5 * self.diameter)
		scene.meshes.append(self.mesh)
		pyglet.clock.schedule(self.update)

	def update(self, dt, planet=None):
		self.mesh.rotation.y += self.rotationSpeed * dt
		if planet:
			self.orbit(dt, planet)
		if self.children:
			for child in self.children:
				child.update(dt, planet=self)

	def orbit(self, dt, planet, factor=8):
		x, y, z = self.position
		ox, _, oz = planet.position

		degrees = dt * factor / self.period * 360
		radians = math.radians(degrees)

		nx = (x - ox) * math.cos(radians) - ((z - oz) * math.sin(radians)) + ox
		nz = (z - oz) * math.cos(radians) + ((x - ox) * math.sin(radians)) + oz

		self.position = nx, y, nz
		self.mesh.position.xyz = [i * 3 for i in self.position]


def update(dt):
	if keys[key.D]:
		scene.camera.position.x += dt * 5
	if keys[key.A]:
		scene.camera.position.x -= dt * 5
	if keys[key.W]:
		scene.camera.position.z -= dt * 5
	if keys[key.S]:
		scene.camera.position.z += dt * 5


pyglet.clock.schedule(update)

sun = Planet(1,
	name="Sun",
	children=[
		Planet(.25,
			name="Mercury",
			pos=(.387, 0, 0),
			period=88),
		Planet(.75,
			name="Venus",
			pos=(.723, 0, 0),
			period=224.7),
		Planet(.75,
			name="Earth",
			pos=(1, 0, 0),
			period=365.2,
			children=[
				Planet(.1,
					name="Moon",
					pos=(1.384, 0, 0),
					period=27.3)
		]),
		Planet(.5,
			name="Mars",
			pos=(1.52, 0, 0),
			period=687)
])


@window.event
def on_mouse_scroll(x, y, sx, sy):
	scene.camera.position.y += sy * -.5
	scene.camera.position.z += sy * -.5


@window.event
def on_draw():
	with rc.default_shader, rc.default_states:
		scene.draw()


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	print(x, y, dx, dy, buttons, modifiers)


pyglet.app.run()
