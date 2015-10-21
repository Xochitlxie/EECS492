

#ifndef state_hpp
#define state_hpp

#include <stdio.h>
#include <opencv2/core/core.hpp>
#include <random>
#include "draw.hpp"

using namespace cv;
using namespace std;

const int MAX_VERTEX = 6;
const int MIN_VERTEX = 3;
const int NUM_OF_POLYGON = 100;

class State{
    

    
public:
    int cols;
    int rows;
    double scores;
    
    const Point * polygons[NUM_OF_POLYGON];
    Point polyArr[NUM_OF_POLYGON][MAX_VERTEX];
    Scalar colors[NUM_OF_POLYGON];
    int vertexCounts[NUM_OF_POLYGON];
    Mat getImage();
        
    State(default_random_engine &randEngine, Mat& source);
    State(State &s1, State &s2, const int C, Mat& source);
    State();
    void calculateScore(Mat & source);
    double scoreOfState(Mat & source);
    
    ~State();
};

#endif /* state_hpp */
