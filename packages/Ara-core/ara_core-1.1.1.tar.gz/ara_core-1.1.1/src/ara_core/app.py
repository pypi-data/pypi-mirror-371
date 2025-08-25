import inspect
import glfw
from collections import defaultdict, deque
from .exceptions import *
from ara_log import Log


class App:
    """Ara application core with dependency-based callback scheduling."""

    NAME = "core"

    _KEYS_CODES = {
        # Letters
        "a": glfw.KEY_A, "b": glfw.KEY_B, "c": glfw.KEY_C,
        "d": glfw.KEY_D, "e": glfw.KEY_E, "f": glfw.KEY_F,
        "g": glfw.KEY_G, "h": glfw.KEY_H, "i": glfw.KEY_I,
        "j": glfw.KEY_J, "k": glfw.KEY_K, "l": glfw.KEY_L,
        "m": glfw.KEY_M, "n": glfw.KEY_N, "o": glfw.KEY_O,
        "p": glfw.KEY_P, "q": glfw.KEY_Q, "r": glfw.KEY_R,
        "s": glfw.KEY_S, "t": glfw.KEY_T, "u": glfw.KEY_U,
        "v": glfw.KEY_V, "w": glfw.KEY_W, "x": glfw.KEY_X,
        "y": glfw.KEY_Y, "z": glfw.KEY_Z,
        
        # Digits
        "0": glfw.KEY_0, "1": glfw.KEY_1, "2": glfw.KEY_2,
        "3": glfw.KEY_3, "4": glfw.KEY_4, "5": glfw.KEY_5,
        "6": glfw.KEY_6, "7": glfw.KEY_7, "8": glfw.KEY_8,
        "9": glfw.KEY_9,
        
        # Arrow keys
        "right": glfw.KEY_RIGHT,
        "left":  glfw.KEY_LEFT,
        "down":  glfw.KEY_DOWN,
        "up":    glfw.KEY_UP,
        
        # Functional keys
        "f1": glfw.KEY_F1, "f2":  glfw.KEY_F2,  "f3":  glfw.KEY_F3,  "f4":  glfw.KEY_F4,
        "f5": glfw.KEY_F5, "f6":  glfw.KEY_F6,  "f7":  glfw.KEY_F7,  "f8":  glfw.KEY_F8,
        "f9": glfw.KEY_F9, "f10": glfw.KEY_F10, "f11": glfw.KEY_F11, "f12": glfw.KEY_F12,
        
        # Special characters
        "`": glfw.KEY_GRAVE_ACCENT, "-": glfw.KEY_MINUS,         "=":  glfw.KEY_EQUAL,
        "[": glfw.KEY_LEFT_BRACKET, "]": glfw.KEY_RIGHT_BRACKET, "\\": glfw.KEY_BACKSLASH,
        ";": glfw.KEY_SEMICOLON,    "'": glfw.KEY_APOSTROPHE,    ",":  glfw.KEY_COMMA,
        ".": glfw.KEY_PERIOD,       "/": glfw.KEY_SLASH,
        
        # Special keys
        "space":     glfw.KEY_SPACE,
        "escape":    glfw.KEY_ESCAPE,
        "enter":     glfw.KEY_ENTER,
        "tab":       glfw.KEY_TAB,
        "caps_lock": glfw.KEY_CAPS_LOCK,
        "backspace": glfw.KEY_BACKSPACE,
        "delete":    glfw.KEY_DELETE,
        
        "insert":       glfw.KEY_INSERT,
        "page_up":      glfw.KEY_PAGE_UP,
        "page_down":    glfw.KEY_PAGE_DOWN,
        "home":         glfw.KEY_HOME,
        "end":          glfw.KEY_END,
        "scroll_lock":  glfw.KEY_SCROLL_LOCK,
        "num_lock":     glfw.KEY_NUM_LOCK,
        "print_screen": glfw.KEY_PRINT_SCREEN,
        "pause":        glfw.KEY_PAUSE,
        
        # Modifiers
        "left_shift":    glfw.KEY_LEFT_SHIFT,
        "left_control":  glfw.KEY_LEFT_CONTROL,
        "left_alt":      glfw.KEY_LEFT_ALT,
        "left_super":    glfw.KEY_LEFT_SUPER,
        "right_shift":   glfw.KEY_RIGHT_SHIFT,
        "right_control": glfw.KEY_RIGHT_CONTROL,
        "right_alt":     glfw.KEY_RIGHT_ALT,
        "right_super":   glfw.KEY_RIGHT_SUPER,
        "menu":          glfw.KEY_MENU,
        
        "shift":   (glfw.KEY_LEFT_SHIFT,   glfw.KEY_RIGHT_SHIFT  ),
        "control": (glfw.KEY_LEFT_CONTROL, glfw.KEY_RIGHT_CONTROL),
        "alt":     (glfw.KEY_LEFT_ALT,     glfw.KEY_RIGHT_ALT    ),
        "super":   (glfw.KEY_LEFT_SUPER,   glfw.KEY_RIGHT_SUPER  )
    }

    _MOUSE_CODES = {
        "left":   glfw.MOUSE_BUTTON_LEFT,
        "right":  glfw.MOUSE_BUTTON_RIGHT,
        "middle": glfw.MOUSE_BUTTON_MIDDLE
    }

    def __init__(self, title="New app", width=800, height=600, log_level="warning"):
        """Initialize the application.
        
        Args:
            title (str): Window title.
            width (int): Window width.
            height (int): Window height.
            log_level (str): Logging level, default is "warning".
        """
        
        self.log = Log("Ara.Core", log_level)
        self.log.info("Initializing Ara.Core")

        if not glfw.init():
            self.log.error("Failed to initialize GLFW")
            raise AppError("Failed to initialize GLFW")

        self.title, self.width, self.height = title, width, height
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            self.log.error("Failed to create GLFW window")
            raise AppError("Failed to create GLFW window")

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        # --- modules and callbacks ---
        self.modules = {}        # name -> instance
        self.callbacks = {}      # full_name -> function
        self.deps = defaultdict(set)
        self.DEPENDENCIES = {}      # for core’s own callbacks

        # --- timing ---
        self._start_time = glfw.get_time()
        self._last_frame_time = self._start_time
        self._delta_time = 0.0
        self._framerate = []
        self._avg_framerate = 0.0
        self._fps = 0.0

        # --- Input callbacks ---
        self._keys, self._keys_prev = {}, {}
        self._mouse_buttons, self._mouse_buttons_prev = {}, {}
        self._mouse_pos, self._mouse_delta = (0, 0), (0, 0)
        self._mouse_scroll, self._mouse_locked = 0, False

        glfw.set_key_callback(self.window, self._key_callback)
        glfw.set_mouse_button_callback(self.window, self._mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self._cursor_pos_callback)
        glfw.set_scroll_callback(self.window, self._scroll_callback)

        self.log.info("Ara.Core initialized successfully!")


    # ============ Dependency Management ============
    def add_module(self, module, auto_init=True):
        """Register a module
        
        Args:
            module (Module): Module instance or class.
            auto_init (bool): Whether to initialize the module automatically.
        """
        
        if inspect.isclass(module):
            module = module(self)
            
        if auto_init:
            try:
                module.init()
            except Exception as e:
                self.log.error(f"Failed to initialize module {module.NAME}: {e}")
                raise ModuleInitError(f"Failed to initialize module {module.NAME}: {e}")
            
        name = module.NAME
        self.modules[name] = module

        for func_name, rules in module.DEPENDENCIES.items():
            if not hasattr(module, func_name):
                raise DependencyError(f"Module {name} has no function {func_name}, but it is listed in DEPENDENCIES")
            full_name = f"{name}.{func_name}"
            self.callbacks[full_name] = getattr(module, func_name)


    def add_callback(self, func_name, func, before=None, after=None):
        """Register a core-owned callback"""
        full_name = f"{self.NAME}.{func_name}"
        self.callbacks[full_name] = func
        self.DEPENDENCIES[func_name] = {"before": before or [], "after": after or []}


    def build_dependencies(self):
        """Build dependency graph after all modules and core callbacks are added"""
        # modules
        for modname, module in self.modules.items():
            for func_name, rules in module.DEPENDENCIES.items():
                full_name = f"{modname}.{func_name}"
                for dep in rules.get("after", []):
                    self._add_dependency(dep, full_name)
                for dep in rules.get("before", []):
                    self._add_dependency(full_name, dep)

        # core callbacks
        for func_name, rules in self.DEPENDENCIES.items():
            full_name = f"{self.NAME}.{func_name}"
            for dep in rules.get("after", []):
                self._add_dependency(dep, full_name)
            for dep in rules.get("before", []):
                self._add_dependency(full_name, dep)


    def _add_dependency(self, src, dst):
        """Add edge src -> dst, supporting module.*"""
        def expand(name):
            if ".*" in name:
                mod = name.split(".")[0]
                if mod not in self.modules and mod != self.NAME:
                    return []
                return [cb for cb in self.callbacks if cb.startswith(mod + ".")]
            else:
                return [name]

        for expanded_src in expand(src):
            for expanded_dst in expand(dst):
                src_mod = expanded_src.split(".")[0]
                dst_mod = expanded_dst.split(".")[0]

                if (src_mod not in self.modules and src_mod != self.NAME) or \
                   (dst_mod not in self.modules and dst_mod != self.NAME):
                    continue

                if expanded_src not in self.callbacks:
                    raise DependencyError(f"No function {expanded_src}")
                if expanded_dst not in self.callbacks:
                    raise DependencyError(f"No function {expanded_dst}")

                self.deps[expanded_src].add(expanded_dst)


    def topological_sort(self):
        """Kahn’s algorithm with cycle detection"""
        indeg = defaultdict(int)
        for u in self.callbacks:
            indeg[u] = 0
        for u in self.deps:
            for v in self.deps[u]:
                indeg[v] += 1

        q = deque([u for u in self.callbacks if indeg[u] == 0])
        order = []

        while q:
            u = q.popleft()
            order.append(u)
            for v in self.deps[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)

        if len(order) != len(self.callbacks):
            cycle = self._find_cycle()
            raise CycleError("Dependency cycle detected: " + " -> ".join(cycle))

        return order


    def _find_cycle(self):
        """DFS to find cycle"""
        visited = {}
        stack = []

        def dfs(u):
            visited[u] = "gray"
            stack.append(u)
            for v in self.deps[u]:
                if visited.get(v) == "gray":
                    return stack[stack.index(v):] + [v]
                if visited.get(v) is None:
                    cycle = dfs(v)
                    if cycle:
                        return cycle
            stack.pop()
            visited[u] = "black"
            return None

        for u in self.callbacks:
            if visited.get(u) is None:
                cycle = dfs(u)
                if cycle:
                    return cycle
        return []


    # ============ Input API ============
    def _update_input(self):
        """Update input states for the current frame."""
        self._keys_prev = self._keys.copy()
        self._mouse_buttons_prev = self._mouse_buttons.copy()
        self._mouse_delta, self._mouse_scroll = (0, 0), 0
        
        
    def _key_callback(self, window, key, scancode, action, mods):
        """GLFW key callback handler."""
        if action == glfw.PRESS:
            self._keys[key] = True
        elif action == glfw.RELEASE:
            self._keys[key] = False


    def _mouse_button_callback(self, window, button, action, mods):
        """GLFW mouse button callback handler."""
        if action == glfw.PRESS:
            self._mouse_buttons[button] = True
        elif action == glfw.RELEASE:
            self._mouse_buttons[button] = False


    def _cursor_pos_callback(self, window, xpos, ypos):
        """GLFW cursor position callback handler."""
        if self._mouse_locked:
            w, h = glfw.get_window_size(window)
            cx, cy = w // 2, h // 2
            self._mouse_delta = (xpos - cx, cy - ypos)
            glfw.set_cursor_pos(window, cx, cy)
        self._mouse_pos = (xpos, ypos)


    def _scroll_callback(self, window, xpos, ypos):
        """GLFW scroll callback handler."""
        self._mouse_scroll = ypos
        
    
    def key_pressed(self, key):
        """Check if a key is currently pressed.
        
        Args:
            key (str): Key name to check.
            
        Returns:
            bool: True if the key is pressed.
        """
        key_code = self._KEYS_CODES.get(key)
        
        if key_code is None:
            raise ValueError(f"Invalid key name: {key}")
        
        if type(key_code) == tuple:
            return any(self._keys.get(k) for k in key_code)
        else:
            return self._keys.get(key_code)


    def key_down(self, key):
        """Check if a key was just pressed this frame.
        
        Args:
            key (str): Key name to check.
            
        Returns:
            bool: True if the key was pressed this frame.
        """
        key_code = self._KEYS_CODES.get(key)

        if key_code is None:
            raise ValueError(f"Invalid key name: {key}")

        if type(key_code) == tuple:
            return any((self._keys.get(k) and not self._keys_prev.get(k)) for k in key_code)
        else:
            return self._keys.get(key_code) and not self._keys_prev.get(key_code)


    def key_up(self, key):
        """Check if a key was just released this frame.
        
        Args:
            key (str): Key name to check.
            
        Returns:
            bool: True if the key was released this frame.
        """
        key_code = self._KEYS_CODES.get(key)

        if key_code is None:
            raise ValueError(f"Invalid key name: {key}")

        if type(key_code) == tuple:
            return any((not self._keys.get(k) and self._keys_prev.get(k)) for k in key_code)
        else:
            return not self._keys.get(key_code) and self._keys_prev.get(key_code)


    def mouse_button_pressed(self, btn):
        """Check if a mouse button is currently pressed.
        
        Args:
            btn (str): Button name to check.
            
        Returns:
            bool: True if the button is pressed.
        """
        btn_code = self._MOUSE_CODES.get(btn)
        
        if btn_code is None:
            raise ValueError(f"Invalid mouse button: {btn}")
        
        return self._mouse_buttons.get(btn_code)


    def mouse_button_down(self, btn):
        """Check if a mouse button was just pressed this frame.
        
        Args:
            btn (str): Button name to check.
            
        Returns:
            bool: True if the button was pressed this frame.
        """
        btn_code = self._MOUSE_CODES.get(btn)
        
        if btn_code is None:
            raise ValueError(f"Invalid mouse button: {btn}")

        return self._mouse_buttons.get(btn_code) and not self._mouse_buttons_prev.get(btn_code)


    def mouse_button_up(self, btn):
        """Check if a mouse button was just released this frame.
        
        Args:
            btn (str): Button name to check.
            
        Returns:
            bool: True if the button was released this frame.
        """
        btn_code = self._MOUSE_CODES.get(btn)

        if btn_code is None:
            raise ValueError(f"Invalid mouse button: {btn}")

        return not self._mouse_buttons.get(btn_code) and self._mouse_buttons_prev.get(btn_code)


    def get_mouse_pos(self):
        """Get current mouse position.
        
        Returns:
            tuple: (x, y) mouse coordinates.
        """
        return self._mouse_pos


    def get_mouse_delta(self):
        """Get mouse movement delta (only when mouse is locked).
        
        Returns:
            tuple: (dx, dy) mouse movement since last frame.
        """
        return self._mouse_delta if self._mouse_locked else (0, 0)


    def get_mouse_scroll(self):
        """Get mouse scroll amount.
        
        Returns:
            float: Scroll amount since last frame.
        """
        return self._mouse_scroll


    def set_mouse_lock(self, lock):
        """Toggle mouse lock (cursor visibility and confinement).
        
        Args:
            lock (bool): Whether to lock the mouse.
        """
        self._mouse_locked = lock
        glfw.set_input_mode(self.window, glfw.CURSOR,
            glfw.CURSOR_DISABLED if self._mouse_locked else glfw.CURSOR_NORMAL)
        
    
    # ============ Utilities API ===========
    def close(self):
        """Close the application window."""
        glfw.set_window_should_close(self.window, True)
    
    
    # ============ Runtime API ============
    def time(self):
        """Get the current time in seconds since the start of the application."""
        return glfw.get_time() - self._start_time


    def dt(self):
        """Get the time delta since the last frame."""
        return self._delta_time


    def fps(self):
        """Get the average FPS."""
        return self._fps


    def _update_framerate(self):
        self._framerate.append(self._delta_time)
        
        if len(self._framerate) > 60:
            self._framerate.pop(0)
            
        self._avg_framerate = sum(self._framerate) / len(self._framerate)
        
        if abs(self._avg_framerate) > 1e-6:
            self._fps = 1 / self._avg_framerate
        else:
            self._fps = 9999.0


    # ============ Main Loop ============
    def run(self, render=None, update=None, terminate=None):
        """Run main loop with dependency-resolved callbacks
        
        Args:
            render (function, optional): Render callback. Defaults to None.
            update (function, optional): Update callback. Defaults to None.
            terminate (function, optional): Terminate callback. Defaults to None.
        """
        
        # Adding default callbacks
        if render is None:
            render = lambda: None
            
        if update is None:
            update = lambda: None
            
        self.add_callback("render", render, after="core.update")
        self.add_callback("update", update)
        
        # Building dependencies
        self.log.info("Building dependencies...")
        
        self.build_dependencies()
        order = self.topological_sort()
        
        # Main loop
        self.log.info("Main loop started!")
        
        try:
            while not glfw.window_should_close(self.window):
                # Runtime updating
                current_time = self.time()
                self._delta_time = max(current_time - self._last_frame_time, 0.0)
                self._last_frame_time = current_time
                
                self._update_framerate()
                
                # Events and input
                self._update_input()
                glfw.poll_events()

                # Callbacks
                for name in order:
                    callback = self.callbacks[name]
                    
                    try:
                        callback()
                            
                    except Exception as e:
                        self.log.error(f"Error in callback {name}: {e}")
                        raise CallbackError(f"Error in callback {name}: {e}")

                glfw.swap_buffers(self.window)

        finally:
            try:
                if terminate:
                    terminate()
                        
            except Exception as e:
                self.log.error(f"Terminate error: {e}")
                

            for module in self.modules.values():
                try:
                    if hasattr(module, "terminate"):
                        module.terminate()

                except Exception as e:
                    self.log.error(f"Module {type(module).__name__} terminate error: {e}")
            
            glfw.terminate()
            
            self.log.info("Main loop terminated!")