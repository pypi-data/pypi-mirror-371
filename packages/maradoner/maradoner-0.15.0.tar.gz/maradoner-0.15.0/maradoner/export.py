#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pandas import DataFrame as DF
# add dot
from .utils import read_init, openers, ProjectData
from .fit import FOVResult, ActivitiesPrediction, FitResult
from .grn import grn
from scipy.stats import norm, chi2, multivariate_normal, Covariance
from scipy.linalg import eigh, lapack, cholesky, solve
from statsmodels.stats import multitest
import numpy as np
from enum import Enum
from tqdm import tqdm
import multiprocessing as mp
from functools import partial
from scipy.integrate import quad
import math
import time
import dill
import os


class Standardization(str, Enum):
    full = 'full'
    std = 'std'
    
class ANOVAType(str, Enum):
    positive = 'positive'
    negative = 'negative'
    
def chol_inv(x: np.array):
    """
    Calculate invserse of matrix using Ctestholesky decomposition.

    Parameters
    ----------
    x : np.array
        Data with columns as variables and rows as observations.
    return_chol : bool
        Returns cholesky decomposition if True.

    Raises
    ------
    np.linalg.LinAlgError
        Rises when matrix is either ill-posed or not PD.

    Returns
    -------
    c : np.ndarray
        x^(-1).

    """
    c, info = lapack.dpotrf(x)
    if info:
        raise np.linalg.LinAlgError
    lapack.dpotri(c, overwrite_c=True)
    mx = c + c.T - np.diag(c.diagonal())
    return mx

    
class Information():
    eps = 1e-10
    
    def __init__(self, fim: np.ndarray, slc=None, use_preconditioner=False, filter_items=None):
        self.filter_items = filter_items
        if filter_items is not None:
            fim = np.delete(fim, filter_items, axis=0)
            fim = np.delete(fim, filter_items, axis=1)
        self.square_root_inv = self._square_root_inv(fim, slc, corr=True)
        precond = 1 / fim.diagonal() ** 0.5
        if not use_preconditioner:
            precond[:] = 1
        fim = precond.reshape(-1, 1) * fim * precond
        self.fim = fim
        self.precond = precond
        self.slice = slice(None, None) if slc is None else slc
    
    def _inv(self, x: np.ndarray):
        x = np.array(x)
        # t = np.linalg.eigh(x)
        try:
            x = chol_inv(x)
        except:
            print('Failed to compute inverse using Cholesky decomposition. ')
            print('This can be a sign of a numerical errors during parameters estimation.')
            print('Will use pseudo-inverse now. The minimal and maximal eigenvalues are:')
            # print(x.diagonal().min())
            assert np.allclose(x, x.T), x - x.T
            x = np.linalg.eigh(x)
            print(x[0].min(), x[0].max())
            # x = np.linalg.pinv(x, hermitian=True)
            x = x[1] * (1/np.clip(x[0], self.eps, float('inf'))) @ x[1].T
        return x
    
    def _square_root_inv(self, x: np.ndarray, slc=None, corr=True):
        x = self._inv(x)
        if corr:
            istd =  1 / x.diagonal() ** 0.5
            x = istd.reshape(-1, 1) * x * istd
        if slc is not None:
            x = x[slc, slc]
        try:
            x = cholesky(x)
        except:
            x = np.linalg.eigh(x)
            x = x[1] * x[0] ** (1 / 2) @ x[1].T
        return x
    
    def standardize(self, x: np.ndarray, 
                    mode: Standardization=Standardization.std,
                    return_std=True):
        if self.filter_items is not None:
            x = np.delete(x, self.filter_items)
        x = x / self.precond[self.slice]
        cov = self._inv(self.fim)
        cov = cov[self.slice, self.slice]
        std = cov.diagonal() ** 0.5
        if mode == mode.std:
            x /= std
        elif mode == mode.full:
            istd = 1 / std
            cor = istd.reshape(-1, 1) * cov * istd
            e = np.linalg.eigh(cor)
            T = istd.reshape(-1,1) * e[1] * e[0] ** (-0.5) @ e[1].T
            x = T @ x.reshape(-1, 1)
        if return_std:
            return x.flatten(), std * self.precond[self.slice]
        return x.flatten()
    
    def covariance(self):
        cov = self._inv(self.fim)
        cov = cov[self.slice, self.slice]
        return self.precond[self.slice].reshape(-1, 1) * cov * self.precond[self.slice]

    def correlation(self):
        cov = self.covariance()
        d = cov.diagonal() ** (-0.5)
        return d.reshape(-1, 1) * cov * d
    
    def cholesky_transform(self, x: np.ndarray):
        if self.square_root_inv is None:
            self.square_root_inv = self.square_root_inv(self.fim, self.slice, corr=True)
        return self.square_root_inv.T @ x
        



def export_fov(fovs: tuple[FOVResult], folder: str,
               promoter_names: list[str], sample_names: list[str]):
    os.makedirs(folder, exist_ok=True)
    cols = ['null', 'means', 'motif_means']
    fov_null, fov_means, fov_motif_means = fovs
    total = [fov_null.total, fov_means.total, fov_motif_means.total]
    DF(total, index=cols, columns=['FOV']).T.to_csv(os.path.join(folder, 'total.tsv'), sep='\t')
    promoters = [fov_null.promoter[:, None], fov_means.promoter[:, None], fov_motif_means.promoter[:, None]]
    promoters = np.concatenate(promoters, axis=-1)
    DF(promoters, index=promoter_names, columns=cols).to_csv(os.path.join(folder, 'promoters.tsv'), sep='\t')
    samples = [fov_null.sample[:, None], fov_means.sample[:, None], fov_motif_means.sample[:, None]]
    samples = np.concatenate(samples, axis=-1)
    DF(samples, index=sample_names, columns=cols).to_csv(os.path.join(folder, 'samples.tsv'), sep='\t')




def posterior_anova(activities: ActivitiesPrediction, fit: FitResult, 
                    B: np.ndarray, corr_stat=False, map_cov=False):
    precs = list()
    istds = list()
    covs = list()
    mean = 0.0
    bad_inds = np.zeros(activities.U.shape[0], dtype=bool)
    # for cov, U, nu in zip(activities.cov(), activities.U.T, fit.motif_variance.group):
    #     mot = fit.motif_variance.motif
    #     mot = np.delete(mot, activities.filtered_motifs)
    #     ind = mot * nu < cov.diagonal() + 1e-9
    #     bad_inds[ind] = True
    # mot = fit.motif_variance.motif
    # mot = np.delete(mot, activities.filtered_motifs)[~bad_inds]
    motif_variance = fit.motif_variance.motif
    if activities.filtered_motifs is not None:
        motif_variance = np.delete(motif_variance, activities.filtered_motifs)
        B = np.delete(B, activities.filtered_motifs, axis=1)
    U = activities.U
    if map_cov:
        # fit.motif_variance.m
        BTB = B.T @ B
        BTB_s = BTB * motif_variance ** 0.5
        BTB_s = BTB_s @ BTB_s.T
    for cov, U, sigma, n, nu in zip(activities.cov(), U.T, 
                          activities._cov[-2], 
                          fit.error_variance.variance, fit.motif_variance.group):
        # cov = cov[~bad_inds, ~bad_inds]
        # cov = cov[..., ~bad_inds]
        # cov = cov[~bad_inds]
        if map_cov:
            D = BTB_s * nu  + np.identity(len(BTB)) * sigma
            cov = cov @ D @ cov.T * n / sigma ** 2 
        covs.append(cov)
        # U = U[~bad_inds]
        # prec = np.linalg.inv(np.diag(mot * nu) - cov)
        prec = np.linalg.pinv(cov, hermitian=True)
        mean += prec @ U
        precs.append(prec)
    total_prec = sum(precs)
    total_cov = np.linalg.pinv(total_prec, hermitian=True)
    mean = total_cov @ mean
    stats = activities.U[~bad_inds] - mean.reshape(-1, 1)
    # if corr_stat:
    #     istd = 1 / total_cov.diagonal() ** 0.5
    #     total_cor = istd.reshape(-1, 1) * total_cov * istd
    #     stats = total_cor @ stats
    #     total_cov = total_cor @ total_cov @ total_cor
    # stats = (1 / total_cov.diagonal().reshape(-1, 1)) ** 0.5 * stats
    istds = [1 / c.diagonal() ** 0.5 for c in covs]
    istds = np.array(istds).T 
    stats = stats * istds
    stats = stats ** 2
    stats = stats.sum(axis=-1)
    pvalues = chi2.sf(stats, len(precs) - 1)
    fdr = multitest.multipletests(pvalues, alpha=0.05, method='fdr_by')[1] 
    return stats, pvalues, fdr, bad_inds
    

def export_results(project_name: str, output_folder: str,
                   std_mode: Standardization, 
                   anova_mode: ANOVAType=ANOVAType.positive,
                   weighted_zscore=False,
                   alpha=0.05,
                   n_jobs=6):
    
    def calc_z_test(x):
        if anova_mode == ANOVAType.negative:
            import mpmath
            mpmath.mp.dps = 500
            pval = np.array([float(2 * mpmath.ncdf(t) - 1) for t in x])
        else:
            pval = 2 * norm.sf(np.abs(x))
        return pval

    data = read_init(project_name)
    fmt = data.fmt
    motif_names = data.motif_names
    prom_names = data.promoter_names
    # del data
    with openers[fmt](f'{project_name}.fit.{fmt}', 'rb') as f:
        fit: FitResult = dill.load(f)
    if fit.promoter_inds_to_drop:
        prom_names = np.delete(prom_names, fit.promoter_inds_to_drop)
    group_names = fit.group_names
    with openers[fmt](f'{project_name}.predict.{fmt}', 'rb') as f:
        act: ActivitiesPrediction = dill.load(f)
    if act.filtered_motifs is not None:
        motif_names_filtered = np.delete(motif_names, act.filtered_motifs)
    else:
        motif_names_filtered = motif_names
    
    os.makedirs(output_folder, exist_ok=True)
    # grn(data, act, fit, os.path.join(output_folder, 'grn'))
    error_variance = fit.error_variance.variance
    error_variance_fim = Information(fit.error_variance.fim)
    error_variance_stat, error_variance_std = error_variance_fim.standardize(error_variance, 
                                                                             mode=Standardization.std)
    
    motif_variance = fit.motif_variance.motif
    motif_variance_fim = Information(fit.motif_variance.fim, slice(None, len(motif_names_filtered)), 
                                     filter_items=act.filtered_motifs)
    motif_variance_stat, motif_variance_std = motif_variance_fim.standardize(motif_variance, 
                                                                             mode=Standardization.std)
    
    motif_group_variance = fit.motif_variance.group
    excluded_motif_group = fit.motif_variance.fixed_group
    motif_group_variance_fim = Information(fit.motif_variance.fim, slice(len(motif_names), None))
    motif_group_variance_std = motif_group_variance_fim.covariance().diagonal() ** 0.5
    
    
    motif_mean = fit.motif_mean.mean.flatten()
    motif_mean_fim = Information(fit.motif_mean.fim)
    motif_mean_stat, motif_mean_std = motif_mean_fim.standardize(motif_mean,
                                                                 mode=Standardization.std)
    
    promoter_mean = fit.promoter_mean.mean.flatten()
    # del fit
    
    
    folder = os.path.join(output_folder, 'params')
    os.makedirs(folder, exist_ok=True)
    if os.path.isfile(f'{project_name}.promvar.{fmt}'):
        with openers[fmt](f'{project_name}.promvar.{fmt}', 'rb') as f:
            promvar: np.ndarray = dill.load(f)
        DF(promvar, index=prom_names, columns=group_names).to_csv(os.path.join(folder, 'promoter_variances.tsv'), sep='\t')
    if excluded_motif_group is not None:
        motif_group_variance_std = np.insert(motif_group_variance_std, excluded_motif_group, np.nan)
    DF(np.array([error_variance, error_variance_std, motif_group_variance, motif_group_variance_std]).T,
                index=group_names,
                columns=['sigma', 'sigma_std', 'nu', 'nu_std']).to_csv(os.path.join(folder, 'group_variances.tsv'),
                                                             sep='\t')
    s = 'motif\ttau\tstd\n' + '\n'.join(f'{a}\t{b}\t{c}' for a, b, c in zip(motif_names,
                                                                            motif_variance,
                                                                            motif_variance_std))
    with open(os.path.join(folder, 'motif_variances.tsv'), 'w') as f:
        f.write(s)
    DF(promoter_mean, index=prom_names, columns=['mean']).to_csv(os.path.join(folder, 'promoter_means.tsv'),
                                                                 sep='\t')
    DF(np.array([motif_mean, motif_mean_std]).T,
       index=motif_names, columns=['mean', 'std']).to_csv(os.path.join(folder, 'motif_means.tsv'),
                                                          sep='\t')
    folder = os.path.join(folder, 'correlations')
    os.makedirs(folder, exist_ok=True)
    DF(fit.sample_mean.mean).to_csv(os.path.join(folder, 'sample_means.tsv'),
                                                                      sep='\t')
    DF(motif_mean_fim.correlation(), index=motif_names, columns=motif_names).to_csv(os.path.join(folder, 'motif_means.tsv'),
                                                                      sep='\t')
    DF(motif_variance_fim.correlation(), index=motif_names_filtered, columns=motif_names_filtered).to_csv(os.path.join(folder, 'motif_variances.tsv'),
                                                                      sep='\t')
    _group_names = group_names
    if excluded_motif_group is not None:
        _group_names = np.delete(_group_names, excluded_motif_group)
    DF(motif_group_variance_fim.correlation(), index=_group_names, columns=_group_names).to_csv(os.path.join(folder, 'motif_group_variances.tsv'),
                                                                      sep='\t')

    DF(error_variance_fim.correlation(), index=group_names, columns=group_names).to_csv(os.path.join(folder, 'error_variances.tsv'),
                                                                      sep='\t')
    
    
    folder = output_folder

    folder = os.path.join(output_folder, 'tests', 'prediction_based')
    os.makedirs(folder, exist_ok=True)

    stat, pvalue, fdr, bad_inds = posterior_anova(act, fit, B=data.B)
    motif_names_filtered = np.array(motif_names_filtered)[~bad_inds]
    anova = DF([stat, pvalue, fdr], columns=motif_names_filtered, index=['stat', 'p-value', 'FDR']).T
    anova.to_csv(os.path.join(folder, 'anova.tsv'), sep='\t')

    folder = os.path.join(output_folder, 'tests', 'asymptotics_based')
    os.makedirs(folder, exist_ok=True)
    
    anova_ass = motif_variance_stat
    pval = calc_z_test(anova_ass)

    fdrs = multitest.multipletests(pval, alpha=0.05, method='fdr_bh')[1]
    # lrt = 2 * fit.motif_variance.logratios
    # lrt_pvalues = chi2.sf(lrt, 1)
    # lrt_fdr = multitest.multipletests(lrt_pvalues, alpha=0.05, method='fdr_bh')[1]
    anova_ass = DF(np.array([anova_ass, pval, fdrs]).T, index=motif_names_filtered,
                   columns=['stat', 'p-value', 'FDR'])
    anova_ass.to_csv(os.path.join(folder, 'anova.tsv'), sep='\t')
    
    sign = motif_mean.flatten() / motif_mean_std
    neg = norm.cdf(sign)
    pos = norm.sf(sign)
    zero = chi2.cdf(sign ** 2, df=1)

    neg_fdr = multitest.multipletests(neg, alpha=0.05, method='fdr_bh')[1]
    pos_fdr = multitest.multipletests(pos, alpha=0.05, method='fdr_bh')[1]
    zero_fdr = multitest.multipletests(zero, alpha=0.05, method='fdr_bh')[1]
    sign_ass = DF(np.array([sign, zero, zero_fdr, neg, neg_fdr, pos, pos_fdr]).T, columns=['stat', 
                                                                                           'zero', 'fdr_zero',
                                                                                           'pvalue_neg', 'fdr_neg',
                                                                                           'pvalue_pos', 'fdr_pos'],
                  index=motif_names)
    sign_ass.to_csv(os.path.join(folder, 'sign.tsv'), sep='\t')
    
    folder = os.path.join(output_folder, 'activities')
    os.makedirs(folder, exist_ok=True)
    U = list()
    stds = list()
    for u, cov in zip(act.U.T, act.cov()):
        std = cov.diagonal() ** 0.5
        u = u / std
        U.append(u)
        stds.append(std)
    U = np.array(U).T
    DF(U, index=motif_names_filtered, columns=group_names).to_csv(os.path.join(folder, 'activity.tsv'), sep='\t')
    U = U ** 2
    if weighted_zscore:
        U_total = U.sum(axis=1, keepdims=True) / (1 / np.array(stds).T ** 2).sum(axis=1, keepdims=True)
    else:
        U_total = U.mean(axis=1, keepdims=True)
    
    U = np.hstack((U_total, U)) ** 0.5
    DF(U, index=motif_names_filtered,
       columns=['overall'] + list(group_names)).to_csv(os.path.join(folder, 'z_score.tsv'), sep='\t')
    DF(act.U_raw, index=motif_names_filtered, columns=data.sample_names).to_csv(os.path.join(folder, 'activity_raw.tsv'), sep='\t')
    
    if os.path.isfile(f'{project_name}.fov.{fmt}'):
        with open(f'{project_name}.fov.{fmt}', 'rb') as f:
            fov = dill.load(f)
            train = fov.train
            test = fov.test
        folder = os.path.join(output_folder, 'fov')
        if fov.grouped:
            sample_names = data.group_names
        else:
            sample_names = [None] * len(train[0].sample)
            for i, inds in enumerate(data.group_inds):
                name = data.group_names[i]
                for k, j in enumerate(inds):
                    sample_names[j] = f'{name}_{k+1}'
        if fit.promoter_inds_to_drop:
            promoter_names_train = np.delete(data.promoter_names, fit.promoter_inds_to_drop)
        else:
            promoter_names_train = data.promoter_names
        export_fov(train, os.path.join(folder, 'train'), promoter_names=promoter_names_train,
                   sample_names=sample_names)
        if test is not None:
            promoter_names_test = np.array(data.promoter_names)[fit.promoter_inds_to_drop]
            export_fov(test, os.path.join(folder, 'test'), promoter_names=promoter_names_test,
                       sample_names=sample_names)
        
            
def export_loadings_product(project_name: str, output_folder: str,
                            use_hdf: bool = True, intercepts: bool = True,
                            tsv_truncation=4):
    

    data = read_init(project_name)
    fmt = data.fmt
    motif_names = data.motif_names
    prom_names = data.promoter_names
    # del data
    with openers[fmt](f'{project_name}.fit.{fmt}', 'rb') as f:
        fit: FitResult = dill.load(f)
    if fit.promoter_inds_to_drop:
        prom_names = np.delete(prom_names, fit.promoter_inds_to_drop)
    group_names = fit.group_names
    with openers[fmt](f'{project_name}.predict.{fmt}', 'rb') as f:
        act: ActivitiesPrediction = dill.load(f)
    
    output_folder = os.path.join(output_folder, 'loadings-product')
    os.makedirs(output_folder, exist_ok=True)
    
    U = act.U
    B = data.B
    mu = fit.motif_mean.mean 
    
    if act.filtered_motifs is not None:
        motif_names = np.delete(motif_names, act.filtered_motifs)
        B = np.delete(B, act.filtered_motifs, axis=1)
        mu = np.delete(mu, act.filtered_motifs)
    BM = B * mu
    for name, U in zip(group_names, U.T):
        effect = B * U
        if intercepts:
            effect += BM
        if use_hdf:
            effect = effect.astype(np.half)
            filename = os.path.join(output_folder, f'{name}.hdf')
            DF(data=effect, index=prom_names, columns=motif_names).to_hdf(filename, key='lrt', mode='w', complevel=4)
        else:
            filename = os.path.join(output_folder, f'{name}.tsv')
            DF(data=effect, index=prom_names, columns=motif_names).to_csv(filename, sep='\t',
                                                                          float_format=f'%.{tsv_truncation}f')  
        
        
    