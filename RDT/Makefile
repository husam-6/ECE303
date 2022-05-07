INPUT ?= ./biggest.txt
OUTPUT ?= ./output.txt


test: 
	python2 receiver.py > $(OUTPUT) & time python2 sender.py < $(INPUT) &
diff:
	diff $(INPUT) $(OUTPUT)
kill:
	pkill -i python
clean:
	rm *.log $(OUTPUT) *.pyc
