# giancarlo

Named after Gian Carlo Wick, this is a Python library for performing Wick contractions in quantum field theories.

It provides tools to represent and manipulate creation and annihilation operators symbolically and automatically expand products of operators using the Wick theorem.

**License:** GPL-3.0 ([LICENSE](https://github.com/mbruno46/giancarlo/blob/main/LICENSE))

## Authors

Mattia Bruno, maintainer
Francesca A. Bresciani, co-developer

## Features

- Symbolic representation of quantum operators
- Automatic Wick contraction expansion
- Simplification of operator products
- Designed for quantum field theory and many-body physics applications


## Installation

```bash
pip install git+https://github.com/mbruno46/giancarlo.git
```

If you want to hack the library locally

```bash
git clone https://github.com/mbruno46/giancarlo.git
cd giancarlo
pip install -e .
```

This installs the library in editable mode for development.


## Tutorials

The repository contains a `tutorials/` folder with notebooks demonstrating:

- Defining quantum field operators
- Constructing operator products
- Performing Wick contractions
- Simplifying symbolic expressions

These serve as practical examples for learning the library.


## Citation

If you use this library in research or software, please cite it appropriately in publications or acknowledgments.

<!-- ---

## Acknowledgments

Inspired by other symbolic physics libraries and academic tools for operator algebra. Provides a Python-centric approach for Wick contractions in quantum field theory. -->
