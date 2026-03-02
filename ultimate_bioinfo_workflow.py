import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc
from lifelines import KaplanMeierFitter, CoxPHFitter
import gseapy as gp
import os
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# Elite Bioinfo Style Config (Elite Aesthetics)
# ==========================================
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Liberation Sans', 'DejaVu Sans'],
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.labelweight': 'bold',
    'axes.titleweight': 'bold',
    'figure.titlesize': 16,
    'figure.titleweight': 'bold',
    'lines.linewidth': 2,
    'axes.spines.top': False,
    'axes.spines.right': False
})

# Nature / Lancet / JCO Color Palettes
COLOR_PALETTE = ["#E64B35", "#4DBBD5", "#00A087", "#3C8DBC", "#F39B7F", "#8491B4"]

class EliteBioinfoPipeline:
    def __init__(self, out_dir="Ultimate_Results"):
        self.out_dir = out_dir
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        os.chdir(out_dir)
        print(f"[*] Elite Pipeline Initialized. Output: {os.getcwd()}")

    def step1_data_simulation(self, n_genes=5000, n_samples=60):
        print("[Step 1] Generating Multi-Omics Grade Dataset...")
        samples = [f"Ctrl_{i+1:02d}" for i in range(n_samples//2)] + [f"Tumor_{i+1:02d}" for i in range(n_samples//2)]
        genes = [f"Gene_{i:04d}" for i in range(n_genes)]
        
        # Base expression
        data = np.random.lognormal(mean=3, sigma=1.2, size=(n_genes, n_samples))
        
        # Inject Biological Signals
        diff_indices = np.random.choice(n_genes, 200, replace=False)
        # Tumor Overexpression
        data[diff_indices[:120], n_samples//2:] *= np.random.uniform(2, 8, (120, n_samples//2))
        # Tumor Underexpression
        data[diff_indices[120:], n_samples//2:] /= np.random.uniform(2, 8, (80, n_samples//2))
        
        self.counts = pd.DataFrame(data, index=genes, columns=samples)
        self.metadata = pd.DataFrame({
            'Group': ['Healthy']*(n_samples//2) + ['Cancer']*(n_samples//2),
            'Survival_Days': np.random.exponential(120, n_samples) / (data[diff_indices[0], :] / data[diff_indices[0], :].mean()),
            'Status': np.random.binomial(1, 0.75, n_samples)
        }, index=samples)
        
        # Normalize: log2(CPM+1)
        self.log_cpm = np.log2((self.counts / self.counts.sum() * 1e6) + 1)
        return self.log_cpm

    def step2_dimensionality_reduction(self):
        print("[Step 2] Executing PCA & Group Clustering Analysis...")
        X = self.log_cpm.T
        pca = PCA(n_components=2)
        pcs = pca.fit_transform(X)
        pc_df = pd.DataFrame(pcs, columns=['PC1', 'PC2'], index=X.index)
        pc_df['Group'] = self.metadata['Group']
        
        plt.figure(figsize=(7, 6))
        sns.scatterplot(data=pc_df, x='PC1', y='PC2', hue='Group', palette=COLOR_PALETTE[:2], s=100, alpha=0.9, edgecolor='w')
        
        # Add Confidence Ellipses (Elite feature)
        from matplotlib.patches import Ellipse
        for group in pc_df['Group'].unique():
            subset = pc_df[pc_df['Group'] == group]
            cov = np.cov(subset[['PC1', 'PC2']].T)
            lambda_, v = np.linalg.eig(cov)
            lambda_ = np.sqrt(lambda_)
            ell = Ellipse(xy=(subset['PC1'].mean(), subset['PC2'].mean()),
                          width=lambda_[0]*4, height=lambda_[1]*4,
                          angle=np.rad2deg(np.arccos(v[0, 0])),
                          color=COLOR_PALETTE[0] if group=='Cancer' else COLOR_PALETTE[1], alpha=0.1)
            plt.gca().add_artist(ell)
            
        plt.title(f'PCA: Biological Variance (Explained: {pca.explained_variance_ratio_.sum()*100:.1f}%)')
        plt.savefig('Fig1_PCA_Clustering.png')
        plt.close()

    def step3_differential_expression(self):
        print("[Step 3] Robust DE Discovery (T-test + BH Fix)...")
        cancer_idx = self.metadata[self.metadata['Group']=='Cancer'].index
        healthy_idx = self.metadata[self.metadata['Group']=='Healthy'].index
        
        results = []
        for g in self.log_cpm.index:
            t, p = stats.ttest_ind(self.log_cpm.loc[g, cancer_idx], self.log_cpm.loc[g, healthy_idx])
            l2fc = self.log_cpm.loc[g, cancer_idx].mean() - self.log_cpm.loc[g, healthy_idx].mean()
            results.append({'Gene': g, 'log2FC': l2fc, 'pvalue': p})
            
        self.res_df = pd.DataFrame(results).set_index('Gene')
        self.res_df['padj'] = multipletests(self.res_df['pvalue'], method='fdr_bh')[1]
        
        # Plot Elite Volcano
        plt.figure(figsize=(8, 7))
        self.res_df['Status'] = 'Normal'
        self.res_df.loc[(self.res_df['log2FC'] > 1.5) & (self.res_df['padj'] < 0.01), 'Status'] = 'Up'
        self.res_df.loc[(self.res_df['log2FC'] < -1.5) & (self.res_df['padj'] < 0.01), 'Status'] = 'Down'
        
        sns.scatterplot(data=self.res_df, x='log2FC', y=-np.log10(self.res_df['padj']), 
                        hue='Status', palette={'Up': COLOR_PALETTE[0], 'Down': COLOR_PALETTE[1], 'Normal': '#DDDDDD'},
                        alpha=0.6, s=25, edgecolor=None)
        
        plt.axhline(-np.log10(0.01), color='black', ls='--', lw=0.8)
        plt.title('DE Status Overview')
        plt.savefig('Fig2_Elite_Volcano.png')
        plt.close()
        return self.res_df

    def step4_pathway_enrichment(self):
        print("[Step 4] Simulated GSEA & Pathway Enrichment Analysis...")
        # Since running full GSEA requires external databases, we'll mock the top pathways 
        # normally found in such cancers to show visual capability.
        pathways = ['Cell Cycle', 'DNA Repair', 'Hypoxia', 'PI3K Signaling', 'Apoptosis', 'Glycolysis']
        p_vals = np.sort(np.random.uniform(1e-10, 1e-2, len(pathways)))
        rich_factor = np.random.uniform(0.5, 0.9, len(pathways))
        
        enrich_df = pd.DataFrame({'Pathway': pathways, 'P-value': p_vals, 'Enrichment_Score': rich_factor})
        
        plt.figure(figsize=(8, 5))
        sns.barplot(data=enrich_df, x='Enrichment_Score', y='Pathway', palette='viridis')
        plt.title('Top Enriched Pathways (GSEA Style)')
        plt.xlabel('Normalized Enrichment Score (NES)')
        plt.savefig('Fig3_Pathway_Enrichment.png')
        plt.close()

    def step5_predictive_modeling(self):
        print("[Step 5] Machine Learning (Random Forest) Biomarker Selection...")
        X = self.log_cpm.T
        y = (self.metadata['Group'] == 'Cancer').astype(int)
        
        rf = RandomForestClassifier(n_estimators=100, oob_score=True, random_state=42)
        rf.fit(X, y)
        
        importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(20)
        
        plt.figure(figsize=(7, 8))
        importances.sort_values().plot(kind='barh', color=COLOR_PALETTE[3], edgecolor='black')
        plt.title('Machine Learning Feature Importance')
        plt.xlabel('Importance Score')
        plt.savefig('Fig4_ML_Features.png')
        plt.close()
        self.top_gene = importances.index[0]
        return importances

    def step6_prognostic_validation(self):
        print(f"[Step 6] Clinical Survival Analysis for Top Biomarker: {self.top_gene}")
        clinical = self.metadata.copy()
        clinical['Level'] = ['High' if x > self.log_cpm.loc[self.top_gene].median() else 'Low' for x in self.log_cpm.loc[self.top_gene]]
        
        kmf = KaplanMeierFitter()
        plt.figure(figsize=(7, 6))
        for group, color in zip(['High', 'Low'], [COLOR_PALETTE[0], COLOR_PALETTE[1]]):
            mask = (clinical['Level'] == group)
            kmf.fit(clinical.loc[mask, 'Survival_Days'], clinical.loc[mask, 'Status'], label=f'{group} Exp')
            kmf.plot_survival_function(color=color, lw=3)
            
        plt.title(f'Survival Validation: {self.top_gene}')
        plt.ylabel('Survival Probability')
        plt.xlabel('Time (Days)')
        plt.savefig('Fig5_Survival_Final.png')
        plt.close()

if __name__ == "__main__":
    pipeline = EliteBioinfoPipeline()
    
    # Run the Full Circle
    pipeline.step1_data_simulation()
    pipeline.step2_dimensionality_reduction()
    pipeline.step3_differential_expression()
    pipeline.step4_pathway_enrichment()
    pipeline.step5_predictive_modeling()
    pipeline.step6_prognostic_validation()
    
    print("\n" + "*"*20)
    print("[SUCCESS] Top-tier Bioinformatics Workflow Completed!")
    print(f"[*] All high-res figures saved in: {os.getcwd()}")
    print("    - Fig1: PCA Clustering with Confidence Ellipses")
    print("    - Fig2: Differential Expression Volcano Plot")
    print("    - Fig3: GSEA Style Pathway Enrichment")
    print("    - Fig4: ML Feature Importance")
    print("    - Fig5: Clinical Survival Validation")
    print("*"*20)
