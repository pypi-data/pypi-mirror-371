# DON'T run this as root

# If you are in a virtual environment, then it will probably
# install into;
#	 <virtual-path>/cli_logging/lib/python3.X/site-packages/cli_logging
# Otherwise it will probably end up in:
#	<your-HOME>/.local/lib/python3.X/site-packages/cli_logging
# and assume you meant the --user option since you are a normal user and
#  don't have write perms into the system site-packages

help:
	@echo use "'make install'" to install package
	@echo use "'make test'" to run tests
	@echo use "'make build-dist'" to build package from source
	@echo use "'make uninstall'" to uninstall package

install:
	@if [ `whoami` = 'root' ]; then \
		echo "DON'T run this as root!" ; \
	else \
		python3 -m pip install . ; \
	fi

# When developing and debugging, use -e/--editable option to pip for install
install-dev:
	@if [ `whoami` = 'root' ]; then \
		echo "DON'T run this as root!" ; \
	else \
		python3 -m pip install --editable . ; \
	fi

build-dist:
	python3 -m pip install --upgrade build
	python3 -m build

test:
	python3 testing/test.py --debug

clean:
	rm -f cli_logging.pyc

uninstall:
	python3 -m pip uninstall cli_logging
