---
title: Above the hood
layout: default
nav_order: 2
---

* Table of contents
{:toc}

# Installation

TopasIO resides on Pypi, so you can use `pip install topasio` and it will install the latest version. I suggest you use [uv](https://docs.astral.sh/uv/) instead and using:

```python
mkdir topasio_example
cd topasio_example
uv init
uv add topasio
```

You can then change the main file and run it using `uv run main.py`.


# Quick-start

This library reads a lot like Topas code, except with `.` wherever there was a `/`. For this reason, slashes aren't supported inside names, and neither are dots. Also, contrary to Topas, this library does care about the first two letters of a paramter: `Ge.World` and `Gr.World` are different things in TopasIO, while in Topas you can define a geometry component like the latter.

To start, import TopasIO:
```python
import topasio
from topasio import Ge, TsBox
```

You don't have to define a `World`: TopasIO has a built-in World that you can manipulate:

```python
Ge.World.Material = "G4_AIR"
```

Notice that python is not a typed language and the type of `Ge.World.Material` is inferred. TopasIO supports python's strings, floats, bools, integers. Lists of these types will be considered vectors (all elements in a list must have the same type). Topas' `dimensioned` type is implemented through the `quantities` package:

```python
import quantities as q
Ge.Phantom.HLX                           = 10 * q.cm  # Dimensioned Double
Ge.MagnetDipole.MagneticFieldDirectionX  = 1.0        # Unitless Double
Sc.DoseScorer.ZBins                      = 100        # Integer
Sc.DoseScorer.Active                     = True       # Boolean
Ge.Phantom.Material                      = "G4_WATER" # String
Ge.RMW_Track1.Angles         = [69.1, 92.2, 111.0, 126.0]  * q.deg  # Dimensioned Double Vector
Ma.Phantom_Plastic.Fractions = [0.05549, 0.75575, 0.18875]          # Unitless Double Vector
Gr.Color.yellow              = [225, 255, 0]                        # Integer Vector
Tf.ScoringOnOff.Values       = [True, False, True]                  # Boolean Vector
Ma.MyPlastic.Components      = ["Hydrogen", "Carbon", "Oxygen"]     # String Vector
```

To run a simulation, just use:

```python
topasio.run_simulation()
```

All parameters will be dumped to a folder named `autotopas`, a script called `autotopas/temp.sh` will be created and launched. TopasIO finds your Topas executable in your PATH or your .bashrc if you have defined it with an alias. It will be destroyed after use. The folder will also contain the outputs in a folder called `autotopas/outputs/topas_output_{i}` where `i` is an index that serves to guarantee that TopasIO doesn't overwrite previous outputs. For example, calling `topasio.run_simulation()` three times will result in folders:

```
autotopas/topas_output_0
autotopas/topas_output_1
autotopas/topas_output_2
```

And so on. This information is enough for you to start writing scripts that extend Topas, but stay here and let me explain a couple more things.

# Modifying TopasIO's defaults

If you want your output folder to be called something other than `autotopas`, if TopasIO isn't finding the Topas executable, etc. then this is the place for you. To change the TopasIO defaults, use:

```python
from topasio.config import cfg
cfg[{parameter}] = {value}
```

Here are the current TopasIO parameters:

```json
"output_dir": "autotopas"          # Directory to put outputs in, relative to cwd
"overwrite_scorer_outputs": False  # Whether to set all scorers to 'overwrite' if file exists
"output_format": "binary"          # Default output format for scorers
"topas_path": None                 # Path to the TOPAS executable, if None it will search in PATH and .bashrc
"suppress_topas_output": True,     # Whether to suppress TOPAS output in the console
"geometry:print_children": True,   # Whether to print children in geometry dumps
"write_parameter_summary": False,  # Also outputs an almost-json file that includes the parameters used for this sim
```

A couple of notes:
- TopasIO supports Parquet as output: if you set `cfg["output_format"] = "parquet"`, TopasIO will have Topas output in binary and then use its Scorer awareness to convert all files to parquet. The originals won't be overwritten. From my tests, this works better than `topas2numpy` (which is a python module for converting scorer outputs to pandas) because it uses polars (which is faster than pandas) and it supports scorers binned in energy (while said module doesn't). `topas2numpy` is still needed for importing phase space files into python.
- If not set, TopasIO will set `"topas_path"` by searching (in this order): 
    - The default OpenTopas installation directory (`/home/{os.getenv('USER')}/Applications/TOPAS/OpenTOPAS-install/bin/topas`)
    - The PATH for any string containing the word `topas`
    - The `.bashrc` file for any aliases whose name contains the word `topas` or whose path contains the word `topas`

    If you notice clashes in this order, set the path manually.
- `"geometry:print_children"`, if True, will: for each geometry element, write a comment in the dumps that reads: `# Children: [Child1, Child2]`. This will be written right below the includeFiles of that element's children but it's not useless since a file name might not correspond to a component's name
    For example, a file might read:
    ```
    Ge/Accelerator/Type = "Group"
    ...
    includeFile = /home/user/project/sim/autotopas/geometry/Accelerator/Jaws.tps
    # Children = [Jaw0, Jaw1, Jaw2] 
    ```

# Features added by TopasIO

Launching Topas from python should be enough to take advantage of python's capabilities, but I've added a lot of quality of life improvements to it.

## Pretty printing

For any Space/Element, calling `print(element.getrepr())` (where `element` could be `Ge`, `Ge.World`, etc.) will pretty-print a readable version of its contents. It will only print attributes that you have modified (ie, non-defaults).

## Contexts ("with Element")

Instead of having to repeat the first parts of a line every time, you can use a simpler construct.

Instead of using:

```python
Ge.Box = TsBox()
Ge.Box.HLX = 1 * q.m
Ge.Box.HLY = 1 * q.m
Ge.Box.HLZ = 1 * q.m
```

You can use:

```python
Ge.Box = TsBox()
with Ge.Box:
    HLX = 1 * q.m
    HLY = 1 * q.m
    HLZ = 1 * q.m
```

Any new variables defined in the indented block will be added to the element directly. Notice that "new" means that you must not define a variable called (for example) HLX in your main file, otherwise TopasIO will not see a new variable definition and won't work. 


## Geometry elements

Instead of writing `Ge.BoxExample.Type = "TsBox"` you can use:

```python
from topasio import TsBox, Ge
Ge.BoxExample = TsBox()
```

Supported geometric elements are:

```
TsBox, TsJaws, TsCylinder, Group, G4Cons, G4Trd, VizComponent, GElement
```

You can add the rest of Topas's supported shapes as subclasses of `GElement`, which is just an `Element` with a couple of predefined fields. You can define Geometry elements as the latter, but the former should be preferred. The `VizComponent` is a simple red `TsBox` useful for debugging.

GElements also support the following methods:

- `self.AbsPosX()` will return the element's TransX with respect to the center of the World, by scaling up the parent ladder. AbsPosY and AbsPosZ are also supported. This is useful if you want to set the position of an element A as relative to another element B without setting B as a parent of A 
- `self.getChainAbove()` will return an ordered list of strings where the i-th element is the parent of the i-1th element. Element 0 in the list is self's parent.
- `self.printChainAbove()` will directly pretty-print the chain above in a visual way using the `rich` module.


Also, when defining a `Group()`, you can pass to it `expand=False` (default: `True`). If you do, TopasIO will try to output it and all of its children to the same file, limiting the number of files produced. This is particularly useful if you have a group with many children that have no children (remember that you can access an element's children with `Ge.getChildrenOf("element")`) and want to write everything to a single file.

## Scorers

You can define a scorer by using:

```python
from topasio import Ge, TsBox, Scorer
Ge.Box = TsBox()
Ge.Scorer = Scorer()
Ge.Scorer.Component = "Box"
```

A `PhaseSpaceScorer` is also implemented for better syntax highlighting and suggestions.

## Sources

You can define a source by using:

```python
from topasio import Ge, TsBox, Source
Ge.Box = TsBox()
Ge.Source = Source()
Ge.Source.Component = "Box"
Ge.Source.NumberOfHistoriesInRun = 5
```

But `Beam` and `PhaseSpaceSource` are also implemented for better syntax highlighting and suggestions.

## Loading a Space from excel

Sometimes you might want to keep related parameters in an excel file if you don't plan on ever touching them. I find this particularly useful for materials definitions so that I don't have to write boilerplate code in the main file. Here is an example of an excel file you might write to define ABS plastic and steel:

| ABS    |    Components	|Carbon	|Hydrogen	|Nitrogen	|
|        |    Fractions	    |0.85	|0.08	    |0.07	    |
|        |    State		    |Solid	|           |           | #Predefined
|        |    Density	    | 1.08	|g/cm3		|           |
|        |    MeanExcitationEnergy|	|	        |           |#Predefined
||||||
| Steel  |    Components	|Iron	|Chromium	|
|        |    Fractions	    |0.8	|0.2	    |
|        |    State		    |		|           | #Predefined
|        |    Density	    | 8.0	|g/cm3		|
|        |    MeanExcitationEnergy|	|	        |#Predefined

You define little tables with all of the parameters. The leftmost column should include only the names of the elements you are defining. Each table should then be as wide as needed with padding added, and comments should go on the rightmost column of the table (they are not required though, so that column can be omitted). Note that the column of comments is not the same for each table. Fields that are left blank will use the Topas defaults (and their respective rows could be skipped while defining the table). For materials, the State default is "Solid" and the excitation energies will be calculated by Topas.

For example, another table like this could be concatenated to the first two:

| Steel2  |    Components	|Iron	|Chromium	
|        |    Fractions	    |0.8	|0.2	    
|        |    Density	    | 8.0	|g/cm3	

Notice that the TopasIO interpreter will expect a field to be:

| Blank or element name | Element attribute name | Element attribute value(s)

The last part consists of one or more non-blank cells.

- A single non-blank cell will be interpreted as integer/float/bool.
- A pair of non-blank cells with a number and a string will be interpreted as a dimensioned value.
- Anything else will be interpreted as a vector whose lenght is the number of non-blank cells (optional comment cell is obviously not counted).

From TopasIO, then import the file as:

```python
Ma.from_xlsx("myparams.xlsx")
```

Note that this internally calls `Ma.update()` so any content that was in `Ma` before importing the xlsx will persist and be overwritten only if needed. For example:

```python
Ma.ABS.Components = ["Iron", "Gold"]
Ma.from_xlsx("myparams.xlsx")
```

Will overwrite ABS's components.


## Special Spaces

By default, Spaces are dumped to `main.tps`, but the most verbose spaces have had their dumping algorithm altered.

### Geometry

The tree-like structure of the geometry elements is used by TopasIO to guide where each element should be written to. A tree is created automatically when dumping the `Ge` to file, but you can force it by calling:

```python
tree = Ge.getTree("World")
```

Which will create and return a geometry tree starting from the World. The returned tree can be printed with either of:

```python
tree.print()
tree.printAsDir()
```

The former will print using indentation to specify levels in the tree, while the latter will: for each leaf element, print all of the chain above it (up to the World) with slashes as separators, like a directory structure. Note that this directory structure is not related in any way to the directory structure of the dumped output parameters. Also note that forcing the generation of a tree this way will not keep it updated. To avoid this, before running the simulation (and after you're finished using the tree), call `Ge["_tree"]=None`. This will force the simulation to regenerate an up to date tree. Also, note that the simulation expects the tree to be `None` at startup, so you should do this even if you haven't modified the tree.

You can also call `Ge.getChildrenOf("World")` to retrieve a list of all of the children of the World. The same can be done for any element.


### Graphics

Graphics are implemented as a special class with the following methods:

```python
from topasio import Gr
Gr.enable()
Gr.disable()
```

That respectively activate and deactivate a Qt window creation on startup. Graphics is enabled by default.

Another option for setting up graphics is to pass `view_only=True` to `topasio.run_simulation()`. Doing so will disable all the sources and enable graphics automatically. 

### Scorers and sources

Both scorers and sources are implemented as special classes so that each scorer/source is dumped to the same file where its Component resides.


## A note on `quantities`'s inner workings

While the module usually works expectedly, you should keep in mind that it passes its objects by reference and not by value:

```python
x = 1 * q.m
y = x
y += 1 * q.m
print(x, y) # prints "2m, 2m"
```

So be careful when dealing with constructs such as cumulative sums:

```python
Ge.World.HLX = 1 * q.m
cumsum = Ge.World.HLX
for HL in [0.1, 0.2, 0.3] * q.cm:
    cumsum -= HL
print(cumsum, Ge.World.HLX) # prints "1.06m, 1.06m"
```

If you need to bypass this behaviour, use `copy.copy` or `copy.deepcopy`:

```python
from copy import deepcopy
Ge.World.HLX = 1 * q.m
cumsum = deepcopy(Ge.World.HLX)
for HL in [0.1, 0.2, 0.3] * q.cm:
    cumsum -= HL
print(cumsum, Ge.World.HLX) # prints "1.06m, 1m"
```







