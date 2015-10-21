

#include "matchEngine.hpp"

MatchEngine::MatchEngine(string sourcePath, int numOfStates, int numOfChildren){
    this->numOfChildren = numOfChildren;
    this->numOfStates = numOfStates;
   	this->sourcePath = sourcePath; 
    randEngine = new default_random_engine(1);
    source = new Mat(imread(sourcePath));
    for(int i = 0; i < numOfStates; ++i){
        states.push_back(new State(*randEngine, *source));
    }
}

void MatchEngine::iterate(int times){

	cout << "Generating images for " << sourcePath << endl;
	cout << "Going to generate " << times << " generations. " << endl; 
	cout << "Scores : ( print every 1000 / K attemps) "<< endl;
    
    string imageDirPath = "generatedImages/" + sourcePath.substr(0, sourcePath.size() - 4);
	mkdir(imageDirPath.c_str(), S_IRWXU | S_IRWXG | S_IROTH);
	for(int i = 0; i < times; ++i){
        generateChild();
        mutation();
        eliminateStates();
        if(i % (1000/numOfChildren) == 0){
            std::cout<< states[0]->scores<< ", ";
			cout.flush();
            ostringstream fileOut;
            fileOut << "generatedImages/" << sourcePath.substr(0, sourcePath.size() - 4) << "/PolyImage_" << states[0]->scores << ".jpg";
            string filename = fileOut.str();
            
            // Use the OpenCV imwrite function to write the generated image to a file
            imwrite(filename, states[0]->getImage()); //Extension determines write format
        }
        if(i % 10000 == 0 && i != 0)
            MUTATION_MODIFIER = MUTATION_RATE_DETERIATOR * MUTATION_MODIFIER;
    }
    
    std::cout<< endl <<"----------------------" << "Best Score: " << states[0]->scores <<endl << endl;;
}

void MatchEngine::generateChild(){
    double scoreSum = 0;
    for(int i = 0; i < states.size(); ++i){
        scoreSum += states[i]->scores;
    }
    uniform_real_distribution<double> distribution(0, scoreSum);
    uniform_int_distribution<int> crossover(0, NUM_OF_POLYGON);

    for(int k = 0; k < numOfChildren; ++k){
        int s1 = -1, s2 = -1;
        double rand1 = distribution(*randEngine);
        double rand2 = distribution(*randEngine);

        for(size_t i = 0; i < numOfStates; ++i){
            if(rand1 < states[i]->scores){
                s1 = (int)i;
                break;
            }
            else
                rand1 -= states[i]->scores;
        }
        
        for(size_t i = 0; i < numOfStates; ++i){
            if(rand2 < states[i]->scores){
                s2 = (int)i;
                break;
            }
            else
                rand2 -= states[i]->scores ;
        }
        
      
        states.push_back(new State(*states[s1], *states[s2], crossover(*randEngine), *source));

    }
}

void MatchEngine::eliminateStates(){
    std::sort(states.begin(), states.end(), MatchEngine::compareScore);
    for(int i = numOfStates; i < states.size(); ++i){
        delete states[i];
    }
    states.resize(numOfStates);
}

bool MatchEngine::compareScore(const State * s1, const State * s2){
    return s1->scores > s2->scores;
}

void MatchEngine::mutation(){
    for(int index = numOfStates; index < states.size(); index ++){
        
        double dice =   VERTEX_NUM_MODIFIER +
                        VERTEX_MUTATION_MODIFIER +
                        COLOR_MUTATION_MODIFIER +
                        ALPHA_MUTATION_MODIFIER +
                        SWAP_MUTATION_MODIFIER +
                        RANDOM_PLOYGON_MODIFIER;
        uniform_real_distribution<double> diceDis(0, dice);
        double num = diceDis(*randEngine);
        if(num < VERTEX_NUM_MODIFIER){
            vertexNumMutation(*states[index]);
        }else if(num < VERTEX_NUM_MODIFIER + ALPHA_MUTATION_MODIFIER){
            alphaMutation(*states[index]);
        }
        else if(num < VERTEX_NUM_MODIFIER + ALPHA_MUTATION_MODIFIER + COLOR_MUTATION_MODIFIER){
            colorMutation(*states[index]);
        }
        else if(num < VERTEX_NUM_MODIFIER + ALPHA_MUTATION_MODIFIER + COLOR_MUTATION_MODIFIER
                + VERTEX_MUTATION_MODIFIER){
            vertexLocMutation(*states[index]);
        }
        else if(num < VERTEX_NUM_MODIFIER + ALPHA_MUTATION_MODIFIER + COLOR_MUTATION_MODIFIER
                + VERTEX_MUTATION_MODIFIER + SWAP_MUTATION_MODIFIER){
            swapPolygons(*states[index]);
        }
        else{
            randomPolygon(*states[index]);
        }
        
    }
    
    for(int index = numOfStates; index < states.size(); index ++)
        states[index]->calculateScore(*source);
}

void MatchEngine::vertexNumMutation(State & s){
    uniform_int_distribution<int> distribution(0, NUM_OF_POLYGON-1);
    int index = distribution(*randEngine);
    
    if(s.vertexCounts[index] == MIN_VERTEX || (binary(0.5, *randEngine) && s.vertexCounts[index] < MAX_VERTEX)){
        double xMean = 0, yMean = 0;
        int vertex1 = rand() % (s.vertexCounts[index] - 1);
        int vertex2 = rand() % (s.vertexCounts[index] - 1);
        
        xMean += (double)s.polyArr[index][vertex1].x / 2;
        xMean += (double)s.polyArr[index][vertex2].x / 2;
        yMean += (double)s.polyArr[index][vertex1].y / 2;
        yMean += (double)s.polyArr[index][vertex2].y / 2;
        
        normal_distribution<double> xValGen(xMean, source->cols * VERTEX_DEVIATION_FACTOR * MUTATION_MODIFIER);
        normal_distribution<double> yValGen(yMean, source->rows * VERTEX_DEVIATION_FACTOR * MUTATION_MODIFIER);

        s.polyArr[index][s.vertexCounts[index]].x = max(min((int)xValGen(*randEngine), source->cols), 0);
        s.polyArr[index][s.vertexCounts[index]].y = max(min((int)yValGen(*randEngine), source->rows), 0);
        s.vertexCounts[index]++;
    }
    else if(s.vertexCounts[index] > MIN_VERTEX){
        // Randomly delete a vertex
        int vertexDeleted = rand() % (s.vertexCounts[index] - 1);
        s.polyArr[index][vertexDeleted] = s.polyArr[index][s.vertexCounts[index] - 1];
        s.vertexCounts[index]--;
    }
}

void MatchEngine::alphaMutation(State & s){
    uniform_int_distribution<int> distribution(0, NUM_OF_POLYGON-1);
    int index = distribution(*randEngine);
    Scalar color = s.colors[index];
    normal_distribution<double> alphaDistribution(color.val[3], ALPHA_DEVIATION * MUTATION_MODIFIER);
    double alpha = alphaDistribution(*randEngine);
    if(alpha > 1)   alpha = 1;
    if(alpha < 0)   alpha = 0;
    s.colors[index].val[3] = alpha;
}

void MatchEngine::colorMutation(State & s){
    uniform_int_distribution<int> distribution(0, NUM_OF_POLYGON-1);
    int index = distribution(*randEngine);
    Scalar color = s.colors[index];
    normal_distribution<double> redDistribution(color.val[0], 256 * COLOR_DEVIATION * MUTATION_MODIFIER);
    normal_distribution<double> greenDistribution(color.val[1], 256 * COLOR_DEVIATION * MUTATION_MODIFIER);
    normal_distribution<double> blueDistribution(color.val[2], 256 * COLOR_DEVIATION * MUTATION_MODIFIER);
    //int red =redDistribution(*randEngine);
    s.colors[index].val[0] = max(min((int)redDistribution(*randEngine), 255), 0);
    s.colors[index].val[1] = max(min((int)greenDistribution(*randEngine), 255), 0);
    s.colors[index].val[2] = max(min((int)blueDistribution(*randEngine), 255), 0);
}

void MatchEngine::vertexLocMutation(State & s){
    uniform_int_distribution<int> distribution(0, NUM_OF_POLYGON-1);
    int index = distribution(*randEngine);
    int vertex = rand() % (s.vertexCounts[index]);
    normal_distribution<double> xValGen(s.polyArr[index][vertex].x, source->cols * VERTEX_LOC_DEVIATION * MUTATION_MODIFIER);
    normal_distribution<double> yValGen(s.polyArr[index][vertex].y, source->rows * VERTEX_LOC_DEVIATION * MUTATION_MODIFIER);
    s.polyArr[index][vertex].x = max(min((int) xValGen(*randEngine), source->cols), 0);
    s.polyArr[index][vertex].y = max(min((int) yValGen(*randEngine), source->rows), 0);
}

void MatchEngine::swapPolygons(State & s){
    uniform_int_distribution<int> distribution(0, NUM_OF_POLYGON-1);
    int index1 = distribution(*randEngine);
    int index2 = distribution(*randEngine);
    for(int i = 0; i < MAX_VERTEX; ++i){
        Point temp(s.polyArr[index1][i].x, s.polyArr[index1][i].y);
        s.polyArr[index1][i].x = s.polyArr[index2][i].x;
        s.polyArr[index1][i].y = s.polyArr[index2][i].y;
        s.polyArr[index2][i].x = temp.x;
        s.polyArr[index2][i].y = temp.y;
    }
    int numOfVertex = s.vertexCounts[index1];
    s.vertexCounts[index1] = s.vertexCounts[index2];
    s.vertexCounts[index2] = numOfVertex;
    
    Scalar temp = s.colors[index1];
    s.colors[index1] = s.colors[index2];
    s.colors[index2] = temp;
    
}

void MatchEngine::randomPolygon(State & s){
    uniform_int_distribution<int> distribution(0, NUM_OF_POLYGON-1);
    int index = distribution(*randEngine);
    uniform_int_distribution<int> xValGen(0, source->cols-1);
    uniform_int_distribution<int> yValGen(0, source->rows-1);
    uniform_int_distribution<int> colorValGen(0, 255);
    uniform_real_distribution<double> alphaValGen(0, 1);
    
    int centerX = xValGen(*randEngine);
    int centerY = yValGen(*randEngine);
    
    normal_distribution<double> normXValGen(centerX, NEW_VERTEX_DEVIATION * source->cols);
    normal_distribution<double> normYValGen(centerY, NEW_VERTEX_DEVIATION * source->rows);
    
    for(int i = 0; i < 3; ++i){
        s.polyArr[index][i].x = max(min((int)normXValGen(*randEngine), 255), 0);
        s.polyArr[index][i].y = max(min((int)normYValGen(*randEngine), 255), 0);
    }
    s.vertexCounts[index] = 3;
    s.colors[index].val[0] = colorValGen(*randEngine);
    s.colors[index].val[1] = colorValGen(*randEngine);
    s.colors[index].val[2] = colorValGen(*randEngine);
    s.colors[index].val[3] = alphaValGen(*randEngine);
}

bool MatchEngine::binary(double p, default_random_engine randEngine){
    uniform_real_distribution<double> distribution(0, 1);
    double r = distribution(randEngine);
    return (r < p);
}



Mat MatchEngine::finalImage(){
    sort(states.begin(), states.end(), MatchEngine::compareScore);
    return states[0]->getImage();
}
