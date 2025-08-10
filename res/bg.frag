#version 330 core

uniform sampler2D uTextureBGTile;
uniform vec2 uCanvasWH;
const vec2 tileWH = vec2(96, 96);

in vec2 uvTile;

void main() {
    vec2 newUv = fract(uvTile*uCanvasWH/tileWH);
    gl_FragColor = texture2D(uTextureBGTile, newUv);
}