'''
Data sources:
https://nssdc.gsfc.nasa.gov/planetary/factsheet/

!add:
use API to place planets according to specific epoch

add:
orbital eccentricity
orbital inclination
asteroid field generation

buttons:

	space: speeeeeed
	wasd: control camera

	up: enlarge sun
	dn: shrink sun
	lf: stop growth

	f:  set sun to 1
	r:  delete closest planets

'''

import pyglet, ratcave as rc, math, os
from pyglet.window import key

# global factors
speedFactor = 1
distanceFactor = 5
massFactor = .5

# animation vars
secs = 0  # seconds since program start
class AnimStates:
	state = None

	GROWING = 1
	SHRINKING = 2
	PLASMA = 3


# pyglet inits
window = pyglet.window.Window(width=1280, height=960, screen=0)
keys = key.KeyStateHandler()
window.push_handlers(keys)

# ratcave inits
default = rc.WavefrontReader(rc.resources.obj_primitives)
scene = rc.Scene(
	meshes=[],
	bgColor=(45 / 255, 45 / 255, 45 / 255),
	light=rc.Light(position=(0, 10_000, 0)),
	camera=rc.Camera(position=(0, 7, 7), rotation=(-45, 0, 0)))


class Planet:
	def __init__(self, diameter, pos=(0, 0, 0), day=24, period=None, name="", children=None, schedule=False):
		"""
		:param diameter:
			radius of planet (0-1, not to scale)
		:param pos:
			distance from the sun in 3 axis (AU)
		:param period:
			orbital period (days to encircle the parent-celestial-object), 365.2 in earth's case
		:param day:
			hours in this object's day
		"""

		self.diameter = diameter
		self.position = pos  # this is accurate in IRL AU units (scaled down), however it is rendered at 3x the scale
		self.period = period
		self.day = day
		self.name = name
		self.children = children
		# the default mesh diameter is 2, hence the halving in diameter below

		self.mesh = default.get_mesh("Sphere",
									position=[i * distanceFactor for i in self.position],
									scale=0.5 * self.diameter)

		scene.meshes.append(self.mesh)
		if schedule:
			pyglet.clock.schedule(self.update)

	def update(self, dt, planet=None):
		self.mesh.rotation.y += dt * speedFactor * (24 / self.day * 360)
		if planet:
			self.orbit(dt, planet)
		if self.children:
			for child in self.children:
				child.update(dt, planet=self)

	def orbit(self, dt, planet, degrees=None):
		x, y, z = self.position
		ox, _, oz = planet.position
		# earth will take 365.2 secs to completely revolve at default speed
		if not degrees:
			degrees = dt * speedFactor / self.period * 360
		radians = math.radians(degrees)

		nx = (x - ox) * math.cos(radians) - ((z - oz) * math.sin(radians)) + ox
		nz = (z - oz) * math.cos(radians) + ((x - ox) * math.sin(radians)) + oz

		self.position = nx, y, nz
		self.mesh.position.xyz = [i * distanceFactor for i in self.position]


def update(dt):
	global speedFactor, secs
	secs += dt

	# reset controls
	if keys[key.F]:
		AnimStates.state = None
		sun.mesh.scale.xyz = 1, 1, 1
	if keys[key.R]:
		for child in sun.children[:3]:
			child.position = 1000, 1000, 1000


	# state controls
	AnimStates.state = \
		AnimStates.GROWING if keys[key.UP] else \
		AnimStates.SHRINKING if keys[key.DOWN] else \
		AnimStates.PLASMA if keys[key.RIGHT] else \
		None if keys[key.LEFT] else AnimStates.state

	# perform actions based on current animation state
	if AnimStates.state == AnimStates.GROWING:
		sun.mesh.scale.xyz = [i + (dt/(massFactor*distanceFactor)) for i in sun.mesh.scale.xyz]

	if AnimStates.state == AnimStates.SHRINKING:
		sun.mesh.scale.xyz = [i - (dt/(massFactor*distanceFactor)) for i in sun.mesh.scale.xyz]

	# camera control
	if keys[key.D]:
		scene.camera.position.x += dt * 5
	if keys[key.A]:
		scene.camera.position.x -= dt * 5
	if keys[key.W]:
		scene.camera.position.z -= dt * 5
	if keys[key.S]:
		scene.camera.position.z += dt * 5

	# speed control
	if keys[key.SPACE]:
		speedFactor = 32
	else:
		speedFactor = 1


pyglet.clock.schedule(update)
planetDiameter = lambda d: d/4879*.25*massFactor  # mercury dia/4 is fixed in relation to other planets

sun = Planet(1,
	name="Sun",
	day=27,
	schedule=True,
	children=[
		Planet(planetDiameter(4879),
			name="Mercury",
			pos=(.387, 0, 0),
			day=4222.6,
			period=88),
		Planet(planetDiameter(12_104),
			name="Venus",
			pos=(.723, 0, 0),
			day=2802,
			period=224.7),
		Planet(planetDiameter(12_756),
			name="Earth",
			pos=(1, 0, 0),
			day=24,
			period=365.2,
			children=[
				Planet(planetDiameter(3475),
					name="Moon",
					pos=(1.257, 0, 0), # 1.00257
					day=708.7,
					period=27.3),
		]),
		Planet(planetDiameter(6792),
			name="Mars",
			pos=(1.52, 0, 0),
			day=24.7,
			period=687),
		Planet(planetDiameter(142_984),
			name="Jupiter",
			pos=(5.2, 0, 0),
			day=9.9,
			period=4331)
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
