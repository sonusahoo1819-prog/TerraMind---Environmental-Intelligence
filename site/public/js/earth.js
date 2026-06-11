// TerraMind 3D Earth Canvas Rendering
(function() {
    const canvas = document.getElementById('earth-canvas');
    if (!canvas) return;

    const width = canvas.parentElement.clientWidth;
    const height = canvas.parentElement.clientHeight;

    const scene = new THREE.Scene();
    
    // Perspective Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 6;

    // WebGL Renderer
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x00C26E, 1.2);
    dirLight1.position.set(5, 5, 5);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x4DAFFF, 0.8);
    dirLight2.position.set(-5, -5, 5);
    scene.add(dirLight2);

    // Earth Group
    const earthGroup = new THREE.Group();
    scene.add(earthGroup);

    // Earth Wireframe Grid (Futuristic Tech Vibe)
    const earthGeo = new THREE.SphereGeometry(2, 40, 40);
    const earthMat = new THREE.MeshPhongMaterial({
        color: 0x0A1C14,
        emissive: 0x00C26E,
        emissiveIntensity: 0.2,
        shininess: 30,
        wireframe: true,
        transparent: true,
        opacity: 0.8
    });
    const earth = new THREE.Mesh(earthGeo, earthMat);
    earthGroup.add(earth);

    // Inner glowing sphere (solid core)
    const coreGeo = new THREE.SphereGeometry(1.95, 32, 32);
    const coreMat = new THREE.MeshBasicMaterial({
        color: 0x070E1A,
        transparent: true,
        opacity: 0.9
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    earthGroup.add(core);

    // Outer Atmosphere Glow
    const atmosGeo = new THREE.SphereGeometry(2.2, 32, 32);
    const atmosMat = new THREE.MeshBasicMaterial({
        color: 0x00C26E,
        transparent: true,
        opacity: 0.08,
        side: THREE.BackSide
    });
    const atmosphere = new THREE.Mesh(atmosGeo, atmosMat);
    scene.add(atmosphere);

    // Emission / Sensor Rings (orbiting lines)
    const ringGroup = new THREE.Group();
    earthGroup.add(ringGroup);

    const createRing = (radius, color, rotationX, rotationY) => {
        const ringGeo = new THREE.RingGeometry(radius, radius + 0.02, 64);
        const ringMat = new THREE.MeshBasicMaterial({
            color: color,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.3
        });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = rotationX;
        ring.rotation.y = rotationY;
        ringGroup.add(ring);
    };

    createRing(2.4, 0x00C26E, Math.PI / 2, 0.2);
    createRing(2.6, 0x4DAFFF, Math.PI / 4, -0.4);

    // Orbiting Data Particles
    const particleGeo = new THREE.BufferGeometry();
    const particleCount = 150;
    const posArray = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
        // Distribute points on a sphere shell
        const u = Math.random();
        const v = Math.random();
        const theta = u * 2.0 * Math.PI;
        const phi = Math.acos(2.0 * v - 1.0);
        const r = 2.2 + Math.random() * 0.4; // Shell thickness

        posArray[i] = r * Math.sin(phi) * Math.cos(theta);
        posArray[i + 1] = r * Math.sin(phi) * Math.sin(theta);
        posArray[i + 2] = r * Math.cos(phi);
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particleMat = new THREE.PointsMaterial({
        size: 0.04,
        color: 0xB7FF4A,
        transparent: true,
        opacity: 0.8
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    earthGroup.add(particles);

    // Mouse Interaction Parallax
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - window.innerWidth / 2) / 1000;
        mouseY = (e.clientY - window.innerHeight / 2) / 1000;
    });

    // Animation Loop
    const animate = () => {
        requestAnimationFrame(animate);

        // Smooth rotation
        earth.rotation.y += 0.002;
        ringGroup.rotation.y -= 0.001;
        ringGroup.rotation.x += 0.0005;
        particles.rotation.y += 0.0015;

        // Apply mouse inertia
        targetX += (mouseX - targetX) * 0.05;
        targetY += (mouseY - targetY) * 0.05;
        
        earthGroup.rotation.y += targetX * 0.02;
        earthGroup.rotation.x += targetY * 0.02;

        renderer.render(scene, camera);
    };

    // Resize Handler
    window.addEventListener('resize', () => {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        
        renderer.setSize(w, h);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    });

    animate();
})();
