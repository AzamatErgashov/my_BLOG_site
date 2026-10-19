
(() => {
    const layer = document.getElementById("image-trail");

    if (!layer) return;

    const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    if (prefersReducedMotion) return;

    const imageBase = layer.dataset.imageBase;
    const imageCount = Number(layer.dataset.imageCount) || 30;
    const extension = layer.dataset.imageExtension || "jpg";

    if (!imageBase || imageCount < 1) return;

    let lastX = null;
    let lastY = null;
    let lastSpawnTime = 0;
    let nextImageIndex = 1;

    const randomBetween = (min, max) =>
        Math.random() * (max - min) + min;

    function createTrailImage(x, y, isTouch) {
        const image = new Image();

        image.className = "image-trail-item";
        image.alt = "";
        image.draggable = false;
        image.decoding = "async";

        const imageNumber = String(nextImageIndex).padStart(2, "0");

        image.style.left = `${x}px`;
        image.style.top = `${y}px`;

        image.style.width = isTouch
            ? `${randomBetween(58, 88)}px`
            : `${randomBetween(78, 128)}px`;

        image.style.setProperty(
            "--rotation",
            `${randomBetween(-13, 13)}deg`
        );

        image.style.setProperty(
            "--drift-x",
            `${randomBetween(-30, 30)}px`
        );

        image.style.setProperty(
            "--drift-y",
            `${randomBetween(-25, 30)}px`
        );

        image.style.setProperty(
            "--trail-opacity",
            isTouch
                ? randomBetween(0.55, 0.60).toFixed(2)
                : randomBetween(0.55, 0.60).toFixed(2)
        );

        image.addEventListener("load", () => {
            const maxVisibleImages = isTouch ? 4 : 7;

            while (layer.children.length >= maxVisibleImages) {
                layer.firstElementChild?.remove();
            }

            layer.appendChild(image);
        }, { once: true });

        image.addEventListener("animationend", () => {
            image.remove();
        }, { once: true });

        image.addEventListener("error", () => {
            image.remove();
        }, { once: true });

        image.src = `${imageBase}${imageNumber}.${extension}`;

        nextImageIndex = (nextImageIndex % imageCount) + 1;
    }

    window.addEventListener("pointermove", (event) => {
        const pointerType = event.pointerType;

        if (
            pointerType !== "mouse" &&
            pointerType !== "touch" &&
            pointerType !== "pen"
        ) {
            return;
        }

        const isTouch = pointerType !== "mouse";
        const now = performance.now();

        const minDistance = isTouch ? 40 : 65;
        const minInterval = isTouch ? 90 : 55;

        if (lastX !== null && lastY !== null) {
            const dx = event.clientX - lastX;
            const dy = event.clientY - lastY;
            const distance = Math.hypot(dx, dy);

            if (distance < minDistance) return;
            if (now - lastSpawnTime < minInterval) return;
        }

        lastX = event.clientX;
        lastY = event.clientY;
        lastSpawnTime = now;

        createTrailImage(
            event.clientX,
            event.clientY,
            isTouch
        );
    }, { passive: true });
})();
