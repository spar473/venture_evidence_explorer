# Healthtech source and identity log

Public text checked on **19 November 2026 (Pacific/Auckland)**. Sources are attributed reports; assistant extraction is not independent acceptance. Current retrieval does not prove earlier web availability. No patient data, private records or full copyrighted pages are included.

| Source ID | Publisher / source | Publication label | Verification / locator |
|---|---|---|---|
| `src_ht_mri26` | [University of Auckland: Supermarket scents, sound sleep, smarter scans: Velocity $100k Challenge winners](https://www.auckland.ac.nz/en/news/2026/10/22/entrepreneurship-velocity-100k-winners-auckland.html) | 2026-10-22 | Public HTML; heading/paragraph locators on each claim; direct HTTPS client |
| `src_ht_formus22` | [PR Newswire (release provided by Formus Labs): Formus Labs Raises $5 Million; Partners With Zimmer Biomet](https://www.prnewswire.com/news-releases/formus-labs-raises-5-million-to-automate-orthopedic-surgery-planning-partners-with-zimmer-biomet-to-supercharge-global-launch-301473244.html) | 2022-02-02 | Public HTML; heading/paragraph locators on each claim; web-reader text |
| `src_ht_formus_repost` | [Formus Labs: Formus Labs Raises $5 Million (company repost)](https://www.formus.com/news/formus-labs-raises-5-million-to-automate-orthopedic-surgery-planning-partners-with-zimmer-biomet-to-supercharge-global-launch) | 2026-05-22 | Public HTML; heading/paragraph locators on each claim; web-reader text |
| `src_ht_formus23` | [US FDA: Formus Hip K213272: decision letter and applicant 510(k) summary](https://www.accessdata.fda.gov/cdrh_docs/pdf21/K213272.pdf) | Unknown (document dates kept separately) | FDA-hosted PDF; page/section locators on each claim; web-reader text |
| `src_ht_formus26` | [Formus Labs: Formus Labs Hip Platform Receives FDA Clearance!](https://www.formus.com/news/formus-labs-hip-platform-receives-fda-clearance) | 2026-05-22 | Public HTML; heading/paragraph locators on each claim; web-reader text |
| `src_ht_volpara10` | [US FDA: Volpara K102556: applicant summary and FDA decision letter](https://www.accessdata.fda.gov/cdrh_docs/pdf10/K102556.pdf) | Unknown (document dates kept separately) | FDA-hosted PDF; page/section locators on each claim; web-reader text |
| `src_ht_volpara24` | [Lunit: Lunit completes acquisition of Volpara](https://www.lunit.io/en/media-hub/lunit-completes-acquisition-of-volpara-pioneering-next-level-of-ai-driven-cancer-care/) | 2024-05-22 | Public HTML; heading/paragraph locators on each claim; web-reader text |
| `src_ht_n22` | [University of Auckland: Cutting-edge brain technology takes out top Velocity prize](https://www.auckland.ac.nz/en/news/2022/11/01/brain-tech-takes-out-top-velocity-prize.html) | 2022-11-01 | Public HTML; heading/paragraph locators on each claim; direct HTTPS client |
| `src_ht_n23` | [University of Auckland: Making brain surgery smarter with artificial intelligence](https://www.auckland.ac.nz/en/news/2023/11/10/making-brain-surgery-smarter-artificial-intelligence.html) | 2023-11-10 | Public HTML; heading/paragraph locators on each claim; direct HTTPS client |
| `src_ht_p26` | [Medtech-iQ Tāmaki Makaurau: Medtech-iQ prize awarded to PulseMap PAD Detector](https://medtechiq.org.nz/news/medtech-iq-tamaki-makaurau-prize-was-awarded-to-pulsemap-pad-detector) | 2026-06-05 | Public HTML; heading/paragraph locators on each claim; direct HTTPS client |
| `src_ht_i25` | [University of Auckland: Start-ups reach for the stars – literally – in $100k Challenge](https://www.auckland.ac.nz/en/news/2025/10/17/start-ups-reach-for-the-stars---literally---in--100k-challenge-.html) | 2025-10-17 | Public HTML; heading/paragraph locators on each claim; direct HTTPS client |
| `src_ht_x25` | [University of Auckland: The latest start-ups emerging from the University’s incubator](https://www.auckland.ac.nz/en/news/2025/08/25/latest-start-ups-emerging-from-the-universitys-incubator.html) | 2025-08-25 | Public HTML; heading/paragraph locators on each claim; direct HTTPS client |
| `src_ht_t22` | [University of Auckland: Eyes wide open – the journey from academic to entrepreneur](https://www.auckland.ac.nz/en/news/2022/06/28/eyes-wide-open-academic-entrepreneur.html) | 2022-06-28 | Public HTML; heading/paragraph locators on each claim; web-reader text |
| `src_ht_t23` | [National Vision: Toku Inc. Series A Preferred Investment Round](https://www.nationalvision.com/news/2023/04/17/toku-inc-series-a-preferred-investment-round-led-by-national-vision-inc-and-topcon-healthcare/) | 2023-04-17 | Public HTML; heading/paragraph locators on each claim; web-reader text |
| `src_ht_well_booster` | [Booster announcement on NZX](https://www.nzx.com/announcements/426110) | 2024-02-13 | Transaction notice, product description |
| `src_ht_well_study` | [Barker et al., Scientific Reports](https://www.nature.com/articles/s41598-026-80754-0) | 2026-11-18 | Abstract, ethics and competing interests. Investigators disclose prototype support and company personnel. |
| `src_ht_ali_study` | [Varghese et al., Clinical and Translational Gastroenterology](https://pmc.ncbi.nlm.nih.gov/articles/PMC10684143/) | 2023-08-17 | Online publication date. Study design, changes in clinical management and limitations. |
| `src_ht_ali_sites` | [Alimetry company announcement](https://www.alimetry.com/press/alimetry-raises-an-oversubscribed-us-18m) | 2024-10-25 | Early uptake following FDA approval, site sign-ups. The earlier clinical series and this commercial report have different denominators. |

The web reader could not open the MRI university article. Direct HTTPS retrieval succeeded and the displayed date, MRI section and prizegiving date were inspected. Expansion retrieval initially failed in Python’s local certificate store; the system HTTPS client verified TLS and retrieved the five cited pages. These were access-tool limitations resolved during research, not evidence that the projects lack evaluations. No archive witness was retrieved.

The inventory’s FDA database leads were followed to the regulator-hosted K102556 and K213272 decision letters and applicant summaries. Decision dates are occurrence/context evidence; the PDF publication/upload dates remain unknown. Regulator hosting does not transfer responsibility for applicant validation statements to FDA.

## Reconciliation before import

| Inventory case | Existing records checked | Imported research identity / disposition |
|---|---|---|
| MRI Reporting | No seed, existing research or staged discovery match | `subj_ht_mri`; proposed external `v_automated_breast_mri_reporting`; project/product/legal identity unresolved |
| Formus | Seed `v_formus`, `v_formus_product`, `v_formus_connection`; staged `discovery_formuslabs`, `cand_formus` | `subj_ht_formus`; proposed `v_formus` link; no accepted legal crosswalk |
| Volpara | No seed, existing research or staged discovery match | `subj_ht_volpara`; proposed `v_volpara`; Matakina applicant and later corporate group correspondence unresolved |
| Neurofanos | No seed, existing research or staged discovery match | `subj_ht_neurofanos`; project, university research grant recipient and proposed IP licensee remain distinct |
| PulseMap | No seed, existing research or staged discovery match | `subj_ht_pulsemap`; proposed `v_pulsemap_pad_detector`; sparse evidence, abstain |
| IVF | Seed `v_ivf_tool`, alias IVF support tool; shared 2025 university source | `subj_ht_ivf`; proposed `v_ivf_tool`, not a new accepted base venture |
| VistaVision | No seed, existing research or staged discovery match | `subj_ht_vistavision`; proposed `v_vistavision`; portfolio description only |
| Toku | `discovery_toku`, `discovery_tokueyes` and their existing unresolved alias case | `subj_ht_toku`; source labels remain unresolved; investor’s Toku Inc. report is separately attributable |
| RosterLab | Existing `subj_rosterlab`, proposed `v_rosterlab` | Reused original dossier unchanged; contrast abstains on diagnostic-imaging relevance |
| Alimetry | Seed `v_alimetry`, staged `discovery_alimetry` and `cand_alimetry` | `subj_ht_alimetry` proposes the existing brand link. Legal identity and product revisions remain open. |
| Wellumio | Staged `discovery_wellumio` | `subj_ht_wellumio` proposes external `v_wellumio`. Booster names Wellumio Limited and the clinical team names the Axana prototype. Registry identity remains open. |

## Material boundaries and next research

- **Formus:** the original wire release is dated 2 February 2022. The company repost displays a May 2026 header but retains the 2022 body dateline. Its planned US evaluation is not a completed evaluation. The K213272 letter is dated 31 March 2023; the separate company clearance page displays 22 May 2026 without a submission identifier. Preserve both reports until product/version/submission correspondence is resolved.
- **Volpara:** the v1.3 applicant summary documents technical and beta-site testing. Its adjunctive mammographic-density intended use differs from MRI report drafting. The later acquisition report cannot identify the earliest provider evaluation or prove payment at the reported sites.
- **Neurofanos:** the September 2023 grant is reported for the university research team. Intended licensing, an IP negotiation and preparation for a pre-seed round do not establish an executed licence or closed VC round.
- **IVF:** clinic co-development, intended evaluation, completed evaluation and paid use are different claims. Only the first two are represented here.
- **VistaVision / Toku:** the analogy is scoped to eye-care access/commercialisation. Telerobotic care and retinal-analysis software differ; Toku’s 2022 wellness positioning cannot be assumed for its later named products.
- **All cases:** verified provider admission criteria, first paid deployment and archived early-stage availability remain open. Obtain a dated provider-side protocol or evaluation agreement before claiming what a provider required. Reconcile identities before joining events into a longitudinal outcome.
