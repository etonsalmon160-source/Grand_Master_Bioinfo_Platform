import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests
import os

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']  # For Chinese support if needed
plt.rcParams['axes.unicode_minus'] = False

def generate_mock_data(n_genes=2000, n_samples=6):
    """Generate synthetic RNA-seq count data."""
    print(f"[*] Generating mock data: {n_genes} genes, {n_samples} samples...")
    
    # Random library sizes
    lib_sizes = np.random.randint(5e6, 1e7, n_samples)
    
    # Baseline expression (log-normal)
    baseline = np.random.lognormal(mean=5, sigma=2, size=n_genes)
    
    # Count matrix
    counts = np.zeros((n_genes, n_samples))
    for i in range(n_samples):
        counts[:, i] = np.random.poisson(baseline * (lib_sizes[i] / lib_sizes.mean()))
    
    # Introduce DE genes
    de_indices = np.random.choice(n_genes, 100, replace=False)
    # Strong Up-regulation in Treated (samples 3, 4, 5)
    counts[de_indices[:50], 3:] *= np.random.uniform(5, 10, (50, 3))
    # Strong Down-regulation in Treated
    counts[de_indices[50:], 3:] /= np.random.uniform(5, 10, (50, 3))
    
    # Gene names
    genes = [f"Gene_{i:04d}" for i in range(n_genes)]
    samples = [f"Control_{i+1}" for i in range(3)] + [f"Treated_{i+1}" for i in range(3)]
    
    df = pd.DataFrame(counts.astype(int), index=genes, columns=samples)
    
    # Metadata
    metadata = pd.DataFrame({
        'Sample': samples,
        'Group': ['Control']*3 + ['Treated']*3
    }).set_index('Sample')
    
    return df, metadata

def perform_dea(counts_df, metadata):
    """Perform a simple T-test based DEA on log-CPM data."""
    print("[*] Performing Differential Expression Analysis...")
    
    # 1. Normalization (CPM)
    cpm = (counts_df / counts_df.sum()) * 1e6
    
    # 2. Log transformation (log2(CPM + 1))
    log_cpm = np.log2(cpm + 1)
    
    # 3. Statistical testing
    results = []
    ctrl_cols = metadata[metadata['Group'] == 'Control'].index
    treat_cols = metadata[metadata['Group'] == 'Treated'].index
    
    for gene in log_cpm.index:
        ctrl_vals = log_cpm.loc[gene, ctrl_cols]
        treat_vals = log_cpm.loc[gene, treat_cols]
        
        # Calculate Log2FC
        mean_ctrl = ctrl_vals.mean()
        mean_treat = treat_vals.mean()
        l2fc = mean_treat - mean_ctrl
        
        # T-test
        t_stat, p_val = stats.ttest_ind(ctrl_vals, treat_vals)
        
        results.append({
            'Gene': gene,
            'log2FoldChange': l2fc,
            'pvalue': p_val,
            'mean_ctrl': mean_ctrl,
            'mean_treat': mean_treat
        })
    
    res_df = pd.DataFrame(results).set_index('Gene')
    
    # 4. Multiple testing correction (BH)
    res_df['padj'] = multipletests(res_df['pvalue'], method='fdr_bh')[1]
    
    return res_df, log_cpm

def plot_volcano(res_df):
    """Generate Volcano Plot."""
    print("[*] Generating Volcano Plot...")
    plt.figure(figsize=(10, 8))
    
    # Determine significance
    res_df['Significance'] = 'Not Sig'
    res_df.loc[(res_df['log2FoldChange'] > 1) & (res_df['padj'] < 0.05), 'Significance'] = 'Up-regulated'
    res_df.loc[(res_df['log2FoldChange'] < -1) & (res_df['padj'] < 0.05), 'Significance'] = 'Down-regulated'
    
    colors = {'Up-regulated': 'red', 'Down-regulated': 'blue', 'Not Sig': 'grey'}
    
    sns.scatterplot(
        data=res_df, 
        x='log2FoldChange', 
        y=-np.log10(res_df['pvalue']), 
        hue='Significance', 
        palette=colors,
        alpha=0.6,
        edgecolor=None
    )
    
    plt.axhline(-np.log10(0.05), color='black', linestyle='--', alpha=0.5)
    plt.axvline(1, color='black', linestyle='--', alpha=0.5)
    plt.axvline(-1, color='black', linestyle='--', alpha=0.5)
    
    plt.title('Bulk RNA-seq 差异表达火山图 (Volcano Plot)')
    plt.xlabel('log2(Fold Change)')
    plt.ylabel('-log10(P-value)')
    plt.savefig('volcano_plot.png', dpi=300)
    plt.close()

def plot_heatmap(log_cpm, res_df):
    """Generate Heatmap of top DE genes."""
    print("[*] Generating Heatmap...")
    # Get top 30 significant genes
    significant_res = res_df[res_df['padj'] < 0.05]
    if significant_res.empty:
        print("[!] No significant genes found for heatmap. Selecting top 30 by p-value instead.")
        top_genes = res_df.sort_values('pvalue').head(30).index
    else:
        top_genes = significant_res.sort_values('padj').head(30).index
    
    heatmap_data = log_cpm.loc[top_genes]
    
    # Z-score normalization across rows
    heatmap_data_z = heatmap_data.apply(lambda x: (x - x.mean()) / x.std(), axis=1)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(heatmap_data_z, cmap='RdBu_r', center=0, annot=False)
    plt.title('差异表达基因热图 (Top 30 DE Genes)')
    plt.savefig('heatmap.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    # Create results directory
    if not os.path.exists('analysis_results'):
        os.makedirs('analysis_results')
    os.chdir('analysis_results')
    
    # Run pipeline
    counts, metadata = generate_mock_data()
    counts.to_csv('counts_matrix.csv')
    metadata.to_csv('sample_metadata.csv')
    
    results, log_cpm = perform_dea(counts, metadata)
    results.to_csv('dea_results.csv')
    
    plot_volcano(results)
    plot_heatmap(log_cpm, results)
    
    print("\n[OK] Analysis complete!")
    print(f"[*] Results saved in: {os.getcwd()}")
    print("    - counts_matrix.csv (原始计数矩阵)")
    print("    - dea_results.csv (差异分析结果)")
    print("    - volcano_plot.png (火山图)")
    print("    - heatmap.png (热图)")
