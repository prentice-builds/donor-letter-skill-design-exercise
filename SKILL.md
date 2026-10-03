---
name: donor-letter-drafting
description: >-
  Generates draft donor outreach letters with tier-based ask amounts from a
  donor data file the user provides. Use when fundraising staff ask to create
  personalized letters for a campaign and have donor data available. Output is
  drafts for staff review, never final sends.
---

# Donor Letter Drafting

Generate personalized donor letter drafts for a fundraising campaign, working
from donor data the user provides. Every letter this skill produces is a draft
for a fundraising staff member to review, edit, and send through the
organization's own channels. Nothing goes to a donor directly.

The core rule for everything below: a letter may only contain facts that come
from the donor's record or from campaign details the user has confirmed. If a
fact is not in one of those two places, it does not go in a letter. Donors
trust these communications, and one invented detail (a match that doesn't
exist, a staff member who isn't real) damages that trust in a way no
personalization can win back.

## Inputs

Two inputs are required before drafting anything.

**1. Donor data file.** One file per run, provided by the user (a CSV export
from the CRM or similar). This file is the only source of donor facts for the
run. Do not supplement it from memory, from prior sessions, or from any other
source. Required columns:

- `first_name`, `last_name`
- `largest_gift` (largest single gift, USD)
- `lifetime_total` (USD)
- `last_gift_year`
- `volunteer` (yes/no)

Optional columns: `title` (Mr./Ms./Dr. etc.), `region`, `giving_history`
(year: amount pairs, used for personalization), `do_not_contact` (yes/no).
Donors marked do-not-contact get no letter; list them in the exceptions
report as excluded by preference.

**2. Campaign details.** Best provided as a short campaign brief file
attached alongside the donor file, written once when the campaign launches
and reused for every run. Answers in chat work for a one-off. Either way,
ask for anything missing before drafting:

- Campaign type (see Campaign Types below) and campaign year
- Sender's real name and title (the staff member signing the letters)
- Donation URL
- Verified campaign facts, if any: a confirmed matching gift (who is matching,
  up to what amount), confirmed naming opportunities, event registration
  numbers. Only facts the user states may be used. If the user doesn't mention
  a match, there is no match.

If required donor columns are missing from the file entirely, or campaign
details are incomplete, stop and ask before drafting. If individual donors
have gaps (a missing largest_gift, an unparseable year), do not guess values
and do not stop the whole run: skip drafting for those donors and list them in
the exceptions report.

## Workflow

1. Read the donor file. Confirm required columns exist.
2. Run `scripts/calculate_ask.py` on the file (see Ask Amounts). It assigns
   each donor a tier and an ask amount, and flags rows with missing or
   suspect data.
3. Draft one letter per donor using the tier tone, campaign angle, and
   template below. Use only facts from that donor's row and the campaign
   details.
4. Write each letter to its own file so staff can edit them individually.
5. Write the exceptions report (see Output and Review).
6. Return the drafts and the report together. State clearly that these are
   drafts pending staff review.

## Donor Tiers

Tiers are assigned by the script from the data, not taken from a column, so
tier and giving history can never disagree. The dollar thresholds and the
lapsed cutoff are defined once, in the script's constants block, and nowhere
else; read them there if you need them. Use the `tier` column the script
outputs.

The tones below are starting defaults. If the organization has a brand or
voice guide, or the user gives tone direction, that overrides these.

- **Platinum**: Formal, personal. Reference specific gifts from their history.
  Mention a naming opportunity only if the user confirmed one exists.
- **Gold**: Warm and professional. Mention legacy giving as an option to
  discuss, not a pitch.
- **Silver**: Friendly. Offer the monthly giving option.
- **Bronze**: Encouraging and brief. Mention peer fundraising pages.
- **Lapsed**: Warm and forward-looking. Welcome them back; do not apologize,
  guilt, or dwell on the gap. One sentence acknowledging time has passed is
  plenty.

## Campaign Types

- **Emergency Appeal**: Urgency is fine; fabrication is not. Describe the real
  situation the user provides. Mention matching only if confirmed.
- **Annual Fund**: Consistency and community. Reference the donor's giving
  streak only if `giving_history` shows one.
- **Capital Campaign**: Legacy and permanence.
- **Event Fundraiser**: Community and participation. Cite registration numbers
  only if the user provided them.

If the campaign type is not one of these, ask the user rather than defaulting.

## Ask Amounts

Never calculate ask amounts in prose or in your head. Run
`scripts/calculate_ask.py` and use its output. The script exists so the same
donor always gets the same ask: the formula's constants (tier percentages,
uplifts, rounding) are defined once at the top of the script where fundraising
staff can review and change them, and the order of operations is fixed in
code. If the script fails or a donor's inputs don't parse, that donor goes in
the exceptions report, not into a letter with a guessed number. If your
environment cannot execute the script at all, stop and tell the user;
reproducing the formula in prose or mental math defeats the reason it exists.

## Letter Rules

**Salutations.** Never infer a title or gender from a name.

- Platinum and Gold with a `title` on file: "Dear [Title] [Last Name],"
- Platinum and Gold without a title: "Dear [First Name] [Last Name],"
- Silver, Bronze, Lapsed: "Dear [First Name],"

**Template.** Fill every placeholder from the donor row or campaign details.
A placeholder with no source value means the letter goes to exceptions, not
into print with a blank or a guess.

```
[DATE]

[SALUTATION]

Thank you paragraph: reference their actual giving (lifetime total or a
specific past gift from giving_history).

Campaign paragraph: 2-3 sentences on this campaign, using the campaign type
angle and only user-confirmed facts.

Ask paragraph: invite a gift of $[ASK_AMOUNT from script], plus the
tier-specific option (naming, legacy, monthly, peer page).

How to give: [DONATION_URL].

With gratitude,
[SENDER_NAME]
[SENDER_TITLE]
```

Write each draft as a plain markdown file, one per donor, named
`lastname_firstname.md`. Staff edit these directly; final formatting (email
HTML, print layout) happens in the organization's sending tools downstream.

## Guardrails

These exist because letters go to real donors under the organization's name.

- Never state or imply a matching gift, naming opportunity, deadline, or any
  campaign fact the user has not confirmed.
- Never invent a staff name. Letters are signed by the real sender the user
  named, or they don't go out.
- Never fill missing donor data with assumptions. Missing data is reported,
  not guessed.
- Never infer gender, title, age, or wealth from a name or region.
- Never present a draft as ready to send.
- Donor data stays contained: it appears in the letters and the exceptions
  report, nowhere else.

## Output and Review

Return two things:

1. **The letter drafts**, one file per donor.
2. **An exceptions report** (`exceptions.md`) listing: donors skipped and why,
   donors drafted but flagged by the script (missing optional data, ask amount
   exceeding their largest-ever gift, possible duplicates), and any campaign
   facts you needed but didn't have.

The report is what makes staff review fast: a reviewer should be able to check
the flagged items first instead of proofreading every letter cold. End every
run by reminding the user that drafts require review before sending.
