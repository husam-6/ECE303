INPUT ?= ./file_test.txt
OUTPUT ?= ./output.txt


test:
	python2 receiver.py > $(OUTPUT) & time python2 sender.py < $(INPUT) &
diff:
	diff $(INPUT) $(OUTPUT)
kill:
	pkill Python
clean:
	rm *.log $(OUTPUT) *.pyc
