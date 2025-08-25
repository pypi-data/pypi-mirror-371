<p align="left">
    <img src="https://user-images.githubusercontent.com/70604831/174466253-c4310d66-c687-4864-9893-8f0f70dd4084.png" width="800">
</p>

## Sagebox - A High-Performance, Procedural GUI Designed for Rapid, Creative Development (and Fun)

### Write plain linear, procedural code with no boilerplate.

Sagebox (aka Pybox) is a GUI architecture and toolset for Python that lets you add windows, GUI controls, and graphical output using simple linear, procedural code, without any boilerplate or the overhead of an event-driven framework.

Sagebox was created to bring back the simplicity of creating fun-with-graphics programs, while providing the power and scalability to build full-scale applications with advanced GUI controls.


[Sagebox Github Project](https://github.com/Sagebox/pybox) — Click to see the Github Page where there are many examples and the future roadmap. 

[YouTube Examples](https://www.youtube.com/@projectsagebox) — These examples are for the Rust version, but most work in Python already. [Sagebox Github page](https://github.com/Sagebox/pybox)

### Features
- Procedural, linear programming style
- No macros or boilerplate
- Console-mode support with add-on GUI-Control integration
- Compatible with other GUI libraries
- Accepts all Python native types for all functions
- Designed to stay out of the way of your existing Python code

## Installation

You can install the package directly with pip:

```bash
pip install sagebox
```

## importing Sagebox

```
import sagebox
```

## Dependencies

```
numpy (any version)
```



## Sample "Hello World" Full-Program Example

This program creates a Hello World program using a graphic window.  Creating a graphic window is not required to use Sagebox, and is just one of many features.

You can also create controls (e.g. sliders, buttons, checkboxes) with one line of code, either in a console-only program or with more graphics features such as the graphics window created in the example.

```
import sagebox

win = sagebox.new_window();                      # Create a default graphic window (not required)
win.write("Hello World",font=100,center=True)    # Write "Hello World" in large font, centered in window
sagebox.exit_button()                            # bring up a button in small window to press, letting the
                                                 # user know the program has ended.
```

See the github page for examples with graphics and easy-to-use controls — [Sagebox Github page](https://github.com/Sagebox/pybox)



