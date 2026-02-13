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
					pos: "pos-bottom-left",
					w: "20vw",
					ratio: "16 / 12",
					src:
						"assets/1966.jpg",
					alt: "Pennoni Associates Inc Logo",
					title: "Pennoni Associates Inc Logo",
					depth: 10,
					z: 1
				},
				{
					type: "text",
					pos: "pos-top-right-10",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1966",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li><b>C.R. Pennoni began the firm as a one-person structural engineering practice in West Philadelphia, PA at 67th Street and Haverford Avenue.</b></li>" +
						"<li>The first three part-time hires were engineering students from Temple University\n\n• Headquarters (HQ) moved to Center City office at 17th and Cherry Streets in Philadelphia, PA to serve increased client base</li>" +
						"<li>First Private Client - C&J Construction Company, Philadelphia, PA</li>" +
						"<li>First Government Project - City of Philadelphia Police Station at 20th and Pennsylvania Avenue as a sub to Gene Dichter, Architect</li></ul>",
					depth: 20,
					z: 4
				},
				{
					type: "text",
					pos: "pos-bottom-right",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1967",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Business entity changed from sole practitioner to business corporation on July 21, 1967</li>" +
						"<li>Expanded out of Pennsylvania with first New Jersey office in Cinnaminson, Burlington County</li>" +
						"<li>First Employee - Leo Storniolo</li></ul>",
					depth: 20,
					z: 4
				},
				{
					type: "image",
					pos: "pos-top-left-10",
					w: "35vw",
					ratio: "16 / 9",
					src:
						"assets/1967.png",
					alt: "Chuck Pennoni at a desk in 1967",
					title: "Chuck Pennoni at a desk in 1967",
					depth: 25,
					z: 1
				}
			]
		},
		{
			id: "MNT",
			year: "1968-71",
			theme: "howls",
			tiles: [
				{
					type: "text",
					pos: "pos-top-left",
					w: "40vw",
					ratio: "9 / 16",
					heading: "1968",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>HQ relocated to 1920 Chestnut Street in Philadelphia, PA</li>" +
						"<li>First international project was a feasibility study on the Mediterranean coast in Spain</li></ul>",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-middle-left",
					w: "40vw",
					ratio: "1 / 1",
					heading: "1970",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Leo F. O’Connor, PE joined the firm as the first Vice President</li>" +
						"<li>First Government Client - Township of Falls Authority, Fallsington, Bucks County, PA</li></ul>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-left-25",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1971",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Expanded to Bucks County with an office in Langhorne, PA</li></ul>",
					depth: 20,
					z: 4
				},
			]
		},
		{
			id: "SPA",
			year: "1972-77",
			theme: "spiritedAway",
			tiles: [
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1973",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>HQ relocated to a historic four-story brownstone at 2006 Walnut Street near Rittenhouse Square in Philadelphia, PA</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-bottom-left-2",
					w: "20vw",
					ratio: "9 / 16",
					src: "assets/1973.png",
					poster:
						"assets/1973.png",
					alt: "Main office building. 2006 Walnut Street, Philadelphia, PA",
					title: "Main office building. 2006 Walnut Street, Philadelphia, PA",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-middle-right",
					w: "40vw",
					ratio: "1 / 1",
					heading: "1976",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>A temporary office was established in Iran, following civil engineering work for the new cities of Sarcheshmeh, Lavizon, Kan, and the expansion of Ahwaz.</li>"+
						"<li><b>49 employees</b></li></ul>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-right-3",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1977",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Formed Computer Graphics with Yerkes, Huth and Richardson</li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "HOWLS",
			year: "1978-86",
			theme: "totoro",
			tiles: [
				{
					type: "text",
					pos: "pos-top-left",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1979",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>HQ relocated to renovated top floor of modern office building located at 1911 Arch Street near Logan Circle, Philadelphia, PA</li>"+
						"<li>Acquired the assets of <b>George E. Schilling & Associates</b>, an engineering, surveying, and planning firm in Atlantic County, NJ with history dating back to the early 1800s, which established an Absecon, NJ office</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-top-right",
					w: "35vw",
					ratio: "12 / 10",
					src: "assets/1979.png",
					poster:
						"assets/1979.png",
					alt: "Office building located at 1911 Arch Street near Logan Circle, Philadelphia, PA",
					title: "Office building located at 1911 Arch Street near Logan Circle, Philadelphia, PA",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-middle-left",
					w: "40vw",
					ratio: "1 / 1",
					heading: "1980",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Rothbaum & Davis</b>, consulting structural engineers of Philadelphia, PA, which had an origin traced back to the early 1920s</li></ul>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-left-3",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1986",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Schulcz & Padlasky</b>, consulting and structural engineers of Delaware County, PA founded in 1952</li>"+
						"<li><b>152 employees</b></li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "ALT",
			year: "1987-91",
			theme: "alt",
			tiles: [
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1988",
					copy:
						// "• HQ relocated to the newly renovated historic Middishade Building at 1600 Callowhill Street in the Franklintown area of Philadelphia, PA",
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>HQ relocated to the newly renovated historic Middishade Building at 1600 Callowhill Street in the Franklintown area of Philadelphia, PA</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-top-left",
					w: "35vw",
					ratio: "16 / 6",
					src: "assets/1988.png",
					poster:
						"assets/1988.png",
					alt: "Main office building. 2006 Walnut Street, Philadelphia, PA",
					title: "Main office building. 2006 Walnut Street, Philadelphia, PA",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-middle-right",
					w: "40vw",
					ratio: "1 / 1",
					heading: "1989",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Robert G. Werden Associates, Inc.</b>, an MEP firm organized in 1958, which established an office in Elkins Park, Jenkintown, PA</li></ul>",
						// "\n<img src='assets/Acquisitions/PRIME-WARE.png' alt='Prime Ware logo' style='width: 100px; margin-top: 12px;'>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-right-3",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1991",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Macomber Associates</b>, a bridge and highway engineering firm founded in 1955, which established an office in Camp Hill, PA</li>"+
						"<li>Acquired the assets of <b>Mann-Talley</b>, a survey and engineering firm, which established an office in Wilmington, DE</li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "ALT",
			year: "1992-96",
			theme: "howls",
			tiles: [
				{
					type: "text",
					pos: "pos-top-left",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1996",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Introduced first home page on the World Wide Web</li>"+
						"<li>Expanded to New Hampshire with office in Concord, NH</li>"+
						"<li>Acquired the assets of <b>E.L. Conwell & Co.</b>, an inspection and testing firm established in 1895</li>"+
						"<li>Acquired the assets of <b>Barnes & Jarnis, Inc.</b>, a multidisciplinary consulting engineering firm established in 1953 to expand New England market with office in Boston, MA</li>"+
						"<li>EnviroTEL Japan was incorporated and renamed as Pennoni International Inc., and Hart Crowser de Mexico was renamed Pennoni International de Mexico</li>"+
						"<b><li>385 employees</b></li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-bottom-left-30",
					w: "130px",
					ratio: "9 / 9",
					src: "assets/Acquisitions/PRIME-WARE.png",
					poster:
						"assets/1988.png",
					alt: "Logo of Prime Ware",
					title: "Logo of Prime Ware",
					depth: 5,
					z: 2
				},
				{
					type: "image",
					pos: "pos-middle-right",
					w: "40vw",
					ratio: "1 / 1",
					src: "assets/1997.png",
					poster:
						"assets/1997.png",
					alt: "Office building located at 1911 Arch Street near Logan Circle, Philadelphia, PA",
					title: "Office building located at 1911 Arch Street near Logan Circle, Philadelphia, PA",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-left-3",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1997",
					copy:
						"• Acquired the assets of <b>Schulcz & Padlasky</b>, consulting and structural engineers of Delaware County, PA founded in 1952"+
						"\n\n<b>• 152 employees</b>",
					depth: 20,
					z: 1
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
				img.title = tileData.title || "";
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
			bg: "#39D87D",
			fg: "#264831",
			muted: "#264831",
			year: "#264831",
			cardBg: "#ccebe1",
			cardBorder: "transparent",
			yearLayerOpacity: 0.43
		},
		spiritedAway: {
			bg: "#02b07c",
			fg: "#02b07c",
			muted: "#ffffff",
			year: "#222",
			cardBg: "#222",
			cardBorder: "transparent",
			yearLayerOpacity: 0.33
		},
		howls: {
			bg: "#ccebe1",
			fg: "#1d3535",
			muted: "#4b6868",
			year: "#1d3535",
			cardBg: "#ecf5f2ff",
			cardBorder: "transparent",
			yearLayerOpacity: 0.42
		},
		alt: {
			bg: "#2e2e2e",
			fg: "#eee",
			muted: "#ffffffff",
			year: "#eee",
			cardBg: "#414141ff",
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
