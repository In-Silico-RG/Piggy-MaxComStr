#!/usr/bin/env python3

import os
import argparse
import requests
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from rdkit import DataStructs
import multiprocessing as mp
import csv
import time
from tqdm import tqdm
import logging

# === Configurable parameters (CLI will override these) ===
DEFAULT_SMILES_BASE = 'CC(=O)OC1=CC=CC=C1C(=O)O'
DEFAULT_SIMILARITY_THRESHOLD = 0.7
DEFAULT_PAUSE = 0.2
DEFAULT_TIMEOUT = 10
DEFAULT_NBITS = 2048
DEFAULT_RADIUS = 2
DEFAULT_INPUT_FILE = 'compounds.txt'
DEFAULT_OUTPUT_FILE = 'resultados_similares_kegg.csv'
DEFAULT_FAILED_FILE = 'failed_kegg_ids.csv'
DEFAULT_IMAGE_FILE = 'mols_grid.png'

def setup_logger():
    logging.basicConfig(
        filename='smiles_data_miner.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

def read_kegg_ids(filename):
    """Read KEGG compound IDs from a local file."""
    if not os.path.exists(filename):
        logging.error(f"File not found: {filename}")
        return []
    with open(filename, 'r') as f:
        return [line.strip().split('\t')[0] for line in f if line.strip()]

def get_smiles_from_kegg(kegg_id, pause, timeout):
    """Fetch the SMILES string for a given KEGG ID using the KEGG REST API."""
    url = f'https://rest.kegg.jp/get/{kegg_id}/mol'
    try:
        time.sleep(pause)
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        mol = Chem.MolFromMolBlock(response.text)
        if mol:
            return Chem.MolToSmiles(mol)
    except Exception as e:
        logging.warning(f"[{kegg_id}] Error fetching SMILES: {e}")
    return None

def tanimoto_similarity_pair(smiles1, smiles2, nbits, radius):
    """Calculate Tanimoto similarity between two SMILES strings."""
    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)
    if mol1 and mol2:
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, radius=radius, nBits=nbits)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, radius=radius, nBits=nbits)
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    return 0.0

def evaluar_similitud(args):
    """Wrapper for parallel similarity evaluation."""
    kegg_id, smiles_base, threshold, pause, timeout, nbits, radius = args
    if not kegg_id or not isinstance(kegg_id, str):
        return None
    smiles = get_smiles_from_kegg(kegg_id, pause, timeout)
    if smiles:
        sim = tanimoto_similarity_pair(smiles_base, smiles, nbits, radius)
        if sim >= threshold:
            return (kegg_id, smiles, sim)
    return None

def main():
    setup_logger()

    parser = argparse.ArgumentParser(description="KEGG SMILES Similarity Miner")
    parser.add_argument('--smiles_base', default=DEFAULT_SMILES_BASE, help='Reference SMILES string')
    parser.add_argument('--threshold', type=float, default=DEFAULT_SIMILARITY_THRESHOLD, help='Similarity threshold')
    parser.add_argument('--pause', type=float, default=DEFAULT_PAUSE, help='Pause between requests (seconds)')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Request timeout (seconds)')
    parser.add_argument('--nbits', type=int, default=DEFAULT_NBITS, help='Number of fingerprint bits')
    parser.add_argument('--radius', type=int, default=DEFAULT_RADIUS, help='Fingerprint radius')
    parser.add_argument('--input', default=DEFAULT_INPUT_FILE, help='Input KEGG IDs file')
    parser.add_argument('--output', default=DEFAULT_OUTPUT_FILE, help='Output CSV file')
    parser.add_argument('--failed', default=DEFAULT_FAILED_FILE, help='Failed KEGG IDs file')
    parser.add_argument('--img', default=DEFAULT_IMAGE_FILE, help='Output image file')
    parser.add_argument('--processes', type=int, default=mp.cpu_count(), help='Number of parallel processes')
    args = parser.parse_args()

    # Read KEGG IDs
    kegg_ids = read_kegg_ids(args.input)
    if not kegg_ids:
        print("No KEGG IDs found.")
        return

    print(f"Total KEGG compounds to analyze: {len(kegg_ids)}")

    # Prepare pool arguments
    pool_args = [
        (kegg_id, args.smiles_base, args.threshold, args.pause, args.timeout, args.nbits, args.radius)
        for kegg_id in kegg_ids
    ]

    # Parallel processing with progress bar
    print(f"Processing in parallel with {args.processes} processes...")
    resultados = []
    failed_ids = []
    with mp.Pool(args.processes) as pool:
        for res, kegg_id in zip(tqdm(pool.imap_unordered(evaluar_similitud, pool_args), total=len(kegg_ids)), kegg_ids):
            if res is not None:
                resultados.append(res)
            else:
                failed_ids.append(kegg_id)

    # Sort results by similarity descending
    resultados.sort(key=lambda x: x[2], reverse=True)

    # Save results to CSV
    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["KEGG_ID", "SMILES", "Tanimoto_Similarity"])
        writer.writerows(resultados)
    print(f"✅ Total similar compounds found: {len(resultados)}")
    print(f"📁 Results saved to: {args.output}")

    # Save failed IDs
    if failed_ids:
        with open(args.failed, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["KEGG_ID"])
            for fid in failed_ids:
                writer.writerow([fid])
        print(f"⚠️  Failed KEGG IDs saved to: {args.failed}")

    # Show/save molecular images
    if resultados:
        mols = [Chem.MolFromSmiles(r[1]) for r in resultados[:6]]
        img = Draw.MolsToGridImage(mols, molsPerRow=3, subImgSize=(200, 200))
        img.save(args.img)
        print(f"🖼️  Top molecules grid image saved as: {args.img}")

if __name__ == '__main__':
    main()
# Guardar los identificadores en el archivo
with open(ruta_archivo, "w") as file:
    for identificador in sorted(todos_identificadores):
        file.write(identificador + "\n")

print("Identificadores guardados en:", ruta_archivo)
