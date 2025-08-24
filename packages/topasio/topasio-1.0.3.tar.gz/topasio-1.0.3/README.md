This is a python wrapper around [OpenTOPAS](https://github.com/OpenTOPAS/OpenTOPAS), which is a tool for radiation transport simulation that itself wraps around [Geant4](https://geant4.web.cern.ch/).

The goal of this library is extend the Topas functionalities without forcing the user to rely on Geant. For example, this library implements python for-loops, conditionals, and all operations. It also extends functionalities by reducing the number of repeated code, implementing printing, and allowing interaction with the full python scientific computing suite. For example, one might have a single file that both launches a simulation and analyses its results, or even launches multiple simulations sequentially. 

For more details, see the wiki at https://gchristille.github.io/topasio