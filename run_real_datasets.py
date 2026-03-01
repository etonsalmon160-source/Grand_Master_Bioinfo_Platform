import logging
from custom_geo_parser import fetch_real_geo_matrix_with_genes
from master_bioinfo_suite import MasterBioinfoPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_dataset(gse_id):
    logging.info(f"Starting run for {gse_id}")
    counts, meta = fetch_real_geo_matrix_with_genes(gse_id)
    logging.info(f"Fetched counts: {counts.shape}, meta: {meta.shape}")

    pipeline = MasterBioinfoPipeline(out_dir=f"Run_{gse_id}_Results")
    pipeline.run_pre_processing(custom_counts=counts, custom_meta=meta)
    pipeline.run_dea()
    pipeline.run_wgcna_lite()
    if hasattr(pipeline, 'run_advanced_ml'):
        pipeline.run_advanced_ml()
    else:
        try:
            pipeline.run_ml_biomarkers()
        except Exception:
            logging.warning('No ML entrypoint found, skipping ML step')
    pipeline.run_survival()
    pipeline.run_enrichment()
    pipeline.generate_report()
    logging.info(f"Completed run for {gse_id}. Results saved to {pipeline.out_dir}")

if __name__ == '__main__':
    # Change this list to try other GEO accessions
    datasets = ['GSE31210']
    for ds in datasets:
        try:
            run_dataset(ds)
        except Exception as e:
            logging.exception(f"Failed to process {ds}: {e}")
