<p align="center">
  <!-- If you used a different path, update the src accordingly -->
  <img src="docs/assets/logo.png" alt="bezierv logo" width="260"/>
</p>

<h1 align="center">bezierv</h1>
<p align="center">
  <em>Fit smooth Bézier random variables to empirical data &mdash; elegant, differentiable, and fast.</em>
</p>

<p align="center">
  <!-- Add real badges once you publish to PyPI / set up CI -->
  <img alt="PyPI" src="https://img.shields.io/pypi/v/bezierv?style=flat-square">
  <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/EstebanLeiva/bezierv/ci.yml?style=flat-square">
  <img alt="License" src="https://img.shields.io/github/license/EstebanLeiva/bezierv?style=flat-square">
</p>

---

## Why Bézier random variables?  
Classical parametric distributions can be too rigid; non-parametric methods can be noisy.  
Bézier curves offer a sweet spot: **smooth** and **shape-controlled**.  
With **bezierv** you can:

* Fit Bézier CDFs/PDFs to sample data of any shape.
* Evaluate moments and quantiles.
* Compose variables via convolution.

---

## Installation

```bash
pip install bezierv            # from PyPI (coming soon)
# or, for development:
git clone https://github.com/your-org/bezierv
cd bezierv
pip install -e .
