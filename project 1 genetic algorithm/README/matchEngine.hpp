

#ifndef matchEngine_hpp
#define matchEngine_hpp

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <stdio.h>
#include <algorithm>
#include <iostream>
#include "state.hpp"
#include <sys/stat.h>
//#include "draw.hpp"


using namespace cv;
using namespace std;

class MatchEngine{
    Mat * source;
    vector<State * > states;
    default_random_engine * randEngine;
    
//    int crossOver;
    int numOfChildren;
    int numOfStates;
    string sourcePath;
	double MUTATION_MODIFIER = 1;        // Total probability of mutation
    const double MUTATION_RATE_DETERIATOR = 0.95;
    
    const double VERTEX_NUM_MODIFIER = 0.3;       // Probability of vertex change
    const double VERTEX_MUTATION_MODIFIER = 0.5;    // Probability of vertex Location change
    const double COLOR_MUTATION_MODIFIER = 0.3;      // Probability of color change
    const double ALPHA_MUTATION_MODIFIER = 0.3;    // Probability of transparency change
    const double SWAP_MUTATION_MODIFIER = 0.2;
    const double RANDOM_PLOYGON_MODIFIER = 0.5;
    
    const double NEW_VERTEX_DEVIATION = 0.2;
    
    const double VERTEX_DEVIATION_FACTOR = 0.05;
    const double ALPHA_DEVIATION = 0.1;
    const double COLOR_DEVIATION = 0.1;
    const double VERTEX_LOC_DEVIATION = 0.05;
    
    void generateChild();
    void eliminateStates();
    void mutation();
    
    void vertexNumMutation(State & s);
    void alphaMutation(State & s);
    void colorMutation(State & s);
    void vertexLocMutation(State & s);
    void swapPolygons(State & s);
    void randomPolygon(State & s);
    
    static bool compareScore(const State * s1, const State * s2);
    bool binary(double p, default_random_engine randEngine);
    
public:
    MatchEngine(string sourcePath, int numOfStates, int numOfChildren);
    void iterate(int times);
    Mat finalImage();
};

#endif /* matchEngine_hpp */
