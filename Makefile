all: history.pdf

.PHONY: tikz-history.tex

tikz-history.tex:
	./git-log-to-tikz.py --testfile ./testfile.json master feature1 feature2 > tikz-history.tex

history.pdf: history.tex tikz-history.tex
	pdflatex history.tex
