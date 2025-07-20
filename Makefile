run-demo:
	@if [ ! -d "venv" ]; then
		python -m venv venv;
		source venv/bin/activate;
	fi
	pip install -e .
	python -c "from universalinit.universalinit import main; main()"
	npm --prefix ./output/ start

build-env:
	cd universalinit-env && poetry build

install-env:
	pip install universalinit-env/dist/universalinit_env-*.whl

test-env:
	cd universalinit-env && PYTHONPATH=src pytest ../test/test_envmapper.py -v

clean-env:
	rm -rf universalinit-env/dist/
	rm -rf universalinit-env/build/
	rm -rf universalinit-env/*.egg-info/
