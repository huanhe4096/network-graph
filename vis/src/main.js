import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

import { initVisualization, loadData, animate } from "./vis.js";

async function main() {
    const sceneObjects = initVisualization();
    await loadData(sceneObjects);
    animate();
}

main();


createApp(App).mount('#app')
