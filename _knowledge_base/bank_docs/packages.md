Below is a thorough breakdown of all the interest-rate tracks (מסלולים), their descriptions, and corresponding tooltips, as gleaned from the current Poalim web source. We’ll first list the fixed “Bank of Israel” packages exactly as shown in the HTML (called “סל אחיד” or “baskets 1–3”), then enumerate the flexible self-service options available under “סל מוצע” (the user-defined basket).

⸻

1. Bank of Israel Fixed Packages

These are the three “סלים” (baskets) predefined by the Bank of Israel. Each basket has a static allocation of interest tracks. The user can still tweak interest rates within each track, but the track composition is fixed.

1.1 סל אחיד 1
	•	Composition: 100% קבועה לא צמודה (“100% Fixed, not linked to CPI”)
	•	Tooltip (translated / summarized):
ריבית קבועה לא צמודה למדד המחירים לצרכן.
הריבית במסלול זה קבועה לאורך חיי ההלוואה ואין הצמדה, לכן ההחזר החודשי קבוע ואינו משתנה.

In practice, this means the user gets:
	•	No CPI linkage (no monthly fluctuations from inflation).
	•	A single, unchanging interest rate for the entire life of the loan.

1.2 סל אחיד 2
	•	Composition (three sub-tracks, each ~⅓):
	1.	⅓ קבועה לא צמודה (“Fixed, not linked to CPI”)
	2.	⅓ משתנה פריים (“Variable Prime-based”)
	3.	⅓ משתנה צמודה כל 5 שנים על בסיס אג”ח ממשלתי (“Variable CPI-linked every 5 years, based on government bonds”)
	•	Tooltips:
	•	⅓ קבועה לא צמודה:
הריבית במסלול זה קבועה לאורך חיי ההלוואה ואין הצמדה, לכן ההחזר החודשי קבוע.
	•	⅓ משתנה פריים:
הריבית במסלול זה מורכבת מריבית הפריים (ריבית בנק ישראל + 1.5%) בתוספת או הפחתה של מרווח. משתנה אחת לחודש.
שינוי בריבית ישפיע על גובה ההחזר החודשי.
	•	⅓ משתנה צמודה כל 5 שנים:
הריבית מתעדכנת כל 60 חודשים על פי תשואות אג”ח ממשלת ישראל צמוד למדד המחירים לצרכן.
ההחזר החודשי מתעדכן גם בעקבות שינויי המדד עצמו (אינפלציה / דפלציה).

1.3 סל אחיד 3
	•	Composition (two sub-tracks, each ~½):
	1.	½ קבועה לא צמודה (“Fixed, not linked to CPI”)
	2.	½ משתנה פריים (“Variable Prime-based”)
	•	Tooltips:
	•	½ קבועה לא צמודה: Same as above (“rival” to inflation, stable monthly payment).
	•	½ משתנה פריים: Tied to prime (Bank of Israel interest rate + 1.5%), can change monthly.

⸻

2. Flexible (Self-Service) Packages

Under the section labeled “סל מוצע” or “Add your own basket,” the user can individually choose from nine distinct tracks. Each track has a tooltip describing its interest calculation mechanism. The user can combine multiple tracks in any ratio (with the usual regulatory constraints).

Below is a list of these nine available tracks with short translations from the tooltips:
	1.	קבועה צמודה (“Fixed, CPI-linked”)
	•	Tooltip:
הריבית במסלול זה קבועה וקיימת הצמדה למדד המחירים לצרכן.
ההחזר החודשי משתנה מדי חודש בהתאם לעליית/ירידת המדד.
	2.	קבועה לא צמודה (“Fixed, not linked to CPI”)
	•	Tooltip:
הריבית קבועה לא צמודה למדד המחירים לצרכן. אין הצמדה, לכן ההחזר החודשי נותר קבוע.
	3.	משתנה פריים (“Variable Prime-based”)
	•	Tooltip:
הריבית מורכבת מריבית הפריים (ריבית בנק ישראל + 1.5%) ± מרווח. עשויה להשתנות אחת לחודש.
	4.	משתנה צמודה כל 5 שנים על בסיס אג”ח ממשלתי
	•	Tooltip:
ריבית ההלוואה תשתנה כל 60 חודשים לפי תשואות אג”ח ממשלת ישראל צמודות למדד.
ההחזר החודשי מתעדכן מדי חודש בגלל הצמדה למדד המחירים לצרכן (מדד ה-CPI).
	5.	משתנה לא צמודה כל 5 שנים על בסיס אג”ח ממשלתי
	•	Tooltip:
הריבית תשתנה כל 60 חודשים לפי תשואות אג”ח ממשלת ישראל שקלית (ללא הצמדה למדד).
הקרן אינה צמודה למדד, לכן שינויים באינפלציה לא משפיעים על היתרה, אבל הריבית עצמה עשויה לעלות/לרדת.
	6.	משתנה צמודה כל 3 שנים על בסיס אג”ח ממשלתי
	•	Tooltip:
הריבית תתעדכן כל 36 חודשים לפי תשואות אג”ח ממשלתיות צמודות מדד.
ההחזר משתנה גם עקב הצמדה למדד המחירים לצרכן.
	7.	משתנה צמודה כל 10 שנים על בסיס אג”ח ממשלתי
	•	Tooltip:
הריבית תשתנה כל 120 חודשים לפי תשואות אג”ח ממשלת ישראל צמודות למדד.
גם כאן, ההחזר מושפע מהצמדה למדד באופן חודשי.
	8.	משתנה לא צמודה כל 3 שנים על בסיס אג”ח ממשלתי
	•	Tooltip:
הריבית משתנה כל 36 חודשים לפי אג”ח ממשלת ישראל שקלית (ללא הצמדה).
העלייה או הירידה היא בהתאם לשינוי בתשואות האג”ח, אך אין השפעה מצד מדד המחירים לצרכן.
	9.	משתנה לא צמודה כל 10 שנים על בסיס אג”ח ממשלתי
	•	Tooltip:
הריבית משתנה כל 120 חודשים לפי אג”ח ממשלת ישראל שקלית (ללא הצמדה).
אין הצמדה למדד, אך כל 10 שנים הריבית עלולה לעלות או לרדת בהתאם לתשואות.

⸻

3. Key Observations & Distinctions
	1.	Bank of Israel Packages (סל אחיד 1, 2, 3)
	•	Predefined mixes that reflect certain regulation or typical distributions.
	•	The user can’t change the ratio of tracks (e.g., 1/3 each in סל אחיד 2 remains fixed).
	2.	Flexible / Self-Service Basket
	•	User chooses each track independently.
	•	They can add multiple lines in the “סל מוצע” table, each line being a different track.
	•	Ratios must sum up to 100% of the loan (in practice).
	•	Subject to regulatory constraints (e.g., maximum prime portion).
	3.	Indexation (צמודה) vs. Non-Indexation (לא צמודה)
	•	“צמודה” indicates the principal is linked to the CPI, so monthly payments can change based on inflation/deflation.
	•	“לא צמודה” means no monthly changes due to CPI, but the base interest rate itself might still be variable if it’s prime-based or re-pegged to government bond yields.
	4.	Update Frequency
	•	“משתנה פריים” → Potential monthly changes.
	•	“משתנה צמודה כל 5 שנים” → Rate is recalculated every 60 months (plus monthly inflation adjustments if “צמודה”).
	•	“משתנה לא צמודה כל X שנים” → Rate changes every X years, but no inflation indexing.
	5.	Tooltip Summaries
	•	Each track’s tooltip clarifies two main things:
	1.	Whether it’s fixed or variable, and how often it changes.
	2.	Whether the principal is CPI-linked (צמודה) or not.

⸻

4. Practical Usage in a Simulator
	•	Bank of Israel Baskets:
	1.	Basket 1: (100% fixed-no-CPI) – simplest scenario, stable.
	2.	Basket 2: A “thirds” approach (1/3 fixed, 1/3 prime, 1/3 variable linked).
	3.	Basket 3: A “halves” approach (½ fixed, ½ prime).
	•	Self-Service:
	•	Users can create a custom distribution out of the nine track options.
	•	For example: 20% fixed not linked, 40% prime, 40% variable indexed every 5 years, etc.
	•	The logic will need to handle multiple lines, sum them to 100%, and apply each track’s formula for monthly payment and total interest.

⸻

Conclusion

In the current Poalim mortgage calculator:
	1.	Fixed Packages (סל אחיד 1/2/3) are mandated by the Bank of Israel and must stay as is. They each combine a few standard tracks in predefined ratios.
	2.	Flexible Packages (“סל מוצע”) allow the user to pick any of nine distinct tracks (both CPI-linked and non-linked variations, with different re-pegging intervals).
	3.	Each track’s tooltip text clarifies how its interest rate and CPI linkage behave, giving the user insight into potential payment fluctuations.

This structure provides a clear line between the bank’s standard baskets (which remain fixed) and the flexible self-service simulator (where the user can freely experiment with any track combination).