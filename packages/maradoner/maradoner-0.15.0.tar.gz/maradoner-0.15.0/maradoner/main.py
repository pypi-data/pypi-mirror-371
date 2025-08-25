# -*- coding: utf-8 -*-
from . import check_packages
from enum import Enum
from click import Context
from typer import Typer, Option, Argument
from typer.core import TyperGroup
from typing import List
from rich import print as rprint
from jax import __version__ as jax_version
from scipy import __version__ as scipy_version
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from .create import create_project
from pathlib import Path
from .fit import fit, ClusteringMode, calculate_fov, predict, GOFStat, GOFStatMode
from .grn import estimate_promoter_variance, grn
from .synthetic_data import generate_dataset
from time import time
from dill import __version__ as dill_version
from .export import export_results, export_loadings_product, Standardization, ANOVAType
from . import __version__ as project_version
from .select import select_motifs_single
import json

# logging.getLogger("jax._src.xla_bridge").addFilter(logging.Filter("No GPU/TPU found, falling back to CPU."))
# logging.getLogger("jax._src.xla_bridge").addFilter(logging.Filter("An NVIDIA GPU may be present on this machine, but a CUDA-enabled jaxlib is not installed. Falling back to cpu."))

__all__ = ['main']

class Compression(str, Enum):
    lzma = 'lzma'
    gzip = 'gzip'
    bz2 = 'bz2'
    raw = 'raw'

class LoadingTransform(str, Enum):
    none = 'none'
    ecdf = 'ecdf'
    esf = 'esf'

class OrderCommands(TyperGroup):
  def list_commands(self, ctx: Context):
    """Return list of commands in the order appear."""
    return list(self.commands)    # get commands using self.commands

_DO_NOT_UPDATE_HISTORY = False

def update_history(name: str, command: str, **kwargs):
    if _DO_NOT_UPDATE_HISTORY:
        return
    try:
        with open(f'{name}.json', 'r') as f:
            d = json.load(f)
    except FileNotFoundError:
        d = dict()
    if command == 'create':
        d.clear()
        d['jax'] = jax_version
        d['maradoner'] = project_version
        d['scipy'] = scipy_version
        d['dill'] = dill_version
        d['name'] = name
    elif command == 'fit':
        for k in ('test', 'test_binom', 'difftest', 'combine', 'export', 'plot'):
            if k in d:
                del d[k]
        for k in list(d):
            if k.startswith('export'):
                del d[k]
    d[command] = kwargs
    with open(f'{name}.json', 'w') as f:
        json.dump(d, f, indent=4)
    
doc = f'''
[bold]MARADONER[/bold] version {project_version}: [bold]M[/bold]otif [bold]A[/bold]ctivity [bold]R[/bold]esponse [bold]A[/bold]nalaysis [bold]Done R[/bold]ight 
\b\n
\b\n
A typical [bold]MARADONER[/bold] session consists of sequential runs of [bold cyan]create[/bold cyan], [bold cyan]fit[/bold cyan],  [bold cyan]predict[/bold cyan] and, finally, \
[bold cyan]export[/bold cyan] commands. [bold]MARADONER[/bold] accepts files in the tabular format (.tsv or .csv, they also can come in gzipped-flavours), \
and requires the following inputs:
[bold orange]•[/bold orange] Promoter expression table of shape [blue]p[/blue] x [blue]s[/blue], where [blue]p[/blue] is a number of promoters and \
[blue]s[/blue] is a number of samples;
[bold orange]•[/bold orange] Matrix of loading coefficients of motifs onto promoters of shape [blue]p[/blue] x [blue]m[/blue], where [blue]m[/blue] \
is a number of motifs;
[bold orange]•[/bold orange] [i](Optional)[/i] Matrix of motif expression levels in log2 scale per sample of shape [blue]m[/blue] x [blue]s[/blue];
[bold orange]•[/bold orange] [i](Optional)[/i] JSON dictionary or a text file that collects samples into groups (if not supplied, it is assumed that \
each sample is a group of its own).
[red]Note:[/red] all tabular files must have named rows and columns.
All of the input files are supplied once at the [cyan]create[/cyan] stage. All of the commands are very customizable via numerous options, more \
details can be found in their respective helps, e.g.:
[magenta]>[/magenta] [cyan]maradoner fit --help[/cyan]

\b\n
If you found a bug or have any questions, feel free to contact us via
a) e-mail: [blue]iam@georgy.top[/blue] b) issue-tracker at [blue]github.com/autosome-ru/maradoner[/blue]
'''
app = Typer(rich_markup_mode='rich', cls=OrderCommands, add_completion=False, help=doc)

from .mara.main import app_old
app.add_typer(app_old, name='mara', help='Run classical (IS)MARA framework. For testing purposes.')

help_str = 'Initialize [bold]MARADONER[/bold] project initial files: do parsing and filtering of the input data.'

@app.command('create', help=help_str)
def _create(name: str = Argument(..., help='Project name. [bold]MARADONER[/bold] will produce files for internal usage that start with [cyan]'
                                            'name[/cyan].'),
            expression: Path = Argument(..., help='A path to the promoter expression table. Expression values are assumed to be in a log-scale.'),
            loading: List[Path] = Argument(..., help='A list (if applicable, separated by space) of filenames containing loading matrices. '),
            loading_transform: List[LoadingTransform] = Option([LoadingTransform.esf], '--loading-transform', '-t',
                                                               help='A type of transformation to apply to loading '
                                                                'matrices. [orange]ecdf[/orange] substitutes values in the table with empricical CDF,'
                                                                ' [orange]esf[/orange] with negative logarithm of the empirical survival function.'),
            motif_expression: List[Path] = Option(None, help='A list of paths (of length equal to the number of loading matrices) of motif expression'
                                                  ' tables. All expression values are assumed to be in log2-scale.'),
            sample_groups: Path = Option(None, help='Either a JSON dictionary or a text file with a mapping between groups and sample names they'
                                          ' contain. If a text file, each line must start with a group name followed by space-separated sample names.'),
            filter_lowexp_w: float = Option(0.9, help='Truncation boundary for filtering out low-expressed promoters. The closer [orange]w[/orange]'
                                            ' to 1, the more promoters will be left in the dataset.'),
            filter_max_mode: bool = Option(True, help='Use max-mode of filtering. Max-mode keeps promoters that are active at least for some samples.'
                                                       ' If disabled, filtration using GMM on the averages will be ran instead.'),
            filter_plot: Path = Option(None, help='Expression plot with a fitted mixture that is used for filtering.'),
            loading_postfix: List[str] = Option(None, '--loading-postfix', '-p', 
                                                help='String postfixes will be appeneded to the motifs from each of the supplied loading matrices'),
            motif_filename: Path = Option(None, '--motif-filename', help='If provided, then only motifs with names present in this fill will be kept'),
            compression: Compression = Option(Compression.raw.value, help='Compression method used to store results.')):
    if type(compression) is Compression:
        compression = str(compression.value)
    if sample_groups:
        sample_groups = str(sample_groups)
    loading = list(map(str, loading))
    loading_transform = [x.value if issubclass(type(x), Enum) else str(x) for x in loading_transform]
    t0 = time()
    p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(description="Initializing project...", total=None)
    p.start()
    r = create_project(name, expression, loading_matrix_filenames=loading, motif_expression_filenames=motif_expression, 
                       loading_matrix_transformations=loading_transform, sample_groups=sample_groups, 
                       promoter_filter_lowexp_cutoff=filter_lowexp_w,
                       promoter_filter_plot_filename=filter_plot,               
                       promoter_filter_max=filter_max_mode,
                       compression=compression, 
                       motif_postfixes=loading_postfix,
                       motif_names_filename=motif_filename,
                       verbose=False)
    p.stop()
    dt = time() - t0
    p, s = r['expression'].shape
    m = r['loadings'].shape[1]
    g = len(r['groups'])
    rprint(f'Number of promoters: {p}, number of motifs: {m}, number of samples: {s}, number of groups: {g}')
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')
    

@app.command('fit', help='Estimate variance parameters and motif activities.')
def _fit(name: str = Argument(..., help='Project name.'),
          clustering: ClusteringMode = Option(ClusteringMode.none, help='Clustering method.'),
          num_clusters: int = Option(200, help='Number of clusters if [orange]clustering[/orange] is not [orange]none[/orange].'),
          test_chromosomes: List[str] = Option(None, '--test-chromosomes', '-t', help='Test chromosomes'),
          gpu: bool = Option(False, help='Use GPU if available for most of computations.'), 
          gpu_decomposition: bool = Option(False, help='Use GPU if available or SVD decomposition.'), 
          x64: bool = Option(True, help='Use high precision algebra.')):
    """
    Fit a a mixture model parameters to data for the given project.
    """

    t0 = time()
    p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(description="Fitting model to the data...", total=None)
    p.start()
    fit(name, clustering=clustering, num_clusters=num_clusters,
        gpu=gpu, test_chromosomes=test_chromosomes,
        gpu_decomposition=gpu_decomposition, x64=x64)
    p.stop()
    dt = time() - t0
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')

@app.command('gof', help='Estimate GOFs given test/train data split. Provides test info only if [orange]test-chromosomes[/orange] is not None in [cyan]fit[/cyan].')
def _gof(name: str = Argument(..., help='Project name.'),
         use_groups: bool = Option(False, help='Compute statistic for sammples aggragated across groups.'), 
         stat_type: GOFStat = Option(GOFStat.fov, help='Statistic type to compute'),
         stat_mode: GOFStatMode = Option(GOFStatMode.total, help='Whether to compute stats for residuals or accumulate their effects'),
         gpu: bool = Option(False, help='Use GPU if available for most of computations.'), 
         x64: bool = Option(True, help='Use high precision algebra.')):
    """
    Fit a a mixture model parameters to data for the given project.
    """

    t0 = time()
    p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(description="Calculating FOVs...", total=None)
    p.start()
    res = calculate_fov(name, stat_mode=stat_mode, stat_type=stat_type, use_groups=use_groups, gpu=gpu, x64=x64)
    if stat_type == GOFStat.corr:
        title = 'Pearson correlation'
    else:
        title = 'Fraction of variance explained'
    if stat_mode == GOFStatMode.residual:
        title += ' (Residual)'
    else:
        title += ' (Total)'
    t = Table('Set', 'null', 'intercepts', 'motif_mean',
              title=title)
    row = [f'{t.total:.6f}' for t in res.train]
    t.add_row('train', *row)
    if res.test is not None:
        row = [f'{t.total:.6f}' for t in res.test]
        t.add_row('test', *row)
    p.stop()
    dt = time() - t0
    rprint(t)
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')

@app.command('predict', help='Estimate deviations of motif activities from their means.')
def _predict(name: str = Argument(..., help='Project name.'),
         filter_motifs: bool = Option(True, help='Do not predict deviations from motifs whose variance is low.'),
         filter_order: int = Option(7, help='Motif variance is considered low if it is [orange]filter-order[/orange] orders of magnitude smaller that a median motif variance.'),
         tau_search: bool = Option(False, help='Search for tau multiplier using CV'),
         cv_repeats: int = Option(3, help='CV repeats in [orange]RepeatedKFold[/orange]'),
         cv_splits: int = Option(5, help='CV splits in [orange]RepeatedKFold[/orange]'),
         tau_left: float = Option(0.1, help='Left bound for tau search'),
         tau_right: float = Option(1.0, help='Right bound for tau search. Values > 1 imply that we believe that variance could be underestimated'),
         tau_num: int = Option(10, help='Number of splits in np.linspace(tau_left, tau_right, tau_num)'),
         pinv: bool = Option(False, help='Use plain Moore-Penrose pseudoinverse with Tikhonov regularization for tau > 1. Applicable for testing purposes'),
         gpu: bool = Option(False, help='Use GPU if available for most of computations.'), 
         x64: bool = Option(True, help='Use high precision algebra.')):
    """
    Fit a a mixture model parameters to data for the given project.
    """

    t0 = time()
    p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(description="Predicting motif activities...", total=None)
    p.start()
    predict(name, tau_search=tau_search, cv_splits=cv_splits, cv_repeats=cv_repeats,
            tau_left=tau_left, tau_right=tau_right, tau_num=tau_num, pinv=pinv,
            filter_motifs=filter_motifs, filter_order=filter_order, gpu=gpu, x64=x64)
    p.stop()
    dt = time() - t0
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')

@app.command('generate', help='Generate synthetic dataset for testing purporses.')
def _generate(output_folder: Path = Argument(..., help='Output folder.'),
                p: int = Option(2000, help='Number of promoters.'),
                m: int = Option(500, help='Number of motifs.'),
                g: int = Option(10, help='Number of groups.'),
                min_samples: int = Option(5, help='Minimal number of observations per each group.'),
                max_samples: int = Option(6, help='Maximal number of observations per each group.'),
                non_signficant_motifs_fraction: float = Option(0.20, help='Fraction of non-significant motifs.'),
                sigma_rel: float = Option(1e-1, help='Ratio of nu to sigma. The higher this value, the higher is FOV.'),
                means: bool = Option(True, help='Non-zero groupwise and promoter-wise intercepts'),
                seed: int = Option(1, help='Random seed.')
            ):
    t0 = time()
    pr = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    pr.add_task(description="Generating synthetic dataset...", total=None)
    pr.start()
    generate_dataset(folder=output_folder, p=p, m=m, g=g, min_samples=min_samples, max_samples=max_samples,
                     non_signficant_motifs_fraction=non_signficant_motifs_fraction, sigma_rel=sigma_rel,
                     means=means, 
                     B_cor=0, U_cor=0, E_cor=0, motif_cor=0,
                     seed=seed)
    pr.stop()
    dt = time() - t0
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')

@app.command('export', help='Extract motif activities, parameter estimates, FOVs and statistical tests.')
def _export(name: str = Argument(..., help='Project name.'),
            output_folder: Path = Argument(..., help='Output folder.'),
            std_mode: Standardization = Option(Standardization.full, help='Whether to standardize activities with plain variances or also decorrelate them.'),
            anova_mode: ANOVAType = Option(ANOVAType.positive, help='If negative, look for non-variative motifs'),
            weighted_zscore: bool = Option(False, help='Reciprocal variance weighted Z-scores'),
            alpha: float = Option(0.05, help='FDR alpha.'),
            loadings_product: bool = Option(False, help='Export loading matrix-acitvity 3D tensor. This will produce num_of_groups tabular files.'),
            lp_hdf: bool = Option(True, help='Each loadings-product table will be stored in hdf format (occupies much less space than plain tsv) using float16 precision.'),
            lp_intercepts: bool = Option(True, help='Include motif means in the 3D tensor.'),
            lp_tsv_truncation: int = Option(4, help='Number of digits after a floating point to truncate. Decreases the output size of a tabular if [orange]lp-hdf[/orange] is disabled.')):
    t0 = time()
    p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(description="Exporting results...", total=None)
    p.start()
    export_results(name, output_folder, std_mode=std_mode, anova_mode=anova_mode, alpha=alpha,
                   weighted_zscore=weighted_zscore)
    p.stop()
    
    if loadings_product:
        p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
        p.add_task(description="Exporting results...", total=None)
        p.start()
        export_loadings_product(name, output_folder, use_hdf=lp_hdf, intercepts=lp_intercepts)
        p.stop()
    
    dt = time() - t0
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')
    


__select_motif_doc = 'Selects best motif variants when the project was created from multiple loading matrices, each with an unique postfix.'\
                     'Best motif variant is select by comparing their standardized contribution/z-score of both intercepts and deviations.'\
                     'The resulting list of motif names with the appropriate postfixes will be then stored in [orange]filename[/orange].'\
                     'It''s assumed that [orange]filename[/orange] will be supplied as [orange]motif_filename[/orange] to the [bold cyan]create[/bold cyan].'
@app.command('select-motifs',
             help=__select_motif_doc)
def _select_motifs(name: str = Argument(..., help='Project name'),
                   filename: Path = Argument(..., help='Filename where a list of best motif variants will be stored')):
    t0 = time()
    p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(description="Selecting motifs...", total=None)
    p.start()
    select_motifs_single(name, filename)
    p.stop()
    dt = time() - t0
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')


__grn_doc = 'Tests each promoter against each motif per each group. Some people call it GRN.'
@app.command('grn',
             help=__grn_doc)
def _grn(name: str = Argument(..., help='Project name'),
         folder: Path = Argument(..., help='Output folder where results will be stored. In total, expect number_of_groups tables of size'
                                           ' comparable to the expression file size.'),
         hdf: bool = Option(True, help='Use HDF format instead of tar.gz files. Typically eats much less space'),
         stat: bool = Option(True, help='Save statistics alongside probabilities.'),
         prior_h1: float = Option(1/10, help='Prior belief on the expected fraction of motifs active per promoter.'),
         means: bool = Option(True, help='Include motif-specific means in both H_0 and H_1 models, otherwise only activities deviations are being tested.')):
    t0 = time()
    p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(description="Building GRN...", total=None)
    p.start()
    grn(name, output=folder, use_hdf=hdf, save_stat=stat, prior_h1=prior_h1, include_mean=means)
    p.stop()
    dt = time() - t0
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')
    
__estimate_promvar_doc = 'Estimates each promoter variance for each group using empirical Bayesian shrinkage.'\
                         ' A very recommended step before computing GRN.'
@app.command('estimate-promoter-variance',
             help=__estimate_promvar_doc)
def _estimate_promoter_variance(name: str = Argument(..., help='Project name'),
                                prior_top: float = Option(0.90,
                                                          help='The fraction from the bottom as ranked by sample'
                                                          ' variance of promoters to be used for estimating global group-wise variance.'
                                                          ' Higher values result in higher prior variance and weaken the prior.'
                                                          )):
    t0 = time()
    p = Progress(SpinnerColumn(speed=0.5), TextColumn("[progress.description]{task.description}"), transient=True)
    p.add_task(description="Estimating each promoter's variance...", total=None)
    p.start()
    estimate_promoter_variance(name, prior_top=prior_top)
    p.stop()
    dt = time() - t0
    rprint(f'[green][bold]✔️[/bold] Done![/green]\t time: {dt:.2f} s.')

def main():
    check_packages()
    app()
