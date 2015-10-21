

#include "draw.hpp" // renderPolyImage(), score()
#include <opencv2/core/core.hpp> // Mat, Point, Scalar
#include <opencv2/highgui/highgui.hpp> // imread(), imwrite(), imshow()
#include <random> //default_random_engine, uniform_int_distribution<>, uniform_real_distribution<>
#include <iostream> // cerr, cout
#include <sstream> // ostringstream
#include <string> // string
#include <fstream>
#include "state.hpp"
#include "matchEngine.hpp"
#include <sys/stat.h>
using namespace cv;
using namespace std;

string imageFileNames[5];
default_random_engine randEngine(1);

int main(int argc, char** argv){
    if(argc < 4){
        cerr << "Usage: ./ga + [N] + [K] + [E]" << endl;
        return 0;
    }
   	
	mkdir("generatedImages/", S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
	fstream pathFinder("imagePaths");

    // Create a random generator, seed it with the value 1
    // Found in the c++ standard library <random>
    default_random_engine randEngine(1);
    
    const int N = atoi(argv[1]);
    const int K = atoi(argv[2]);
    const int E = atoi(argv[3]);
    
    int T = (E - N)/K;

	string fileName;
	
	while(getline(pathFinder, fileName)){
    	MatchEngine m(fileName, N, K);
    	m.iterate(T);
	}
    return 0;
}

