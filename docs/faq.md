# FAQ

## How do I report an issue or make a feature request?

Please go to <https://github.com/giswqs/eefolium/issues>.

## How do I cite eefolium in publications?

Wu, Q., (2020). eefolium: A Python package for interactive mapping with Google Earth Engine. _The Journal of Open Source Software_, 5(51), 2305. <https://doi.org/10.21105/joss.02305>

```
Bibtex:
@article{wu2020eefolium,
    title={eefolium: A Python package for interactive mapping with Google Earth Engine},
    author={Wu, Qiusheng},
    journal={Journal of Open Source Software},
    volume={5},
    number={51},
    pages={2305},
    year={2020}
}
```

## Why does eefolium use two plotting backends: folium and ipyleaflet?

A key difference between [ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) and [folium](https://github.com/python-visualization/folium) is that ipyleaflet is built upon ipywidgets and allows bidirectional communication between the front-end and the backend enabling the use of the map to capture user input, while folium is meant for displaying static data only ([source](https://blog.jupyter.org/interactive-gis-in-jupyter-with-ipyleaflet-52f9657fa7a)). Note that [Google Colab](https://colab.research.google.com/) currently does not support ipyleaflet ([source](https://github.com/googlecolab/colabtools/issues/60#issuecomment-596225619)). Therefore, if you are using eefolium
with Google Colab, you should use `import eefolium.eefolium as eefolium`. If you are using eefolium with a local Jupyter notebook server, you can
use `import eefolium`, which provides more functionalities for capturing user input (e.g., mouse-clicking and moving).
