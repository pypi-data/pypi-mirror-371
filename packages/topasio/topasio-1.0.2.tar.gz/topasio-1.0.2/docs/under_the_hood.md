---
title: Under the hood
layout: default
nav_order: 3
---

* Table of contents
{:toc}

# Dot syntax
Under the hood, the library defines the elements as dictionaries. The python attribute (dot) syntax is implemented to reduce the amount of typing needed compared to dictionaries. Whenever the value of an element attribute is set, TopasIO adds its name to a "_modified" attribute of the element. This is a list of the names of all attributes that have been modified for that element. This allows TopasIO to only write the parameters that differ from the defaults.

# The "_modified" attribute
Element attributes starting with "_" are private and used internally by TopasIO to work properly. All objects implemented in TopasIO have their "_modified" attribute set to all the keys that OpenTOPAS requires to operate. For example, the TsCylinder has HL in its "_modified" because in Topas defining a cylinder without HL would result in an error. Most of these values are set to 0 except for angle spans, which are set to 360°. All spaces have their defaults implemented (for example, accessing `Gr.Color.White` will work out of the box), but their `_modified` set to `[]` so that `Gr.Color.White` is not dumped by default.

# Difference between Elements and Spaces
You should not use these interchangeably. Even though Spaces are subclasses of Elements, the main difference between them is that Spaces create new elements whenever you try to access a nonexisting key, while Elements error out:

```python
element.Child.Name = "element" # Errors out
space.Child.Name = "element" # Works fine
```

This allows defining the child of a space without having to explicitly call it:

```python
# this:
space.Child = Element()
space.Child.Name = "element"

# is the same as this:
space.Child.Name = "element"
```

This is because in the last line, python internally tries to get `space["Child"]` and then set its `Name` to `"element"`. This property of Spaces should only be used this way since it may have unintended consequences if you are actually trying to get a nonexisting element. For example:

```python
space.Child1.HLX = space.Child2.HLX
```

Will error out since an `Element()` has no `HLX`.

# Element.update()

This will work like a `dict().update()` but will also update the `_modified` lists. This method alone lets you write Topas files as json and import them.

Note: while translating json to Topas is supported through this method, dimensioned quantities won't work unless you write some code to differentiate between strings and dimensioned quantities.

Note: the translation from TopasIO to json is not currently supported, but since each Space is a dictionary, it should be easy to implement as you need. Keep in mind that to have a human-readable version of Space, the `print(space.getrepr())` method should be preferred over `print(space)`

# Contexts

Using the `inspect.currentframe`, TopasIO will save the `globals()` state upon entering the context and check it again after exiting. Any globals defined in the meantime will be saved as attributes and added to the `_modified`


# Geometry and dumping

This Space is the most complex due to how much Topas relies on geometry: while, at least in my experience, a parameter file without geometry could be 100 lines long, a parameter file with geometry will easily be ten times that. To avoid dumping all of the parameters in `main.tps`, Geometry implements a file-assignment system that is aware of the tree-like structure of the geometry itself: if A is an Element of Geometry with a child B, then A's file will be above in the directory structure. The actual file-assignment process is implemented in `Geometry()`'s methods. It is a bit wonky, since a tree can't be mapped easily onto a directory tree (since in a directory elements are either parents or leaves, while Topas Elements can be both at the same time). Here are the general guidelines:

- All of the geometry will be put inside a `geometry` subdirectory
- Its entry point will be a file called `World.tps` that contains at least the World definition.
- Scorers and sources are dumped to their `Component`'s file
- The `includeFile` chain works out of the box no matter how complex the parent tree
- `Group`s normally create directories (and get dumped to their parent's file), while `Element`s normally create files and are dumped there.
- The process normally results in many more files than I'd personally like, but I still prefer it over dumping everything into `main.tps` or `geometry.tps`.
