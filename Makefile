all: history.pdf

.PHONY: tikz-history.tex

tikz-history.tex:
	git log --graph --branches --oneline --parents --no-color | ./git-log-to-tikz.py > tikz-history.tex

history.pdf: history.tex tikz-history.tex
	pdflatex history.tex
