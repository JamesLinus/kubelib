init:
	sudo apt-get install build-essential libssl-dev libffi-dev python-dev
	pip install -r requirements.txt

coverage:
	py.test --cov=kubelib tests

test:
	py.test -s tests

docs-init:
	apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra texlive-latex-recommended

	mkdir -p ../kubelib-docs
	cd ../kubelib-docs; git clone git@github.com:safarijv/kubelib.git html
	cd ../kubelib-docs; git checkout -b gh-pages remotes/origin/gh-pages
