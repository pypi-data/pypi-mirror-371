---
title: Review of common constructs
layout: default
nav_order: 2.5
---

This is intended as a cheatsheet, since TopasIO's syntax extends Topas's. You could write a TopasIO file as you were writing in Topas (by changing slashes to dots, etc.) but TopasIO's syntax is more expressive so here are easier ways to do things. 

* Table of contents
{:toc}

# For loops

Say you want to define three boxes with the same HLX and HLY but different TransZ and HLZ. Here is the code for it.

```python
thicknesses = [1, 2, 3] * q.m
positions = [1, -1, 5] * q.m
sidelength = 3 * q.cm

for i, thickness, position in zip(range(len(thicknesses), thicknesses, positions)):
    setattr(Ge, f"box_{i}", TsBox())
    box = getattr(Ge, f"box_{i}")
    with box:
        HLX = HLY = sidelength
        HLZ = thickness / 2
        TransZ = position
```

Note that the Parent of each box was not specified: TopasIO will set undefined parents to be World to comply with Topas requirements. Any bugs that this creates will likely cause an overlap and trigger an error, so it's not a big deal.

Big note: here are the reasons for using `setattr` and `getattr` instead of other syntax:

- Even if all Elements (and thus Spaces) are embellished dictionaries (so `Ge["Elem"]["HLX"]` is valid TopasIO syntax), using the dictionary syntax does not let TopasIO remember that a key was modified. Thus, using the dictionary syntax will have TopasIO not output parameters properly. Thus, TopasIO prefers (in fact, it prescribes) the python "dot" syntax (`Ge.Elem.HLX`)
- Ideally, you'd want to write `Ge.box_i = TsBox()` for setting and then `box = Ge.box_i` for getting. This doesn't work because `.box_i` isn't interpreted by python as you'd want it to. You have to use the built-in functions and parse the [f-strings](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals) manually. Still, note that after the for loop finishes, `Ge.box_0` will work fine: the problem with the dot syntax only arises if you want to access an attribute programmatically.

# Importing

If you want to split you code in a file called `main.py` and one called `linac.py`, you can do so by writing in the main:

```python
# main.py:
from topasio import Ge, TsBox
Ge.World.HLZ = 1 * q.m
import linac

# linac.py:
from topasio import Ge, TsBox
Ge.LinacHead = TsBox()
Ge.LinacHead.HLZ = 50 * q.cm
```

This will work as intended (the defined parameters will be merged), but notice that python `import`s (and thus TopasIO) don't work like Topas's `includeFile`: 
- in Topas, importing files can overwrite parameters in imported files and the order does not matter. 
- in TopasIO, importing files can overwrite parameters in imported files only if the overwrites happen after the import.

For example, in topas:
```python
Ge/World/HLX = 1 m
includeFile = "World.tps" # defines World/HLX = 2m
```
Will result in HLX being 1m. Instead, in TopasIO:
```python
# Case 1:
Ge.World.HLX = 1 * q.m
import World # defines World.HLX = 2 * q.m
# Case 2:
import World # defines World.HLX = 2 * q.m
Ge.World.HLX = 1 * q.m
```
The second case will work like Topas's, but the first will have the imported file overwrite HLX to be 2m. 

# Conditionals

Python conditionals are supported by default, but you can even extend them by using conditional imports. Say you have a file `detector1.py` and another `detector2.py` that define two different detectors you're testing. In the main file, you can write:

```python
detector_num = 1
if detector_num == 1:
    import detector1
elif detector_num == 2:
    import detector2
```


# Using numpy and pandas

If you want to load a spectrum, you might need to read a csv file. To do this, you can use:


```python
df = pd.read_csv("data/Spectrum.csv")  # Load the data
energies = df["Energy [MeV]"].values * q.MeV  # Extract energies
weights = df["Density"].values  # Extract weights
weights /= np.sum(weights)  # Normalize weights

So.MainSource.BeamEnergySpectrumValues = energies.tolist()  # List of energies in MeV
So.MainSource.BeamEnergySpectrumWeights = weights.tolist()  # Corresponding weights
```

# Example: symmetric stack of layers


Say you want to create a TsBox that is a layered stack of materials and that the stack has a symmetry around the middle. For example:

| Pb(1mm) | W(2mm) | Cu(3mm) | W(2mm) | Pb(1mm)|

```python
thicknesses = {
    "Cu" : 3 * q.mm,
    "W"  : 2 * q.mm,
    "Pb"   : 1 * q.mm,
}
colors = {k:v for k, v in zip(thicknesses.keys(), ["red", "green", "blue"])}

Ge.Stack = Group()

Ge.CentralCu = TsBox()
with Ge.CentralCu:
    Parent = "Stack"
    HLZ = ticknesses["Cu"]/2
    Material = "Cu"
    Color = colors["Cu"]

running_cumsum = deepcopy(Ge.CentralCu.HLZ)
for material, thickness in thicknesses.items():
    if material == "Cu":
        continue # already defined
    running_cumsum += thickness # notice that we add the full thickness, not half
    for sign in [-1, +1]:
        setattr(Ge, f"{material}_{(sign+1)//2}", TsBox())
        with Ge[f"{material}_{(sign+1)//2}"]:
            Parent = "Stack"
            HLZ = thickness / 2
            TransZ = sign * (running_cumsum - thickness/2)
            Material = material
            Color = colors[material] 
```

Note that in the for loop, we get the TsBox with the dictionary syntax instead of using `getattr`. This is to prove that Spaces and Elements are just dictionaries with custom properties, and it also proves that TopasIO mostly works fine even if using this syntax. The main downside of the dictionary syntax (as opposed to `getattr`) is that, if you're trying to get an attribute of a Space, you'll get an error instead of proper functionality. This works:

```python
# start of file
Ge.Elem.HLX = 3 * q.m
```

Even if you've never defined `Ge.Elem`, while this does not:

```python
# start of file
Ge["Elem"]["HLX"] = 3 * q.m
```

Since you'll get an error because `Ge` has no `Elem` key. Also, note that here we are _getting_ the `Elem` attribute of `Ge` but we are _setting_ `HLX` for that attribute. Even if there were no errors, setting an attribute using the dictionary syntax is bad practice in TopasIO because the attribute you've just set will likely never be dumped to a file (due to TopasIO inner workings). To recap: you can get an attribute with either syntax (but `getattr` or dots should be preferred) while you can set only with `setattr` or the dot syntax. Thus, this construct (which is what was used in the Stack example) is borderline syntax:

```python
Ge.Elem = TsBox()
Ge["Elem"].HLX = 3 * q.cm
```


# Multiple sequential simulations

If you want to call `topasio.run_simulation()` multiple times in the same python call, you must delete the geometry tree that was introduced in the previous section. This is because the simulation expects the tree to be None and generates it. If it finds it already, it will crash (this is not the intended behavior but I'm fine with it). So, you should do this:
```python
for i in range(3):
    topasio.run_simulation()
    Ge["_tree"] = None
```
Since this is not a very useful loop to write, below is a more complete example of multiple simulations:
```python
for thickness in [0.1, 0.2, 0.3] * q.m:
    Ge.Box.HLZ = thickness / 2
    topasio.run_simulation()
    Ge["_tree"] = None
```
This will create 3 folders in your outputs with sequential numbering (the numbering won't start from 0 if the output folder is not empty), each using a different thickness for the Box. If you run multiple simulations per python call, I suggest you enable the config `write_parameter_summary` so that even if you forget which output folder number corresponds to which thickness you'll have a summary in each folder that includes all of the parameters used in that particular simulation (including `Ge.Box.HLZ`). 

