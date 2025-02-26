run-demo:
	@if [ ! -d "venv" ]; then
		python -m venv venv;
		source venv/bin/activate;
	fi
	pip install -e .
	python -c "from universalinit.universalinit import main; main()"
	npm --prefix ./output/ start
