# Ara_core

Ara.Core is a lightweight Python framework for building interactive applications with GLFW.
It provides an easy way to manage windows, handle input, integrate modules, and run the main loop with logging and error handling out of the box.

---

Features

Window Management – Create and control an OpenGL context window.

Input Handling – High-level API for keyboard and mouse state:

pressed, down, and up queries for keys and mouse buttons

Cursor locking, movement delta, and scroll tracking

Module System – Plug in custom modules with lifecycle methods

Timing Utilities – Frame delta (dt), elapsed time, and FPS measurement.

Logging – Integrated logging system with configurable levels.

Callbacks – Flexible callback hooks in the main loop.


---

Quick Start
```
from ara_core import App

# Create application instance
core = App(title="My First App", width=1280, height=720, log_level="info")

def render(core):
    print("GUI rendering")

def update(core):
    print(f"Frame time: {core.dt()}")

def terminate(core):
    print("Cleanup done!")

# Run with custom callbacks
core.run(render, callback, terminate)
```
---

Input API
```py
core.key_pressed("w")      # True while 'W' is held
core.key_down("space")     # True only on the frame space was pressed
core.key_up("escape")      # True only on the frame escape was released

core.mouse_button_pressed("left")
pos = core.get_mouse_pos()
dx, dy = core.get_mouse_delta()
scroll = core.get_mouse_scroll()
```

---

Module System

Modules can be classes or instances.
They may implement any of the lifecycle methods:
```py
class ExampleModule:
    NAME = "module_example"

    DEPENDENCIES = {
        "update_callback": {
            "before": ["core.update"],
            "after": ["module_example.other_callback"]
        },

        "other_callback": {
            "before": [],
            "after": []
        }
    }

    def __init__(self, core):
        self.core = core

    def init(self):
        print("Module initialized")

    def update_callback(self):
        print("Module updated")

    def other_callback(self):
        print("Module other callback")

    def terminate(self):
        print("Module terminated")

core.add_module(ExampleModule)
```

---

Utilities

app.close() – close the window

app.time() – elapsed time since start

app.dt() – delta time of last frame

app.fps() – current frames per second


---

Requirements

Python 3.8+

GLFW

Ara_log

Install dependencies:

pip install glfw, pyopengl, ara_log


---

License

MIT License.
Feel free to use and modify for your projects.

