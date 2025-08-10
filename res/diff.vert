#version 330 core

in vec2 inCoord;
uniform vec2 uCanvasWH;
uniform vec2 uPageWH;
uniform vec2 uLHSWH;
uniform vec2 uRHSWH;
uniform vec2 uPos;
uniform float uScale;
uniform float uTheta;

out vec2 uvLHS;
out vec2 uvRHS;

void main() {
    // do these steps since we're not using these uniforms yet
    float theta = uTheta*0;
    vec2 pos = uPos*0;
    vec2 something = uPageWH*0;
    vec2 something2 = uCanvasWH*0;
//    pos = aTexCoord;

//    vec4 position = vec4(aPosition, 1.0);
//    position.xy = position.xy * 2 - 1;

    if (uLHSWH.x > 0){
        uvLHS = inCoord/uLHSWH;
    }
    if (uRHSWH.x > 0){
        uvRHS = inCoord/uRHSWH;
    }
    vec2 canvScale = 2*uPageWH/uCanvasWH;

    vec2 inCoordNorm = (inCoord+uPos)/uPageWH;

    vec2 outCoord = uScale*(inCoordNorm);

    // finally, scale by the relative size of the canvas and shift 0,0 to top-left
    gl_Position = vec4(outCoord*canvScale-1, 0.0, 1.0);
}