import {test, expect} from '@playwright/test';

async function openMRI(page: import('@playwright/test').Page) {
  await page.goto('/');
  await page.getByRole('button', {name:'Research dossiers',exact:true}).click();
  await page.getByRole('button', {name:'Automated Breast MRI Reporting',exact:true}).click();
  const dossier = page.getByRole('dialog', {name:'Automated Breast MRI Reporting research dossier'});
  const comparison = dossier.getByRole('region', {name:'Provider evaluation comparison',exact:true});
  await expect(comparison.locator('.healthtech-peer')).toHaveCount(3);
  return {dossier, comparison};
}

test('MRI dossier exposes three attributable pathway precedents and separated later milestones', async ({page}, info) => {
  const errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  const {dossier, comparison} = await openMRI(page);
  await expect(comparison).toContainText('Same-stage comparison: abstain');
  const volpara = comparison.locator('.healthtech-peer').filter({has:page.getByRole('heading', {name:'Volpara Health Technologies',exact:true})});
  const formus = comparison.locator('.healthtech-peer').filter({has:page.getByRole('heading', {name:'Formus Labs',exact:true})});
  await expect(volpara).toContainText('mammographic density measurement is not breast MRI report drafting');
  await expect(formus).toContainText('intended US evaluation, not completed evaluation');
  await volpara.getByText('Reference-document evidence · 5 claims', {exact:true}).click();
  await expect(volpara).toContainText('beta-site integration and usability testing');
  await expect(volpara.getByRole('link', {name:'Volpara K102556: applicant summary and FDA decision letter'}).first()).toHaveAttribute('href', 'https://www.accessdata.fda.gov/cdrh_docs/pdf10/K102556.pdf');
  await volpara.getByText('Dates and source record', {exact:true}).first().click();
  await expect(volpara).toContainText('Historical web availability: not verified');
  await formus.getByText('Later reports and milestones · 6 claims', {exact:true}).click();
  await expect(formus).toContainText('31 March 2023');
  await expect(formus).toContainText('no submission number');
  await formus.getByText('Unknowns and unresolved mappings', {exact:true}).click();
  await expect(formus).toContainText('Identify the submission number and device version');
  await comparison.getByRole('link', {name:'obs_ht_formus_validation23',exact:true}).first().click();
  await expect(dossier.locator('#research-obs_ht_formus_validation23')).toBeFocused();
  await expect(dossier.getByLabel('Evidence subjects')).toHaveValue('all');
  await expect(dossier.locator('#research-obs_ht_formus_validation23')).toContainText('Claim responsibility: company');
  await dossier.getByLabel('Evidence field').selectOption('');
  await dossier.locator('.healthtech-comparison').scrollIntoViewIfNeeded();
  await dossier.screenshot({path: info.outputPath('mri-comparison.png')});
  expect(errors).toEqual([]);
});

test('historical cutoff clears future comparison content and sparse healthcare contrast abstains', async ({page}) => {
  const {dossier, comparison} = await openMRI(page);
  await comparison.getByLabel('Comparison evidence view').selectOption('historical');
  await comparison.getByLabel('Comparison cutoff').fill('2022-02-02');
  await expect(comparison).toContainText('Historical cutoff: 2022-02-02');
  await expect(comparison.locator('.healthtech-peer')).toHaveCount(0);
  await expect(comparison).toContainText('No historical availability witness');
  await expect(comparison).not.toContainText('K213272');
  await expect(comparison).not.toContainText('acquisition');
  await comparison.getByLabel('Comparison evidence view').selectOption('research');
  await expect(comparison).toContainText('prepared after this research cutoff');
  await expect(comparison.locator('.healthtech-peer')).toHaveCount(0);
  await page.keyboard.press('Escape');
  await page.getByRole('button', {name:'RosterLab',exact:true}).click();
  const roster = page.getByRole('dialog', {name:'RosterLab research dossier'});
  const contrast = roster.getByRole('region', {name:'Provider evaluation comparison',exact:true});
  await expect(contrast).toContainText('Shared healthcare wording alone is insufficient');
  await expect(contrast.locator('.healthtech-peer')).toHaveCount(0);
  await expect(roster.locator('#research-obs_rl_solution')).toBeVisible();
});

test('MRI comparison recovers from API errors, downloads provenance and fits a narrow drawer', async ({page}, info) => {
  await page.setViewportSize({width:390,height:844});
  await page.route('**/api/research/subjects/subj_ht_mri/comparisons?**', async route => route.fulfill({status:503,body:'Temporary test failure'}));
  await page.goto('/');
  await page.getByRole('button', {name:'Research dossiers',exact:true}).click();
  await page.getByRole('button', {name:'Automated Breast MRI Reporting',exact:true}).click();
  const dossier = page.getByRole('dialog', {name:'Automated Breast MRI Reporting research dossier'});
  const comparison = dossier.getByRole('region', {name:'Provider evaluation comparison',exact:true});
  await expect(comparison.getByRole('button', {name:'Retry comparison'})).toBeVisible();
  await page.unroute('**/api/research/subjects/subj_ht_mri/comparisons?**');
  await comparison.getByRole('button', {name:'Retry comparison'}).click();
  await expect(comparison.locator('.healthtech-peer')).toHaveCount(3);
  await comparison.getByText('Comparison method and provenance', {exact:true}).click();
  const download = page.waitForEvent('download');
  await comparison.getByRole('link', {name:'Comparison JSON ↓'}).click();
  const stream = await (await download).createReadStream();
  if (!stream) throw new Error('Comparison download unavailable');
  const chunks=[];
  for await (const chunk of stream) chunks.push(chunk);
  const data=JSON.parse(Buffer.concat(chunks).toString('utf8'));
  expect(data.peers).toHaveLength(3);
  expect(data.policy_version).toBe('healthtech-curated-pathways-1.0');
  expect(data.source_packet_sha256s.length).toBeGreaterThan(0);
  expect(await dossier.evaluate(node => node.scrollWidth <= node.clientWidth)).toBe(true);
  await dossier.locator('.healthtech-comparison').scrollIntoViewIfNeeded();
  await dossier.screenshot({path:info.outputPath('mri-mobile.png')});
});

test('expanded university projects expose their own evidence, scoped precedents and sparse abstention', async ({page}) => {
  await page.goto('/');
  await page.getByRole('button', {name:'Research dossiers',exact:true}).click();
  for (const [name,peer,count] of [['Neurofanos','Wellumio',2],['IVF Decision Support Tool','Alimetry',2],['VistaVision','Toku Eyes / Toku Inc. (unresolved)',1],['PulseMap PAD Detector','',0]] as const) {
    await page.getByRole('button', {name,exact:true}).click();
    const dossier=page.getByRole('dialog', {name:`${name} research dossier`});
    const comparison=dossier.getByRole('region', {name:'Provider evaluation comparison',exact:true});
    await expect(comparison.locator('.healthtech-peer')).toHaveCount(count);
    if (peer) await expect(comparison.getByRole('heading', {name:peer,exact:true})).toBeVisible();
    else await expect(comparison).toContainText('measurement modality');
    if (name==='Neurofanos') {
      const grant=dossier.locator('#research-obs_ht_neuro_grant');
      await expect(grant).toContainText('research funding to its research team');
      await expect(grant).toContainText('not a reported equity investment');
    }
    if (name==='IVF Decision Support Tool') await expect(dossier.locator('#research-obs_ht_ivf_evaluation_plan')).toContainText('intention target');
    await expect(dossier.locator('#research-section-unknowns')).toContainText('procurement authority');
    await page.keyboard.press('Escape');
    await expect(page.getByRole('button', {name,exact:true})).toBeFocused();
  }
});

test('directory counts distinct ventures and opens the hospital feasibility evidence', async ({page}) => {
  await page.goto('/');
  await page.getByRole('button', {name:'Research dossiers',exact:true}).click();
  const coverage = page.getByRole('region', {name:'Healthtech comparison coverage'});
  await expect(coverage).toContainText('4 of 5 university projects');
  await expect(coverage).toContainText('8 project–venture pairs use 5 distinct reference ventures');
  await page.getByLabel('Search research dossiers').fill('Automated Breast MRI');
  const row = page.locator('.research-directory-row');
  await expect(row).toHaveCount(1);
  await expect(row).toContainText('3 pathway precedents · Volpara Health Technologies, Formus Labs, Wellumio');
  await row.getByRole('button').click();
  const drawer = page.getByRole('dialog');
  const wellumio = drawer.locator('.healthtech-peer').filter({has: page.getByRole('heading', {name:'Wellumio',exact:true})});
  await wellumio.getByText('Later reports and milestones · 3 claims').click();
  await expect(wellumio).toContainText('HREC/105831/MH-2024');
  await expect(wellumio).toContainText('Of 49 stroke participants, 40 had successful scans.');
  await wellumio.getByRole('link', {name:'obs_ht_well_ethics',exact:true}).first().click();
  await expect(drawer.locator('#research-obs_ht_well_ethics')).toBeFocused();
  await expect(drawer.getByRole('link', {name:/^Source packet .* JSON/})).toHaveCount(3);
  const csvUrl = await drawer.getByRole('link', {name:'observations CSV ↓',exact:true}).getAttribute('href');
  const csv = await (await page.request.get(csvUrl!)).text();
  expect(csv).toContain('obs_ht_well_ethics');
  expect(csv).toContain('obs_ht_volpara_validation');
});
