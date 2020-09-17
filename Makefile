

process:
	scripts/parse.py --head 5 -j 0004_20200917_014959_HiResPhase.json  -vv test_data/0004_20200917_014959_HiResPhase.kmall
	scripts/parse.py --head 5 -j 0006_20200917_015203_LowResPhase.json  -vv test_data/0006_20200917_015203_LowResPhase.kmall


.PHONY: process
