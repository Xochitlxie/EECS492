all: draw.hpp matchEngine.hpp state.hpp
	g++ -std=c++11 `pkg-config --cflags opencv` -o generate draw.cpp main.cpp matchEngine.cpp state.cpp `pkg-config --libs opencv`

clean:
	rm generate
	rm -r generatedImages
