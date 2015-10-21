#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <cmath>
using namespace cv;

#ifndef DRAW_H
#define DRAW_H

/***************
 renderPolyImage
 ****************
 Takes a list of polygons and renders them into an image
 
 Returns:
	An OpenCV "Mat" object, a matrix specifying the image
 
 Arguments:
	int imWidth:
 Width of the image
 
	int imHeight:
 height of the image
 
	int numPolygons:
 The number of polygons being passed in
 
 const Point** polygons:
 A pointer to an array of pointers to arrays of OpenCV Points,
 Each array of points specifies the vertices of a polygon
 Example:
 Point polyArr[100][6];
 for (int i = 0; i < 100; i++) {
 for (int j = 0; j < 6; j++) {
 polyArr[i][j] = Point(... , ...);
 //Initialize each point randomly
 }
 }
 const Point* polygons[100];
 //Array of constant pointers to arrays of Points
 for (int i = 0; i < 100; i++) {
 polygons[i] = &polyArr[i][0];
 // Initialize each pointer to point to a polygon
 }
 
 // "polyArr" is of type Point*[6]
 // "polygons" is of type Point**, which we need
 
	const int* vertexCounts:
 A pointer to an array of integers
 containing the number of vertices of each polygon
 Example:
 int vertexCounts[100];
 for (int i = 0; i < 100; i++) vertexCounts[i] = 3;
 // Initialize number of vertices to 3
 
 vertexCounts[9];
 // Number of vertices in the polygon at index 9
 // in the "polygons" array
 
 const Scalar* colors:
 A pointer to an array of OpenCV Scalar objects
 Each object specifies the color and opacity of a polygon
 Each scalar object stores color information in BGRA format
 The BGR fields must be between 0 and 255
 The opacity field must be between 0 and 1
 Example:
 Scalar polyColor(40, 255, 38, 0.7);
 // Creates a scalar object where
 //		blue = 40
 // 		green = 255
 // 		red = 38
 //		opacity = 0.7
 //These can be accessed and modified using the "val" field:
 polyColor.val[0] = 90; //Change blue to 90
 polyColor.val[1] = 65; //change green to 65
 polyColor.val[2] = 100; //Change red to 100
 polyColor.val[3] = 0.2; //Change opacity to 0.2
 
 Scalar colors[100];
 for (int i = 0; i < 100; i++) {
 colors[i] = Scalar(..., ..., ..., ...);
 // Randomly initialize each color value
 }
 
 colors[9];
 //The colors of the polygon at index 9 in the "polygons" array
 
 */
Mat renderPolyImage(
                    int imHeight,
                    int imWidth,
                    int numPolygons,
                    const Point** polygons,
                    const int* vertexCounts,
                    const Scalar* colors
                    );

/*****
 score
 ******
 Returns:
	The fitness score of the polygon image as compared to the
	reference image.
 
 Arguments:
	polyImage:
 The image made of polygons
	referenceImage:
 The image we are trying to approximate
 
 */
double score(const Mat& polyImage, const Mat& referenceImage);

#endif