import dossier from "./rookie-precedents.json";

export const categories = {
  health: "Health & Medtech",
  education: "Education & Learning Technology",
  climate: "Climate & Circular Economy",
  agriculture: "AgriTech & Bioinnovation",
} as const;

export type Category = keyof typeof categories;
export type Venture = (typeof dossier)[number];
export type Milestone = Venture["events"][number];
type Analogue = {
  venture: string;
  event: number;
  role: "Upside" | "Development" | "Downside";
  reason: string;
};
type Subject = {
  id: string;
  name: string;
  category: Category;
  date: string;
  summary: string;
  source: string;
  goal: string;
  question: string;
  peers: Analogue[];
};

const cie = "https://www.auckland.ac.nz/en/news/";
const ideas2026 =
  cie + "2026/05/22/university-innovators-recognised-for-tackling-real-world-problems.html";
const ideas2025 = cie + "2025/05/23/2025-velocity-ideas-challenge-winners.html";

export const subjects: Subject[] = [
  {
    id: "breast-mri",
    name: "Automated Breast MRI Reporting",
    category: "health",
    date: "22 October 2026",
    summary:
      "A University of Auckland team proposed software to draft reports from breast MRI scans.",
    source: cie + "2026/10/22/entrepreneurship-velocity-100k-winners-auckland.html",
    goal: "A provider agrees to evaluate the software in its workflow",
    question: "Who owns the evaluation, and who can approve a purchase if it works?",
    peers: [
      {
        venture: "qlarity-imaging",
        event: 1,
        role: "Upside",
        reason:
          "Same imaging modality and university origin. Compare translation after the QuantX regulatory milestone; its product characterised findings.",
      },
      {
        venture: "formus-labs",
        event: 1,
        role: "Development",
        reason:
          "A New Zealand clinical workflow software example at commercial launch. Its buyer and surgical planning task differ.",
      },
      {
        venture: "kheiron-medical-technologies",
        event: 1,
        role: "Downside",
        reason:
          "The mammography test bed surfaced pricing and procurement barriers. This describes that pilot; the company later exited.",
      },
    ],
  },
  {
    id: "pulsemap",
    name: "PulseMap PAD Detector",
    category: "health",
    date: "22 May 2026",
    summary:
      "A university project described a portable approach to non-invasive vascular screening.",
    source: ideas2026,
    goal: "A provider sponsors a documented device evaluation",
    question: "What screening comparator and field conditions will the provider require?",
    peers: [
      {
        venture: "butterfly-network",
        event: 2,
        role: "Upside",
        reason:
          "Portable diagnostic hardware with a later commercial product line. Different indication and regulatory route.",
      },
      {
        venture: "alimetry",
        event: 1,
        role: "Development",
        reason:
          "Local university spinout with a device-specific evidence path. Gastric and vascular use cases differ.",
      },
      {
        venture: "kheiron-medical-technologies",
        event: 1,
        role: "Downside",
        reason:
          "Adjacent provider buying example. The test-bed report documents procurement friction for imaging software.",
      },
    ],
  },
  {
    id: "atlasor",
    name: "AtlasOR",
    category: "education",
    date: "22 May 2026",
    summary:
      "The university team described patient-specific digital anatomy models for medical education and rehearsal.",
    source: ideas2026,
    goal: "A teaching institution adopts the tool in a course",
    question: "Who owns the course budget and what evidence would justify a renewal?",
    peers: [
      {
        venture: "labster",
        event: 2,
        role: "Upside",
        reason:
          "Simulation in institutional science education. Match the learning evaluation path, with differences in subject matter.",
      },
      {
        venture: "banqer",
        event: 2,
        role: "Development",
        reason:
          "An NZ example of a simulation entering teaching through a school partnership. Its audience and buyer differ.",
      },
      {
        venture: "edmodo",
        event: 1,
        role: "Downside",
        reason:
          "Adjacent case for service continuity following educator adoption. Its classroom collaboration product is different.",
      },
    ],
  },
  {
    id: "writewise",
    name: "WriteWise English Tutor",
    category: "education",
    date: "23 May 2025",
    summary: "The team proposed AI-generated essay feedback for NCEA English students.",
    source: ideas2025,
    goal: "A school adopts the product with a paid or funded pilot",
    question:
      "Which teacher workflow, feedback quality measure and data responsibilities would the pilot test?",
    peers: [
      {
        venture: "kami",
        event: 2,
        role: "Upside",
        reason:
          "A local example of improving a task teachers already perform. Its early product supported annotation rather than automated feedback.",
      },
      {
        venture: "education-perfect",
        event: 1,
        role: "Development",
        reason:
          "NZ curriculum-aligned digital learning expanded from a narrow subject. Its origin interval is broad.",
      },
      {
        venture: "edmodo",
        event: 1,
        role: "Downside",
        reason:
          "Classroom adoption and later service closure highlight the need to verify who pays and how the service is sustained.",
      },
    ],
  },
  {
    id: "wastexpert",
    name: "WasteXpert",
    category: "climate",
    date: "8 October 2024",
    summary:
      "The university profile describes a young construction-waste diversion company and its early work.",
    source: cie + "2024/10/08/turning-waste-into-wins.html",
    goal: "A repeatable construction-site deployment with measurable material recovery",
    question:
      "What contractor commitment and measured diversion result would support repeat deployment?",
    peers: [
      {
        venture: "mint-innovation",
        event: 1,
        role: "Upside",
        reason:
          "Local materials recovery case with a documented later facility. Waste streams and capital requirements differ.",
      },
      {
        venture: "redwood-materials",
        event: 1,
        role: "Development",
        reason:
          "Supply-chain partner precedent. Its automaker and battery input differ from contractors and construction waste.",
      },
      {
        venture: "li-cycle",
        event: 1,
        role: "Downside",
        reason:
          "A downstream scale-up setback after preprocessing operations. Use only for capacity commitments and financing questions.",
      },
    ],
  },
  {
    id: "neocrete",
    name: "Neocrete",
    category: "climate",
    date: "11 June 2026",
    summary:
      "The university profiled the lower-carbon construction materials start-up after a reported pre-Series A round.",
    source: cie + "2026/06/11/there-are-no-concrete-answers-in-entrepreneurship.html",
    goal: "A customer qualifies the material for repeat commercial use",
    question: "Which performance tests and signed commitments are required for routine use?",
    peers: [
      {
        venture: "carboncure-technologies",
        event: 1,
        role: "Upside",
        reason:
          "Concrete production and a scale demonstration. The process and climate accounting claims differ.",
      },
      {
        venture: "mint-innovation",
        event: 1,
        role: "Development",
        reason:
          "NZ example of validating a process with an industrial buyer. Output standards and feedstock differ.",
      },
      {
        venture: "northvolt",
        event: 2,
        role: "Downside",
        reason:
          "Adjacent manufacturing case. First output and commercial deliveries preceded restructuring; useful for distinguishing qualification from repeatable production.",
      },
    ],
  },
  {
    id: "quickmas",
    name: "QuickMas",
    category: "agriculture",
    date: "17 October 2024",
    summary:
      "The university reported prototype testing for the team's on-farm mastitis diagnostic concept.",
    source: cie + "2024/10/17/innovating-until-the-cows-come-home.html",
    goal: "A named farm trial produces evidence that supports a buying decision",
    question: "What farm decision would the test change, and who would pay for repeat use?",
    peers: [
      {
        venture: "halter",
        event: 2,
        role: "Upside",
        reason:
          "A local example of deployment into farm management. Its virtual fencing workflow differs from dairy diagnostics.",
      },
      {
        venture: "innerplant",
        event: 3,
        role: "Development",
        reason:
          "A diagnostic signal intended to change a farm decision. Crop and livestock products have different evidence needs.",
      },
      {
        venture: "agbiome",
        event: 1,
        role: "Downside",
        reason:
          "Adjacent commercialisation comparison. Product registration and later operating disruption illustrate different milestones.",
      },
    ],
  },
  {
    id: "agriphage",
    name: "AgriPhage",
    category: "agriculture",
    date: "23 May 2025",
    summary:
      "An entrant summary proposed a livestock-health product and the team received Ideas Challenge recognition.",
    source: ideas2025,
    goal: "An independently documented farm evaluation",
    question: "What buyer, evaluation criteria, and route to repeat orders can be confirmed?",
    peers: [
      {
        venture: "pivot-bio",
        event: 1,
        role: "Upside",
        reason:
          "An example of grower validation preceding a sales channel. Crop inputs and livestock health have different requirements.",
      },
      {
        venture: "biolumic",
        event: 2,
        role: "Development",
        reason:
          "NZ university-origin commercialisation through farm supply partners. Its crop product is a pathway analogy.",
      },
      {
        venture: "agbiome",
        event: 1,
        role: "Downside",
        reason:
          "Product milestones preceded a layoff notice and asset transfers. Use for business continuity, not technical equivalence.",
      },
    ],
  },
];

export const precedents = new Map(dossier.map((venture) => [venture.id, venture]));
const month = (365.2425 * 86400000) / 12;

export function elapsedMilestones(venture: Venture, entry: Milestone, horizon: number) {
  const earliest = Date.parse(entry.start);
  const latest = Date.parse(entry.end);
  const entryIndex = venture.events.indexOf(entry);
  return venture.events
    .slice(entryIndex)
    .filter((event) => Date.parse(event.end) >= earliest)
    .map((event) =>
      event.id === entry.id
        ? { event, from: 0, through: 0, entry: true }
        : {
            event,
            from: Math.max(0, Math.floor((Date.parse(event.start) - latest) / month)),
            through: Math.ceil((Date.parse(event.end) - earliest) / month),
            entry: false,
          },
    )
    .filter(({ through }) => through <= horizon)
    .sort((left, right) => left.from - right.from || left.through - right.through);
}

export function scenarioPath(advance: number, stall: number, steps: 1 | 2, quarters: number) {
  const path = [{ quarter: 0, reached: 0, stalled: 0, inProgress: 1 }];
  let initial = 1;
  let intermediate = 0;
  for (let quarter = 1; quarter <= quarters; quarter++) {
    const last = path[quarter - 1];
    const reached = last.reached + (steps === 1 ? initial : intermediate) * advance;
    const stalled = last.stalled + (initial + intermediate) * stall;
    const stay = 1 - advance - stall;
    intermediate = intermediate * stay + (steps === 2 ? initial * advance : 0);
    initial *= stay;
    path.push({ quarter, reached, stalled, inProgress: initial + intermediate });
  }
  return path;
}
