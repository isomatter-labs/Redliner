#version 330 core

in vec2 inCoord;
out vec2 uvTile;

void main() {
    uvTile = inCoord;
    gl_Position = vec4(inCoord*2-1, 0, 1);
}