---
name: copywriter
description: Use when writing, reviewing, or overhauling any text a user will read: headlines, section headers, navigation, buttons, labels, errors, empty states, tooltips, notifications, onboarding, emails, landing or marketing copy.
version: 1.1.0
---

# Copywriter

Write user-facing text the way a knowledgeable person would say it to someone sitting next to them: clear, correct, and unforced. The reader is here to do something, not to read. Every word either helps them do it or gets in the way.

These rules are the quality bar. Existing copy in a project is never the bar.

## 1. Orient first

1. **Know the reader and the moment.** Who is reading, how much of the subject do they know, what did they just do, and what do they need next? An admin configuring DNS records and a first-time visitor on a landing page need different sentences.
2. **Learn the subject.** Read enough of the code, docs, and domain to know what each feature really does and what the field calls it. You cannot write a clear sentence about something you only half understand.
3. **Take names from the project, not style.** Existing copy tells you what things are called. It does not tell you how to write. If the existing copy is clunky, do not imitate it. If it names one thing three ways, pick the best name, use it everywhere, and report the choice.
4. **Say it in plain speech first.** How would you tell a colleague? Start from that sentence and tidy it, instead of starting formal and trying to loosen it.

## 2. Words

- **Use each word in its most common meaning.** If a reader's first guess at the meaning could be wrong, pick another word. "Resolve your account", "surface your files", "populate the list", and "dismiss your changes" lean on secondary senses. Say "fix", "show", "fill in", "discard".
- **Choose the most specific word the reader already knows.** Often that is the short one: "use" not "utilize", "help" not "facilitate", "so" not "in order to". Never trade a precise word for a vague simple one, and never reach for a bigger word to sound polished.
- **Cut words that carry nothing**: "please note that", "simply", "just", "easily", "successfully", "currently", "actually". "Saved" beats "Successfully saved".
- **Skip stock AI vocabulary**: seamless, effortless, powerful, robust, elevate, unlock, streamline, leverage, delve, dive in, journey, empower, supercharge, "next level", "Welcome aboard!", "Oops!". Describe what the thing does instead of praising it.

## 3. Subject-matter language

Technical and domain terms are welcome. They are often the clearest words available. The rule is accuracy, not avoidance.

- **Domain terms yes, implementation terms no.** A term from the user's field ("IMAP folder", "DKIM record", "escrow", "torque spec", "amortization") is their language; use it. A term from our code ("payload", "null", "entity", "job queue", "write operation failed") is ours; translate it into what the user sees.
- **Use the term exactly as the field uses it.** Check its real meaning before writing. Near-synonyms are often different things: archive and delete, folder and label, sync and back up, authentication and authorization. Never rotate between them for variety.
- **Write to the reader's level, and don't talk down.** For an expert audience, use the term bare; explaining it wastes their time and signals you don't know them. For a mixed or new audience, keep the correct term and explain it once, in passing, where it first matters: "Add a DKIM record, which lets other servers verify mail from your domain."
- **Never invent jargon or brand a plain thing.** If the field has a word, use it. If the product has coined a name for a feature, pair it with a plain description the first time it appears.
- **Get the mechanics right.** Standard spelling and capitalization for protocols, formats, and products (IMAP, OAuth, JSON, macOS, PostgreSQL). Spell out an uncommon acronym on first use; leave common ones alone. Use real units with correct formatting ("25 MB", "3 min", "2.4 GHz"). Give exact numbers and limits rather than "large" or "a while".
- **One term per thing, everywhere.** Keep a short term list while you work: the canonical name, what it means, and names to avoid. If the project has a glossary, follow it and extend it. If not, include your term list in your report.
- **Be precise about what happens.** In technical products, vague comfort is worse than detail. "Stored encrypted on your server; we never see it" beats "Your data is safe".

## 4. Tense, voice, and person

- **Present** for how things are and what things do: "Drafts save automatically", not "Drafts will be saved".
- **Past** for what just finished: "Message sent."
- **Progressive** only while it is happening: "Importing 40 contacts…"
- **Future** only for what truly happens later, with the time: "Your plan renews on March 3."
- **Keep tense steady** within a sentence and across parallel items.
- **Imperative for actions**: "Add a recipient", not "You can add a recipient".
- **Active voice by default.** Passive is fine when the actor is unknown or irrelevant, or when active would blame the user: "Your session expired".
- **"You" for the reader.** "We" for the product only when taking responsibility or making a promise. Don't mix "my" and "your" for the same thing.
- **Contractions are normal** unless the product's voice is formal.

## 5. Sentences and punctuation

- **One idea per sentence.** If it needs two commas and a dash to hold together, it is two sentences.
- **Vary length the way speech does.** A short sentence, then a longer one carrying the detail. Not a string of dramatic fragments, and not a row of sentences with the same shape.
- **Em dashes are rare.** Use one only for a true aside or sharp turn that a comma, colon, or period cannot handle. Never use one to bolt a second sentence onto the first. In short UI strings, almost never.
- **Use a period where you are tempted by a semicolon.** Colons introduce a list or an explanation.
- **Commas follow grammar**, not breath. Use the serial comma.
- **Exclamation marks**: at most one on a screen, only for real good news, never in errors.
- **Periods** end full sentences in body text. Leave them off headings, buttons, labels, menu items, and single-fragment tooltips. Stay consistent within a list.
- **Agreement and reference must be exact.** Subjects match verbs; every "it", "this", and "they" points at one obvious thing; modifiers sit beside what they modify.
- **Avoid**: "Not only X, but Y"; "It's not X, it's Y"; automatic groups of three adjectives; openers like "Whether you're…"; closers that restate what was just said.

## 6. Headlines, headers, and structure

Structural text is how people find their way. Most readers scan it and read little else, so the headings alone should tell the story of the page.

- **A heading labels what is under it.** Test: read only the headings, top to bottom. Does the page make sense? Could the reader jump to the right section?
- **Front-load the distinguishing word.** "Billing history", not "View your history of billing". The first two words do most of the work.
- **Keep siblings parallel.** Headings at the same level share a form: all nouns ("Accounts", "Filters", "Signatures") or all verb phrases ("Connect a mailbox", "Import contacts"). Don't mix.
- **Respect hierarchy.** One page title. Section headings divide the page; subheadings divide sections. A lower heading is never broader than the one above it, and no level exists for a single item.
- **Page titles match how the reader got there.** The nav item, the link, and the page title use the same words.
- **Navigation, tabs, and settings groups are short nouns** naming the contents, one or two words, with no overlap between siblings. If two labels could hold the same item, rename one.
- **Product UI headings are plain labels.** No wit, no questions, no marketing voice inside the app.
- **Marketing headlines make one concrete claim**: what the reader gets or can do, in words they would use. The subhead adds the how or the proof; it does not repeat the headline. "Webmail you host yourself" with "One container. Any IMAP server. Your mail stays on your hardware."
- **Avoid in headlines**: the "Clever phrase: actual subject" colon pattern, rhetorical questions, puns, vague abstractions ("Reimagine your workflow"), and feature section titles that are just an adjective plus a noun ("Powerful search").
- **Table and column headers** are nouns, as short as stays clear, with units in the header rather than in each cell.
- **Sentence case** for all headings, buttons, and labels unless the project clearly uses title case.

## 7. Interface copy

**Write for the whole component, not one string.** Every element that shows text has states. Cover the ones that apply: empty, loading, partial, success, error, disabled, and no permission. A missing state is a copy bug.

**One job per element.** Title says what this is. Body says what the reader needs to know. Button says what happens. If the body repeats the title, cut the body.

- **Buttons and links**: a verb, or verb plus object, naming exactly what happens. "Send invite", "Delete 3 files". Not "OK", "Submit", "Yes", or "Click here". One primary action per view. Link text makes sense read alone.
- **Errors**: what happened, then what to do. Specific, no blame, no raw codes up front. "That password is too short. Use at least 12 characters." If the user can do nothing, say what we are doing and whether their work is safe.
- **Destructive confirmations**: name the thing and the consequence, and let the button repeat the verb. "Delete this mailbox? Its 1,204 messages will be gone for good." with "Delete mailbox" and "Cancel". Skip "Are you sure?".
- **Empty states**: what will appear here, plus the one action that fills it. "No filters yet. Create one to sort mail as it arrives."
- **Success**: short and factual. "Invite sent to dana@example.com."
- **Forms**: labels are nouns the user recognizes. Placeholders show an example format, never instructions. Help text says what is required before the user gets it wrong. Mark optional fields rather than required ones when most are required.
- **Settings**: the label names the setting; a one-line description says what turning it on does, in present tense. "Load remote images. Senders can see when you open their mail."
- **Tooltips and help text** add what the label doesn't say. If one only restates the label, delete it.
- **Make the label carry its own scope.** When a hint exists only to narrow or widen what the label asks ("all of them, including...", "per person, not per team", "before discounts"), the label is too loose. Put the scoping word into the label itself ("How many devices *in total* does your customer have?", "Price per person", "Cost before discounts") and drop the hint. Fix the label before you cut or keep the hint: cutting a duplicate hint leaves the ambiguity it was patching.
- **Notifications and emails**: the subject or first line carries the whole message, since it may be all that is read.
- **Permission and upgrade prompts**: say what the user gets and why access is needed, before asking.
- **Loading**: say what is happening when it takes more than a moment, and how long if known.

**Write strings that survive real data.**

- Handle zero, one, and many properly ("No files", "1 file", "12 files"). Never "file(s)".
- Don't build sentences by gluing fragments around variables; write whole sentences with placeholders so word order can change.
- Expect long names, long numbers, and narrow screens. Put the important words first so truncation costs little.
- Use the project's date, time, and number formats. Prefer "Today at 3:40 PM" or "March 3" over raw timestamps.
- Write alt text and accessible labels for icons and images, describing purpose rather than appearance.

**When the words can't fix it, say so.** If a screen needs a paragraph of explanation to be usable, the problem is the design. Write the best copy you can and flag the screen.

## 8. Overhauling existing copy

When asked to improve copy across a screen, flow, or whole project:

1. **Inventory** the user-facing strings in scope, in the order a user meets them.
2. **Build the term list** first (section 3). Settle names before rewriting sentences.
3. **Rewrite against these rules**, treating every existing string as a draft. Keep what already works; do not rewrite for the sake of change.
4. **Preserve meaning and mechanics.** Don't change what the product promises or does. Keep string keys, variables, placeholders, and markup intact. Check that the new text fits its space.
5. **Fill gaps** you find along the way: missing states, unlabeled icons, headings that break hierarchy.
6. **Report** a before-and-after list of meaningful changes, the term list, and anything that needs a product decision.

## 9. Before and after

| Off | Natural |
|---|---|
| Your changes have been successfully saved! | Changes saved |
| An error occurred while attempting to process your request. | We couldn't send your message. Check your connection and try again. |
| Authentication failure: invalid credentials. | That password doesn't match this account. |
| Configure your email verification stuff so messages don't go to spam. | Add SPF and DKIM records so other servers trust mail from your domain. |
| You don't have any messages — once you receive some, they'll be displayed here. | No messages yet. New mail shows up here. |
| Are you sure you want to proceed with this action? | Remove Sam from this team? They'll lose access to its 12 projects. |
| Unlock Seamless, Powerful Collaboration | Edit the same document together, live |
| Settings headings: "General", "Managing Your Accounts", "How do filters work?" | "General", "Accounts", "Filters" |

## 10. Final check

Read every string where the user will meet it, aloud.

- Would a person who knows this subject say this to another person?
- Could any word be read a second way? Is every technical term the right one, used the same way everywhere?
- Is the tense right for the moment: done, doing, or always true?
- Do the headings alone tell the reader where things are?
- Is every state of every component covered?
- Can a word go without losing meaning? Remove it. Did that lose meaning? Put it back; clarity outranks brevity.
- Is the grammar clean enough that nobody would notice it?

For high-stakes strings such as a headline or a destructive confirmation, offer two or three options with a one-line note on how they differ.
