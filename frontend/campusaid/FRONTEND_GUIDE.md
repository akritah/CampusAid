# CampusAid — Frontend Styling Guide
> Keep this file open in VSCode. Tell Copilot: "Follow FRONTEND_GUIDE.md for all styling."

---

## Ground Rules

1. **Never touch logic.** No fetch, useState, useEffect, onSubmit, useRouter, or auth code.
2. **Never rename files, components, props, or variables.**
3. **Only change:** className, style={{}}, CSS files, and CSS module values.
4. **One file at a time.** Restyle, then move to the next.
5. **Use var(--token) always.** Never hardcode hex values directly in components.

---

## Step 0 — globals.css (do this first)

Add to the very top of your existing `globals.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
```

Add inside your existing `:root {}` block (or create one):

```css
:root {
  /* Brand */
  --navy:        #0D1B3E;
  --navy-mid:    #142254;
  --navy-light:  #1E3170;
  --gold:        #C8922A;
  --gold-light:  #E5A83C;
  --gold-pale:   #F5E6C8;
  --cream:       #FAF7F2;

  /* Semantic */
  --success:     #2E7D52;
  --success-bg:  #E8F5EE;
  --warning:     #C05621;
  --warning-bg:  #FEF3E2;
  --danger:      #9B2335;
  --danger-bg:   #FDE8EC;
  --info:        #1E5799;
  --info-bg:     #E8F0FB;

  /* Neutrals */
  --slate:       #4A5568;
  --slate-light: #718096;
  --border:      #E2E8F0;

  /* Typography */
  --font-display: 'Playfair Display', serif;
  --font-body:    'DM Sans', sans-serif;
  --font-mono:    'DM Mono', monospace;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(13,27,62,0.08);
  --shadow-md: 0 4px 12px rgba(13,27,62,0.10);
  --shadow-lg: 0 10px 30px rgba(13,27,62,0.12);

  /* Radius */
  --radius-sm: 6px;
  --radius:    10px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

body {
  font-family: var(--font-body);
  background: #F5F7FA;
  color: var(--navy);
}
```

---

## Step 1 — Page Layout

```css
/* Main content wrapper (the div next to sidebar) */
.main-content {
  margin-left: 240px;
  padding: 32px;
  background: #F5F7FA;
  min-height: 100vh;
}

/* Page title — the h1 at top of every page */
.page-title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: 4px;
}

/* Subtitle under page title */
.page-subtitle {
  font-size: 13px;
  color: var(--slate-light);
  margin-bottom: 28px;
}

/* Section label (small ALL-CAPS above a section) */
.section-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 8px;
}
```

---

## Step 2 — Sidebar

```css
.sidebar {
  width: 240px;
  height: 100vh;
  background: var(--navy);
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  padding: 24px 0;
  z-index: 100;
}

/* Logo area */
.sidebar-brand {
  padding: 0 20px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 8px;
}

.sidebar-logo-mark {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--navy);
}

.sidebar-logo-text {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 700;
  color: white;
}

.sidebar-logo-sub {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  letter-spacing: 0.5px;
}

/* Section label inside sidebar */
.sidebar-section-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.3);
  padding: 12px 20px 4px;
}

/* Every nav link/item */
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 16px;
  margin: 2px 8px;
  border-radius: var(--radius);
  color: rgba(255,255,255,0.6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
  border: 1px solid transparent;
}

.sidebar-item:hover {
  background: rgba(255,255,255,0.07);
  color: white;
}

/* The currently active nav item */
.sidebar-item.active,
.sidebar-item[aria-current="page"] {
  background: rgba(200,146,42,0.15);
  color: var(--gold-light);
  border-color: rgba(200,146,42,0.2);
}

/* Notification badge on nav items */
.sidebar-badge {
  margin-left: auto;
  background: var(--danger);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

/* Bottom user info strip */
.sidebar-footer {
  margin-top: auto;
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--gold), var(--gold-light));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--navy);
  flex-shrink: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: white;
}

.user-role {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
}
```

---

## Step 3 — Topbar

```css
.topbar {
  height: 60px;
  background: white;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 28px;
  gap: 16px;
  margin-left: 240px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.topbar-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 600;
  color: var(--navy);
}

.topbar-search input {
  padding: 8px 14px 8px 36px;
  border: 1.5px solid var(--border);
  border-radius: 20px;
  font-size: 13px;
  font-family: var(--font-body);
  background: var(--cream);
  outline: none;
  width: 300px;
}

.topbar-search input:focus {
  border-color: var(--navy-light);
}
```

---

## Step 4 — Cards

```css
/* Generic content card */
.card {
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--navy);
}

.card-body {
  padding: 20px;
}

/* Dark card (used for voice complaint, CTA sections) */
.card-dark {
  background: linear-gradient(135deg, var(--navy), var(--navy-mid));
  border: none;
  border-radius: var(--radius-lg);
  padding: 24px;
  color: white;
}
```

---

## Step 5 — Stat Cards

```css
.stat-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  box-shadow: var(--shadow-sm);
  position: relative;
}

/* Coloured left border — add one of these classes */
.stat-card.blue   { border-left: 4px solid var(--navy-light); }
.stat-card.gold   { border-left: 4px solid var(--gold);       }
.stat-card.green  { border-left: 4px solid var(--success);    }
.stat-card.red    { border-left: 4px solid var(--danger);     }

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-bottom: 12px;
}

.stat-icon.blue  { background: rgba(30,49,112,0.08); }
.stat-icon.gold  { background: var(--gold-pale);     }
.stat-icon.green { background: var(--success-bg);    }
.stat-icon.red   { background: var(--danger-bg);     }

.stat-value {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--navy);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--slate-light);
  font-weight: 500;
}

.stat-trend {
  font-size: 11px;
  font-weight: 600;
  margin-top: 8px;
}

.stat-trend.up   { color: var(--success); }
.stat-trend.down { color: var(--danger);  }
```

---

## Step 6 — Buttons

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--radius);
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.2px;
  transition: all 0.2s;
  text-decoration: none;
  white-space: nowrap;
}

/* Sizes */
.btn-sm { padding: 7px 14px;  font-size: 12px; }
.btn-lg { padding: 14px 28px; font-size: 15px; }

/* Variants */
.btn-primary {
  background: linear-gradient(135deg, var(--navy-light), var(--navy));
  color: white;
  box-shadow: 0 4px 14px rgba(13,27,62,0.3);
}
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(13,27,62,0.4);
}

.btn-gold {
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  color: var(--navy);
  box-shadow: 0 4px 14px rgba(200,146,42,0.35);
}
.btn-gold:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(200,146,42,0.45);
}

.btn-outline {
  background: transparent;
  color: var(--navy);
  border: 1.5px solid var(--border);
}
.btn-outline:hover {
  border-color: var(--navy);
  background: rgba(13,27,62,0.04);
}

.btn-ghost {
  background: transparent;
  color: var(--slate);
  border: none;
}
.btn-ghost:hover {
  background: rgba(13,27,62,0.06);
  color: var(--navy);
}

.btn-danger {
  background: linear-gradient(135deg, #c0392b, var(--danger));
  color: white;
}
```

---

## Step 7 — Status Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

/* Dot before label */
.badge::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
}

/* One class per status value from your API */
.badge-submitted    { background: var(--info-bg);    color: var(--info);    }
.badge-assigned     { background: var(--gold-pale);  color: var(--gold);    }
.badge-under-review { background: var(--warning-bg); color: var(--warning); }
.badge-resolved     { background: var(--success-bg); color: var(--success); }
.badge-escalated    { background: var(--danger-bg);  color: var(--danger);  }
```

Map your status value to a class like this (keep your existing logic, just change className):
```tsx
// Keep ALL your existing logic. Only change the className line.
const statusClass = {
  submitted:    'badge badge-submitted',
  assigned:     'badge badge-assigned',
  under_review: 'badge badge-under-review',
  resolved:     'badge badge-resolved',
  escalated:    'badge badge-escalated',
}[complaint.status];

// Then on the element:
<span className={statusClass}>{complaint.status}</span>
```

---

## Step 8 — Forms & Inputs

```css
.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--navy);
  letter-spacing: 0.2px;
}

.input-field {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--navy);
  background: white;
  transition: all 0.2s;
  outline: none;
}

.input-field:focus {
  border-color: var(--navy-light);
  box-shadow: 0 0 0 3px rgba(30,49,112,0.08);
}

.input-field::placeholder {
  color: var(--slate-light);
}

/* Select dropdown arrow */
.select-field {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%234A5568' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}
```

---

## Step 9 — Tables

```css
.table-wrap {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

thead {
  background: var(--navy);
}

thead th {
  padding: 12px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.7);
}

tbody tr {
  border-bottom: 1px solid var(--border);
  background: white;
  transition: background 0.15s;
}

tbody tr:hover         { background: rgba(13,27,62,0.02); }
tbody tr:last-child    { border-bottom: none; }

tbody td {
  padding: 12px 16px;
  color: var(--slate);
  vertical-align: middle;
}

tbody td:first-child {
  color: var(--navy);
  font-weight: 500;
}

/* Complaint ID cells */
.cell-id {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--slate-light);
}
```

---

## Step 10 — Complaint List Items

```css
.complaint-item {
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.complaint-item:hover {
  border-color: var(--navy-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.complaint-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius);
  background: var(--info-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.complaint-id {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--slate-light);
  margin-bottom: 3px;
}

.complaint-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--navy);
  margin-bottom: 4px;
}

.complaint-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 11px;
  color: var(--slate-light);
}
```

---

## Step 11 — Login Page

```css
/* Outer wrapper — split screen */
.auth-screen {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

/* Left dark panel */
.auth-left {
  background: linear-gradient(145deg, var(--navy), var(--navy-mid), #1E3170);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;
}

.auth-left-title {
  font-family: var(--font-display);
  font-size: 40px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
  margin-bottom: 16px;
}

.auth-left-subtitle {
  font-size: 15px;
  color: rgba(255,255,255,0.6);
  line-height: 1.7;
  max-width: 300px;
}

/* Feature highlight cards on the left panel */
.auth-feature-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.auth-feature-card span:first-child { font-size: 24px; }

.auth-feature-title {
  font-size: 13px;
  font-weight: 600;
  color: white;
}

.auth-feature-desc {
  font-size: 11px;
  color: rgba(255,255,255,0.45);
}

/* Right light panel */
.auth-right {
  background: var(--cream);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.auth-form-wrap {
  width: 100%;
  max-width: 400px;
}

.auth-form-title {
  font-family: var(--font-display);
  font-size: 30px;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: 6px;
}

.auth-form-subtitle {
  font-size: 14px;
  color: var(--slate);
  margin-bottom: 32px;
}
```

---

## Step 12 — Timeline (Complaint Detail)

```css
.timeline {
  position: relative;
  padding-left: 28px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 6px;
  bottom: 0;
  width: 2px;
  background: var(--border);
}

.timeline-item {
  position: relative;
  padding-bottom: 24px;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -24px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
  border: 2.5px solid var(--border);
  z-index: 1;
}

.timeline-item.active::before { border-color: var(--navy);   background: var(--navy);   }
.timeline-item.done::before   { border-color: var(--success); background: var(--success); }

.timeline-date {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--slate-light);
  margin-bottom: 3px;
}

.timeline-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--navy);
  margin-bottom: 2px;
}

.timeline-sub {
  font-size: 12px;
  color: var(--slate);
}
```

---

## Quick Reference — What Goes Where

| Element                  | Class to use                          |
|--------------------------|---------------------------------------|
| Page wrapper             | `.main-content`                       |
| Page h1                  | `.page-title`                         |
| Subtitle under h1        | `.page-subtitle`                      |
| ALL-CAPS section label   | `.section-label`                      |
| Any content box          | `.card` + `.card-header` + `.card-body` |
| Dark CTA card            | `.card-dark`                          |
| Number summary box       | `.stat-card.blue/gold/green/red`      |
| Primary action button    | `.btn .btn-primary`                   |
| CTA / highlight button   | `.btn .btn-gold`                      |
| Secondary button         | `.btn .btn-outline`                   |
| Subtle button            | `.btn .btn-ghost`                     |
| Destructive button       | `.btn .btn-danger`                    |
| Small / large button     | add `.btn-sm` or `.btn-lg`            |
| Status pill              | `.badge .badge-{status}`              |
| Text input               | `.input-group` > `.input-label` + `.input-field` |
| Select dropdown          | `.input-field .select-field`          |
| Data table               | `.table-wrap` > `table`               |
| Complaint ID text        | `.cell-id`                            |
| Complaint row/card       | `.complaint-item`                     |
| Complaint ID inside card | `.complaint-id`                       |
| Complaint title          | `.complaint-title`                    |
| Resolution timeline      | `.timeline` > `.timeline-item.done/active` |

---

## Copilot Instructions

When working on any file in this project, follow this guide exactly:

- **Adding styles?** Use classes from this guide. Never invent new color values.
- **Existing className?** Replace it with the matching class from the Quick Reference table above.
- **No className yet?** Add one from this guide. Don't change anything else on the line.
- **CSS module file?** Rewrite the values only — keep all class names as they are.
- **Unsure which class to use?** Ask — don't guess with a random color.
- **Logic line?** Skip it. Move to the next visual element.
