python implementation of Björn Ottosson's oklab colour space (https://bottosson.github.io/posts/oklab/) (https://en.wikipedia.org/wiki/Oklab_color_space)

# install

run the following in your terminal:

```shell
pip install oklab
```

# example

```python
import oklab

oklab.lch_to_hex((0.75, 0.125, 300.0))
# '#cdb7f3'
```


