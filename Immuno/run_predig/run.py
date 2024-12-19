#!/root/.local/share/mamba/envs/predig_env/bin/python

import os
import argparse
import xgboost as xgb
import pandas as pd
import random
import typing as t

import utils as u


def runPredIG(
    type,
    alleles,
    input_file,
    modelXG,
    output_file=None,
    seed=None,
    alpha=0.5,
    precursor_length=9,
):
    """
    Run the PredIG block
    """

    if output_file is None:
        output_file = input_file + "_output.csv"

    simulation_map = {
        "fasta": 1,
        "uniprot": 2,
        "recombinant": 3,
    }

    simulation = simulation_map[type.lower()]

    if simulation != 1:
        input_text = open(input_file, "r").read()
        # If the file contains tab spaces, save a .csv file
        if "\t" in input_text:
            input_text = input_text.replace("\t", ",")
        elif "," in input_text:
            pass
        else:
            raise ValueError(
                "The input file must contain tab or comma separated values."
            )
        input_file = ".input.csv"
    else:

        if not os.path.exists(alleles):
            raise ValueError(
                "The input HLA alleles file does not exist. Please provide a valid CSV file."
            )

        if alleles.endswith(".csv"):
            df_alleles = pd.read_csv(alleles)

            # Allow the column to be "allele", "alleles", HLA_allele
            df_alleles = df_alleles.rename(
                columns={"allele": "HLA_allele", "alleles": "HLA_allele"}
            )

            if not "HLA_allele" in df_alleles.columns:
                raise ValueError(
                    "The input HLA alleles CSV file must contain a 'HLA_allele' column."
                )

            alleles = "\n".join(df_alleles["HLA_allele"])
        else:
            alleles = open(alleles, "r").read()
            if not alleles or alleles == "":
                raise ValueError(
                    "No HLA alleles were provided. Those are required when running PredIG with fasta files."
                )

        import re

        wrong_alleles = []
        for allele in [a.strip() for a in alleles.split("\n") if a.strip() != ""]:
            match = re.match(r"^HLA-[ABC]\*[0-9]{1,3}:[0-9]{1,3}$", allele)
            if not match:
                wrong_alleles.append(allele)

        if len(wrong_alleles) > 0:

            raise ValueError(
                "Please modify or remove the alleles in your list that are not part of the HLA 4-digits resolution format established by IMGT. e.g HLA-A*02:01 or HLA-A*100:101. Binding predictions within PredIG can not interpret other allelic nomenclatures correctly: \n{}".format(
                    "\n".join(wrong_alleles)
                )
            )
        alleles = "\n".join(
            [allele.strip() for allele in alleles.split("\n") if allele.strip() != ""]
        )

        input_text = open(input_file, "r").read()
        input_file = ".input.fasta"

    # print("====================INPUTS======================")
    # print("Input file: ", input_file)
    # print("Input text: ", input_text)
    # if alleles:
    #     print("HLA alleles: ", alleles)
    print(f"Simulation type: {simulation} ({type})")
    # print("==========================================")

    with open(input_file, "w", encoding="utf-8") as file:
        # Clean the input CSV by removing unnedded quotes "" before writting
        file.write(input_text)

    # Get the seed
    seed = seed or random.randint(0, 10000)

    model = "/Immuno/noah/model.pkl"

    peptide_len = None

    modelXG_name = (modelXG or "neoant").lower()
    if modelXG_name == "noncan":
        modelXG = "/Immuno/predig/models/predig_noncan.model"
    elif modelXG_name == "path":
        modelXG = "/Immuno/predig/models/predig_path.model"
    else:  # "PredIG-NeoA"
        modelXG = "/Immuno/predig/models/predig_neoant.model"

    mat = "/Immuno/netctlpan/tap.logodds.mat"

    # Get the PCH path
    pchPath = "/Immuno/PCH/predig_pch_calc.R"

    # Get the MHCflurry path
    mhcflurryPath = "/root/.local/share/mamba/envs/predig_env/bin/mhcflurry-predict"

    # Get the NetCleave path
    netCleavePath = "/Immuno/NetCleave/NetCleave.py"

    # Get the NOah path
    noahPath = "/Immuno/Neoantigens-NOAH/noah/main_NOAH.py"

    # Get the netCTLpan path
    tapmat_pred_fsa_path = "/Immuno/netctlpan/tapmat_pred_fsa"

    # Check if the input file is valid
    if not os.path.isfile(input_file):
        raise ValueError("The input file is not valid")

    df = None
    fasta = None
    if simulation == 1:
        fasta = input_file.replace('"', "").replace("'", "")
    else:
        df = pd.read_csv(input_file)

        # Replace cells that have "" or ''
        df = df.replace('"', "")
        df = df.replace("'", "")

        # Verify that each row has the correct number of columns (all are filled)
        column_lenght = df.shape[1]

        for i, row in df.iterrows():
            if len(row) != column_lenght:
                raise ValueError(
                    "The input CSV file must contain the same number of columns in each row."
                )

        if df.shape[0] > 5000:
            raise ValueError("The input CSV file must contain less than 5000 rows.")

    print("Running NetCleave")
    # Run the NetCleave / can be placed before to generate csv when case of Fasta
    # When fasta set Hallele in input
    output_netcleave = u.runPredigNetCleave(
        df_csv=df, predigNetcleave_path=netCleavePath, mode=simulation, fasta=fasta
    )

    # If we are runnign with a fasta, concatenate the results of netcleave with HLA alleles
    if simulation == 1:
        df = output_netcleave

        list_alleles = alleles.split("\n")

        # Initialize an empty list to hold DataFrames
        df_list = []

        # Loop through the list of values and create a DataFrame for each one
        for value in list_alleles:
            df_copy = df.copy()
            df_copy["HLA_allele"] = value.strip()
            df_list.append(df_copy)

        df = pd.concat(df_list, ignore_index=True)

        # Remove the index colum (does not have names)
        df = df.reset_index(drop=True)

    else:
        df = t.cast(pd.DataFrame, df)

    # Run the PCH ["epitope"]
    print("Running PCH")
    output_pch = u.runPredigPCH(
        df_csv=df,
        seed=int(seed),
        predigPCH_path=pchPath,
    )

    print("Running MHCflurry")
    # Run the MHCflurry ["epitope", "hla_allele"]
    output_flurry = u.runPredigMHCflurry(
        df_csv=df,
        predigMHCflurry_path=mhcflurryPath,
    )

    print("Running NOAH")

    python_exect = "/root/.local/share/mamba/envs/predig_env/bin/python"
    # Run the NOAH, ["HLA", "epitope", "NOAH_score"] id="HLA", "epitope"
    output_noah = u.runPredigNOAH(
        df_csv=df, predigNOAH_path=noahPath, model=model, python_exec=python_exect
    )

    print("Running tapmat_pred_fsa")
    output_tapmap = u.run_Predig_tapmap(
        df_csv=df,
        tapmap_path=tapmat_pred_fsa_path,
        mat=mat,
        peptide_len=peptide_len,
        alpha=alpha,
        precursor_len=precursor_length,
    )

    print("Joining the outputs")

    # Sequentially merge the DataFrames on a common non-overlapping column, for example 'epitope'
    # df_joined = output_pch.merge(output_flurry, on="epitope", how="inner")
    # df_joined = df_joined.merge(output_netcleave, on="epitope", how="inner")
    # df_joined = df_joined.merge(output_tapmap, on="epitope", how="inner")
    # df_joined = df_joined.merge(output_noah, on="epitope", how="inner")

    df_joined = output_pch.merge(
        output_flurry, left_index=True, right_index=True, how="left"
    )

    if simulation == 1:
        df_joined = df_joined.merge(df, left_index=True, right_index=True, how="left")
    else:
        df_joined = df_joined.merge(
            output_netcleave, left_index=True, right_index=True, how="left"
        )

    df_joined = df_joined.merge(
        output_tapmap,
        left_index=True,
        right_index=True,
        how="left",
        suffixes=("", "_tapmap"),
    )

    df_joined["id"] = df_joined["hla_allele"] + "_" + df_joined["epitope"]
    output_noah["id"] = output_noah["hla_allele"] + "_" + output_noah["epitope"]
    df_joined = df_joined.merge(
        output_noah, on="id", how="left", suffixes=("", "_noah")
    )

    print("Launching the XGBoost model...")
    if "hla_allele_y" in df_joined.columns:
        df_joined = df_joined.drop(columns=["hla_allele_y"])
    if "hla_allele_x" in df_joined.columns:
        df_joined = df_joined.rename(columns={"hla_allele_x": "hla_allele"})

    df_xgboost = df_joined[
        [
            "netcleave",
            "NOAH",
            "mw_peptide",
            "mw_tcr_contact",
            "hydroph_peptide",
            "hydroph_tcr_contact",
            "charge_peptide",
            "charge_tcr_contact",
            "stab_peptide",
            "mhcflurry_affinity",
            "mhcflurry_affinity_percentile",
            "mhcflurry_processing_score",
            "mhcflurry_presentation_score",
        ]
    ]

    # df_xgboost.to_csv("df_xgboost.csv", index=False)
    predig_model = xgb.Booster()
    predig_model.load_model(modelXG)
    predig_input_matrix = xgb.DMatrix(df_xgboost)
    predig_score = predig_model.predict(predig_input_matrix)
    df_joined = pd.concat([df_joined, pd.Series(predig_score, name="predig")], axis=1)

    df_joined["id"] = df_joined["hla_allele"] + "_" + df_joined["epitope"]

    # Rename and sort the columns
    name_mapping = {
        "Id": "ID",
        "Epitope": "epitope",
        "Hla_allele": "HLA_allele",
        "Predig": "PredIG",
        "NOAH": "NOAH",
        "TAP": "TAP",
        "Netcleave": "NetCleave",
        "Mhcflurry_affinity": "mhcflurry_affinity",
        "Mhcflurry_affinity_percentile": "mhcflurry_affinity_percentile",
        "Mhcflurry_presentation_score": "mhcflurry_presentation_score",
        "Mhcflurry_processing_score": "mhcflurry_processing_score",
        "Hydroph_peptide": "Hydrophobicity_peptide",
        "Mw_peptide": "MW_peptide",
        "Charge_peptide": "Charge_peptide",
        "Stab_peptide": "Stab_peptide",
        "Tcr_contact": "TCR_contact",
        "Hydroph_tcr_contact": "Hydrophobicity_tcr_contact",
        "Mw_tcr_contact": "MW_tcr_contact",
        "Charge_tcr_contact": "Charge_tcr_contact",
    }

    name_mapping = {key.lower(): value for key, value in name_mapping.items()}

    df_joined = df_joined.rename(str.lower, axis="columns")

    # Sort based on the mapping
    df_joined = df_joined[name_mapping.keys()]

    # Rename
    df_joined = df_joined.rename(columns=name_mapping)

    # Remove unwanted columns
    columns_to_delete: list[str] = [
        "TAP",
        "mhcflurry_affinity",
        "mhcflurry_affinity_percentile",
        "mhcflurry_processing_score",
        "mhcflurry_presentation_score",
        "epitope_noah",
        "epitope_tapmap",
        "epitope_y",
        "hla_allele_noah",
        "mhcflurry_best_allele",
        "mhcflurry_presentation_percentile",
    ]

    columns_to_delete = [c.lower() for c in columns_to_delete]

    for col in df_joined.columns:
        if col.lower() in columns_to_delete:
            df_joined = df_joined.drop(columns=col)

    # Remove any *_output.csv file to prevent other programs messing the folder
    import glob

    for file in glob.glob("*output*.csv"):
        os.remove(file)

    # Save the results as a CSV
    filename = output_file

    if not filename.endswith(".csv"):
        filename += ".csv"

    df_joined.to_csv(filename, index=False)

    print("PredIG simulations finished")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        help="Path to the input file. Should be a CSV for Uniprot/Recombinant mode or a FASTA for FASTA mode",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="Name of the output file. Defaults to the input file name with '_output.csv'",
    )
    parser.add_argument(
        "--modelXG",
        type=str,
        default="modelXG",
        help="PredIG XGBoost model. Can be noncan, neoant or path",
    )
    parser.add_argument("--alleles", help="Path to the alleles file", default=None)
    parser.add_argument("--alpha", type=int, default=None)
    parser.add_argument("--precursor-length", type=int, default=None)
    parser.add_argument(
        "--type",
        type=str,
        default="uniprot",
        help="Type of input file: uniprot, fasta or recombinant",
    )

    return parser.parse_args()


if __name__ == "__main__":

    # Get arguments
    arguments = parse_args()

    runPredIG(**vars(arguments))
