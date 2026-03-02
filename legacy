import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
from lifelines import KaplanMeierFitter, CoxPHFitter
import os

# ==========================================
# 🚨 PUBLICATION STYLE CONFIGURATION (Nature/Science)
# ==========================================
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'axes.linewidth': 1.2,
    'savefig.transparent': False,
    'savefig.bbox': 'tight'
})

# Nature Publishing Group Color Palette
NPG_COLORS = ["#E64B35", "#4DBBD5", "#00A087", "#3C8DBC", "#F39B7F", "#8491B4", "#91D1C2", "#DC0000"]

def generate_full_dataset(n_genes=3000, n_samples=40):
    """Generate large-scale dataset for ML and Survival Analysis."""
    print(f"[*] Simulating clinical dataset: {n_genes} genes, {n_samples} samples...")
    
    # 1. Expression counts
    samples = [f"Sample_{i:02d}" for i in range(n_samples)]
    genes = [f"Gene_{i:04d}" for i in range(n_genes)]
    
    data = np.random.lognormal(mean=4, sigma=1.5, size=(n_genes, n_samples))
    
    # 2. Clinical Metadata
    # Group: 20 Healthy, 20 Disease
    groups = ['Healthy']*20 + ['Cancer']*20
    
    # Introduce real biomarkers (top 50 genes)
    biomarker_indices = range(50)
    # Cancer samples have higher expression in these 50 genes
    data[biomarker_indices, 20:] *= np.random.uniform(2.5, 6, (50, 20))
    
    # 3. Survival Simulation
    # Assume high expression of Gene_0000 correlates with poor survival
    survival_time = np.random.exponential(100, n_samples)
    hazard_ratio = (data[0, :] / data[0, :].mean())
    survival_time = survival_time / hazard_ratio  # Higher Gene_0000 -> Faster event time
    
    # Event: 1 for death/event, 0 for censored
    status = np.random.binomial(1, 0.8, n_samples)
    
    counts_df = pd.DataFrame(data, index=genes, columns=samples)
    
    clinical_df = pd.DataFrame({
        'Sample': samples,
        'Group': groups,
        'Survival_Time': survival_time,
        'Status': status
    }).set_index('Sample')
    
    return counts_df, clinical_df

def plot_volcano_pro(res_df):
    """Enhanced Volcano plot with journal aesthetics."""
    print("[*] Plotting Professional Volcano plot...")
    plt.figure(figsize=(7, 6))
    
    res_df['Significance'] = 'NS'
    res_df.loc[(res_df['log2FC'] > 1) & (res_df['padj'] < 0.05), 'Significance'] = 'Up'
    res_df.loc[(res_df['log2FC'] < -1) & (res_df['padj'] < 0.05), 'Significance'] = 'Down'
    
    sns.scatterplot(
        data=res_df, x='log2FC', y=-np.log10(res_df['pvalue']),
        hue='Significance', hue_order=['Down', 'NS', 'Up'],
        palette={'Up': '#E64B35', 'Down': '#4DBBD5', 'NS': '#999999'},
        s=40, alpha=0.7, edgecolor='none'
    )
    
    plt.axvline(1, color='gray', linestyle='--', linewidth=0.8)
    plt.axvline(-1, color='gray', linestyle='--', linewidth=0.8)
    plt.axhline(-np.log10(0.05), color='gray', linestyle='--', linewidth=0.8)
    
    plt.title('Differential Expression Profile', fontweight='bold')
    plt.xlabel('log2(Fold Change)')
    plt.ylabel('-log10(adj P-value)')
    plt.legend(frameon=False, loc='upper right')
    plt.savefig('Fig1_Volcano_Journal.png')
    plt.close()

def run_ml_biomarkers(counts_df, clinical_df):
    """Integrate Machine Learning for Feature Selection."""
    print("[*] Running Machine Learning (Random Forest)...")
    
    # Transpose for ML (Samples as rows)
    X = counts_df.T
    y = (clinical_df['Group'] == 'Cancer').astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    # Feature Importance
    importances = pd.Series(rf.feature_importances_, index=counts_df.index).sort_values(ascending=False)
    
    # ROC Plot
    y_score = rf.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_score)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color='#E64B35', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Biomarker Prediction Performance (ROC)')
    plt.legend(loc="lower right", frameon=False)
    plt.savefig('Fig2_ROC_ML.png')
    plt.close()
    
    return importances.head(10)

def run_survival_analysis(counts_df, clinical_df, target_gene):
    """Perform KM Survival Analysis and Cox Regression."""
    print(f"[*] Running Survival Analysis for {target_gene}...")
    
    # Split samples into High/Low group based on median
    median_exp = counts_df.loc[target_gene].median()
    clinical_df['Exp_Level'] = ['High' if x > median_exp else 'Low' for x in counts_df.loc[target_gene]]
    
    kmf = KaplanMeierFitter()
    plt.figure(figsize=(7, 6))
    
    for group in ['High', 'Low']:
        mask = (clinical_df['Exp_Level'] == group)
        kmf.fit(clinical_df.loc[mask, 'Survival_Time'], 
                clinical_df.loc[mask, 'Status'], 
                label=f'{target_gene} {group}')
        kmf.plot_survival_function(color='#E64B35' if group == 'High' else '#4DBBD5', lw=2)
    
    plt.title(f'Kaplan-Meier Survival Analysis ({target_gene})', fontweight='bold')
    plt.xlabel('Days Post-Diagnosis')
    plt.ylabel('Survival Probability')
    plt.grid(False)
    plt.savefig('Fig3_KM_Survival.png')
    plt.close()
    
    # Cox Proportional Hazards
    cph_data = clinical_df[['Survival_Time', 'Status']].copy()
    cph_data['Gene_Exp'] = counts_df.loc[target_gene]
    
    cph = CoxPHFitter()
    cph.fit(cph_data, duration_col='Survival_Time', event_col='Status')
    print(f"Cox Model Result for {target_gene}:")
    print(cph.summary[['coef', 'exp(coef)', 'p']])

if __name__ == "__main__":
    out_dir = 'Pro_Bioinfo_Results'
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    os.chdir(out_dir)
    
    # 1. DATA GENERATION
    counts, clinical = generate_full_dataset()
    
    # 2. DE ANALYSIS (Simple version for pro plots)
    log_cpm = np.log2((counts / counts.sum() * 1e6) + 1)
    results = []
    cancer_idx = clinical[clinical['Group']=='Cancer'].index
    healthy_idx = clinical[clinical['Group']=='Healthy'].index
    
    for g in log_cpm.index:
        t, p = stats.ttest_ind(log_cpm.loc[g, cancer_idx],
                               log_cpm.loc[g, healthy_idx])
        l2fc = log_cpm.loc[g, cancer_idx].mean() - log_cpm.loc[g, healthy_idx].mean()
        results.append({'Gene': g, 'log2FC': l2fc, 'pvalue': p})
    
    res_df = pd.DataFrame(results).set_index('Gene')
    res_df['padj'] = multipletests(res_df['pvalue'], method='fdr_bh')[1]
    
    # 3. JOURNAL PLOTS
    plot_volcano_pro(res_df)
    
    # 4. MACHINE LEARNING
    top_features = run_ml_biomarkers(counts, clinical)
    print("\n[ML] Top 10 Biomarkers Identified:")
    print(top_features)
    
    # 5. SURVIVAL ANALYSIS
    run_survival_analysis(counts, clinical, target_gene=top_features.index[0])
    
    print("\n" + "="*40)
    print("[OK] 全能生信自动化平台分析完成!")
    print(f"[*] 结果已输出至: {os.getcwd()}")
    print("    - Fig1_Volcano_Journal.png (顶刊审美差异火山图)")
    print("    - Fig2_ROC_ML.png (机器学习分类效能图)")
    print("    - Fig3_KM_Survival.png (Kaplan-Meier 生存曲线)")
    print("="*40)
