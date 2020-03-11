import pyglet, ratcave as rc
from pyglet.window import key

window = pyglet.window.Window()
keys = key.KeyStateHandler()
window.push_handlers(keys)

def update(dt):
	star.rotation.y += 15 * dt
pyglet.clock.schedule(update)

def stages(dt):
	if keys[key.UP]:
		star.scale.x += dt
		star.scale.z += dt
		star.scale.y += dt
	if keys[key.DOWN]:
		star.scale.x -= dt
		star.scale.z -= dt
		star.scale.y -= dt
pyglet.clock.schedule(stages)

default = rc.WavefrontReader(rc.resources.obj_primitives)

star = default.get_mesh("Sphere")
star.position.xyz = 0, 0, -4

scene = rc.Scene(meshes=[star], bgColor=(0, 158/255, 158/255))



@window.event
def on_draw():
	with rc.default_shader, rc.default_states:
		scene.draw()

pyglet.app.run()