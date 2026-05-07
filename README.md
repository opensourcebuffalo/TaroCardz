# Taro sez... swipe through City Hall
2026 Startup Wednesday Project

TAROCARDZ
Taro Sez… Swipe Through City Hall

TaroCardz is a civic participation platform that transforms Buffalo government agendas, hearings, and public meetings into interactive civic cards residents can understand, share, and act on.

The core idea is simple:

Important local government decisions are buried inside PDFs, procedural jargon, and meetings where often nobody participates because they never even know the issue exists.

We want to change that.

MVP

The MVP converts real Buffalo agenda items into swipeable “Taro Cards” containing:

AI-generated summaries
hearing dates
public comment deadlines
agency context
neighborhood relevance
share/follow/support actions

“Taro Sez” is the project’s civic media layer:

meeting summaries
weekly analysis
civic alerts
short-form public interest reporting
Civic Architecture
Major Arcana

Buffalo Charter articles:

Council
Mayor
Budget
Contracts
Planning
Elections
Assessments
Minor Arcana

Daily agenda items from:

Common Council
Planning Board
ZBA
BURA
BFSA
BMHA
Sewer Authority
Water Board
Current Goal

Build a working Buffalo-first prototype that:

ingests agenda items
summarizes them into plain English
displays them as civic cards
increases awareness and public participation
Tech Stack
Next.js / Tailwind
PHP + MySQL
Python scraping + AI summarization
Open data + public agendas
Initial Data Sources
| Agency / Source                            | URL                                                                                                            | Agenda Access | Video / Livestream | Public Comment | Data Format      | Notes / Research Questions                        |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- | ------------- | ------------------ | -------------- | ---------------- | ------------------------------------------------- |
| Buffalo Charter                            | [https://ecode360.com/11766266](https://ecode360.com/11766266)                                                 | N/A           | No                 | N/A            | HTML             | Can Charter articles become “Major Arcana”?       |
| Common Council                             | [https://buffalony.legistar.com](https://buffalony.legistar.com)                                               | Yes           | Yes                | Yes            | Legistar / PDF   | Best source for legislation, hearings, committees |
| Planning Board                             | [https://www.buffalony.gov/456/Planning-Board](https://www.buffalony.gov/456/Planning-Board)                   | Yes           | Sometimes          | Yes            | PDF              | Development, zoning, SEQR actions                 |
| Zoning Board of Appeals (ZBA)              | [https://www.buffalony.gov/463/Zoning-Board-of-Appeals](https://www.buffalony.gov/463/Zoning-Board-of-Appeals) | Yes           | Limited/Unknown    | Yes            | PDF              | Variances, appeals, neighborhood disputes         |
| Buffalo Urban Renewal Agency (BURA)        | [https://www.buffalourbanrenewal.com](https://www.buffalourbanrenewal.com)                                     | Yes           | Sometimes          | Limited        | PDF              | Economic development, land disposition            |
| Buffalo Fiscal Stability Authority (BFSA)  | [https://www.bfsa.state.ny.us](https://www.bfsa.state.ny.us)                                                   | Yes           | Yes                | Limited        | PDF              | Budget oversight, financial monitoring            |
| Buffalo Municipal Housing Authority (BMHA) | [https://www.bmhahousing.com](https://www.bmhahousing.com)                                                     | Yes           | Unknown            | Limited        | PDF              | Housing policy, redevelopment                     |
| Buffalo Sewer Authority                    | [https://www.buffalosewer.org](https://www.buffalosewer.org)                                                   | Unknown       | Unknown            | Limited        | PDF/HTML         | Infrastructure, environmental projects            |
| Buffalo Water Board                        | [https://www.buffalowaterboard.com](https://www.buffalowaterboard.com)                                         | Unknown       | Unknown            | Limited        | PDF/HTML         | Water infrastructure, rates                       |
| Open Data Portal                           | [https://data.buffalony.gov](https://data.buffalony.gov)                                                       | N/A           | No                 | N/A            | API / CSV / JSON | Potential source for maps, parcels, 311, budget   |
| City Clerk / Public Meetings               | [https://www.buffalony.gov](https://www.buffalony.gov)                                                         | Partial       | Partial            | Partial        | Mixed            | Need mapping of all boards/commissions            |
| YouTube / Public Access Archives           | TBD                                                                                                            | N/A           | Yes                | N/A            | Video            | Research clipping/transcription pipeline          |


Current Questions
How do we reduce friction between citizens and city hall?
How do we increase meaningful public comment?
How should civic information be visualized?
What does “TikTok/Tinder for local government” actually look like?
Looking For
frontend developers
AI engineers
civic hackers
GIS/open data people
designers
storytellers
Buffalo policy nerds
people who believe local government should be understandable

🃏 Draw Your City.
