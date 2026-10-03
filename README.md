# Donor letter skill, a design exercise

A design exercise. I took a drafted AI agent skill for writing donor outreach letters, assessed whether it was fit for use in a large organization, and rewrote it to a standard I would ship.

## Repo map

- [`ASSESSMENT.md`](ASSESSMENT.md). The issues in the original draft, listed most serious first, and the rewritten description line.
- [`SKILL.md`](SKILL.md). The full rewrite, the instructions the agent follows.
- [`scripts/calculate_ask.py`](scripts/calculate_ask.py). The math, kept in code so the same donor always gets the same number.
- [`examples/`](examples). Test data and verified outputs.

The original draft is not included. The assessment describes what was in it.

## Design of the rewrite

The rewrite is built on one boundary. A letter may only contain facts that come from the donor's record or from campaign details the user has confirmed. Everything else follows from enforcing that boundary.

The work is split by nature. Generative work, where variation is a feature, stays with the model, the letters and their tone. Deterministic work, where variation is a defect, moves to code. Tier assignment and ask amounts live in a bundled script so the same donor always gets the same number. The script's strategy constants sit in one commented block that fundraising staff own, so tuning the ask formula never means touching logic, and every change is versioned in this repo.

Donor data moved out of the skill entirely. The skill defines an input contract, required and optional columns, and the data arrives at runtime from the organization's CRM export, where access controls already exist. Tiers are computed from the giving data rather than read from a column, so tier and history can never disagree.

Unknowns are never guessed. Structural gaps stop the run with a question. Row level gaps skip that donor and land in an exceptions report, which also flags asks that exceed a donor's largest ever gift, lapsed major donors who deserve a gift officer's call instead of a form letter, and possible duplicates. Every letter is a draft for staff review, and the exceptions report is what makes that review fast. The reviewer checks flagged items first instead of proofreading cold.

## Testing

The script was verified behaviorally. [`examples/sample_donors.csv`](examples/sample_donors.csv) covers the edge cases, a Platinum volunteer who gave last year, a lapsed donor, a donor with missing data, and a duplicate row. [`examples/expected_output.csv`](examples/expected_output.csv) is the verified result, checkable by hand with a calculator.

The original draft carried its own table of fifty donors. I ran that table through the script. It processed cleanly and surfaced six tier labels that violate the draft's own rules, plus seven Bronze donors whose flat ask exceeds the largest gift they have ever made. Those findings are in [`ASSESSMENT.md`](ASSESSMENT.md). The table itself is not included here.

The whole system was then tested end to end in a fresh session, with the skill, script, and data uploaded cold. It refused to draft before campaign details were confirmed, caught a stale campaign year in the brief and asked rather than assumed, ran the script instead of doing arithmetic in prose, skipped the donor with missing data, produced the exceptions report, and answered "is this ready to send" with no. When instructed to add an unconfirmed matching gift claim to a letter, it declined, explained the trust risk, asked whether a real match exists, and offered honest alternatives.

## Deployment considerations

Two things belong outside the skill file. First, a feedback loop. Reviewer corrections are the best signal for improving the skill, so edits staff make to drafts should be collected periodically and folded into the skill as versioned changes. Second, integration. The skill's input contract doesn't change whether data arrives as a CSV export or through a direct CRM connection, so the organization can wire up live data later without redesigning the skill.

## Process

I built this by directing an AI on design and implementation, then verifying behavior against expected outputs I computed independently. I specified the rules, the boundaries, and the test cases. The AI wrote the code. The verification, and every design decision in this repo, is mine. That is how I build my other AI tools.

## What this is and is not

It is a design exercise on a fictional fundraising scenario. It shows how I assess an agent skill and where I draw the line between what a model should do and what code should do.

It has not been deployed. No real donor data appears anywhere in this repo.

## Contact

Ryan Prentice, Senior Project Manager, Boston

[rprentice99@gmail.com](mailto:rprentice99@gmail.com) and [LinkedIn](https://www.linkedin.com/in/ryan-prentice-45666b57/)
