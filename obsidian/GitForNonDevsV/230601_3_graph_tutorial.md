[[graph_tutorial]]

# [[lib]]
## [[bus.js]]

```
import eventify from 'ngraph.events';

const bus = eventify({});

export default bus;
```


This piece of JavaScript code is quite simple but interesting. Here's the breakdown:

1. `import eventify from 'ngraph.events';`
    
    This line is importing a function called [[eventify]] from a package named [[ngraph.events]]. The [[ngraph.events]] library is a part of [[ngraph]] project, which provides a bunch of utilities for graph processing in JavaScript. In this particular case, the `eventify` function is used to add [[event emitter]] capabilities to any JavaScript object.
    
2. `const bus = eventify({});`
    
    Here, an empty object `{}` is being passed into the `eventify` function. The result is an event emitter, which is assigned to the constant [[bus]]. An event emitter is an object that can trigger custom events when something happens to it, and other parts of the code can listen for these events and react accordingly. In this case, the `bus` object is being used as an "event bus", a common design pattern for decoupling components in a software system. Components can emit events to the bus and listen for events from the bus, without having to know about each other.
    
3. `export default bus;`
    
    Finally, `bus` is being exported as the default export of this module, which means it can be imported by other modules in your application. The `default` keyword indicates that `bus` is the primary exported value from this file. When another file imports this one without specifying a named import, it'll receive the `bus` object.
    

In summary, this code is creating an event bus using the `eventify` function from `ngraph.events`, and then exporting it so it can be used elsewhere in the application. Other modules can import `bus` and use it to emit and listen for custom events. This is a common pattern for managing state and passing messages between different parts of a JavaScript application, especially in event-driven or reactive programming paradigms.

## [[createGraphScene.js]]

```
import {createScene} from 'w-gl';

import LineCollection from './LineCollection';

import PointCollection from './PointCollection';

import MSDFTextCollection from './MSDFTextCollection';

import bus from './bus';

import getGraph from './getGraph';

import createLayout from 'ngraph.forcelayout';

  

export default function createGraphScene(canvas) {

let drawLinks = true;

let drawLabels = true;

  

// Since graph can be loaded dynamically, we have these uninitialized

// and captured into closure. loadGraph will do the initialization

let graph, layout;

let scene, nodes, lines, labels;

  

let layoutSteps = 0; // how many frames shall we run layout?

let rafHandle;

  

loadGraph(getGraph());

bus.on('load-graph', loadGraph);

  

return {

dispose,

runLayout,

};

  

function loadGraph(newGraph) {

if (scene) {

scene.dispose();

scene = null

cancelAnimationFrame(rafHandle);

}

scene = initScene();

graph = newGraph

  

layout = createLayout(graph, {

timeStep: 0.5,

springLength: 10,

springCoefficient: 0.8,

gravity: -12,

dragCoefficient: 0.9,

});

  

layout.step();

initUIElements();

  

rafHandle = requestAnimationFrame(frame);

}

  

function runLayout(stepsCount) {

layoutSteps += stepsCount;

}

  

function initScene() {

let scene = createScene(canvas);

scene.setClearColor(12/255, 41/255, 82/255, 1)

let initialSceneSize = 40;

scene.setViewBox({

left: -initialSceneSize,

top: -initialSceneSize,

right: initialSceneSize,

bottom: initialSceneSize,

});

return scene;

}

function initUIElements() {

nodes = new PointCollection(scene.getGL(), {

capacity: graph.getNodesCount()

});

  

graph.forEachNode(node => {

var point = layout.getNodePosition(node.id);

let size = 1;

if (node.data && node.data.size) {

size = node.data.size;

} else {

if (!node.data) node.data = {};

node.data.size = size;

}

node.ui = {size, position: [point.x, point.y, point.z || 0], color: node.data.color || 0x90f8fcff};

node.uiId = nodes.add(node.ui);

});

  

lines = new LineCollection(scene.getGL(), { capacity: graph.getLinksCount() });

  

graph.forEachLink(link => {

var from = layout.getNodePosition(link.fromId);

var to = layout.getNodePosition(link.toId);

var line = { from: [from.x, from.y, from.z || 0], to: [to.x, to.y, to.z || 0], color: 0xFFFFFF10 };

link.ui = line;

link.uiId = lines.add(link.ui);

});

  

scene.appendChild(lines);

scene.appendChild(nodes);

if (drawLabels) {

labels = new MSDFTextCollection(scene.getGL());

redrawLabels();

scene.appendChild(labels);

}

}

  

function frame() {

rafHandle = requestAnimationFrame(frame);

  

if (layoutSteps > 0) {

layoutSteps -= 1;

layout.step();

// Drawing labels is heavy, so avoid it if we don't need it

redrawLabels();

}

drawGraph();

scene.renderFrame();

}

  

function drawGraph() {

graph.forEachNode(node => {

let pos = layout.getNodePosition(node.id);

let uiPosition = node.ui.position;

uiPosition[0] = pos.x;

uiPosition[1] = pos.y;

uiPosition[2] = pos.z || 0;

nodes.update(node.uiId, node.ui)

});

  

if (drawLinks) {

graph.forEachLink(link => {

var fromPos = layout.getNodePosition(link.fromId);

var toPos = layout.getNodePosition(link.toId);

let {from, to} = link.ui;

from[0] = fromPos.x; from[1] = fromPos.y; from[2] = fromPos.z || 0;

to[0] = toPos.x; to[1] = toPos.y; to[2] = toPos.z || 0;

lines.update(link.uiId, link.ui);

})

}

}

  

function redrawLabels() {

if (!drawLabels) return;

labels.clear();

graph.forEachNode(node => {

const text = '' + ((node.data && node.data.label) || node.id);

  

labels.addText({

text,

x: node.ui.position[0],

y: node.ui.position[1] - node.ui.size / 2,

limit: node.ui.size,

cx: 0.5

});

});

}

  

function dispose() {

cancelAnimationFrame(rafHandle);

  

scene.dispose();

bus.off('load-graph', loadGraph);

}

}
```




The script you provided appears to be a part of a larger JavaScript application that deals with creating and manipulating graphs, likely in a visual manner. Here's an explanation of what the script does, along with the role of the `bus` object from your previous script:

1. The script imports several functions and objects, among them is `bus` from `./bus`. The `bus` object is an event bus that we discussed earlier, which can emit and listen for custom events.
    
2. The exported function `createGraphScene(canvas)` is likely used elsewhere in your application to create a visual graph scene on a specified canvas. This function sets up a new graph scene, initializes all necessary collections for nodes and links of the graph (points and lines), text labels, and sets up a layout for the graph.
    
3. The `loadGraph(newGraph)` function initializes a new graph scene with `newGraph` and sets up the initial UI elements (nodes, lines, and optionally labels) of the scene. It then starts a render loop by requesting an animation frame for the `frame()` function.
    
4. `bus.on('load-graph', loadGraph);` is where the connection to `bus` lies. This code sets up a listener on `bus` for the `'load-graph'` event, which will trigger the `loadGraph` function. This means that elsewhere in your application, something can trigger a `'load-graph'` event on the `bus` event bus with a new graph as the payload, and this module will react by setting up a new graph scene with the new graph.
    
5. The `frame()` function is repeatedly called for every frame of the animation, with `requestAnimationFrame(frame)`. This function steps the graph layout if necessary, redraws labels, draws the graph, and then renders the frame.
    
6. The `dispose()` function cancels the animation frame request, disposes of the scene, and removes the listener for the `'load-graph'` event on `bus`. This is a cleanup function that you would call when you're done with the graph scene and want to free up resources.
    

In summary, this script creates a graph scene on a canvas with nodes, links, and labels. It listens to the `bus` event bus for `'load-graph'` events, and reloads the graph scene when such an event is triggered. It continuously renders frames of the scene until it's disposed of.

## [[utils.js]]

The provided JavaScript code is a utility module that exports three different functions which are common and useful for a range of mathematical and statistical applications. Here's a brief overview of what each function does:

1. `smoothStep(edge0, edge1, x)`: This function performs a Hermite interpolation for a given value `x` between two provided edges `edge0` and `edge1`. The interpolation is done using the smoothstep function, a common method for smoothing out the transition between two values. It's often used in animation or in cases where a value needs to smoothly transition from one state to another. 

2. `clamp(x, min, max)`: The clamp function restricts an input `x` to a specified range between `min` and `max`. If `x` is less than `min`, it will return `min`. If `x` is more than `max`, it will return `max`. Otherwise, it just returns `x`.

3. `collectStatistics(array)`: This function calculates and returns a set of statistical properties for a given array of numbers. These properties include: 

   - `min`: the smallest number in the array.
   - `max`: the largest number in the array.
   - `avg`: the average (mean) of the numbers in the array.
   - `sigma`: the standard deviation of the numbers in the array. This provides a measure of the amount of variation or dispersion of the set of values.
   - `mod`: the mode of the array, which is the number that appears most frequently.
   - `count`: the total number of elements in the array.

All of these functions can be imported and used elsewhere in the code base, making them versatile tools for handling numerical data.

```
/**
* Set of function that I find useful for explorations.
*/

/**
* Performs hermit interpolation of `x` between two edges
*/

export function smoothStep(edge0, edge1, x) {

let t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);

return t * t * (3.0 - 2.0 * t);

}

/**
* Clamp `x` to [min, max] range.
*/

export function clamp(x, min, max) {

return x < min ? min : x > max ? max : x;

}

  

/**
* Collects main statistical properties of a collection
*/

export function collectStatistics(array) {

if (array.length === 0) {

return {

min: undefined,

max: undefined,

avg: undefined,

sigma: undefined,

mod: undefined,

count: 0

}

}

let min = Infinity;

let max = -Infinity;

let sum = 0;

let counts = new Map();

array.forEach(x => {

if (x < min) min = x;

if (x > max) max = x;

sum += x;

counts.set(x, (counts.get(x) || 0) + 1)

});

let mod = Array.from(counts).sort((a, b) => b[1] - a[1])[0][0]

  

let avg = sum /= array.length;

let sigma = 0;

array.forEach(x => {

sigma += (x - avg) * (x - avg);

});

sigma = Math.sqrt(sigma / (array.length + 1));

let count = array.length;

return {min, max, avg, sigma, mod, count};

}

```


## [[PointCollection.js]]

This script defines a custom WebGL collection called `PointCollection`, which is a collection of points to be drawn in a WebGL context. The points will be rendered using the shader programs defined in this class. The class extends `GLCollection` from the 'w-gl' package.

Here is a breakdown of the important elements:

1. `constructor(gl)`: This is the constructor of `PointCollection` class. It accepts a WebGL context (`gl`), which is needed to create and compile the shader programs.

2. `let program = defineProgram({...})`: This code defines a WebGL shader program, which is a set of instructions that tells the GPU how to process vertex and pixel data. The program has two parts:

   - `vertex`: This is the vertex shader. It describes what to do with each vertex of each point. It receives attributes (`size`, `position`, `color`, and `point`) for each point, and calculates the final position of the point (`gl_Position`) and passes varying variables (`vColor` and `vPoint`) to the fragment shader.

   - `fragment`: This is the fragment shader. It describes what to do with each pixel (fragment) within the point. It discards pixels that are too far from the center of the point, and sets the color of the remaining pixels to `vColor`.

3. `attributes: { color: new ColorAttribute() }`: This defines an attribute buffer for colors, which will hold the color data for each point.

4. `instanced: { point: new InstancedAttribute(...) }`: This defines an instanced attribute buffer for point vertices. An instanced attribute is an attribute that has the same value for all vertices of each instance, but can have different values for different instances. In this case, each instance is a point, and the point vertices are the same for each point.

5. `preDrawHook(/* programInfo */)`, `postDrawHook()`: These hooks enable depth testing before drawing the points and disable it afterwards. Depth testing is used in 3D graphics to determine which objects (or parts of objects) are hidden behind others.

6. `super(program)`: This passes the defined program to the `GLCollection` constructor. The `GLCollection` class handles the actual setup and drawing of the collection using the given program.

In summary, this script defines a `PointCollection` class for rendering a collection of points in a WebGL context, with a specific vertex layout and drawing behavior. This class can be imported and used elsewhere in the application to create collections of points.

  
```
import { GLCollection, defineProgram, ColorAttribute, InstancedAttribute } from 'w-gl';

  

export default class PointCollection extends GLCollection {

constructor(gl) {

let program = defineProgram({

gl,

vertex: `

uniform mat4 modelViewProjection;

  

attribute float size;

attribute vec3 position;

attribute vec4 color;

  

attribute vec2 point; // instanced

  

varying vec4 vColor;

varying vec2 vPoint;

void main() {

gl_Position = modelViewProjection * vec4(position + vec3(point * size, 0.), 1.0);

vColor = color.abgr;

vPoint = point;

}`,

  

fragment: `

precision highp float;

varying vec4 vColor;

varying vec2 vPoint;

void main() {

float dist = length(vPoint);

if (dist >= 0.5) {discard;}

gl_FragColor = vColor;

}`,

// These are just overrides:

attributes: {

color: new ColorAttribute(),

},

instanced: {

point: new InstancedAttribute([

-0.5, -0.5, -0.5, 0.5, 0.5, 0.5,

0.5, 0.5, 0.5, -0.5, -0.5, -0.5,

])

},

  

preDrawHook(/* programInfo */) {

return `gl.enable(gl.DEPTH_TEST);

gl.depthFunc(gl.LEQUAL);`;

},

postDrawHook() {

return 'gl.disable(gl.DEPTH_TEST);';

},

});

  

super(program);

}

}
```

## [[MSDFTextCollection.js]]

This script defines a custom WebGL collection called `MSDFTextCollection` that is used for rendering text using Multi-channel Signed Distance Field (MSDF) technique. This approach is used to render smooth, scalable text in WebGL.

Here are the main parts of the script:

1. `constructor(gl, options = {})`: The constructor for the `MSDFTextCollection` class. It accepts a WebGL context and an optional options object. It retrieves the MSDF font information and image from an external source, and it initializes a queue to hold text objects to be added when the font image is loaded.

2. `clear()`: This function resets the count of the elements in the collection to 0, effectively clearing all elements.

3. `draw(gl, drawContext)`: The draw function, which is responsible for rendering the text elements on the WebGL canvas. It does so by setting up some uniform values and calling the `draw()` method of the program twice, once for the outlined text and another for the filled text.

4. `stress(x, y)`: This function fetches the text of the book "War and Peace" and adds each line of the book as a text element to the WebGL canvas. It's likely used for performance testing.

5. `addText(textInfo)`: This function adds a string of text to the WebGL canvas at the specified position. It does so by creating an object for each character of the string, and adding the object to the collection.

6. `getTextProgram(gl, options)`: This function defines the shader program for rendering the text. It uses a vertex shader to calculate the position of each character and a fragment shader to color each pixel of the character. The fragment shader uses the MSDF technique to smoothly interpolate the color of each pixel based on its distance to the character's boundaries.

In summary, this script defines a `MSDFTextCollection` class for rendering text in a WebGL context using the MSDF technique. The class can be imported and used elsewhere in your application to add text to a WebGL canvas.

```
import {defineProgram, InstancedAttribute, GLCollection} from 'w-gl';

  

export default class MSDFTextCollection extends GLCollection {

constructor(gl, options = {}) {

gl.getExtension('OES_standard_derivatives');

  

super(getTextProgram(gl, options));

  

let img = (this.msdfImage = new Image());

img.crossOrigin = 'Anonymous';

this.isReady = false;

this.queue = [];

this.fontSize = options.fontSize || 2;

this.fontInfo = null;

  

let fontPath = 'fonts';

fetch(`${fontPath}/Roboto.json`, { mode: 'cors' })

.then((x) => x.json())

.then((fontInfo) => {

this.fontInfo = fontInfo;

this.alphabet = new Map();

fontInfo.chars.forEach((char) => {

let charValue = String.fromCharCode(char.id);

this.alphabet.set(charValue, char);

});

  

this.msdfImage.onload = () => {

this._sdfTextureChanged = true;

this.program.setTextureCanvas('msdf', this.msdfImage);

this.isReady = true;

this.sdfTextureWidth = img.width;

this.sdfTextureHeight = img.height;

  

this.queue.forEach((q) => this.addText(q));

this.queue = [];

};

this.msdfImage.src = `${fontPath}/Roboto0.png`;

});

}

  

clear() {

this.program.setCount(0);

}

  

draw(gl, drawContext) {

if (!this.uniforms) {

this.uniforms = {

modelViewProjection: this.modelViewProjection,

color: [0.9, 0.9, 0.9, 1.0],

bias: 0.5,

};

}

  

this.uniforms.color[0] = 0.2;

this.uniforms.color[1] = 0.4;

this.uniforms.color[2] = 0.8;

this.uniforms.color[3] = 0.8;

this.uniforms.bias = 0.35;

this.program.draw(this.uniforms);

  

this.uniforms.color[0] = 0.9;

this.uniforms.color[1] = 0.9;

this.uniforms.color[2] = 0.9;

this.uniforms.color[3] = 1;

this.uniforms.bias = 0.5;

this.program.draw(this.uniforms);

}

  

stress(x, y) {

let dy = 0;

fetch(

'https://raw.githubusercontent.com/mmcky/nyu-econ-370/master/notebooks/data/book-war-and-peace.txt'

)

.then((b) => b.text())

.then((text) => {

let lineCount = 0;

text.split('\n').forEach((line) => {

this.addText({ text: line, x, y: y + dy });

dy -= this.fontSize;

lineCount += 1;

if (lineCount > 1000) {

lineCount = 0;

x += 80;

dy = 0;

}

});

});

}

  

addText(textInfo) {

if (!this.isReady) {

this.queue.push(textInfo);

return;

}

let { text, x = 0, y = 0, z = 0 } = textInfo;

if (text === undefined) {

throw new Error('Text is not defined in ' + textInfo)

}

let dx = 0;

let fontSize = textInfo.fontSize || this.fontSize;

if (textInfo.limit !== undefined) {

let w = 0;

for (let char of text) {

let sdfPos = this.alphabet.get(char);

if (!sdfPos) continue;

w += sdfPos.xadvance;

}

fontSize = (textInfo.limit * this.fontInfo.info.size) / w;

}

  

let scale = fontSize / this.fontInfo.info.size;

if (textInfo.cx !== undefined) {

let w = 0;

for (let char of text) {

let sdfPos = this.alphabet.get(char);

if (!sdfPos) continue;

  

w += sdfPos.xadvance;

}

dx -= w * textInfo.cx * scale;

}

if (textInfo.cy !== undefined) {

y += fontSize * textInfo.cy;

}

  

for (let char of text) {

let sdfPos = this.alphabet.get(char);

if (!sdfPos) {

console.error(char + ' is missing in the font');

continue;

}

  

this.add({

position: [x + dx, y - sdfPos.yoffset * scale, z],

charSize: [

(fontSize * sdfPos.width) / 42,

(-fontSize * sdfPos.height) / 42,

],

texturePosition: [

sdfPos.x / this.sdfTextureWidth,

1 - sdfPos.y / this.sdfTextureHeight,

sdfPos.width / this.sdfTextureWidth,

-sdfPos.height / this.sdfTextureHeight,

],

});

dx += sdfPos.xadvance * scale;

}

if (this.scene) this.scene.renderFrame();

}

}

  

function getTextProgram(gl, options) {

return defineProgram({

capacity: options.capacity || 1,

buffer: options.buffer,

debug: options.debug,

gl,

vertex: `

uniform mat4 modelViewProjection;

uniform vec4 color;

  

// Position of the text character:

attribute vec3 position;

// Instanced quad coordinate:

attribute vec2 point;

attribute vec2 charSize;

// [x, y, w, h] - of the character in the msdf texture;

attribute vec4 texturePosition;

  

varying vec2 vPoint;

  

void main() {

gl_Position = modelViewProjection * vec4(

position + vec3(

vec2(point.x, point.y) * charSize,

position.z),

1.);

vPoint = texturePosition.xy + point * texturePosition.zw;

}`,

  

fragment: `

#ifdef GL_OES_standard_derivatives

#extension GL_OES_standard_derivatives : enable

#endif

precision highp float;

varying vec2 vPoint;

  

uniform vec4 color;

uniform float bias;

uniform sampler2D msdf;

  

float median(float r, float g, float b) {

return max(min(r, g), min(max(r, g), b));

}

  

void main() {

vec3 sample = texture2D(msdf, vPoint).rgb;

float sigDist = median(sample.r, sample.g, sample.b) - bias;

float alpha = clamp(sigDist / fwidth(sigDist) + bias, 0.0, 1.0);

gl_FragColor = vec4(color.rgb, color.a * alpha);

}`,

instanced: {

point: new InstancedAttribute([0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1]),

},

});

}
```



	## [[LineCollection.js]]

This script is used to load a graph data structure from a file that the user has dropped into the application. It supports both DOT (a plain text graph description language) and JSON formats. 

The exported default function `loadDroppedGraph(files)` receives a list of files, and it reads the first file. Once the file is read, it attempts to parse the content as DOT and JSON formats in the order.

Here's a brief explanation of the main parts of the script:

1. `reader.readAsText(file, "UTF-8");`: Reads the file content as a UTF-8 encoded text string.

2. `reader.onload = e => { ... }`: Defines what happens when the file reading is completed successfully. It attempts to parse the file content using `tryDot(content)` and `tryJson(content)` functions, and if the graph is successfully loaded, it fires the 'load-graph' event with the graph as the payload.

3. `reader.onerror = (e) => { ... }`: Defines what happens when an error occurs while reading the file. It simply logs the error to the console.

4. `tryDot(fileContent)`: Tries to parse the given file content as a DOT graph using `fromDot(fileContent)` from 'ngraph.fromdot'. If an error occurs, it logs the error to the console and returns undefined.

5. `tryJson(fileContent)`: Tries to parse the given file content as a JSON graph using `fromJson(JSON.parse(fileContent))` from 'ngraph.fromjson'. If an error occurs, it logs the error to the console and returns undefined.

The 'bus' object is an event bus that allows different parts of the application to communicate with each other. The `bus.fire('load-graph', graph)` line is used to send an event to the rest of the application that a graph has been loaded.


```
import {GLCollection, defineProgram, InstancedAttribute, ColorAttribute} from 'w-gl';

  

export default class LineCollection extends GLCollection {

constructor(gl, options = {}) {

let program = defineProgram({

gl,

vertex: `

uniform mat4 modelViewProjection;

uniform float width;

uniform vec2 resolution;

  

attribute vec4 color;

attribute vec3 from, to;

attribute vec2 point;

  

varying vec4 vColor;

varying vec2 vPoint;

  

void main() {

vec4 clip0 = modelViewProjection * vec4(from, 1.0);

vec4 clip1 = modelViewProjection * vec4(to, 1.0);

  

vec2 screen0 = resolution * (0.5 * clip0.xy/clip0.w + 0.5);

vec2 screen1 = resolution * (0.5 * clip1.xy/clip1.w + 0.5);

  

vec2 xBasis = normalize(screen1 - screen0);

vec2 yBasis = vec2(-xBasis.y, xBasis.x);

  

// Offset the original points:

vec2 pt0 = screen0 + width * point.x * yBasis;

vec2 pt1 = screen1 + width * point.x * yBasis;

  

vec2 pt = mix(pt0, pt1, point.y);

vec4 clip = mix(clip0, clip1, point.y);

  

gl_Position = vec4(clip.w * (2.0 * pt/resolution - 1.0), clip.z, clip.w);

vColor = color.abgr; // mix(.abgr, aToColor.abgr, aPosition.y);

}`,

  

fragment: `

precision highp float;

varying vec4 vColor;

  

void main() {

gl_FragColor = vColor;

}`,

attributes: {

color: new ColorAttribute()

},

instanced: {

point: new InstancedAttribute([

-0.5, 0, -0.5, 1, 0.5, 1, // First 2D triangle of the quad

-0.5, 0, 0.5, 1, 0.5, 0 // Second 2D triangle of the quad

])

}

});

super(program);

this.width = options.width || 2;

}

  

draw(_, drawContext) {

if (!this.uniforms) {

this.uniforms = {

modelViewProjection: this.modelViewProjection,

width: this.width,

resolution: [drawContext.width, drawContext.height]

}

}

this.uniforms.resolution[0] = drawContext.width;

this.uniforms.resolution[1] = drawContext.height;

this.program.draw(this.uniforms);

}

  

// implement lineRenderTrait to allow SVG export via w-gl

forEachLine(cb) {

let count = this.program.getCount()

for (let i = 0; i < count; ++i) {

let vertex = this.program.get(i);

let from = { x: vertex.from[0], y: vertex.from[1], z: vertex.from[2], color: vertex.color }

let to = { x: vertex.to[0], y: vertex.to[1], z: vertex.to[2], color: vertex.color }

cb(from, to);

}

}

  

getLineColor(from) {

let count = this.program.getCount()

let c = from ?

from.color :

count > 0 ? this.program.get(0).color : 0xFFFFFFFF;

  

return [

(c >> 24) & 0xFF / 255,

(c >> 16) & 0xFF / 255,

(c >> 8) & 0xFF / 255,

(c >> 0) & 0xFF / 255,

]

}

}

```


# [[App.vue]] 

     

# [[main.js]]