from emv_tools.ffi.scipion import xmipp_pdb_label_from_volume


def main():
    
    exit_code = xmipp_pdb_label_from_volume(
        "/dev/null/deepres/atom.pub",
        pdb="pdb_path",
        volume="volume_path",
        mask="mask_path",
        sampling="sampling_path",
        origin="origin"
    )

#     # subprocess.run(["scipion", "run", "xmipp_pdb_label_from_volume"])

#     # os.system(
#     #     'scipion3'
#     # )

if __name__ == "__main__":
    main()