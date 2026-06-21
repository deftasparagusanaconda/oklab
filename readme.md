lightweight python implementation of [Björn Ottosson](https://bottosson.github.io/)'s oklab/oklch colour space. 

i like oklab but there isnt a straightforward python package for working with it. so i made it.

![gamut fixed chroma demo](<https://github.com/deftasparagusanaconda/oklab/blob/main/demos/gamut fixed chroma demo.webp>)
![gamut hull demo](<https://github.com/deftasparagusanaconda/oklab/blob/main/demos/gamut hull demo.webp>)
![gamut clamp demo](<https://github.com/deftasparagusanaconda/oklab/blob/main/demos/gamut clamp demo.webp>)

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

try this fancy demo!

```python
import os, oklab
C, R = os.get_terminal_size()
for row in range(R - 1, -1, -1):
    string = []
    for col in range(C):
        l = row / (R - 1) * 0.85 + 0.15
        c = 0.125
        h = col / (C - 1) * 360
        colour = oklab.lch_to_rgb((l, c, h))
        if not all(0 < c < 1 for c in colour):
			# out of gamut
            string.append(f' ')
            continue
        r, g, b = tuple(round(c * 255) for c in colour)
        string.append(f'\x1b[38;2;{r};{g};{b}m█')
    print(''.join(string))
```

# features

- ✅ 8 formats: `hex`, `srgb`, `dp3`, `bt2020`, `xyz`, `lms`, `oklab`, `oklch`
- ✅ 26 conversion functions
- ✅ numerical correctness + roundtrip precision
- ✅ source correctness
- ✅ zero dependencies
- ✅ CLI convenience tools
- ✅ python ≥3.8 compatibility
- ✅ sRGB, Display P3, ITU-R BT.2020 (Rec. 2020) support
- ✅ clamping: chroma reduction (default) + point projection
- 🚧 MINDE clamping
- 🚧 reference-grade correctness
- ❌ CMYK support (scope creep w/non-RGB spaces) 

todo:

- give -c --clamp option in CLI tools

# sources

- function names inspired by [hsluv](https://github.com/hsluv/hsluv-python)
- outputs sanity-checked against [oklch.com](https://oklch.com/) and [wikipedia](https://en.wikipedia.org/wiki/Oklab_color_space)
- `M0` sourced from [Björn's CSSWG comment](https://github.com/w3c/csswg-drafts/issues/6642#issuecomment-945714988)
- `M2_inv` sourced from [Björn's blogpost](https://bottosson.github.io/posts/oklab/)
- matrices sourced from [colour science](https://www.colour-science.org/)
- `M1`, `M1_inv`, `M2`, … derived numerically using [numpy](https://github.com/numpy/numpy)
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
