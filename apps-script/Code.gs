/**
 * Rider Gate Staff Performance Dashboard API
 *
 * Keep the Google Sheets PRIVATE.
 * Configure all sheet IDs/names and the API token under:
 * Apps Script -> Project Settings -> Script properties
 *
 * Required properties:
 * API_TOKEN
 * PERSON_1_NAME
 * PERSON_1_SHEET_ID
 * PERSON_2_NAME
 * PERSON_2_SHEET_ID
 *
 * Add PERSON_3_NAME / PERSON_3_SHEET_ID, etc. as needed.
 */

const HEADER_VARIANTS = {
  date: ["date of visit", "date visit", "visit date", "date"],
  dealer: ["dealer name", "dealer"],
  bikeListing: ["bike listing", "bike listings", "listing", "listings"],
  sales: ["no. of sales", "no of sales", "number of sales", "sales"]
};

function doGet() {
  return json_({
    ok: false,
    error: "POST requests only."
  });
}

function doPost(e) {
  try {
    const body = parseBody_(e);
    const props = PropertiesService.getScriptProperties();
    const expectedToken = String(props.getProperty("API_TOKEN") || "");
    const suppliedToken = String(body.token || "");

    if (!expectedToken) {
      return json_({ ok: false, error: "API_TOKEN is not configured in Apps Script properties." });
    }

    if (!constantTimeEquals_(suppliedToken, expectedToken)) {
      return json_({ ok: false, error: "Unauthorised." });
    }

    const staff = getStaffConfig_(props);
    if (!staff.length) {
      return json_({ ok: false, error: "No staff sheets are configured in Apps Script properties." });
    }

    const rows = [];
    const errors = [];

    staff.forEach(person => {
      try {
        const staffRows = readStaffSheet_(person);
        staffRows.forEach(row => rows.push(row));
      } catch (err) {
        errors.push({
          staffId: person.id,
          staffName: person.name,
          error: err && err.message ? err.message : String(err)
        });
      }
    });

    return json_({
      ok: true,
      updatedAt: new Date().toISOString(),
      staff: staff.map(person => ({ id: person.id, name: person.name })),
      rows: rows,
      errors: errors
    });
  } catch (err) {
    return json_({
      ok: false,
      error: err && err.message ? err.message : String(err)
    });
  }
}

function getStaffConfig_(props) {
  const staff = [];
  for (let i = 1; i <= 50; i++) {
    const name = String(props.getProperty(`PERSON_${i}_NAME`) || "").trim();
    const sheetId = String(props.getProperty(`PERSON_${i}_SHEET_ID`) || "").trim();
    if (name && sheetId) {
      staff.push({ id: `person-${i}`, name: name, sheetId: sheetId });
    }
  }
  return staff;
}

function readStaffSheet_(person) {
  // Because the Web App executes as YOU, the spreadsheet may remain Restricted.
  const spreadsheet = SpreadsheetApp.openById(person.sheetId);
  const sheet = spreadsheet.getSheets()[0];
  const values = sheet.getDataRange().getDisplayValues();

  if (!values || !values.length) return [];

  const header = findHeaderRow_(values);
  if (!header) {
    throw new Error("Could not find Date of Visit, Dealer Name, Bike Listing and No. of Sales headers.");
  }

  const rows = [];
  for (let r = header.rowIndex + 1; r < values.length; r++) {
    const row = values[r];
    const date = pick_(row, header.indexes.date);
    const dealer = pick_(row, header.indexes.dealer);
    const bike = pick_(row, header.indexes.bikeListing);
    const sales = pick_(row, header.indexes.sales);

    if (!date && !dealer && !bike && !sales) continue;
    if (!dealer) continue;

    rows.push({
      staffId: person.id,
      staffName: person.name,
      date: date,
      dealer: dealer,
      bikeListing: toNumber_(bike),
      sales: toNumber_(sales)
    });
  }
  return rows;
}

function findHeaderRow_(matrix) {
  const maxRows = Math.min(matrix.length, 20);
  for (let r = 0; r < maxRows; r++) {
    const row = matrix[r].map(normaliseHeader_);
    const indexes = {};

    Object.keys(HEADER_VARIANTS).forEach(key => {
      indexes[key] = row.findIndex(cell => HEADER_VARIANTS[key].indexOf(cell) !== -1);
    });

    if (Object.keys(indexes).every(key => indexes[key] >= 0)) {
      return { rowIndex: r, indexes: indexes };
    }
  }
  return null;
}

function normaliseHeader_(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[._-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function pick_(row, index) {
  return index < row.length ? String(row[index] || "").trim() : "";
}

function toNumber_(value) {
  const cleaned = String(value || "")
    .replace(/,/g, "")
    .replace(/[^\d.-]/g, "");
  const number = Number(cleaned);
  return Number.isFinite(number) ? number : 0;
}

function parseBody_(e) {
  if (!e || !e.postData || !e.postData.contents) return {};
  try {
    return JSON.parse(e.postData.contents);
  } catch (_) {
    return {};
  }
}

function constantTimeEquals_(a, b) {
  a = String(a || "");
  b = String(b || "");
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
