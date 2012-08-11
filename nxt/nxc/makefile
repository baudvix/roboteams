CC=nbc
NXCFLAGS=-T=NXT
SOURCES=explorer.nxc
OBJECTS=$(SOURCES:.nxc=.nbc) 
EXECUTABLE=explorer.rxe

all: $(SOURCES) $(EXECUTABLE) semiclean
	
$(EXECUTABLE): $(LIBNBC) $(OBJECTS) 
	$(CC) $(NXCFLAGS) $(OBJECTS) -O=$@

%.nbc: %.nxc
	$(CC) $(NXCFLAGS) $< -asm=$@

bricks: 
	echo "NXT 1: 00165310494D - NXT 2: 0016531048E7 - NXT 3: 0016531048F3"

download1: all
	$(CC) -b -S=USB0::0X0694::0X0002::00165310494D::RAW -d $(EXECUTABLE)	
download2: all
	$(CC) -b -S=USB0::0X0694::0X0002::0016531048E7::RAW -d $(EXECUTABLE)
download3: all
	$(CC) -b -S=USB0::0X0694::0X0002::0016531048F3::RAW -d $(EXECUTABLE)

semiclean:
	rm -f *.nbc

clean:
	rm -f *.nbc
	rm -f *.rxe

# $@ Regel
# $< erste Abhaengigkeit
# $^ alle Abhaengigkeiten
