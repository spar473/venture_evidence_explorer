import {test,expect} from '@playwright/test';
test('discovery staging totals, scope filters, unresolved aliases and withheld promotion',async({page})=>{
 await page.goto('/?mode=research');await page.getByRole('button',{name:'Discovery queue',exact:true}).click();
 await expect(page.locator('.discovery-workspace')).toContainText('274 staged leads');await expect(page.locator('.discovery-workspace')).toContainText('27 source families');await expect(page.locator('.discovery-workspace')).toContainText('0 promoted');
 await page.getByLabel('Reported outcome period').selectOption('2021');await expect(page.locator('.discovery-table tbody tr')).toHaveCount(2);
 await expect(page.locator('.discovery-table')).toContainText('Vend');await expect(page.locator('.discovery-table')).toContainText('Timely');
 await page.getByLabel('Reported outcome period').selectOption('');await page.getByLabel('Search discovery leads').fill('Kura');await expect(page.locator('.discovery-table tbody tr')).toHaveCount(2);
 const opener=page.getByRole('button',{name:'Kura',exact:true});await opener.click();const dialog=page.getByRole('dialog',{name:'Kura discovery lead'});
 await expect(dialog).toContainText('discovery_kuradynamics');await expect(dialog).toContainText('Promotion withheld');await expect(dialog).toContainText('Unknown / not supplied');
 await expect(dialog.getByRole('button',{name:'Close lead'})).toBeFocused();await page.keyboard.press('Escape');await expect(opener).toBeFocused();
 await page.getByLabel('Search discovery leads').fill('RosterLab');await page.getByRole('button',{name:'RosterLab',exact:true}).click();
 const roster=page.getByRole('dialog',{name:'RosterLab discovery lead'});await expect(roster).toContainText('No actual review decisions supplied');
 await expect(roster.getByRole('link').first()).toHaveAttribute('href',/^https:\/\//);
 const response=await page.request.get('/api/discovery/exports/candidates.csv');expect(response.status()).toBe(200);expect(await response.text()).toContain('discovery_rosterlab');
 const corpus=await page.request.get('/api/ventures');expect((await corpus.json()).total).toBe(10);
});
