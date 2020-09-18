

mat:
	scripts/mwc_to_mat.py --head 5 -z -o 0004_20200917_014959_HiResPhase.mat  -vv test_data/0004_20200917_014959_HiResPhase.kmall
	scripts/mwc_to_mat.py --head 5 -z -o 0006_20200917_015203_LowResPhase.mat -vv test_data/0006_20200917_015203_LowResPhase.kmall

json:
	scripts/parse.py --head 5 -o 0004_20200917_014959_HiResPhase.json  -vv test_data/0004_20200917_014959_HiResPhase.kmall
	scripts/parse.py --head 5 -o 0006_20200917_015203_LowResPhase.json -vv test_data/0006_20200917_015203_LowResPhase.kmall


.PHONY: process
