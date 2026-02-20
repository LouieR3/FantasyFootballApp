/* ====================== */
/* Step 01 - Render Logic */
/* ====================== */
function initTimeline() {
	// Inject text-column styles
	const styleEl = document.createElement("style");
	styleEl.textContent = `
		.text-column {
			--text-col-w: 40vw;
			width: var(--text-col-w) !important;
			aspect-ratio: unset !important;
			height: auto !important;
			display: flex;
			flex-direction: column;
			gap: 5rem;
			position: absolute;
			top: 50%;
			transform: translateY(-50%);
			z-index: var(--z, 2);
			box-shadow: none !important;
			background: transparent !important;
		}
		/* Custom top position support via data-t attribute */
		.text-column[data-t] {
			top: var(--custom-top) !important;
		}
		.text-column .tile__box {
			display: none;
		}
		.text-column .tile__text {
			background: var(--cardBg, #ffffffcc);
			border-radius: 0.5rem;
			padding: 1.5rem 2rem;
			display: block;
		}
		.text-column--left {
			left: 0;
		}
		.text-column--right {
			right: 0;
		}
		@media (max-width: 1000px) {
			.text-column {
				position: relative;
				top: unset;
				transform: none;
				left: unset !important;
				right: unset !important;
				margin: 2rem auto;
				gap: 2rem;
				max-width: 90vw;
			}
		}
	`;
	document.head.appendChild(styleEl);

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
			id: "DARKGREEN",
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
                    t: "60",
					ratio: "16 / 9",
					heading: "1966",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li><b>C.R. Pennoni began the firm as a one-person structural engineering practice in West Philadelphia, PA at 67th Street and Haverford Avenue.</b></li>" +
						"<li>The first three part-time hires were engineering students from Temple University</li>"+
                        "<li>Headquarters (HQ) moved to Center City office at 17th and Cherry Streets in Philadelphia, PA to serve increased client base</li>" +
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
			id: "LIGHTGREEN",
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
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Leo F. O'Connor, PE joined the firm as the first Vice President</li>" +
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
			id: "GRASS",
			year: "1972-77",
			theme: "spiritedAway",
			tiles: [
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
                    t: "30",
					ratio: "16 / 9",
					heading: "1973",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>HQ relocated to a historic four-story brownstone at 2006 Walnut Street near Rittenhouse Square in Philadelphia, PA</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-bottom-left-1",
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
						"<li><b><span style='font-size: 1.25rem;'>49 employees</span></b></li></ul>",
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
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Formed <b>Computer Graphics</b> with Yerkes, Huth and Richardson</li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "BRIGHTGREEN",
			year: "1978-86",
			theme: "totoro",
			tiles: [
				{
					type: "text",
					pos: "pos-top-left",
					w: "40vw",
                    t: "40",
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
					pos: "pos-bottom-right",
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
						"<li><b><span style='font-size: 1.25rem;'>152 employees</span></b></li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "GRAY",
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
					pos: "pos-top-left-25",
					w: "35vw",
					ratio: "16 / 6",
					src: "assets/1988.png",
					poster:
						"assets/1988.png",
					alt: "Historic Middishade Building at 1600 Callowhill Street in the Franklintown area of Philadelphia, PA",
					title: "Historic Middishade Building at 1600 Callowhill Street in the Franklintown area of Philadelphia, PA",
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
			id: "DARKGREEN",
			year: "1992-94",
			theme: "kikis",
			tiles: [
				{
					type: "text",
					pos: "pos-top-left",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1992",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>PrimeWare Associates</b> of Pennsylvania to add new computer technology</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-bottom-right-2",
					w: "15vw",
					ratio: "9 / 16",
					src: "assets/1994.png",
					poster:
						"assets/1994.png",
					alt: "Logo of Prime Ware",
					title: "Logo of Prime Ware",
					depth: 5,
					z: 2
				},
				{
					type: "image",
					pos: "pos-top-right-alt",
					w: "30vw",
					ratio: "16 / 9",
					src: "assets/1992.png",
					poster:
						"assets/1992.png",
					alt: "Richard L. Piccoli",
					title: "Richard L. Piccoli",
					depth: 10,
					z: 2
				},
				{
					type: "image",
					pos: "pos-bottom-center-lg-10",
					w: "120px",
					ratio: "1 / 1",
					src: "assets/1994.jpg",
					poster:
						"assets/1994.jpg",
					alt: "Employee Stock Ownership Logo",
					title: "Employee Stock Ownership Logo",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-left-3",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1994",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li><b>Established ESOP making employees majority owners</b></li>"+
						"<li>Acquired the assets of subsidiary, EnviroTEL, Inc., an environmental engineering firm with satellite offices in Pennsylvania, Massachusetts, and Tokyo</li>"+
						"<li><b>Richard L. Piccoli named President when C.R. Pennoni leaves to serve pro bono as President and COO of Drexel University for the 1994-1995 academic year</b></li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "LIGHTGREEN",
			year: "1995-96",
			theme: "howls",
			tiles: [
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1995",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Subsidiary EnviroTEL purchased <b>Hart Crowser de Mexico S.A. de C.V.</b>, an environmental engineering firm in Mexico City</li>"+
						"<li>Expanded in Massachusetts with office in Hopkinton</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-bottom-left-30",
					w: "130px",
					ratio: "10 / 9",
					src: "assets/1996-2.png",
					poster:
						"assets/1996-2.png",
					alt: "Logo of Pennoni.com",
					title: "Logo of Pennoni.com",
					depth: 5,
					z: 2
				},
				{
					type: "image",
					pos: "pos-top-left-10",
					w: "40vw",
					ratio: "16 / 3.5",
					src: "assets/1996.png",
					poster:
						"assets/1996.png",
					alt: "Pennoni Associates, Inc. logo",
					title: "Pennoni Associates, Inc. logo",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-right-25",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1996",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Introduced first home page on the World Wide Web</li>"+
						"<li>Expanded to New Hampshire with office in Concord, NH</li>"+
						"<li>Acquired the assets of <b>E.L. Conwell & Co.</b>, an inspection and testing firm established in 1895</li>"+
						"<li>Acquired the assets of <b>Barnes & Jarnis, Inc.</b>, a multidisciplinary consulting engineering firm established in 1953 to expand New England market with office in Boston, MA</li>"+
						"<li>EnviroTEL Japan was incorporated and renamed as Pennoni International Inc., and Hart Crowser de Mexico was renamed Pennoni International de Mexico</li>"+
						"<li><b><span style='font-size: 1.25rem;'>385 employees</span></b></li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "GRASS",
			year: "1997-99",
			theme: "spiritedAway",
			tiles: [
				{
					type: "text",
					pos: "pos-top-left",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1997",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Expanded international division to the Philippines</li>"+
						"<li>HQ relocated to 3001 Market Street at One Drexel Plaza in Philadelphia, PA (former Philadelphia Evening Bulletin Building)</li>"+
						"<li>Acquired the assets of <b>Travers Associates Inc.</b>, a consulting engineering firm in Clifton, NJ</li>"+
						"<li>Expanded to Ohio with offices in Cleveland and Parma</li>"+
						"<li>Patricia Querubin became the first female officer</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-top-right",
					w: "35vw",
					ratio: "16 / 8",
					src: "assets/1997.png",
					poster:
						"assets/1997.png",
					alt: "Logo of Pennoni.com",
					title: "Logo of Pennoni.com",
					depth: 5,
					z: 2
				},
				{
					type: "image",
					pos: "pos-bottom-right-45",
					w: "190px",
					ratio: "16 / 10",
					src: "assets/1997.jpg",
					poster:
						"assets/1997.jpg",
					alt: "Employee Stock Ownership Logo",
					title: "Employee Stock Ownership Logo",
					depth: 10,
					z: 2
				},
				{
					type: "image",
					pos: "pos-bottom-right-1",
					w: "25vw",
					ratio: "16 / 9",
					src: "assets/1998.jpg",
					poster:
						"assets/1998.jpg",
					alt: "Pennoni Associates, Inc. logo",
					title: "Pennoni Associates, Inc. logo",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-left-4",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1998",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Pan Asia Architects & Engineers</b> headquartered in Okinawa, Japan, founded over 20 years earlier</li>"+
						"<li><b>Anthony Bartolomeo elected as President following retirement of Richard L. Piccoli</b></li></ul>",
					depth: 20,
					z: 1
				},
				{
					type: "text",
					pos: "pos-bottom-left-1",
					w: "40vw",
					ratio: "16 / 9",
					heading: "1999",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>SCE & Associates</b> of Pennsylvania</li>"+
						"<li>Acquired the assets of <b>Marc Associates</b> of New Jersey</li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "GRAY",
			year: "2000-03",
			theme: "alt",
			tiles: [
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
					ratio: "9 / 16",
					heading: "2001",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Adams Associates, Inc.</b>, a structural firm in Pennsylvania</li></ul>",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-middle-right",
					w: "40vw",
					ratio: "1 / 1",
					heading: "2002",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>GWSM, Inc.</b>, a landscape architecture firm founded in 1975, which established a Pittsburgh office</li></ul>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-right-35",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2003",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Anthony Bartolomeo promoted from President to President & CEO</li></ul>",
					depth: 20,
					z: 4
				},
				{
					type: "image",
					pos: "pos-bottom-left-4",
					w: "250px",
					ratio: "9 / 16",
					src: "assets/2003.png",
					poster:
						"assets/2003.png",
					alt: "Anthony Bartolomeo",
					title: "Anthony Bartolomeo",
					depth: 10,
					z: 2
				}
			]
		},
		{
			id: "BRIGHTGREEN",
			year: "2004-06",
			theme: "totoro",
			tiles: [
				{
					type: "text",
					pos: "pos-top-left",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2004",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Powers & Schram Inc.</b>, which established an office in State College, PA</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-bottom-right-alt",
					w: "250px",
					ratio: "10 / 16",
					src: "assets/2005.png",
					poster:
						"assets/2005.png",
					alt: "Former Philadelphia Eagles' defensive tackle, Darwin Walker",
					title: "Former Philadelphia Eagles' defensive tackle, Darwin Walker",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-middle-left-2",
					w: "40vw",
					ratio: "1 / 1",
					heading: "2005",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Formed strategic alliance with <b>Progressive Engineering Group LLC</b>, formed in Tennessee by former Philadelphia Eagles' defensive tackle, Darwin Walker</li>"+
						"<li>Expanded to Maryland with Ellicott City office</li></ul>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-left-2",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2006",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Meyer, Strong, and Jones Engineers P.C.</b>, a mechanical and electrical consulting engineering firm in New York established in 1902</li>"+
						"<li>Acquired the assets of <b>Swanson Engineering P.C.</b>, a multidisciplinary engineering firm in northeast Philadelphia</li>"+
						"<li>Acquired the assets of <b>G.S. Winters</b>, a consulting engineering and land surveying firm in New Jersey</li>"+
						"<li><b><span style='font-size: 1.25rem;'>685 employees</span></b></li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "DARKGREEN",
			year: "2007-10",
			theme: "kikis",
			tiles: [
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
                    t: "30",
					ratio: "16 / 9",
					heading: "2007",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>C.R. Pennoni established the ELLIPSE Award to annually honor a community member who has improved the quality of life through infrastructure development or redevelopment</li>"+
						"<li>Acquired the assets of <b>Professional Planning & Engineering, LLC</b> of New Jersey</li>"+
						"<li>Established <b>Pennoni Engineering and Surveying of New York P.C.</b></li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-top-left-25",
					w: "18rem",
					ratio: "12 / 16",
					src: "assets/2007-2.png",
					poster:
						"assets/2007-2.png",
					alt: "Ellipse Award logo and list of Past Winners",
					title: "Ellipse Award logo and list of Past Winners",
					depth: 10,
					z: 2
				},
				{
					type: "image",
					pos: "pos-bottom-left-white",
					w: "230px",
					ratio: "16 / 14",
					src: "assets/iis.png",
					poster:
						"assets/iis.png",
					alt: "Logo of IIS",
					title: "Logo of IIS",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-middle-right-2",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2009",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>PennoniGIVES (Giving by Investing in our Volunteering Employees) program was established</li></ul>",
					depth: 20,
					z: 1
				},
				{
					type: "text",
					pos: "pos-bottom-right-2",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2010",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Patton, Harris, Rust & Associates, Inc.</b>, a multidisciplinary firm in Virginia established in 1952</li>"+
						"<li>Acquired the assets of <b>Green Stone Engineering, LLC</b>, a civil and environmental engineering firm in Delaware</li>"+
						"<li>Established <b>Intelligent Infrastructure Systems (IIS)</b> as a separate company, that was instrumental in the development of THMPER and RABIT</li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "GRASS",
			year: "2011-14",
			theme: "spiritedAway",
			tiles: [
				{
					type: "text",
					pos: "pos-top-left-10",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2012",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>AGS, LLC</b>, an MEP engineering firm in New York</li>"+
						"<li>Acquired the assets of <b>Green Stone Engineering, LLC</b>, a civil and environmental engineering firm in Delaware</li>"+
						"<li>Instrumental in development of ICOMPASS, a web-based transportation asset management system for bridge owners</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "text",
					pos: "pos-bottom-left-4",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2013",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Richard Piccolo named first President Emeritus</li></ul>",
					depth: 20,
					z: 1
				},
				{
					type: "text",
					pos: "pos-bottom-left-1",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2014",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>B.D. Abel Inc.</b>, an MEP consulting firm in Delaware</li>"+
						"<li>Acquired the assets of <b>Envisors</b>, a multidisciplinary firm founded in 1975, which established Florida offices</li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "LIGHTGREEN",
			year: "2015-16",
			theme: "howls",
			tiles: [
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2015",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>J2 Engineering, Inc.</b>, a design-build and construction management firm founded in 2001 in Florida</li>"+
						"<li>Acquired the assets of <b>Jones-Stuckey Ltd.</b>, a transportation design firm founded in 1965 in Ohio</li>"+
						"<li>Acquired the assets of <b>Philip Post & Associates</b>, a civil engineering and land surveying firm founded in 1979, which established an office in Chapel Hill, NC</li>"+
						"<li>Developed Pennoni OPTICS, a proprietary web-based energy management software</li></ul>",
					depth: 15,
					z: 1
				},
				{
					type: "image",
					pos: "pos-bottom-left-30",
					w: "20vw",
					ratio: "16 / 9",
					src: "assets/2016.jpg",
					poster:
						"assets/2016.jpg",
					alt: "Pennoni 50th anniversary logo",
					title: "Pennoni 50th anniversary logo",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-right-2",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2016",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>McCarthy and Associates</b>, a structural engineering firm based in Clearwater, FL</li>"+
						"<li>Acquired the assets of <b>RWD Consultants LLC</b>, a multidisciplinary engineering firm out of Camden, NJ</li>"+
						"<li><b><span style='font-size: 1.25rem;'>1200+ employees</span></b></li></ul>",
					depth: 20,
					z: 1
				}
			]
		},
		{
			id: "GRAY",
			year: "2017-20",
			theme: "alt",
			tiles: [
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
                    t: "40",
					ratio: "9 / 16",
					heading: "2017",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>10 Year anniversary of the ELLIPSE Awards</li>"+
						"<li>HQ relocated to <b>1900 Market Street</b> in the Central Business District of Philadelphia, PA</li></ul>",
					depth: 5,
					z: 2
				},
				{
					type: "text",
					pos: "pos-middle-right",
					w: "40vw",
					ratio: "1 / 1",
					heading: "2019",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>David DeLizza named President and CEO</li>"+
						"<li>Pennoni announces that it's ESOP is 100% employee-owned</li>"+
						"<li>10 year anniversary of PennoniGIVES</li>"+
						"<li>Acquired the assets of <b>Group Melvin Design, LLC</b>, a planning service company adding to their Camden, NJ office</li></ul>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-right-25",
					w: "40vw",
                    t: "20",
					ratio: "16 / 9",
					heading: "2020",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Despite the global pandemic, Pennoni was able to work on major projects like the Comcast Technology Center in Philadelphia, PA and</li></ul>",
					depth: 20,
					z: 4
				},
				{
					type: "image",
					pos: "pos-top-right",
					w: "30vw",
					ratio: "16 / 9",
					src: "assets/2017.PNG",
					poster:
						"assets/2017.PNG",
					alt: "1900 Market Street in the Central Business District of Philadelphia, PA",
					title: "1900 Market Street in the Central Business District of Philadelphia, PA",
					depth: 10,
					z: 2
				},
				{
					type: "image",
					pos: "pos-bottom-right-20",
					w: "15rem",
					ratio: "12 / 16",
					src: "assets/Dave-DeLizza.png",
					poster:
						"assets/Dave-DeLizza.png",
					alt: "1900 Market Street in the Central Business District of Philadelphia, PA",
					title: "1900 Market Street in the Central Business District of Philadelphia, PA",
					depth: 10,
					z: 2
				}
			]
		},
		{
			id: "BRIGHTGREEN",
			year: "2021-22",
			theme: "totoro",
			tiles: [
				{
					type: "text",
					pos: "pos-bottom-right-25",
					w: "40vw",
                    t: "20",
					ratio: "16 / 9",
					heading: "2021",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>Cocciardi & Associates, Inc.</b>, an Environmental, Health, and Safety (EHS) company from Mechanicsburg and Jessup, PA</li>"+
						"<li>Acquired the assets of <b>Snyder, Secary, & Associates</b>, a civil engineering, land use planning and development consulting services company from Harrisburg and York, PA</li></ul>",
					depth: 20,
					z: 4
				},
				{
					type: "text",
					pos: "pos-top-right",
					w: "40vw",
					ratio: "9 / 16",
					heading: "2022",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Expanded to The District of Columbia, expanding the ability to better service new and existing clients in the National Capital Region</li>"+
						"<li>Acquired the assets of <b>Kempton Rinard</b>, a landscape architectural and civil engineering company from Tampla, FL</li>"+
						"<li>Acquired the assets of <b>Hygenix, Inc.</b>, an environmental consulting, testing and laboratory services company from Stamford, CT</li>"+
						"<li>Acquired the assets of <b>CH Engineering</b>, an engineering and land surveying company from Raleigh, NC</li>"+
						"<li>Acquired the assets of <b>SMITH Engineering</b>, a land development and civil engineering company from Chantilly, VA</li>"+
						"<li>Response and Recovery: Hurricane Ian - After one of the most damaging storms of the year — Pennoni staff mobilized in Florida to support structural assessments, environmental surveys, forensic engineering, and recovery assistance in heavily impacted areas</li></ul>",
					depth: 5,
					z: 2
				},
				{
					type: "image",
					pos: "pos-top-left-25",
					w: "30vw",
					ratio: "16 / 9",
					src: "assets/2017.png",
					poster:
						"assets/2017.png",
					alt: "1900 Market Street in the Central Business District of Philadelphia, PA",
					title: "1900 Market Street in the Central Business District of Philadelphia, PA",
					depth: 10,
					z: 2
				}
			]
		},
		{
			id: "DARKGREEN",
			year: "2023-24",
			theme: "kikis",
			tiles: [
				{
					type: "text",
					pos: "pos-middle-left",
					w: "40vw",
                    t: "30",
					ratio: "1 / 1",
					heading: "2023",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Expanded to Boston, MA with a new office</li>"+
						"<li>Opened a construction materials testing laboratory in King of Prussia, PA</li>"+
						"<li>I-95 CAP Groundbreaking at Penn's Landing</li>"+
						"<li>Acquired the assets of <b>Andersen Engineering Associates, Inc. (AEA, Inc.)</b>, an engineering and land surveying company from Sellersville, PA</li>"+
						"<li>Acquired the assets of <b>Van Note-Harvey Associates, Inc. (VNHA)</b>, a full-service consulting engineering, environmental, planning and land surveying organization tracing its origin back to 1894, with offices located in Princeton and Cape May, NJ</li></ul>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-left-25",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2024",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Acquired the assets of <b>IRWIN Engineers, Inc.</b>, a professional consulting firm specializing in chemical and environmental engineering services from Natick, MA</li>"+
						"<li>Acquired the assets of <b>Mills & Associates</b>, a ___ company from ___</li>"+
						"<li>20 year anniversary of Pennoni Perspective</li></ul>",
					depth: 20,
					z: 4
				},
				{
					type: "image",
					pos: "pos-top-right-25",
					w: "25vw",
					ratio: "16 / 9",
					src: "assets/hp-project-1.jpg",
					poster:
						"assets/hp-project-1.jpg",
					alt: "Ellipse Award logo and list of Past Winners",
					title: "Ellipse Award logo and list of Past Winners",
					depth: 10,
					z: 2
				}
			]
		},
		{
			id: "GRASS",
			year: "2025-26",
			theme: "spiritedAway",
			tiles: [
				{
					type: "text",
					pos: "pos-middle-left",
					w: "40vw",
                    t: "30",
					ratio: "1 / 1",
					heading: "2025",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Expanded to Boston, MA with a new office</li>"+
						"<li>Acquired the assets of <b>Midatlantic Engineering</b>, an engineering and land surveying company from Pittston Township, PA</li>"+
						"<li>Acquired the assets of <b>MV Engineering LLC</b>, an engineering consulting firm based in Cape May Court House, NJ</li>"+
						"<li>Acquired the assets of <b>Dagher Engineering</b>, a building systems engineering and sustainability consulting firm based in New York City, NY</li></ul>",
					depth: 10,
					z: 2
				},
				{
					type: "text",
					pos: "pos-bottom-left-25",
					w: "40vw",
					ratio: "16 / 9",
					heading: "2026",
					copy:
						"<ul style='list-style-type: disc !important; margin-left: -1.5rem;'><li>Andrew Pennoni Named President and CEO</li>"+
						"<li>20 year anniversary of Pennoni Perspective</li>"+
						"<li><span style='font-size: 1.25rem;'><b>1400+ Employees</b></span></li></ul>",
					depth: 20,
					z: 4
				},
				{
					type: "image",
					pos: "pos-top-left-25",
					w: "18rem",
					ratio: "12 / 16",
					src: "assets/Andrew-Pennoni.png",
					poster:
						"assets/Andrew-Pennoni.png",
					alt: "Andrew Pennoni",
					title: "Andrew Pennoni",
					depth: 10,
					z: 2
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

	// Build a single text card element (not a full tile wrapper)
	const buildTextCard = (tileData) => {
		const textEl = el("div", "tile__text");
		textEl.dataset.reveal = "text";

		const h = el("h3");
		h.textContent = tileData.heading || "";

		const p = el("p");
		p.innerHTML = (tileData.copy || "").replace(/\n\n/g, "<br><br>");

		textEl.append(h, p);
		return textEl;
	};

	const buildMediaTile = (tileData) => {
		const tileEl = el("div", `tile ${tileData.pos || ""}`.trim());

		tileEl.dataset.origW = tileData.w || "30vw";
		tileEl.style.setProperty("--w", tileData.w || "30vw");
		tileEl.style.setProperty("--ratio", tileData.ratio || "16 / 9");
		tileEl.style.setProperty("--z", String(tileData.z ?? 1));
		tileEl.dataset.depth = String(tileData.depth ?? 0);

		const boxEl = el("div", "tile__box");

		if (tileData.type === "image") {
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
		} else if (tileData.type === "video") {
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
		}

		tileEl.appendChild(boxEl);
		return tileEl;
	};

	// Adjust text column widths responsively:
	// >1450px → 40vw, 1000–1450px → 45vw, <1000px → 90vw
	const adjustTileWidths = () => {
		const w = window.innerWidth;
		const textW = w > 1550 ? "40vw" : w > 1000 ? "45vw" : "90vw";

		document.querySelectorAll('.text-column').forEach((col) => {
			col.style.setProperty("--text-col-w", textW);
		});

		// Also adjust any standalone media tiles that use vw-based widths
		document.querySelectorAll('.tile').forEach((t) => {
			const orig = t.dataset.origW || '';
			if (!orig) return;
			t.style.setProperty('--w', orig);
		});
	};

	// simple debounce for resize
	const debounce = (fn, wait = 120) => {
		let id;
		return (...args) => {
			clearTimeout(id);
			id = setTimeout(() => fn(...args), wait);
		};
	};

	const mountPanels = () => {
		const listFrag = document.createDocumentFragment();
		let panelIndex = 0;

		for (const item of timelineItems) {
			const li = el("li");

			const panel = el("article", "panel");
			panel.dataset.entryId = item.id;
			applyThemeData(panel, item.theme);

			const stage = el("div", "panel__stage");

			// Separate text tiles from media tiles
			const textTiles = item.tiles.filter(t => t.type === "text");
			const mediaTiles = item.tiles.filter(t => t.type !== "text");

			// Alternate text column: even panels → right, odd panels → left
			const colSide = panelIndex % 2 === 0 ? "text-column--right" : "text-column--left";

			// Build unified text column if there are text tiles
			if (textTiles.length > 0) {
				const colEl = el("div", `tile text-column ${colSide}`);
				colEl.dataset.depth = String(textTiles[0].depth ?? 0);
				colEl.style.setProperty("--z", String(textTiles[0].z ?? 2));

				// Check if first text tile has custom top position attribute 't'
				if (textTiles[0].t !== undefined) {
					colEl.dataset.t = String(textTiles[0].t);
					colEl.style.setProperty("--custom-top", `${textTiles[0].t}%`);
				}

				for (const tileData of textTiles) {
					const card = buildTextCard(tileData);
					colEl.appendChild(card);
				}

				stage.appendChild(colEl);
			}

			// Build individual media tiles with their original positions
			for (const tileData of mediaTiles) {
				stage.appendChild(buildMediaTile(tileData));
			}

			panel.appendChild(stage);
			li.appendChild(panel);
			listFrag.appendChild(li);
			panelIndex++;
		}

		panelsList.appendChild(listFrag);

		// after panels are mounted, adjust widths and attach resize handler
		adjustTileWidths();
		window.addEventListener('resize', debounce(adjustTileWidths, 150));
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

		// For text cards inside a text-column, use the node itself as trigger
		// so each card reveals independently as it enters the viewport
		const isTextInColumn = kind === "text" && node.closest('.text-column');
		const tileTrigger = isTextInColumn ? node : (node.closest(".tile") || node);

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

		// For cards inside a text-column, trigger on the card itself not the column
		const isInColumn = textBlock.closest('.text-column');

		animateReveal(textBlock, {
			kind: "text",
			triggerStart: isInColumn ? "top 75%" : "top 60%",
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
			fg: "#02b07c",
			muted: "#ffffff",
			year: "#222",
			cardBg: "#222",
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