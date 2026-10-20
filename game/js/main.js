// Bootstrap: create the game on the page canvas and start the loop.
import { Game } from './game.js';

const canvas = document.getElementById('game-canvas');
const game = new Game(canvas);
window.game = game; // handy for debugging in devtools
game.start();
