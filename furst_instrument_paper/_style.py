"""
The appearance shared by every figure in the article.
"""

__all__ = [
    "rc",
]

rc = {
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "legend.title_fontsize": 7,
    "lines.linewidth": 1,
    "lines.markersize": 3,
    "axes.linewidth": 0.5,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "savefig.dpi": 300,
}
"""
The :mod:`matplotlib` settings every figure is drawn with.

The fonts are sized for a journal column, where the text is set at about
ten points and a figure is read at its printed size.
"""
