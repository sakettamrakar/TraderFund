import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';


function resolveFrontendUrl() {
    const runtimePath = path.resolve(__dirname, '../../..', '.runtime', 'service_ports.json');
    if (!fs.existsSync(runtimePath)) {
        return process.env.DASHBOARD_FRONTEND_URL || 'http://127.0.0.1:21011';
    }

    try {
        const runtimeState = JSON.parse(fs.readFileSync(runtimePath, 'utf-8'));
        const service = runtimeState.services?.dashboard_frontend;
        if (service?.public_host && service?.port) {
            return `http://${service.public_host}:${service.port}`;
        }
    } catch {
        return process.env.DASHBOARD_FRONTEND_URL || 'http://127.0.0.1:21011';
    }

    return process.env.DASHBOARD_FRONTEND_URL || 'http://127.0.0.1:21011';
}

test('Verify Inspection Mode', async ({ page }) => {
    // 1. Open Dashboard
    await page.goto(resolveFrontendUrl());
    await page.waitForSelector('.system-status-banner');
    await page.screenshot({ path: 'screenshot_1_live_mode.png' });

    // 2. Check Inspection Banner NOT present
    const banner = await page.$('.alert-banner.inspection');
    if (banner) throw new Error("Inspection banner visible in live mode!");

    // 3. Enter Inspection Mode
    await page.click('.inspection-toggle');
    await page.waitForSelector('.alert-banner.inspection');
    await page.screenshot({ path: 'screenshot_2_inspection_mode.png' });

    // 4. Verify visual indicators
    const bannerText = await page.textContent('.alert-banner.inspection');
    if (!bannerText.includes('INSPECTION MODE ACTIVE')) throw new Error("Banner text incorrect");

    // 5. Verify Data Isolation (Blocked Widgets)
    const blockedWidget = await page.$('.inspection-blocker');
    if (!blockedWidget) throw new Error("Intelligence Panel not blocked!");
    await page.screenshot({ path: 'screenshot_3_blocked_widgets.png' });

    // 6. Exit Inspection Mode
    await page.click('.inspection-toggle');
    await page.waitForSelector('.alert-banner.inspection', { state: 'hidden' });
    await page.screenshot({ path: 'screenshot_4_restored_live.png' });
});
