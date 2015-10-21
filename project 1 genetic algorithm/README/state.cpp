

#include "state.hpp"
#include <iostream>

State::State(){
    
}

State::State(default_random_engine &randEngine, Mat& source){
    
    this->cols = source.cols;
    this->rows = source.rows;
    // Create two uniform distributions, one for randomly generating
    uniform_int_distribution<int> xValGen(0, cols-1);
    uniform_int_distribution<int> yValGen(0, rows-1);
    
    // Create distributions for generating color and opacity values
    uniform_int_distribution<int> BGRgen(0,255);
    uniform_real_distribution<double> alphaGen(0,1);

   // Point polyArr[NUM_OF_POLYGON][MAX_VERTEX];

    for (int i = 0; i < NUM_OF_POLYGON; i++) {
        vertexCounts[i] = MIN_VERTEX;
        
        for (int j = 0; j < vertexCounts[i]; j++) {
            //Initialize each point randomly
            polyArr[i][j].x = xValGen(randEngine);
            polyArr[i][j].y = yValGen(randEngine);
        }
        
        colors[i] = Scalar(BGRgen(randEngine), BGRgen(randEngine),
                           BGRgen(randEngine), alphaGen(randEngine));
    }
    
    for (int i = 0; i < NUM_OF_POLYGON; i++) {
        // Initialize each pointer to point to a polygon
        polygons[i] = &polyArr[i][0];
    }

    calculateScore(source);
}

State::State(State &s1, State &s2, const int C, Mat & source){
    cols = s1.cols;
    rows = s1.rows;
    
    
    for(int i = 0; i < C; ++i){
        vertexCounts[i] = s1.vertexCounts[i];
        for(int j = 0; j < vertexCounts[i]; j++){
            polyArr[i][j].x = s1.polyArr[i][j].x;
            polyArr[i][j].y = s1.polyArr[i][j].y;
        }
        
        colors[i].val[0] = s1.colors[i].val[0];
        colors[i].val[1] = s1.colors[i].val[1];
        colors[i].val[2] = s1.colors[i].val[2];
        colors[i].val[3] = s1.colors[i].val[3];
    }
    
    for(int i = C; i < NUM_OF_POLYGON; ++i){
        vertexCounts[i] = s2.vertexCounts[i];
        for(int j = 0; j < vertexCounts[i]; j++){
            polyArr[i][j].x = s2.polyArr[i][j].x;
            polyArr[i][j].y = s2.polyArr[i][j].y;
        }
        
        colors[i].val[0] = s2.colors[i].val[0];
        colors[i].val[1] = s2.colors[i].val[1];
        colors[i].val[2] = s2.colors[i].val[2];
        colors[i].val[3] = s2.colors[i].val[3];
    }
    
    for (int i = 0; i < NUM_OF_POLYGON; i++) {
        // Initialize each pointer to point to a polygon
        polygons[i] = &polyArr[i][0];
    }
    
    calculateScore(source);
}

void State::calculateScore(cv::Mat &source){
    Mat newMat = renderPolyImage(rows,
                                 cols,
                                 NUM_OF_POLYGON,
                                 polygons,
                                 vertexCounts,
                                 colors
                                 );
    double s = score(source, newMat);
    this->scores = s;
}

Mat State::getImage(){
    return renderPolyImage(rows,
                           cols,
                           NUM_OF_POLYGON,
                           polygons,
                           vertexCounts,
                           colors
                           );
}

double State::scoreOfState(Mat & source){
    Mat newMat = renderPolyImage(rows,
                                 cols,
                                 NUM_OF_POLYGON,
                                 polygons,
                                 vertexCounts,
                                 colors
                                 );
    double s = score(source, newMat);
    return s;
}

State::~State(){
}