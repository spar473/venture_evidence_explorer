# Time Machine field review

22 November 2026. All 72 fields are **proposals awaiting human review**: 69 strict and 3 lenient-only. No field here is confirmed. The [coverage checkpoint](BACKTEST_COVERAGE.md) explains the fixed gate.

Review the linked source version, witness date, locator and interpretation for each field. Corrections or rejections are welcome. Confirmation must identify the company and fields reviewed; a general request to continue does not confirm facts. The packet retains raw values, derivations and rationale. A confirmation also needs reviewer, date and review reference.

Packet SHA-256: `380d9c5217434639db0f466aeed69ed5652ecbd5a6c59de2fe79ff493d0f6bbf`. This review applies only to this packet version.

## Review priority

| Partly-eligible peer | Strict proposals | Could reach five if confirmed? |
|---|---:|---|
| CodeLingo Limited | 5 | Yes |
| First AML | 6 | Yes |
| Firstcheck Ltd | 5 | Yes |
| Myovolt Limited | 5 | Yes |
| Narrative | 6 | Yes |
| Parcelport | 7 | Yes |
| Social Club | 6 | Yes |
| StretchSense | 6 | Yes |
| VidApp | 7 | Yes |
| 1Centre | 0 | No |
| Formus Labs | 3 | No |
| Halter | 0 | No |
| Inhibit Coatings | 3 | No |
| Marama Labs | 4 | No |

## 1Centre

Company ID: `public_1centre`. Accepted entry: 2017-Q2 (quarter).

**S1 — [The Icehouse’s Flux Accelerator Picks 6 Start-Ups for 2017 Cohort](https://nzentrepreneur.co.nz/icehouses-flux-accelerator-picks-6-start-ups-2017-cohort/)** · NZ Entrepreneur / Flux media release · Public by 2017-04-03 · publisher dated.
Locator: Visible publication date: April 3, 2017; cohort list.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | Software streamlines opening and managing trade accounts. | The cohort list describes ongoing trade-account administration. | S1 / lenient |
| `product_type` | workflow | The stated product supports trade-account workflows. | S1 / lenient |
| `sector_normalised` | fintech | The described offering administers trade accounts; current raw sector Fintech is retained separately. | S1 / lenient |

Interpretation limits: Proposed classification of the cited offering; human confirmation required.

## CodeLingo Limited

Company ID: `public_codelingolimited`. Accepted entry: 2018-01-24 (day).

**S1 — [Dunedin startup CodeLingo raises NZ$540000 from Reinventure and Right Click Capital](https://www.rightclickcapital.com/2018/01/24/dunedin-startup-codelingo-raises-nz540000-from-reinventure-and-right-click-capital/)** · Right Click Capital · Public by 2018-01-24 · publisher dated.
Locator: Byline: Daphne on 24 January, 2018.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | Software that helps development teams automate code-quality review and debugging. | The company addresses technical debt by scaling development teams’ code review and debugging processes. | S1 / strict |
| `product_type` | workflow | The offering supports software quality-assurance processes. | S1 / strict |
| `sector_normalised` | enterprise_software | The offering is software for development-team productivity. | S1 / strict |
| `prototype` | yes | The article reports early alpha clients before this financing announcement. | S1 / strict |
| `round_size_band` | 0.5m_to_lt2m | The dated opening reports NZ$540,000 in seed funding. | S1 / strict |

Interpretation limits: Short paraphrase of the product description. Proposed editorial mapping of the cited offering to the preregistered general vocabulary; requires human confirmation. Historical offering supports a proposed enterprise-software grouping; current cohort raw sector Developer software is retained separately. An alpha product used by clients supports an existing prototype; it does not establish payment. 540000 NZD falls in the preregistered 0.5m to less-than-2m band; no currency conversion.

## First AML

Company ID: `public_firstaml`. Accepted entry: 2019-03 (month).

**S1 — [First AML outsourced customer due diligence homepage, January 2019 capture](https://web.archive.org/web/20190127160933/https://www.firstaml.co.nz/)** · First AML · Public by 2019-01-27 · archived capture.
Locator: Homepage: First AML Overview, Why Work with First AML, Services and How it works.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | Technology-assisted outsourced customer due diligence and identity verification for regulated firms. | The historical homepage describes an outsourced compliance service supported by information-capture software. | S1 / strict |
| `product_type` | professional_service | The company offers to assess, coordinate verification and report results on client firms’ behalf. | S1 / strict |
| `buyer` | business | The company explicitly serves firms outsourcing their due diligence work. | S1 / strict |
| `sector_normalised` | fintech | The service supports financial-crime compliance and regulated customer onboarding. | S1 / strict |
| `market_focus` | new_zealand | The page frames its offering around New Zealand’s AML changes. | S1 / strict |
| `prototype` | yes | The homepage reports developed technology and describes the customer verification workflow. | S1 / strict |

Interpretation limits: Preserves the historical managed-service offering; does not backfill the later self-service platform. The historical primary offering is a managed professional service, even though software supports delivery. Client firms buying outsourced services are distinguished from individuals undergoing identity checks. Proposed classification of the cited offering; human confirmation required. Proposed intended service market from the jurisdiction-specific offering; no exclusivity or overseas revenue claim. Company-reported developed service and software; no independent performance, customer count or payment milestone inferred.

## Firstcheck Ltd

Company ID: `public_firstcheckltd`. Accepted entry: 2017-05 (month).

**S1 — [Kiwi startup develops app for early detection of skin cancer](https://www.cio.com/article/204127/kiwi-startup-develops-app-for-early-detection-of-skin-cancer.html)** · CIO New Zealand · Public by 2016-11-14 · publisher dated.
Locator: News dateline 14 Nov 2016; full article read.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | A mobile service routes skin photographs to New Zealand specialists for remote review. | Patients submit photographs and receive a specialist response. | S1 / strict |
| `product_type` | workflow | The app routes photographs to doctors rather than automatically diagnosing images. | S1 / strict |
| `sector_normalised` | healthtech | The reported service provides remote skin-specialist consultations. | S1 / strict |
| `market_focus` | new_zealand | The launch serves New Zealand users through specialists in multiple NZ cities. | S1 / strict |
| `prototype` | yes | The article reports launch and completed tests with users. | S1 / strict |

Interpretation limits: Proposed classification of the cited offering; human confirmation required. Completed use supports a working product; no clinical accuracy or payment conclusion is inferred.

## Formus Labs

Company ID: `discovery_formuslabs`. Accepted entry: 2019 (year).

**S1 — [Interview: innovator and scientist Thor Besier](https://devonportflagstaff.co.nz/interview-innovator-and-scientist-thor-besier/)** · The Devonport Flagstaff · Public by 2018-06-29 · publisher dated.
Locator: Closing Formus Labs paragraphs; article dateline and source edition 29 June 2018.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | Developing customised orthotics using 3D-printing technology. | The closing section identifies Formus Labs and its orthotics development work. | S1 / strict |
| `product_type` | physical_goods | The stated offering is physical orthotics, with 3D-printing assistance. | S1 / strict |
| `sector_normalised` | healthtech | Orthopaedic design supports a proposed healthtech grouping. | S1 / strict |

Interpretation limits: Summarises only the Formus section, not the separate IMeasureU venture described earlier. Broad frozen physical-goods node; no later software offering or device regulatory status inferred. Proposed classification of the cited offering; human confirmation required.

## Inhibit Coatings

Company ID: `discovery_inhibitcoatings`. Accepted entry: 2019-12 (month).

**S1 — [Silver Institute to Sponsor Silver Technology Symposium at TechConnect World Innovation Conference 2018](https://silverinstitute.org/silver-institute-sponsor-silver-technology-symposium-techconnect-world-innovation-conference-2018/)** · The Silver Institute · Public by 2018-03-19 · publisher dated.
Locator: Dateline and Session 2 entry naming Eldon Tate and Inhibit Coatings Ltd.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | Developing coatings that suppress microbes and marine fouling for industrial applications. | The dated announcement names Inhibit Coatings and the subject of its planned presentation. | S1 / strict |
| `product_type` | materials | The named company is presenting coatings for industrial use. | S1 / strict |
| `sector_normalised` | advanced_materials | Proposed grouping follows the technical surface-coating offering. | S1 / strict |

Interpretation limits: Short scope summary; a scheduled presentation does not prove tested or marketed performance. Proposed classification of the cited offering; human confirmation required.

## Marama Labs

Company ID: `discovery_maramalabs`. Accepted entry: 2019-02 (month).

**S1 — [Marama Labs CloudSpec homepage, August 2018 capture](https://web.archive.org/web/20180807195127/http://maramalabs.com/)** · Marama Labs · Public by 2018-08-07 · archived capture.
Locator: Homepage: CloudSpec introduction, Advantages, About us and Contact.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | CloudSpec optical instrument measures absorption, extinction and scattering spectra in clear or turbid liquids. | The historical company page describes its instrument and measurement capabilities. | S1 / strict |
| `product_type` | industrial_equipment | CloudSpec is a physical laboratory spectrophotometer. | S1 / strict |
| `sector_normalised` | manufacturing | The company develops optical measurement equipment. | S1 / strict |
| `prototype` | yes | The captured text describes a developed instrument with a working measurement process. | S1 / strict |

Interpretation limits: Offering summary from the actual company capture, not the later alumni-page revision. Proposed frozen equipment category for a scientific instrument; no software-only or clinical-device claim. Broad equipment-manufacturing grouping; no future life-sciences pivot backfilled. Company-reported product operation, not independent performance validation or evidence of payment.

## Myovolt Limited

Company ID: `public_myovoltlimited`. Accepted entry: 2019-12 (month).

**S1 — [Myovolt product showcase, ISBS 2018 Conference Magazine 4](https://sprinz.aut.ac.nz/__data/assets/pdf_file/0005/192821/ISBS-2018-conference-Magazine-4-040818.pdf)** · Auckland University of Technology / ISBS · Public by 2018-09-01 · publisher dated.
Locator: Fixed magazine product-showcase item on printed p.28; issue footer says 4 August 2018. PDF creation/modification metadata is 1 September 2018; use the later date conservatively..

**S2 — [Myovolt homepage and physical-kit shop links, November 2019 capture](https://web.archive.org/web/20191115095116/https://www.myovolt.com/)** · Myovolt Limited · Public by 2019-11-15 · archived capture.
Locator: Homepage: Shop Now links for Shoulder, Elbow & Wrist, Knee & Leg, and Back kits.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | A wearable device applies vibration for muscle massage. | The showcase describes a body-worn vibration massage product. | S1 / strict |
| `product_type` | medical_device | The item describes a physical wearable therapy device. | S1 / strict |
| `sector_normalised` | healthtech | The offering is wearable physical-therapy technology. | S1 / strict |
| `prototype` | yes | The showcase depicts the product and describes how it is worn and operated. | S1 / strict |
| `business_model` | hardware_sale | The captured homepage offers physical recovery kits through its online shop. | S2 / strict |

Interpretation limits: Proposed classification of the cited offering; human confirmation required. Proposed product category only; it is not a regulatory approval or effectiveness claim. A described physical demonstrator supports prototype yes; this does not validate clinical claims. Proposed hardware-sale model follows the explicit physical-kit shop offering; no purchase, price or revenue amount is claimed.

## Narrative

Company ID: `public_narrative`. Accepted entry: 2019-05-21 (day).

**S1 — [Peter Thiel-led fund backs local creative tech startup Narrative](https://www.nbr.co.nz/investment/peter-thiel-led-fund-backs-local-creative-tech-startup-narrative/)** · NBR · Public by 2019-05-21 · publisher dated.
Locator: Visible dateline: Tue, 21 May 2019; only the public opening is used.

**S2 — [Narrative Blogging App: hands-on review (inspected 2019 archive version)](https://web.archive.org/web/20190504180448/https://www.slrlounge.com/narrative-blogging-app-a-hands-on-review/)** · SLR Lounge / Jay Henington · Public by 2019-05-04 · archived capture.
Locator: Read the complete archived article. Original HTML records publication 17 April and modification 19 April 2019; Pricing, Interface and Conclusion sections inspected..

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | Workflow software intended to improve photographers’ productivity. | The public opening describes productivity tools for photographers. | S1 / strict |
| `product_type` | workflow | The lead frames the offering around photographer workflows. | S1 / strict |
| `sector_normalised` | enterprise_software | The public lead describes workflow productivity software. | S1 / strict |
| `business_model` | saas | The archived pricing section lists monthly plans and hosted blog publishing. | S2 / strict |
| `prototype` | yes | The reviewer describes direct use of the functioning application. | S2 / strict |
| `buyer` | business | The review addresses professional photographers and describes priced plans for their blogging work. | S2 / strict |

Interpretation limits: Only the openly readable lead is used; no paywalled detail is inferred. Proposed editorial mapping of the cited offering to the preregistered general vocabulary; requires human confirmation. Proposed grouping of professional workflow software; retain Photography software as raw. Buyers and payment are unconfirmed. Hosted software subscriptions map to saas. No present-day pricing is used. Hands-on operation establishes a working product, not clinical performance or company revenue. Proposed intended purchaser classification: professional photography businesses buying workflow software. This does not identify a named paying customer.

## Parcelport

Company ID: `public_parcelport`. Accepted entry: 2017-12 (month).

**S1 — [Parcelport / formerly Payport homepage, October 2017 capture](https://web.archive.org/web/20171011022716/http://www.payport.co.nz:80/)** · Parcelport / Payport · Public by 2017-10-11 · archived capture.
Locator: Homepage: introduction, How It Works, Integration Partners and customer testimonials.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | Online courier booking and freight management platform integrating shop orders, shipping labels and parcel tracking. | The homepage describes an operating shipping workflow and integrations with online shops. | S1 / strict |
| `product_type` | workflow | Software covers booking, labels, parcel collection and tracking. | S1 / strict |
| `buyer` | business | The page addresses merchants and quotes business customers using the service. | S1 / strict |
| `business_model` | pay_per_use | The service is offered on a pay-as-you-go invoicing basis. | S1 / strict |
| `sector_normalised` | enterprise_software | The platform streamlines order dispatch and shipping management for businesses. | S1 / strict |
| `market_focus` | international | The stated freight service reach includes New Zealand and international destinations. | S1 / strict |
| `prototype` | yes | Named customer testimonials describe bookings, collections and deliveries through the system. | S1 / strict |

Interpretation limits: Short offering summary of the inspected historical company page. Proposed classification of the cited offering; human confirmation required. Business purchase context comes from invoicing and merchant customer accounts, not from parcel recipients. Classifies the stated charging arrangement; does not claim verified revenue. Geographic offering coverage, not proof of overseas customer revenue. Actual customer operation supports a functioning product; no payment milestone inferred.

## Social Club

Company ID: `public_socialclub`. Accepted entry: 2017-03 (month).

**S1 — [The Social Club talks the rise of influencer marketing in New Zealand](https://idealog.co.nz/venture/2016/12/social-club-talks-rise-influencer-marketing-new-zealand)** · Idealog · Public by 2016-12-15 · publisher dated.
Locator: Date immediately below the title: December 15, 2016.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | An online platform matching brands and social-media influencers for advertising campaigns. | Brands and influencers create profiles and find campaign collaborators. | S1 / strict |
| `product_type` | marketplace | The article describes a two-sided marketplace for campaign collaborations. | S1 / strict |
| `buyer` | business | The reported campaigns serve brands, including named commercial brands. | S1 / strict |
| `sector_normalised` | enterprise_software | The described marketplace supports business advertising workflows. | S1 / strict |
| `market_focus` | new_zealand | The article distinguishes its New Zealand market from planned overseas expansion. | S1 / strict |
| `prototype` | yes | Profiles, matching and actual campaign examples establish a working platform. | S1 / strict |

Interpretation limits: Paraphrase of the described live product. Proposed editorial mapping of the cited offering to the preregistered general vocabulary; requires human confirmation. Brands commission the campaigns; influencer users are not treated as the buyer. Proposed enterprise-software grouping from the contemporaneous offering; retain the current raw label Marketing software separately. Actual platform use supports prototype yes; the founders’ personal employment and company revenue remain unrecorded.

## StretchSense

Company ID: `discovery_stretchsense`. Accepted entry: 2014-11 (month).

**S1 — [StretchSense up for innovation award, UniNews Vol 43 Issue 18](https://www.auckland.ac.nz/assets/about-us/about-the-university/the-university/official-publications/uninews/2013/uoa-news-issue-18-2013.pdf)** · University of Auckland / UniNews · Public by 2013-10-18 · publisher dated.
Locator: Fixed dated university-news article, printed p.2 (17 October 2013). Current PDF metadata identifies a revision on 18 October 2013; that later day is used conservatively..

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | Wireless flexible sensors measure body movement and transmit measurements to mobile software. | The article describes soft sensors and a Bluetooth connection to an Android app. | S1 / strict |
| `product_type` | hardware | The described offering combines physical sensors with transmission circuitry. | S1 / strict |
| `sector_normalised` | manufacturing | The contemporaneous offering is sensor hardware; retain raw cohort sector Sensors. | S1 / strict |
| `market_focus` | international | The article distinguishes local sales from customers gained in the United States. | S1 / strict |
| `prototype` | yes | The article describes developed sensors and existing customers. | S1 / strict |
| `paid_pilot_or_revenue` | yes | The dated article explicitly reports local sales that year. | S1 / strict |

Interpretation limits: Proposed classification of the cited offering; human confirmation required. Reported sales establish some revenue; no amount or profitability is inferred.

## Supie

Company ID: `public_supie`. Accepted entry: 2021-11-09 (day).

**S1 — [Supie Puts $2.5m Towards Growth](https://supermarketnews.co.nz/news/supie-puts-2-5m-towards-growth/)** · Supermarket News · Public by 2021-11-09 · publisher dated.
Locator: FMCG News / Local News dateline: 09/11/2021.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | An online supermarket supplying groceries directly to Auckland households. | The article describes an already launched online grocer with household customers. | S1 / strict |
| `product_type` | food_beverage | The launch offered supermarket groceries rather than a software product sold to other retailers. | S1 / strict |
| `buyer` | household | The founder identifies households spending on groceries as customers. | S1 / strict |
| `sector_normalised` | retail_ecommerce | The online-supermarket offering is retail ecommerce. | S1 / strict |
| `market_focus` | new_zealand | The reported launch serves Auckland. | S1 / strict |
| `prototype` | yes | The article reports a launched service delivering thousands of products to members. | S1 / strict |

Interpretation limits: Short paraphrase of the product and customers. Proposed editorial mapping of the cited offering to the preregistered general vocabulary; requires human confirmation. Proposed normalisation grounded in the dated offering; retain Grocery retail as the raw cohort label. A live delivery service supports prototype yes. Membership counts alone do not establish paid memberships or revenue.

## VidApp

Company ID: `public_vidapp`. Accepted entry: 2017-09 (month).

**S1 — [The Icehouse’s Flux Accelerator Picks 6 Start-Ups for 2017 Cohort](https://nzentrepreneur.co.nz/icehouses-flux-accelerator-picks-6-start-ups-2017-cohort/)** · NZ Entrepreneur / Flux media release · Public by 2017-04-03 · publisher dated.
Locator: Visible publication date: April 3, 2017; cohort list.

**S2 — [Vidapp homepage and pricing, June 2017 capture](https://web.archive.org/web/20170616221058/http://vidapp.com:80/)** · Vidapp · Public by 2017-06-16 · archived capture.
Locator: Homepage: Vid-apps Published Through Our Platform; customer testimonials; Ongoing Support Pricing.

| Field | Proposed value | Evidence paraphrase | Source / timing |
|---|---|---|---|
| `description` | A platform lets video producers distribute and sell content through customised video apps. | The Vidapp cohort entry describes producer-owned video apps and global selling. | S1 / strict |
| `product_type` | workflow | The offering is software for publishing and distributing video content. | S1 / strict |
| `sector_normalised` | enterprise_software | The stated offering supports content-production businesses. | S1 / strict |
| `market_focus` | international | The statement explicitly frames the intended reach as worldwide. | S1 / strict |
| `buyer` | small_business | The named publisher discusses purchasing Vidapp services for its video catalogue. | S2 / strict |
| `business_model` | subscription | The historical pricing section includes a monthly recurring support plan. | S2 / strict |
| `prototype` | yes | The page lists live apps and describes customer use of the platform. | S2 / strict |

Interpretation limits: Proposed classification of the cited offering; human confirmation required. Target market geography, not proof of overseas customers or revenue. Small-business buyer is supported by an explicit priced-service customer account, not by the app audience. Subscription is the broad declared node for the recurring plan; other revenue-share plans coexist. Released apps and named customers establish product operation, without inferring a payment milestone.
