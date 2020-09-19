

MAT_SCRIPT=scripts/mwc_to_mat.py

brief:
	${MAT_SCRIPT} --head 5 -z -o 0004_20200917_014959_HiResPhase_brief.mat  -vv test_data/0004_20200917_014959_HiResPhase.kmall
	${MAT_SCRIPT} --head 5 -z -o 0006_20200917_015203_LowResPhase_brief.mat -vv test_data/0006_20200917_015203_LowResPhase.kmall


mat:
	${MAT_SCRIPT} -z -o 0004_20200917_014959_HiResPhase.mat  -vv test_data/0004_20200917_014959_HiResPhase.kmall
	${MAT_SCRIPT} -z -o 0006_20200917_015203_LowResPhase.mat -vv test_data/0006_20200917_015203_LowResPhase.kmall


.PHONY: brief process
