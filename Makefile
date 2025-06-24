.PHONY: all clean

all:
	python3 compiler.py
ifndef KEEP_ASM
	rm -f out.o out.asm
else
	rm -f out.o
endif

clean:
	rm -f out.o out.asm out
