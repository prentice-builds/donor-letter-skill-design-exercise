# Assessment of the drafted skill

I listed the issues most serious first, which raises the question of what serious means. I ranked by worst plausible outcome for the organization, so the list starts with what could create legal exposure or destroy donor trust and ends with matters of taste.

1. The skill instructs the agent to fabricate claims, a matching gift promised "even if no match is confirmed," letters signed by a relationship manager it has no way to look up, a naming opportunity nobody verified. This matters because it puts lies in front of donors at scale, and trust is the asset a nonprofit runs on.

2. There is no human review step. This matters because review is the containment layer, and without it every other failure on this list travels straight from the agent to a donor's inbox at scale.

3. Donor records are embedded in the skill. This data belongs in the CRM behind access controls, not in a file that gets copied to everyone who installs the skill. The embedded data also becomes outdated over time.

4. It includes two conflicting sources for the same data. Step 1 says read the uploaded file, step 4 says use the embedded table, with no rule for which data set wins when they don't match.

5. The agent resolves unknowns by guessing. Missing fields get assumptions, missing titles get a gender, unknown tiers get defaults. None of it is flagged for anyone to check.

6. The ask calculation is open to interpretation. Arithmetic run by a model can give the same donor different ask amounts on different runs, and the steps don't specify order of operations. The math needs one deterministic answer.

7. The description is a keyword list. It initiates on nearly any communication task instead of defining when this skill actually applies.

8. The output format wasn't chosen against a real workflow. HTML in chat can't be edited by staff, and no delivery system is named to receive it.

9. The skill hardcodes voice decisions, like an apologetic tone for lapsed donors.

## Evidence from testing

Running the draft's own donor table through a deterministic version of its rules confirmed issue 4 with receipts. The embedded tier column disagrees with the draft's own tier definitions for six of fifty donors. One donor has $25,000 in lifetime giving and is labeled Silver, which the draft's own thresholds define as Gold, so that donor would have been asked for 15% of their largest gift instead of 25%. Two donors labeled Platinum last gave in 2020 and are lapsed under the draft's own 3 year rule. The original skill would have silently trusted whichever source the model happened to read.

# The rewritten description line

**The original**

> Use this skill whenever a user mentions donors, fundraising, money, emails, letters, charity, nonprofits, campaigns, giving, volunteers, events, reports, grants, sponsorships, or any kind of outreach or communication task.

**The rewrite**

> Generates draft donor outreach letters with tier-based ask amounts from a donor data file the user provides. Use when fundraising staff ask to create personalized letters for a campaign and have donor data available. Output is drafts for staff review, never final sends.

The description is the routing gate. It is always in context, and the agent uses it to decide whether the skill applies to the current request, so it has to say what the skill does and precisely when it fires. The original is a keyword net that would hijack unrelated work across an organization. The rewrite states what the skill produces, what it requires as input, when it applies, and bakes the review gate into the gate itself, so any agent loading this skill knows before reading a single instruction that nothing goes out unreviewed.
