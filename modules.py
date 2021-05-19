import io
import matplotlib.pyplot as plt
from fastlmm.association import single_snp
from pysnptools.snpreader import Bed, Pheno
import pylab


def run_lmm(geno_file, pheno_file):
    bed_fn = Bed("data/" + geno_file)
    pheno_fn = Pheno("data/" + pheno_file)
    results_df = single_snp(bed_fn, pheno_fn)
    return results_df