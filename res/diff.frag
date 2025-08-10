#version 330 core

uniform sampler2D uTextureLHS;
uniform sampler2D uTextureRHS;
uniform sampler2D uTextureBGTile;
uniform vec2 uLHSWH;
uniform vec2 uRHSWH;
uniform vec2 uCanvasWH;

uniform vec3 colAdd;
uniform vec3 colRem;
uniform bool renderLHS;
uniform bool renderRHS;

uniform vec3 colHilight;
uniform bool doHilight;
uniform float hilightThresh;
uniform int hilightSize;

in vec2 uvLHS;
in vec2 uvRHS;
in vec2 uvTile;


void main() {
    gl_FragColor = vec4(1.0);
    if (renderLHS && uLHSWH.x > 0 && uvLHS.x > 0 && uvLHS.x < 1 && uvLHS.y > 0 && uvLHS.y < 1){
        if (renderRHS && uRHSWH.x > 0 && uvRHS.x > 0 && uvRHS.x < 1 && uvRHS.y > 0 && uvRHS.y < 1){

            // diff magic here
            vec3 pxLhs = texture2D(uTextureLHS, uvLHS).rgb;
            vec3 pxRhs = texture2D(uTextureRHS, uvRHS).rgb;
            float invLhs = 1-(pxLhs.x+pxLhs.y+pxLhs.z)/3;
            float invRhs = 1-(pxRhs.x+pxRhs.y+pxRhs.z)/3;

            float added = clamp(invRhs-invLhs, 0, 1);
            float removed = clamp(invLhs-invRhs, 0, 1);
            float same = clamp(invLhs-removed, 0, 1);

            vec3 px = 1 - (1-colAdd)*added - (1-colRem)*removed - same;
            if (doHilight) {
                float diff = 0.0;
                for (int ix = 0; ix < hilightSize*2; ix++) {
                    for (int iy = 0; iy < hilightSize*2; iy++) {
                        vec2 dc = vec2(ix, iy)-hilightSize;
                        vec2 cLhs = (dc/uLHSWH)+uvLHS;
                        vec2 cRhs = (dc/uRHSWH)+uvRHS;

                        vec3 pxLhs = texture2D(uTextureLHS, cLhs).rgb;
                        vec3 pxRhs = texture2D(uTextureRHS, cRhs).rgb;

                        diff += abs(pxLhs.r-pxRhs.r)+abs(pxLhs.g-pxRhs.g)+abs(pxLhs.b-pxRhs.b);
                    }
                }
                if (diff > hilightThresh) {
                    px -= 1-colHilight;
                }

            }
            gl_FragColor = vec4(clamp(px, 0, 1), 1);
        }
        else {
            gl_FragColor = texture2D(uTextureLHS, uvLHS);
        }
    }
    else if (renderRHS && uRHSWH.x > 0 && uvRHS.x > 0 && uvRHS.x < 1 && uvRHS.y > 0 && uvRHS.y < 1){
        gl_FragColor = texture2D(uTextureRHS, uvRHS);
    }
}