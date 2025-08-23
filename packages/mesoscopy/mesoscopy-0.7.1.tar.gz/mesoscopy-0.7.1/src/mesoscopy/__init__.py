#  Copyright (c) 2022 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>.
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this
#   software and associated documentation files (the "Software"), to deal in the
#   Software without restriction, including without limitation the rights to use, copy,
#   modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
#   and to permit persons to whom the Software is furnished to do so, subject to the
#   following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies
#  or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
#  IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

"""Main entry point to the mesoscopy CLI"""

import os

import click
import h5py
from matplotlib import pyplot as plt

import mesoscopy.register as reg
from mesoscopy import convert
from mesoscopy import export
from mesoscopy import inspect
from mesoscopy import postprocess
from mesoscopy import preprocess
from mesoscopy import process
from mesoscopy import report
from mesoscopy.__about__ import __version__


@click.group()
@click.version_option(__version__)
def cli():
    """Widefield calcium imaging analysis pipeline."""


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.argument("out_dir", type=click.Path(dir_okay=True))
@click.option("--index", default=0, show_default=True, help="Index of frame to sample.")
@click.option("--crop", default=0)
@click.option("--vmin", type=float, default=0)
@click.option("--vmax", type=float, default=255)
@click.option("--key", type=str, default=None, help="Activity column")
def sample(path, out_dir, index, crop=0, vmin=0, vmax=255, key="frames"):
    """Sample an image frame from an HDF5 file and export it as a PNG."""
    click.echo(f"Sampling {path} at index {index}.")

    f = h5py.File(path)
    d = f[f"/{key}"]

    os.makedirs(out_dir, exist_ok=True)
    outpath = out_dir + os.sep + path.split("/")[-1].replace(".h5", f"_sample-{index}.png")

    if crop > 0:
        plt.imsave(outpath, d[index, crop:-crop, crop:-crop], vmin=vmin, vmax=vmax)
    else:
        plt.imsave(outpath, d[index], vmin=vmin, vmax=vmax, cmap="jet")
    click.echo(f"Saved sample at {outpath}")


cli.add_command(preprocess.preprocess_cmd)
cli.add_command(process.process_cmd)
cli.add_command(postprocess.postprocess_cmd)
cli.add_command(reg.register_cmd)
cli.add_command(convert.convert_cmd)
cli.add_command(inspect.inspect_cmd)
cli.add_command(export.export_cmd)
cli.add_command(report.report_cmd)
