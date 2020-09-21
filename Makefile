

MAT_SCRIPT=scripts/mwc_to_mat.py

brief:
	#${MAT_SCRIPT} --head 5 -z -o 0004_20200917_014959_HiResPhase_brief.mat  -vv test_data/0004_20200917_014959_HiResPhase.kmall
	#${MAT_SCRIPT} --head 5 -z -o 0006_20200917_015203_LowResPhase_brief.mat -vv test_data/0006_20200917_015203_LowResPhase.kmall

make_subsets:
	scripts/trim_kmall.py -vv --size 10 test_data/0004_20200917_014959_HiResPhase.kmall 0004_20200917_014959_HiResPhase_subset.kmall
	scripts/parse.py -vv 0004_20200917_014959_HiResPhase_subset.kmall
	scripts/trim_kmall.py -vv --size 10 test_data/0006_20200917_015203_LowResPhase.kmall 0006_20200917_015203_LowResPhase_subset.kmall
	scripts/parse.py -vv 0006_20200917_015203_LowResPhase_subset.kmall

parse_subsets:
	scripts/parse.py -vv 0004_20200917_014959_HiResPhase_subset.kmall
	scripts/parse.py -vv 0006_20200917_015203_LowResPhase_subset.kmall

mat:
	#${MAT_SCRIPT} -z -o 0004_20200917_014959_HiResPhase.mat  -vv test_data/0004_20200917_014959_HiResPhase.kmall
	#${MAT_SCRIPT} -z -o 0006_20200917_015203_LowResPhase.mat -vv test_data/0006_20200917_015203_LowResPhase.kmall
	${MAT_SCRIPT} -z -o 0020_20200918_121933.mat -vv test_data/0020_20200918_121933.kmall


.PHONY: brief process trim_testdata
