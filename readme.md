lightweight python implementation of [Björn Ottosson](https://bottosson.github.io/)'s oklab/oklch colour space. 

i like oklab but there isnt a straightforward python package for working with it. so i made it.

# install

install it from [PyPI](https://pypi.org/project/oklab/):

```sh
python -m pip install oklab
```

# how to use?

use it in python:

```python
import oklab

oklab.lch_to_hex((0.75, 0.125, 310.0))
# '#c697e9'

oklab.hex_to_lch('#ff0000')
# (0.6279536182521783, 0.25762679148825324, 29.227131291763712)

oklab.lab_to_xyz((1.0, 0.0, 0.0))
# (0.9504559270516719, 0.9999999999999998, 1.0890577507598782)
```

or use it in the terminal:

```shell
> oklab -i lch -o hex 0.75 0.125 310
#c697e9

> oklch ff0000
(0.6279536182521783 0.25762679148825324 29.227131291763712)

> oklab -i lab -o xyz 1.0 0.0 0.0
(0.9504559270516719, 0.9999999999999998, 1.0890577507598782)
```

# features

- ✅ 6 formats: `rgb`, `hex`, `lab`, `lch`, `xyz`, `lms`
- ✅ 30 conversion functions (complete graph)
- ✅ numerical accuracy + roundtrip correctness
- ✅ source correctness
- ✅ zero dependencies
- ✅ CLI tool
- ✅ python ≥3.8 compatibility
- 🚧 clamping (in native oklab space via chroma reduction)
- 🚧 configurable RGB primaries (P3, rec2020, …)  
- ❌ CMYK support (scope creep)  

# sources

- function names inspired by [hsluv](https://github.com/hsluv/hsluv-python)
- outputs sanity-checked against [oklch.com](https://oklch.com/) and [wikipedia](https://en.wikipedia.org/wiki/Oklab_color_space)
- `M0` sourced from [Björn's CSSWG comment](https://github.com/w3c/csswg-drafts/issues/6642#issuecomment-945714988)
- `M2_inv` sourced from [Björn's blogpost](https://bottosson.github.io/posts/oklab/)
- `XYZ_TO_RGB`, `RGB_TO_XYZ` sourced from [colour science](https://www.colour-science.org/)
- `M1`, `M1_inv`, `M2`, `RGB_TO_LMS`, `LMS_TO_RGB` derived numerically using [numpy](https://github.com/numpy/numpy)
- `test_oklab.test_xyz` sourced from [Björn's blogpost](https://bottosson.github.io/posts/oklab/)

# conversion graph

here is a graph of the atomic conversions:

![graph of formats and conversions](https://github.com/deftasparagusanaconda/oklab/blob/main/graph.png)

- lab: oklab cartesian space
- lch: oklch cylindrical space
- lms: intermediate lms-like space
- xyz: CIEXYZ space
- rgb: sRGB
- hex: 8-bit sRGB in hexadecimal

all composed conversions are derived via shortest path in this graph

