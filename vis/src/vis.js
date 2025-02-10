import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import Stats from "stats.js";  // ✅ 导入 stats.js

let scene, camera, renderer, controls, stats;  // ✅ 添加 `stats`

// 🚀 **初始化 Three.js 3D 场景**
export function initVisualization() {
    scene = new THREE.Scene();

    // **相机**
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 200);

    // **渲染器**
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // **鼠标交互**
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // **光照**
    const light = new THREE.AmbientLight(0xffffff, 1);
    scene.add(light);

    // **FPS 监视器**
    stats = new Stats();
    stats.showPanel(0);  // 0 = FPS, 1 = 渲染时间, 2 = 内存
    document.body.appendChild(stats.dom);

    // **窗口调整**
    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    return { scene };
}

// 🚀 **加载 `nodes.tsv` 和 `smoothed_edges.tsv`**
export async function loadData() {
    console.log("Fetching nodes.tsv & smoothed_edges.tsv...");
    const [nodesText, edgesText] = await Promise.all([
        fetch("/public/nodes.tsv").then(res => res.text()),
        fetch("/public/smoothed_edges.tsv").then(res => res.text())
    ]);

    parseNodes(nodesText);
    parseEdges(edgesText);
    document.getElementById("loading").style.display = "none";  // 隐藏加载提示
}

// 🚀 **解析 `nodes.tsv` 并渲染 3D 点**
function parseNodes(text) {
    console.log("Parsing nodes.tsv...");
    const lines = text.trim().split("\n").slice(1);
    const geometry = new THREE.BufferGeometry();
    const positions = [];

    lines.forEach(line => {
        const parts = line.split("\t");
        if (parts.length < 4) return;

        const x = parseFloat(parts[1]);
        const y = parseFloat(parts[2]);
        const z = parseFloat(parts[3]);

        positions.push(x, y, z);
    });

    geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({ size: 1, color: "blue" });
    const points = new THREE.Points(geometry, material);
    scene.add(points);
    console.log(`✔ Loaded ${positions.length / 3} nodes.`);
}

// 🚀 **解析 `smoothed_edges.tsv` 并渲染 3D 线**
function parseEdges(text) {
    console.log("Parsing smoothed_edges.tsv...");
    const lines = text.trim().split("\n").slice(1);
    const material = new THREE.LineBasicMaterial({ color: 0xff0000, linewidth: 0.5, transparent: true, opacity: 0.4 });

    lines.forEach(edgeData => {
        const parts = edgeData.split("\t");
        if (parts.length < 3 * 8 + 2) return;

        let positions = [];
        for (let i = 2; i < parts.length; i += 3) {
            const x = parseFloat(parts[i]);
            const y = parseFloat(parts[i + 1]);
            const z = parseFloat(parts[i + 2]);
            positions.push(new THREE.Vector3(x, y, z));
        }

        const geometry = new THREE.BufferGeometry().setFromPoints(positions);
        let edgeLine = new THREE.Line(geometry, material);
        scene.add(edgeLine);
    });

    console.log(`✔ Loaded ${lines.length} edges.`);
}

// 🚀 **动画循环**
export function animate() {
    stats.begin();  // ✅ 开始 FPS 计算

    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);

    stats.end();  // ✅ 结束 FPS 计算
}