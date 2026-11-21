import * as THREE from 'three';
import { GLTFLoader } from './vendor/GLTFLoader.js';

const page = document.getElementById('mgmsLogin');
const canvas = document.getElementById('loginScene');

if (page && canvas) {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const clock = new THREE.Clock();
    const pointer = new THREE.Vector2();
    const target = new THREE.Vector2();
    let renderer;
    let scene;
    let camera;
    let mixer;
    let frameId = 0;
    let resizeObserver;
    let disposed = false;
    let dust;
    let dustPositions;

    function showFallback(error) {
        if (error) console.error('MGMS 3D login scene unavailable; showing the lightweight oilfield fallback.', error);
        page.classList.add('login-scene-fallback');
        page.classList.remove('login-scene-ready');
        canvas.hidden = true;
    }

    function disposeObject(root) {
        const geometries = new Set();
        const materials = new Set();
        const textures = new Set();
        root.traverse((object) => {
            if (!object.isMesh && !object.isPoints && !object.isLine) return;
            if (object.geometry) geometries.add(object.geometry);
            for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
                if (!material) continue;
                materials.add(material);
                for (const value of Object.values(material)) {
                    if (value?.isTexture) textures.add(value);
                }
            }
        });
        for (const texture of textures) texture.dispose();
        for (const material of materials) material.dispose();
        for (const geometry of geometries) geometry.dispose();
    }

    function stopScene() {
        if (disposed) return;
        disposed = true;
        if (frameId) cancelAnimationFrame(frameId);
        resizeObserver?.disconnect();
        window.removeEventListener('resize', resize);
        document.removeEventListener('visibilitychange', onVisibilityChange);
        window.removeEventListener('pointermove', onPointerMove);
        window.removeEventListener('pagehide', stopScene);
        canvas.removeEventListener('webglcontextlost', onContextLost);
        mixer?.stopAllAction();
        if (scene) disposeObject(scene);
        if (renderer) {
            renderer.renderLists.dispose();
            renderer.dispose();
            renderer.forceContextLoss();
        }
    }

    function onContextLost(event) {
        event.preventDefault();
        showFallback(new Error('WebGL context was lost.'));
        stopScene();
    }

    function onVisibilityChange() {
        if (document.hidden) {
            if (frameId) cancelAnimationFrame(frameId);
            frameId = 0;
        } else if (!disposed && !frameId) {
            clock.getDelta();
            frameId = requestAnimationFrame(renderFrame);
        }
    }

    function onPointerMove(event) {
        const bounds = canvas.getBoundingClientRect();
        if (!bounds.width || !bounds.height) return;
        pointer.set(
            THREE.MathUtils.clamp((event.clientX - bounds.left) / bounds.width * 2 - 1, -1, 1),
            THREE.MathUtils.clamp((event.clientY - bounds.top) / bounds.height * 2 - 1, -1, 1)
        );
    }

    function resize() {
        if (!renderer || !camera) return;
        const width = Math.max(1, canvas.clientWidth);
        const height = Math.max(1, canvas.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.position.z = width < 430 ? 5.9 : 5.25;
        camera.updateProjectionMatrix();
    }

    function renderFrame() {
        if (disposed || document.hidden) {
            frameId = 0;
            return;
        }
        const delta = Math.min(clock.getDelta(), 0.05);
        if (mixer && !reducedMotion) mixer.update(delta);
        if (dust && dustPositions) {
            for (let index = 1; index < dustPositions.length; index += 3) {
                dustPositions[index] += delta * 0.035;
                if (dustPositions[index] > 2.5) dustPositions[index] = 0.08;
            }
            dust.geometry.attributes.position.needsUpdate = true;
        }
        if (!reducedMotion) {
            target.x = pointer.x * 0.12;
            target.y = -pointer.y * 0.055;
            camera.position.x += (target.x - camera.position.x) * 0.025;
            camera.position.y += (1.72 + target.y - camera.position.y) * 0.025;
            camera.lookAt(0, 1.12, 0);
        }
        renderer.render(scene, camera);
        frameId = requestAnimationFrame(renderFrame);
    }

    async function startScene() {
        try {
            renderer = new THREE.WebGLRenderer({
                canvas,
                alpha: true,
                antialias: true,
                powerPreference: 'low-power'
            });
            renderer.setClearColor(0x000000, 0);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
            renderer.outputColorSpace = THREE.SRGBColorSpace;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.25;
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;

            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x071a33, 0.055);
            camera = new THREE.PerspectiveCamera(36, 1, 0.1, 80);
            camera.position.set(0, 1.72, 5.25);
            camera.lookAt(0, 1.12, 0);

            scene.add(new THREE.HemisphereLight(0xb9dbf8, 0x091426, 1.15));
            const key = new THREE.DirectionalLight(0xdcecff, 3.2);
            key.position.set(-2.8, 5.5, 4.2);
            key.castShadow = true;
            key.shadow.mapSize.set(1024, 1024);
            key.shadow.camera.left = -4;
            key.shadow.camera.right = 4;
            key.shadow.camera.top = 4;
            key.shadow.camera.bottom = -2;
            key.shadow.bias = -0.00025;
            scene.add(key);
            const blueLight = new THREE.PointLight(0x168bff, 2.5, 8, 2);
            blueLight.position.set(-2.5, 1.8, 1.3);
            scene.add(blueLight);
            const goldLight = new THREE.PointLight(0xd6a84f, 1.2, 6, 2);
            goldLight.position.set(2.4, 2.2, -1.7);
            scene.add(goldLight);

            const ground = new THREE.Mesh(
                new THREE.PlaneGeometry(24, 24),
                new THREE.MeshStandardMaterial({ color: 0x071a2a, roughness: 0.94, metalness: 0.12 })
            );
            ground.rotation.x = -Math.PI / 2;
            ground.position.y = -0.025;
            ground.receiveShadow = true;
            scene.add(ground);
            const grid = new THREE.GridHelper(18, 36, 0x28618a, 0x214867);
            grid.position.y = -0.012;
            for (const material of Array.isArray(grid.material) ? grid.material : [grid.material]) {
                material.transparent = true;
                material.opacity = 0.18;
                material.depthWrite = false;
            }
            scene.add(grid);

            const dustCount = 46;
            dustPositions = new Float32Array(dustCount * 3);
            for (let index = 0; index < dustCount; index += 1) {
                dustPositions[index * 3] = (Math.random() - 0.5) * 5.5;
                dustPositions[index * 3 + 1] = Math.random() * 2.5;
                dustPositions[index * 3 + 2] = (Math.random() - 0.5) * 2.2 - 0.6;
            }
            const dustGeometry = new THREE.BufferGeometry();
            dustGeometry.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3));
            dust = new THREE.Points(dustGeometry, new THREE.PointsMaterial({
                color: 0x94cfff,
                size: 0.018,
                transparent: true,
                opacity: 0.55,
                depthWrite: false
            }));
            scene.add(dust);

            resize();
            const modelUrl = canvas.dataset.modelUrl;
            if (!modelUrl) throw new Error('The engineer model URL is missing.');
            const gltf = await new GLTFLoader().loadAsync(modelUrl);
            if (disposed) {
                disposeObject(gltf.scene);
                return;
            }
            const model = gltf.scene;
            model.traverse((object) => {
                if (object.isMesh) {
                    object.castShadow = true;
                    object.receiveShadow = true;
                    if (object.material) object.material.needsUpdate = true;
                }
            });
            scene.add(model);

            const walkClip = gltf.animations.find((clip) => clip.name === 'Walk to equipment');
            const inspectClip = gltf.animations.find((clip) => clip.name === 'Kneel, inspect and rise');
            if (!walkClip || !inspectClip) throw new Error('The engineer model is missing its walk or inspection animation.');
            mixer = new THREE.AnimationMixer(model);
            const walk = mixer.clipAction(walkClip);
            const inspect = mixer.clipAction(inspectClip);
            walk.setLoop(THREE.LoopOnce, 1);
            walk.clampWhenFinished = true;
            inspect.setLoop(THREE.LoopRepeat, Infinity);
            inspect.clampWhenFinished = false;
            if (!reducedMotion) {
                walk.play();
                mixer.addEventListener('finished', (event) => {
                    if (event.action === walk && !disposed) {
                        inspect.reset().play();
                        inspect.crossFadeFrom(walk, 0.65, true);
                    }
                });
            }

            if ('ResizeObserver' in window) {
                resizeObserver = new ResizeObserver(resize);
                resizeObserver.observe(canvas);
            } else {
                window.addEventListener('resize', resize);
            }
            if (!reducedMotion) window.addEventListener('pointermove', onPointerMove, { passive: true });
            window.addEventListener('pagehide', stopScene, { once: true });
            document.addEventListener('visibilitychange', onVisibilityChange);
            canvas.addEventListener('webglcontextlost', onContextLost, { once: true });
            page.classList.remove('login-scene-fallback');
            page.classList.add('login-scene-ready');
            frameId = requestAnimationFrame(renderFrame);
        } catch (error) {
            showFallback(error);
            stopScene();
        }
    }

    startScene();
}
