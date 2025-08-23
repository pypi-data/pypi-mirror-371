import csv
from collections import defaultdict
import os
import sys
import time
import importlib.util
import subprocess
from Bio import SeqIO

# --- Dependency check and auto-install ---
missing = []
for pkg in ["Bio"]:
    if importlib.util.find_spec(pkg) is None:
        missing.append(pkg)

if missing:
    print("Missing dependencies detected:", ", ".join(missing))
    choice = input("Do you want to install them now? (yes/no): ").strip().lower()
    if choice in ["yes", "y"]:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "biopython"])
            print("Biopython installed successfully.")
        except Exception as e:
            print("Failed to install biopython:", e)
            sys.exit(1)
    else:
        print("Please install manually with: pip install biopython")
        sys.exit(1)

# Kyte-Doolittle hydropathy scale
KD_SCALE = {
    "A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5,
    "Q": -3.5, "E": -3.5, "G": -0.4, "H": -3.2, "I": 4.5,
    "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8, "P": -1.6,
    "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2
}

# Isoelectric points (pI) from provided table
PI_VALUES = {
    "A": 6.00, "R": 10.76, "N": 5.41, "D": 2.77, "C": 5.07,
    "Q": 5.65, "E": 3.22, "G": 5.97, "H": 7.95, "I": 6.02,
    "L": 5.98, "K": 9.74, "M": 5.74, "F": 5.48, "P": 6.30,
    "S": 5.68, "T": 5.60, "W": 5.89, "Y": 5.66, "V": 5.96
}

DNA_CHARS = set("ACGTU-")
PROTEIN_CHARS = set("ACDEFGHIKLMNPQRSTVWY-")

def get_sequence_type():
    stype = input("Are your sequences Protein or DNA/RNA? (protein/dna/rna): ").strip().lower()
    if stype not in ("protein", "dna", "rna"):
        print("Invalid input, defaulting to protein.")
        stype = "protein"
    return stype

def get_input_file():
    path = input("Enter path to alignment file (FASTA or Clustal): ").strip()
    while not os.path.isfile(path):
        print("File not found. Try again.")
        path = input("Enter path to alignment file (FASTA or Clustal): ").strip()
    return path

def detect_format(filename):
    with open(filename) as f:
        first_line = f.readline().strip()
        if first_line.startswith("CLUSTAL"):
            return "clustal"
        else:
            return "fasta"

def read_alignment(filename):
    fmt = detect_format(filename)
    if fmt == "fasta":
        records = list(SeqIO.parse(filename, "fasta"))
    else:
        records = list(SeqIO.parse(filename, "clustal"))
    names = [r.id for r in records]
    seqs = [str(r.seq).upper() for r in records]
    return names, seqs

def validate_seq_type(seq_type, seqs):
    all_chars = set("".join(seqs).replace("-", ""))
    if seq_type in ("dna", "rna") and not all_chars <= DNA_CHARS:
        print(f"Warning: Sequences contain characters not valid for {seq_type.upper()}: {all_chars - DNA_CHARS}")
        ans = input("Do you still want to continue? (yes/no): ").strip().lower()
        if ans not in ("yes", "y"):
            sys.exit("Exiting due to invalid sequence characters.")
    if seq_type == "protein" and not all_chars <= PROTEIN_CHARS:
        print(f"Warning: Sequences contain characters not valid for PROTEIN: {all_chars - PROTEIN_CHARS}")
        ans = input("Do you still want to continue? (yes/no): ").strip().lower()
        if ans not in ("yes", "y"):
            sys.exit("Exiting due to invalid sequence characters.")
    return True

def calculate_hydro_change(a1, a2):
    if a1 in KD_SCALE and a2 in KD_SCALE:
        return KD_SCALE[a2] - KD_SCALE[a1]
    return 0

def calculate_pi_change(a1, a2):
    if a1 in PI_VALUES and a2 in PI_VALUES:
        return PI_VALUES[a2] - PI_VALUES[a1]
    return 0

def compare_alignment(names, seqs, seq_type):
    all_changes = dict()
    hydro_changes = dict()
    pi_changes = dict()
    n = len(names)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            key = (names[i], names[j])
            changes = defaultdict(list)
            hydro = dict()
            pi = dict()
            for idx, (c1, c2) in enumerate(zip(seqs[i], seqs[j]), 1):
                if c1 != c2 and c1 != "-" and c2 != "-":
                    change = f"{c1}>{c2}"
                    changes[change].append(idx)
                    if seq_type == "protein":
                        hydro[change] = calculate_hydro_change(c1, c2)
                        pi[change] = calculate_pi_change(c1, c2)
            all_changes[key] = changes
            if seq_type == "protein":
                hydro_changes[key] = hydro
                pi_changes[key] = pi
    return all_changes, hydro_changes, pi_changes

def save_directional_csv(names, all_changes, hydro_changes=None, pi_changes=None):
    out_file = input("Enter path to save directional list CSV file: ").strip()
    if not out_file.lower().endswith(".csv"):
        out_file += ".csv"
    header = ["From", "To", "Change", "Positions", "Count"]
    if hydro_changes:
        header.append("HydropathyChange")
    if pi_changes:
        header.append("pIChange")

    with open(out_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for p1 in names:
            for p2 in names:
                if p1 == p2:
                    continue
                changes = all_changes.get((p1, p2), {})
                sorted_changes = sorted(changes.items(), key=lambda x: len(x[1]), reverse=True)
                for change, positions in sorted_changes:
                    row = [p1, p2, change, ",".join(map(str, positions)), len(positions)]
                    if hydro_changes:
                        val = hydro_changes.get((p1, p2), {}).get(change, 0)
                        row.append(round(val, 2))
                    if pi_changes:
                        val = pi_changes.get((p1, p2), {}).get(change, 0)
                        row.append(round(val, 2))
                    writer.writerow(row)
    print(f"Directional CSV saved to {out_file}")
    time.sleep(0.5)

def save_substitution_summary_csv(names, all_changes, hydro_changes=None, pi_changes=None):
    out_file = input("Enter path to save substitution count summary CSV file: ").strip()
    if not out_file.lower().endswith(".csv"):
        out_file += ".csv"

    subs_summary = defaultdict(lambda: defaultdict(int))
    total_counts = defaultdict(int)

    for (p1, p2), changes in all_changes.items():
        for change, positions in changes.items():
            subs_summary[change][f"{p1}->{p2}"] = len(positions)
            total_counts[change] += len(positions)

    sorted_changes = sorted(total_counts.items(), key=lambda x: x[1], reverse=True)

    header = ["Change"]
    if hydro_changes:
        header.append("HydropathyChange")
    if pi_changes:
        header.append("pIChange")
    header += [f"{p1}->{p2}" for p1 in names for p2 in names if p1 != p2] + ["Total"]

    rows = []
    for change, total in sorted_changes:
        row = [change]
        if hydro_changes:
            found = False
            for (p1, p2), hydros in hydro_changes.items():
                if change in hydros:
                    row.append(round(hydros[change], 2))
                    found = True
                    break
            if not found:
                row.append(0)
        if pi_changes:
            found = False
            for (p1, p2), pis in pi_changes.items():
                if change in pis:
                    row.append(round(pis[change], 2))
                    found = True
                    break
            if not found:
                row.append(0)
        for p1 in names:
            for p2 in names:
                if p1 == p2:
                    continue
                row.append(subs_summary[change].get(f"{p1}->{p2}", 0))
        row.append(total)
        rows.append(row)

    with open(out_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Substitution summary CSV saved to {out_file}")
    time.sleep(0.5)

def run():
    print("Alignment Substitution Analyzer v0.3")
    time.sleep(1)

    seq_type = get_sequence_type()
    time.sleep(0.5)
    infile = get_input_file()
    time.sleep(0.5)
    names, seqs = read_alignment(infile)

    validate_seq_type(seq_type, seqs)

    print(f"Sequence type confirmed: {seq_type.upper()}")
    time.sleep(0.5)

    all_changes, hydro_changes, pi_changes = compare_alignment(names, seqs, seq_type)

    include_hydro = False
    include_pi = False
    if seq_type == "protein":
        ans = input("Include hydropathy column in CSVs? (yes/no): ").strip().lower()
        if ans in ("yes", "y"):
            include_hydro = True
        ans = input("Include pI column in CSVs? (yes/no): ").strip().lower()
        if ans in ("yes", "y"):
            include_pi = True

    save_directional_csv(
        names, all_changes,
        hydro_changes if include_hydro else None,
        pi_changes if include_pi else None
    )
    save_substitution_summary_csv(
        names, all_changes,
        hydro_changes if include_hydro else None,
        pi_changes if include_pi else None
    )

    print("All tasks completed successfully!")

