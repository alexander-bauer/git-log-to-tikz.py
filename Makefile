all: history.pdf

.PHONY: tikz-history.tex

tikz-history.tex:
	./git-log-to-tikz.py master > tikz-history.tex

history.pdf: history.tex tikz-history.tex
	pdflatex history.tex
