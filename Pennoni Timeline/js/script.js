/* ====================== */
/* Step 01 - Render Logic */
/* ====================== */
function initTimeline() {
	const lenis = new Lenis({ smooth: true });
	lenis.on("scroll", ScrollTrigger.update);

	gsap.ticker.add((t) => lenis.raf(t * 1000));
	gsap.ticker.lagSmoothing(0);

	const timelineRoot = document.querySelector('[data-app="timeline"]');
	if (!timelineRoot) return;

	const panelsList = timelineRoot.querySelector("[data-panels]");
	const yearsRail = timelineRoot.querySelector(
		'[data-timeline="years-wrapper"]'
	);
	if (!panelsList || !yearsRail) return;

	// ---- DATA ----
	const timelineItems = [
		{
			id: "KIKI",
			year: "1966-67",
			theme: "kikis",
			tiles: [
				{
					type: "image",
					pos: "pos-top-left-10",
					w: "25vw",
					ratio: "16 / 12",
					src:
						"assets/1966.jpg",
					alt: "Kiki's Delivery Service",
					depth: 10,
					z: 1
				},
				{
					type: "text",
					pos: "pos-top-right",
					w: "500px",
					ratio: "16 / 9",
					heading: "1966",
					copy:
						"<b>• C.R. Pennoni began the firm as a one-person structural engineering practice in West Philadelphia, PA at 67th Street and Haverford Avenue.</b>" +
						"\n\n• The first three part-time hires were engineering students from Temple University\n\n• Headquarters (HQ) moved to Center City office at 17th and Cherry Streets in Philadelphia, PA to serve increased client base" +
						"\n\n• First Private Client - C&J Construction Company, Philadelphia, PA" +
						"\n\n• First Government Project - City of Philadelphia Police Station at 20th and Pennsylvania Avenue as a sub to Gene Dichter, Architect",
					depth: 20,
					z: 4
				},
				{
					type: "text",
					pos: "pos-bottom-right",
					w: "500px",
					ratio: "16 / 9",
					heading: "1967",
					copy:
						"• Business entity changed from sole practioner to business corpora􀆟on on July 21, 1967" +
						"\n\n• Expanded out of Pennsylvania with first New Jersey office in Cinnaminson, Burlington County" +
						"\n\n• First Employee - Leo Storniolo",
					depth: 20,
					z: 4
				},
				{
					type: "image",
					pos: "pos-bottom-left",
					w: "35vw",
					ratio: "16 / 9",
					src:
						"assets/1967.png",
					alt: "Chuck Pennoni",
					depth: 25,
					z: 1
				}
			]
		},
		{
			id: "MNT",
			year: "1988",
			theme: "totoro",
			tiles: [
				{
					type: "image",
					pos: "pos-top-left",
					w: "280px",
					ratio: "9 / 16",
					src: "assets/1973.png",
					poster:
						"assets/1973.png",
					alt: "1973",
					depth: 5,
					z: 2
				},
				{
					type: "video",
					pos: "pos-top-right",
					w: "280px",
					ratio: "1 / 1",
					src: "/mnt-01.mp4",
					poster:
						"https://i.pinimg.com/1200x/5a/44/ba/5a44baee0bf66e04af973ed3580e84dc.jpg",
					alt: "My Neighbor Totoro",
					depth: 10,
					z: 2
				},
				{
					type: "image",
					pos: "pos-bottom-right-10",
					w: "280px",
					ratio: "1 / 1",
					src:
						"https://i.pinimg.com/736x/73/6c/a1/736ca1530ccfd941af54feb330ba87c4.jpg",
					alt: "My Neighbor Totoro",
					depth: 30,
					z: 3
				},
				{
					type: "text",
					pos: "pos-bottom-left-10",
					w: "500px",
					ratio: "16 / 9",
					heading: "My Neighbor Totoro",
					copy:
						"My Neighbor Totoro is a 1988 Japanese animated fantasy film written and directed by Hayao Miyazaki and animated by Studio Ghibli for Tokuma Shoten.",
					depth: 25,
					z: 4
				}
			]
		},
		{
			id: "SPA",
			year: "2001",
			theme: "spiritedAway",
			tiles: [
				{
					type: "image",
					pos: "pos-bottom-left",
					w: "25vw",
					ratio: "16 / 9",
					src:
						"https://i.pinimg.com/1200x/f4/11/f8/f411f81d47185322cd4ae4e7ff451c3e.jpg",
					alt: "Spirited Away",
					depth: 15,
					z: 1
				},
				{
					type: "video",
					pos: "pos-bottom-right",
					w: "280px",
					ratio: "9 / 16",
					src: "/spa-01.mp4",
					poster:
						"https://i.pinimg.com/1200x/f4/11/f8/f411f81d47185322cd4ae4e7ff451c3e.jpg",
					alt: "Spirited Away",
					depth: 5,
					z: 2
				},
				{
					type: "image",
					pos: "pos-center-center",
					w: "400px",
					ratio: "16 / 9",
					src:
						"https://i.pinimg.com/1200x/4e/da/12/4eda126a3de0561a77b98e7ed25533f2.jpg",
					alt: "Spirited Away",
					depth: 20,
					z: 1
				},
				{
					type: "text",
					pos: "pos-top-quarter-left",
					w: "450px",
					ratio: "1 / 1",
					heading: "Spirited Away",
					copy:
						"Spirited Away is a 2001 Japanese animated fantasy film written and directed by Hayao Miyazaki. It was produced by Toshio Suzuki, animated by Studio Ghibli, and distributed by Toho.",
					depth: 10,
					z: 2
				}
			]
		},
		{
			id: "HOWLS",
			year: "2004",
			theme: "howls",
			tiles: [
				{
					type: "image",
					pos: "pos-bottom-center-lg-10",
					w: "15vw",
					ratio: "9 / 16",
					src:
						"https://i.pinimg.com/1200x/95/45/28/95452872487f4d5756d33d6c031639b4.jpg",
					alt: "Howl's Moving Castle",
					depth: 30,
					z: 1
				},
				{
					type: "video",
					pos: "pos-bottom-right-10",
					w: "20vw",
					ratio: "1 / 1",
					src: "/hmc-01.mp4",
					poster:
						"https://i.pinimg.com/1200x/95/45/28/95452872487f4d5756d33d6c031639b4.jpg",
					alt: "Howl's Moving Castle",
					depth: 20,
					z: 2
				},
				{
					type: "video",
					pos: "pos-bottom-left-0",
					w: "30vw",
					ratio: "16 / 9",
					src: "/hmc-02.mp4",
					poster:
						"https://i.pinimg.com/1200x/95/45/28/95452872487f4d5756d33d6c031639b4.jpg",
					alt: "Howl's Moving Castle",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-top-left",
					w: "500px",
					ratio: "16 / 9",
					heading: "Howl's Moving Castle",
					copy:
						"Howl's Moving Castle is a 2004 Japanese animated fantasy film written and directed by Hayao Miyazaki, based on Diana Wynne Jones' 1986 novel.",
					depth: 25,
					z: 4
				}
			]
		}
	];

	const fallbackSvgDataUri = (label = "Missing") => {
		const svg = `
      <svg xmlns="http://www.w3.org/2000/svg" width="900" height="700">
        <defs>
          <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
            <stop stop-color="#e8e8e8" offset="0"/>
            <stop stop-color="#cfcfcf" offset="1"/>
          </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#g)"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
              font-family="system-ui" font-size="34" fill="#666">
          ${label}
        </text>
      </svg>
    `;
		return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
	};

	const el = (tag, className) => {
		const node = document.createElement(tag);
		if (className) node.className = className;
		return node;
	};

	// Put theme into dataset so Part-3 can work without knowing JSON
	const applyThemeData = (panelEl, theme) => {
		if (!theme) return;

		if (typeof theme === "string") {
			panelEl.dataset.theme = theme;
			return;
		}

		panelEl.dataset.theme = "custom";
		const map = {
			bg: "themeBg",
			fg: "themeFg",
			muted: "themeMuted",
			year: "themeYear",
			cardBg: "themeCardBg",
			cardBorder: "themeCardBorder",
			yearLayerOpacity: "themeYearLayerOpacity"
		};

		for (const [key, dataKey] of Object.entries(map)) {
			const val = theme[key];
			if (val == null) continue;
			panelEl.dataset[dataKey] = String(val);
		}
	};

	const buildTile = (tileData) => {
		const tileEl = el("div", `tile ${tileData.pos || ""}`.trim());

		tileEl.style.setProperty("--w", tileData.w || "30vw");
		tileEl.style.setProperty("--ratio", tileData.ratio || "16 / 9");
		tileEl.style.setProperty("--z", String(tileData.z ?? 1));

		tileEl.dataset.depth = String(tileData.depth ?? 0);

		const boxEl = el("div", "tile__box");

		switch (tileData.type) {
			case "text": {
				boxEl.classList.add("text-only__box");

				const textEl = el("div", "tile__text");
				textEl.dataset.reveal = "text";

				const h = el("h3");
				h.textContent = tileData.heading || "";

				const p = el("p");
				p.innerHTML = (tileData.copy || "").replace(/\n\n/g, "<br><br>");

				textEl.append(h, p);
				boxEl.appendChild(textEl);
				break;
			}
			case "image": {
				const img = el("img", "tile__media");
				img.loading = "lazy";
				img.decoding = "async";
				img.alt = tileData.alt || "";
				img.src = tileData.src;
				img.dataset.reveal = "media";

				img.onerror = () => {
					img.onerror = null;
					img.src = fallbackSvgDataUri(tileData.alt || "Image");
				};

				boxEl.appendChild(img);
				break;
			}
			case "video": {
				const video = el("video", "tile__media");
				video.muted = true;
				video.loop = true;
				video.playsInline = true;
				video.autoplay = true;
				video.preload = "metadata";
				if (tileData.poster) video.poster = tileData.poster;
				video.dataset.reveal = "video";

				const source = el("source");
				source.src = tileData.src;
				source.type = tileData.src?.endsWith(".webm") ? "video/webm" : "video/mp4";

				video.appendChild(source);
				boxEl.appendChild(video);
				break;
			}
		}

		tileEl.appendChild(boxEl);
		return tileEl;
	};

	const mountPanels = () => {
		const listFrag = document.createDocumentFragment();

		for (const item of timelineItems) {
			const li = el("li");

			const panel = el("article", "panel");
			panel.dataset.entryId = item.id;
			applyThemeData(panel, item.theme);

			const stage = el("div", "panel__stage");
			for (const tileData of item.tiles) stage.appendChild(buildTile(tileData));

			panel.appendChild(stage);
			li.appendChild(panel);
			listFrag.appendChild(li);
		}

		panelsList.appendChild(listFrag);
	};

	const mountYears = () => {
		const yearsFrag = document.createDocumentFragment();

		for (const item of timelineItems) {
			const yearEl = el("div", "year");
			yearEl.dataset.timeline = "year";

			for (const ch of String(item.year)) {
				const span = el("span", "char");
				span.textContent = ch;
				yearEl.appendChild(span);
			}

			yearsFrag.appendChild(yearEl);
		}

		yearsRail.appendChild(yearsFrag);
	};

	mountPanels();
	mountYears();
}

/* ====================== */
/* Step 02 - Reveal Logic */
/* ====================== */
function initRevealAndParallax() {
	const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)")
		.matches;

	if (!window.gsap || !window.ScrollTrigger) {
		console.warn("GSAP/ScrollTrigger missing for reveal.");
		return;
	}
	gsap.registerPlugin(ScrollTrigger);

	const showInstant = (node) => {
		node.style.opacity = "1";
		node.style.transform = "none";
	};

	const animateReveal = (node, { kind, triggerStart, duration }) => {
		if (reduceMotion) return showInstant(node);

		const tileTrigger = node.closest(".tile") || node;

		if (kind === "media") {
			gsap.fromTo(
				node,
				{ opacity: 0, scale: 1.1 },
				{
					opacity: 1,
					scale: 1,
					duration,
					ease: "power2.out",
					scrollTrigger: {
						trigger: tileTrigger,
						start: triggerStart,
						once: true
					}
				}
			);
			return;
		}

		// kind === "text"
		gsap.to(node, {
			opacity: 1,
			y: 0,
			duration,
			ease: "power2.out",
			scrollTrigger: {
				trigger: tileTrigger,
				start: triggerStart,
				once: true
			}
		});
	};

	const whenImgReady = (img, cb) => {
		if (img.complete && img.naturalWidth > 0) cb();
		else img.addEventListener("load", cb, { once: true });
	};

	// Images
	document.querySelectorAll('[data-reveal="media"]').forEach((img) => {
		whenImgReady(img, () =>
			animateReveal(img, {
				kind: "media",
				triggerStart: "top 60%",
				duration: 0.8
			})
		);
	});

	// Text blocks
	document.querySelectorAll('[data-reveal="text"]').forEach((textBlock) => {
		if (!reduceMotion) gsap.set(textBlock, { opacity: 0, y: 24 });

		animateReveal(textBlock, {
			kind: "text",
			triggerStart: "top 60%",
			duration: 0.7
		});
	});

	// Videos: reveal + auto play/pause based on visibility
	document.querySelectorAll('[data-reveal="video"]').forEach((videoEl) => {
		const tileTrigger = videoEl.closest(".tile") || videoEl;

		const initVideo = () => {
			animateReveal(videoEl, {
				kind: "media",
				triggerStart: "top 60%",
				duration: 0.8
			});

			ScrollTrigger.create({
				trigger: tileTrigger,
				start: "top center",
				end: "bottom top",
				onEnter: () => videoEl.play().catch(() => {}),
				onEnterBack: () => videoEl.play().catch(() => {}),
				onLeave: () => videoEl.pause(),
				onLeaveBack: () => videoEl.pause()
			});
		};

		if (videoEl.readyState >= 1) initVideo();
		else videoEl.addEventListener("loadedmetadata", initVideo, { once: true });
	});

	// Tile Parallax
	gsap.utils.toArray(".panel").forEach((panelEl) => {
		panelEl.querySelectorAll(".tile").forEach((tileEl) => {
			const parallaxDepth = Number(tileEl.dataset.depth || 18);

			gsap.fromTo(
				tileEl,
				{ y: -parallaxDepth },
				{
					y: parallaxDepth * 5,
					ease: "none",
					scrollTrigger: {
						trigger: panelEl,
						start: "top center",
						end: "bottom center",
						scrub: true
					}
				}
			);
		});
	});

	requestAnimationFrame(() => ScrollTrigger.refresh());
}

/* ===================== */
/* Step 03 - Theme Logic */
/* ===================== */
function initYearSwapAndTheme() {
	const themePresets = {
		kikis: {
			bg: "#264831",
			fg: "#264831",
			muted: "#4f5563",
			year: "#ffece6",
			cardBg: "#ffffffcc",
			cardBorder: "transparent",
			yearLayerOpacity: 0.4
		},
		totoro: {
			bg: "#e4e4e4",
			fg: "#432f23",
			muted: "#6d5546",
			year: "#64441c",
			cardBg: "#ffffffcc",
			cardBorder: "transparent",
			yearLayerOpacity: 0.43
		},
		spiritedAway: {
			bg: "#79b0b4",
			fg: "#79b0b4",
			muted: "#ffffff",
			year: "#012d31",
			cardBg: "#12151ccc",
			cardBorder: "transparent",
			yearLayerOpacity: 0.33
		},
		howls: {
			bg: "#edf8f4",
			fg: "#1d3535",
			muted: "#4b6868",
			year: "#1d3535",
			cardBg: "#ffffffcc",
			cardBorder: "transparent",
			yearLayerOpacity: 0.42
		}
	};

	const panelEls = gsap.utils.toArray(".panel");
	const yearEls = gsap.utils.toArray('[data-timeline="year"]');
	if (!panelEls.length || !yearEls.length) return;

	const getPanelTheme = (panelEl) => {
		const themeName = panelEl.dataset.theme;

		// Named theme
		if (themeName && themeName !== "custom") {
			return themePresets[themeName] || themePresets.light;
		}

		// Custom theme from dataset
		const customTheme = {
			bg: panelEl.dataset.themeBg,
			fg: panelEl.dataset.themeFg,
			muted: panelEl.dataset.themeMuted,
			year: panelEl.dataset.themeYear,
			cardBg: panelEl.dataset.themeCardBg,
			cardBorder: panelEl.dataset.themeCardBorder,
			yearLayerOpacity: panelEl.dataset.themeYearLayerOpacity
				? Number(panelEl.dataset.themeYearLayerOpacity)
				: undefined
		};

		// Merge onto light defaults, ignoring null/undefined
		return {
			...themePresets.light,
			...Object.fromEntries(
				Object.entries(customTheme).filter(([, v]) => v != null)
			)
		};
	};

	const setCssVars = (theme, { animate = true } = {}) => {
		const root = document.documentElement;

		const vars = {
			"--bg": theme.bg,
			"--fg": theme.fg,
			"--muted": theme.muted,
			"--year": theme.year,
			"--cardBg": theme.cardBg,
			"--cardBorder": theme.cardBorder,
			"--yearLayerOpacity": String(theme.yearLayerOpacity ?? 0.4)
		};

		if (!animate) {
			for (const [k, v] of Object.entries(vars)) root.style.setProperty(k, v);
			return;
		}

		gsap.to(root, {
			duration: 0.45,
			ease: "power2.out",
			...vars
		});
	};

	const initYearChars = () => {
		yearEls.forEach((yearEl, i) => {
			const chars = yearEl.querySelectorAll(".char");
			gsap.set(chars, {
				yPercent: i === 0 ? 0 : 100,
				opacity: i === 0 ? 1 : 0
			});
		});
	};

	const setupYearSwap = () => {
		panelEls.forEach((panelEl, i) => {
			if (i === 0) return;

			const prevYearEl = yearEls[i - 1];
			const nextYearEl = yearEls[i];
			if (!prevYearEl || !nextYearEl) return;

			const prevChars = prevYearEl.querySelectorAll(".char");
			const nextChars = nextYearEl.querySelectorAll(".char");

			gsap
				.timeline({
					scrollTrigger: {
						trigger: panelEl,
						start: "top bottom",
						end: "center center",
						scrub: 1
						// markers: true,
					}
				})
				.to(
					prevChars,
					{
						yPercent: -100,
						opacity: 0,
						duration: 4,
						stagger: 1,
						ease: "cubic-bezier(0.23, 1, 0.32, 1)"
					},
					0
				)
				.to(
					nextChars,
					{
						yPercent: 0,
						autoAlpha: 1,
						duration: 4,
						stagger: 1,
						ease: "cubic-bezier(0.23, 1, 0.32, 1)"
					},
					0
				);
		});
	};

	const setupThemeSwitch = () => {
		panelEls.forEach((panelEl) => {
			ScrollTrigger.create({
				trigger: panelEl,
				start: "top center",
				end: "bottom center",
				onEnter: () => setCssVars(getPanelTheme(panelEl), { animate: true }),
				onEnterBack: () => setCssVars(getPanelTheme(panelEl), { animate: true }),
				onLeave: () => setCssVars(getPanelTheme(panelEl), { animate: true }),
				onLeaveBack: () => setCssVars(getPanelTheme(panelEl), { animate: true })
			});
		});
	};

	initYearChars();
	setupYearSwap();
	setupThemeSwitch();

	// Apply first theme immediately
	setCssVars(getPanelTheme(panelEls[0]), { animate: false });

	requestAnimationFrame(() => ScrollTrigger.refresh());
}

document.addEventListener("DOMContentLoaded", () => {
	initTimeline();
	initRevealAndParallax();
	initYearSwapAndTheme();
});
