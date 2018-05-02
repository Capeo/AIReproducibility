import main
from main_gendata import mat_path_coil20 as mcoil20
from main_gendata import mat_path_g50c as mg50c
from main_gendata import mat_path_uspst as muspst

# purely for convenience of running all models with the same pregenerated
# folds as in the reproduction attempt
if __name__ == '__main__':
    path_coil20 = "idx_datasets/pregen/coil20.json"
    path_coil20b = "idx_datasets/pregen/coil20b.json"
    path_g50c = "idx_datasets/pregen/g50c.json"
    path_uspst = "idx_datasets/pregen/uspst.json"
    path_uspstb = "idx_datasets/pregen/uspstb.json"

    main.main_SS("coil20",  main.coil20,  path_coil20,  mcoil20, True, False, offset=0)
    main.main_SS("coil20b", main.coil20b, path_coil20b, mcoil20, True, True,  offset=1)
    main.main_SS("g50c",    main.g50c,    path_g50c,    mg50c,   True, False, offset=2)
    main.main_SS("uspst",   main.uspst,   path_uspst,   muspst,  True, False, offset=3)
    main.main_SS("uspstb",  main.uspstb,  path_uspstb,  muspst,  True, True,  offset=4)