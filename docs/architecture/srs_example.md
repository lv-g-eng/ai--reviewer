Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 1
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
BridgeU
Software Requirement Specification
Zhiyi Pan 652115558
Bachelor of Science
Software Engineering Program
Department College of Arts, Media, and
Technology
Chiang Mai University
December 2025
Project Advisor
Asst. Prof. Pattama Longani, Ph.D.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 2
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Document History
Document
Name
Version History Statu
s
Date Editabl
e
Reviewe
r
BridgeUSR
S
BridgeUSR
S V.0.1
AddChapter1 
•1.1Purposea
nd Scope 
•1.2User 
Character is 
•1.3Acronym
s and
Definitions 
AddChapter2 
Progress1 
•UseCase 
Diagram 
•UseCase 
Description
Draft 12/12/202
5
ZHIYI 
PAN 
Asst.Pro
f. 
Pattama 
Longani, 
Ph.D.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 3
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Chapter 1 Introduction
1.1 Purpose and Scope
The purpose of the software design development is to present a complete 
software design of the BridgeU project. This document contains the outline of the 
software architecture, functions used, and activity diagrams with the user interface for 
this project. BridgeU aims to eliminate language barriers through AI technology and 
establish a bilingual mutual assistance ecosystem connecting Chinese students, global 
students, and local Thai merchants.
1.2 User Characteristics
Users:
 All people who can log in.
Description:
The target users of our software are international students studying in Thailand, 
merchants providing services to the international student community， they share the 
common goal of creating a supportive bilingual community that facilitates adaptation 
to life in Thailand and enables seamless information sharing and communication.
1.3 Acronyms and Definitions
SRS Software Requirement Specification
URS User Requirement Specification
UTC Unit Test Case
STC System Test Case
UC Use Case
SRC Software Requirements Specification
RSS Really Simple Syndication 
JWT JSON Web Token 
AI Artificial Intelligence 
LLM Large Language Model 
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 4
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Definition
Name Definition
IEEE Institute for Electrical and Electronics 
Engineers. Biggest global interest
group for engineers of different 
branches and computer scientists. 
Plan A document series of tasks requires 
meeting an objective, typically
including the associated schedule, 
budget, resources, organizational
description and work breakdown 
structure. 
Feature Feature Transformation of input 
parameters to output parameters based
on a specified algorithm. It describes 
the functionality of the product in
the language of the product. Used for 
requirements analysis, design,
coding, testing or maintenance. 
Project
Management
The application of knowledge, skills, 
tools, and techniques to project
activities in order to meet or exceed 
stakeholder needs and expectations
from a project. 
Project Plan A formal, approved document used to 
guide both project execution and
project control. The primary uses of 
the project plan are to document
planning assumptions and the 
decision, to facilitate communication
among stakeholders, and to document 
approved scope, cost, and
schedule baseline. 
Risk An uncertain event or condition that, if 
it occurs, has a positive or
negative effect on a project’s 
objectives. It is a function of the
probability of occurrence of a given 
threat’s occurrence. 
Risk
Management
The systematic application of 
management policies, procedures and
practices to the tasks of identifying, 
analyzing, evaluating, treating and
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 5
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
monitoring risk. 
System Testing Testing conducted on a complete and 
integrated system for evaluate the
system’s compliance with its specified 
requirements. 
Unit Test A test of individual programs or 
modules in order to remove a design or
programming errors. 
Traceability The ability to trace the history, 
application or location of an item or
activity, or work products or activities, 
by means of recorded
identification. The establishment and 
maintenance of relationships
between such items. Horizontal 
traceability describes the relationship
between work products of the same 
type (e.g. Customer requirements).
Vertical traceability describes the 
relationship between work products,
which build or derived from each other 
(e.g., from customer
requirements to qualification test 
cases). Bidirectional traceability
allows to directly following 
relationships in both directions. 
Use Case A use case is a description of a 
specific interaction between a system
and its users to accomplish a particular 
goal or task. It outlines the
sequence of steps or actions that a user 
performs in the system and
describes the system's responses to 
those actions. Use cases help to
identify and define the functional 
requirements of a system from the
perspective of its users.
Activity Diagram Activity diagram is another important 
behavioral diagram in UML
diagram to describe dynamic aspects 
of the system. Activity diagram is
essentially an advanced version of 
flow chart that modeling the flow
from one activity to another activity.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 6
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Chapter 2 Specification Requirement
2.1 Feature 1
Feature 1: Daily Briefing System
The Daily Briefing System automatically captures and summarizes Thai news 
from Google News, providing bilingual (Chinese/English) access to daily news 
briefings for User. At 8 a.m. every day, the system captures news from the Google 
News, and saves each article as a Daily Briefing record, including original title, 
summary generated by the system call Qwen AI to summarize, source website name, 
original URL, publication time provided by the source. The system generates both 
Chinese and English versions for the title and abstract, and the interface only displays 
one of them in the current language. When the User opens the Daily Briefing page, 
the system returns a paginated list of Daily Briefing record from new to old according 
to the release time. The list card displays: title, summary, source, publication time 
(using only the current interface language), and provides a button to enter the detail 
page. User can also click original button to opens the original URL of the news. Users 
can enter any keywords in the search box on the page. System searches by keyword 
among Daily Briefing titles and abstracts (both Chinese and English versions) in the 
database,then System returns Daily Briefing items related to that word in the current 
language
User can set filtering conditions: start date(daymonthyear), end 
date(daymonthyear). The system applies all filtering conditions, only returns the Daily 
Briefing news that meets the conditions, and displays them in chronological 
order(new to old).
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 7
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
2.1.1 Use Case Diagram
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 8
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
2.1.2 User Requirement Specification
URS01 – View Daily Briefings 
User can open the Daily Briefing page and browse a paginated list of recent Daily 
Briefing items ordered from newest to oldest by publication time in their current 
interface language.
URS02 – View Daily Briefing news details 
User can select a Daily Briefing item from the list and view a news detail page that 
shows the complete information (title, AI generated summary of News, publication 
time,View Original button, "Back" button) for that item in their current interface 
language (English/Chinese).
URS‑03 – Switch Interface Language
User can click a language switch button at any time to change the interface language 
between Chinese and English and continue browsing Daily Briefing items in the 
newly selected language.
URS‑04 – Jump to the original link
User can click an “Open original article” button on a Daily Briefing item and read 
the full original news article on the external official website in a new browser tab.
URS‑05 – Filter Daily Briefings News by Date
The User can filter news based on specific criteria (start date and end date) while 
browsing.
URS06 – Search for Daily Briefing News 
User can type Chinese or English keywords into a search box on the Daily Briefing 
page and view only Daily Briefing items that match the entered keywords.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 9
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
2.1.3 Use Case Description and Activity Diagram
2.1.3.1 UCD01 View Daily Briefings
URS01: User can open the Daily Briefing page and browse a paginated list of recent 
Daily Briefing items ordered from newest to oldest by publication time in their 
current interface language.
 SRS01: The system shall display the "Briefing" navigation item in the sidebar 
navigation menu on every page.
 SRS02: The system shall display the Daily Briefing page [UI01] when the 
"Briefing" navigation item is clicked, showing a paginated list of Daily Briefing 
items.
 SRS03: The system shall order Daily Briefing items from newest to oldest based 
on publication time from the source website.
 SRS04: The system shall display Daily Briefing items in the user's current 
interface language (Chinese or English), showing only the title and summary in 
the selected language.
 SRS05: Each Daily Briefing card on the list shall display: title, AIgenerated 
summary, source website name (original or localized name), and publication time 
(formatted according to the current interface language).
 SRS06: The system shall implement pagination to display Daily Briefing items, 
providing pagination controls (page number, previous/next buttons) for users to 
navigate through pages.
 SRS07: The system shall provide a "View Detail" button on each Daily Briefing 
card to navigate to the news detail page.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 10
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Use Case ID UC01
Use Case 
Name
View Daily Briefings
Created By ZhiYi Pan Last Update By ZhiYi Pan
Date Created 04/01/2026 Last Revision 
Date
Actors User
Description This use case describes the process by which a user navigates to the Daily 
Briefing page and browses a paginated list of recent news items from Google 
News. The list displays news items ordered from Google News new to old by 
publication time, with all content displayed in the user's current interface 
language (Chinese or English).
Trigger User clicks on the "Briefing" navigation item in the sidebar menu.
Preconditions 1. User is logged into the BridgeU platform.
2. User has an active internet connection.
3. The Daily Briefing system has successfully crawled news from approved 
sources (Google News).
Use Case Input Specification
Input type Constraint Example
Current 
Interface 
Language
String Must be "zh" (Chinese) or "en" (English) "en" 
Post conditions User are in "Daily Briefing page" (UI01: Daily Briefing page)
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 11
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Normal Flows User System
1.User clicks on the "Briefing" 
navigation item in the sidebar 
7. User clicks pagination controls 
(e.g., "Next" button).
2. System checks if the user is logged 
in and the login session is valid 
(verifies authentication token)
[E2: User session expired] 
3. System retrieves the user's current 
interface language preference 
(Chinese or English)
4. System queries the database for 
the first page of Daily Briefing items, 
ordered by publication time (newest 
first)
[E1: Cannot connect to database]
[E3: Network timeout]
5. System retrieves the corresponding 
language version (Chinese or 
English) for each Daily Briefing 
item's title and summary
6. System displays the Daily Briefing 
page (UI01) with paginated list of 
news items(Each card includes title, 
summary, source, time, and "View 
Detail" button)
[A1: No news items available]
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 12
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
9. User clicks "View Detail" on a 
specific card.
8. System loads and displays the next 
set of news items.
10. System navigates to the News 
Detail Page.
Alternative 
Flow
A1: No News Items Available
A1.1 System show "No news available at this time" message
A1.2 Use case end.
Exception 
Flow
E1: Cannot connect to database
E1.1 System show "Unable to load news. Please try again later." message
E1.2 System logs the error for administrator review
E1.3 Use case end.
E2: User Session Expired
E2.1 System redirect the user to the login page
E2.2 System show "Your session has expired. Please log in again." message
E2.3 Use case end.
E3: Network Timeout
E3.1 System show "Request timeout. Please check your internet connection 
and try again." message
E3.2 User can retry the operation
E3.3 Go to Step 4
Note 1. The user has a stable internet connection.
2. The Daily Briefing crawling system runs successfully at 8:00 AM daily.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 13
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
AD01: View Daily Briefings 
Activity Diagram for View Daily Briefings, which explains the steps between a User 
and the System for browsing aggregated news.
3. News items have been successfully translated into both Chinese and English 
versions.
4. The user's browser supports modern web technologies (JavaScript, CSS, 
HTML5).
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 14
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 15
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
2.1.3.2 UCD02 View Daily Briefing news details
URS02: User can select a Daily Briefing item from the list and view a news detail 
page that shows the complete information (title, summary, publication time, View 
Original button) for that item in their current interface language (English/Chinese).
 SRS08: The system shall provide a "View Detail" button on each Daily Briefing 
card in the list page (UI01) to navigate to the news detail page (UI02).
 SRS09: The system shall display the News Detail page (UI02) when a user clicks 
the "View Detail" button on a Daily Briefing card.
 SRS10: The system shall retrieve the selected Daily Briefing item from the 
database using the news item ID passed from the list page.
 SRS11: The system shall display the news detail page content in the user's 
current interface language (Chinese or English), showing the title and summary 
in the selected language.
 SRS12: The News Detail page (UI02) shall display the following information in 
the user's current interface language:
- News title
- AI generated summary
- Source website name
- Publication time 
 SRS13: The system shall provide a "Back" button on the News Detail page to 
return to the Daily Briefing list page.
 SRS14: The system shall provide a "View Original" button that triggers the 
browser to open the original news article URL in a new tab when clicked.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 16
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Use Case ID UC02
Use Case 
Name
View Daily Briefing news details
Created By ZhiYi Pan Last Update By
Date Created 04/01/2026 Last Revision 
Date
Actors User
Description User can select a Daily Briefing item from the list and view a news detail page 
that shows the complete information (title, AI generated summary of News, 
publication time,View Original button, "Back" button) for that item in their 
current interface language (English/Chinese).
Trigger User clicks the "View Detail" button on a Daily Briefing card in the Daily 
Briefing list page (UI01)
Precondition
s
1. User has an active internet connection.
2. User is viewing the Daily Briefing list page (UI-01).
3. At least one Daily Briefing item exists in the list.
Use Case Input Specification
Input type Constraint Example
News Item 
ID 
Integer Must be a valid news item ID that exists in the 
database
123
Current 
Interface 
Language
String Must be "zh" (Chinese) or "en" (English) “en”
Post 
conditions
User is viewing the News Detail page (UI02) displaying the complete 
information for the selected Daily Briefing item
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 17
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Normal 
Flows
User System
1. User clicks the "View Detail" button 
on a Daily Briefing card in the list page
2. System retrieves the news item ID 
from the clicked card
3. System retrieves the user's current 
interface language preference 
(Chinese or English)
4. Frontend sends HTTP request to 
backend API with news item ID and 
language parameter
5. Backend receives request 
(authentication not required for this 
endpoint)
6. Backend queries the database for 
the Daily Briefing item using the 
news item ID
[E1: Database error or server error]
[E4: News item not found]
7. Backend retrieves the 
corresponding language version 
(Chinese or English) for the news 
item's title and summary
8. Backend returns response with 
success status and news detail data 
9. Frontend receives HTTP response 
from backend
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 18
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
12. User views the news details
13. User switches the interface 
language (Chinese/English) using the 
language switcher (optional)
[E2: Authentication token invalid or 
expired]
[E3: Network timeout or connection 
error]`
10. Frontend checks if response.status 
is 200 and response.data.success is 
true
11. System displays the News Detail 
page (UI-02) with the complete 
information:
- News title (in current interface 
language)
- AI-generated summary (in current 
interface language)
- Source website name 
- Publication time (formatted 
according to current interface 
language)
- "View Original" button (disabled if 
originalUrl is invalid or missing)
- "Back" button
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 19
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
18. User clicks the "View Original" 
button (optional)
20. User clicks the "Back" button 
(optional) 
14. Frontend triggers a language 
change event and updates the current 
language preference
15. System re-fetches the news detail 
data from the API with the new 
language parameter
16. System updates the News Detail 
page display with content in the new 
language (title, summary, formatted 
dates)
17. Use case continues from Step 12
19. System triggers the browser to 
open the original URL in a new tab
[E5: Original URL invalid or missing]
21. System navigates the user back to 
the Daily Briefing list page (UI-01)
Alternative 
Flow
Exception 
Flow
E1: Database error or server error
E1.1 Backend catches an exception while processing the request
E1.2 Backend returns a 500 Internal Server Error response with message "Failed 
to fetch news detail: [error details]"
E1.3 Backend logs the error with full details for administrator review
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 20
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
E1.4 Frontend receives the 500 error response in catch block
E1.5 Frontend checks if error.response.status === 500
E1.6 Frontend displays the error message from error.response.data.message or 
default localized message 'dailyBriefingDetail.networkError'
E1.7 Use case end.
E2: Authentication token invalid or expired
E2.1 Backend returns a 401 Unauthorized response (if authentication is required 
for this operation)
E2.2 Frontend detects the 401 error and clears the invalid token from 
localStorage
E2.3 Frontend triggers an authentication error event and displays "Login 
expired, please log in again" message
E2.4 System redirects the user to the login page
E2.5 Use case ends.E3: News item not found
E3: Network timeout or connection error
E3.1 Request exceeds the configured timeout or network connection fails
E3.2 Frontend catches the network error or timeout in catch block
E3.3 Frontend checks if error.response exists (defensive check per code 
implementation)
E3.4 If error.response exists and error.response.data.message exists, frontend 
displays that message
E3.5 Otherwise, frontend displays localized error message using i18n key 
'dailyBriefingDetail.networkError' or error.message
E3.6 Use case end.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 21
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
E4: News item not found
E4.1 System queries the database but cannot find a news item with the provided 
ID
E4.2 System returns a 404 Not Found response with message "News not found 
with id: [id]"
E4.3 Frontend receives the 404 error response in catch block
E4.4 Frontend checks if error.response.status === 404
E4.5 Frontend displays the localized error message using i18n key 
'dailyBriefingDetail.notFound'
E4.6 System provides a "Back" button to return to the Daily Briefing list page 
(always displayed at top)
E4.7 Use case end.
E5: Original URL invalid or missing
E5.1 System disables the "View Original" button (rendered with 
`:disabled="!news.originalUrl"`). The button is visually distinct (grayed out) 
and non-clickable.
E5.2 Use case continues (user can still view other details)
Note The news detail page displays information in the user's current interface 
language preference.
If the user switches language while viewing details, the page content should 
update accordingly.
The "View Original" button triggers the browser to open the original article in a 
new tab to preserve the user's current browsing context.
The frontend implements defensive programming checks in the error handling 
catch block, including handling of edge cases such as 200 status codes in catch 
blocks (which should not normally occur but are handled for safety).
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 22
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Error handling follows the activity diagram specification, with detailed checks 
for HTTP response status codes and error message availability.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 23
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
AD02 View Daily Briefing news details
The Activity Diagram for View Daily Briefings shows how the User and 
the System interact when view the daily briefing list（UI01）
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 24
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
2.1.3.3 UCD03
URS‑03 – Switch Interface Language
User can click a language switch button at any time to change the interface language 
between Chinese and English and continue browsing Daily Briefing items in the 
newly selected language.
 SRS15: The system shall provide a language switch button (or language selector) 
on every page of the application, accessible from the sidebar (for loggedin users) 
or login page (for nonloggedin users). The sidebar displays two separate buttons: 
"中文" (Chinese) and "EN" (English), while the login page displays a single 
toggle button showing "EN/中文".
 SRS16: The system shall display the current interface language (Chinese or 
English) in the language switch control, allowing users to toggle between "中文" 
(Chinese) and "English" (English).
 SRS17: When the user clicks the language switch button, the system shall 
immediately update the user's interface language preference and persist it in local 
Storage with the key 'user Language'. Note: The user profile's preferred Language
field is only updated when the user explicitly saves their profile in the My Profile 
page. Language switching via the sidebar buttons only updates local Storage for 
the current session.
 SRS18: The system shall refresh the current page content immediately after the 
language switch, displaying all interface text, labels, buttons, and content in the 
newly selected language.
 SRS19: The system shall refetch any displayed content (e.g., Daily Briefing 
items, news details) from the backend API with the new language parameter 
(lang="zh" or lang="en") to ensure content is displayed in the selected language. 
The system triggers a 'language Changed' custom event with detail { lang: new 
Lang } to notify all components to refresh their content.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 25
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
 SRS20: The system shall maintain the user's current page context (e.g., current 
page number, selected news item ID, filter parameters) when switching 
languages, so the user can continue browsing without losing their place. For 
example, if the user is on page 3 of the Daily Briefing list, switching language 
will reload page 3 in the new language.
 SRS21: The system shall format dates and times in the format "DD-MM-YYYY 
HH:mm" (daymonthyear hour:minute) for both Chinese and English interfaces. 
The date format remains consistent across languages, but all interface labels and 
content text are translated according to the selected language.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 26
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Use Case ID UC03
Use Case 
Name
Switch Interface Language
Created By ZhiYi Pan Last Update By
Date Created 05/01/2026 Last Revision 
Date
Actors User
Description User can click a language switch button at any time to change the interface 
language between Chinese and English and continue browsing Daily Briefing 
items in the newly selected language.
Trigger User clicks the language switch button on any page of the application
Preconditions 1. User may or may not be logged into the BridgeU platform (language 
switching is available on both login page and authenticated pages).
2. User is viewing any page of the application (Login page, Daily Briefing list 
page, News Detail page, Community page, etc.).
3. The system has bilingual content available (Chinese and English versions) 
for the current page.
4. The browser supports local Storage (for storing language preference). 
Use Case Input Specification
Input type Constraint Example
Selected 
Language
String Must be "zh" (Chinese) or "en" (English) "en"
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 27
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Current Page 
Context
Object Contains current page state (page number, 
selected item ID, etc.) 
{ page: 1, 
itemId: 12345 }
Post 
conditions
1.User's interface language preference is updated to the newly selected language
2.Current page content is refreshed and displayed in the newly selected 
language
3.User can continue browsing in the newly selected language without losing 
their current context
Normal 
Flows
User System
1. User clicks the language switch 
button (e.g., "🇨🇳 中文" or "🇺🇸 EN" in 
sidebar, or "EN/中文" toggle on login 
page) on the current page
2. System calls setLanguage
(newLang) function, which validates 
the language code ("zh" or "en")
[E1: Language change event fails]
3. System updates the current 
language state and attempts to store 
the preference in localStorage with 
key 'userLanguage'
• Note: The user profile's 
preferredLanguage field is NOT 
automatically updated here. It is only 
updated when the user explicitly 
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 28
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
saves their profile in the My Profile 
page. 
• System triggers a 
'languageChanged' custom event 
with detail { lang: newLang } to 
notify all listening components (the 
event is triggered as part of the 
localStorage write attempt, so it fires 
even if localStorage write fails) 
[E2: Storage update fails]
4. All components listening to 
'languageChanged' event receive the 
notification
• Each component uses its current 
state (page number, selected item ID, 
filter parameters, etc.) to maintain 
context
• Components refetch their content 
from the backend API with the new 
language parameter (lang="zh" or 
lang="en")
• For Daily Briefing list: calls 
fetchDailyBriefing() with 
params.lang = newLang, maintaining 
current page and filters
• For News Detail: calls 
fetchNewsDetail(newsId) with 
params.lang = newLang, maintaining 
the same newsId<br> 
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 29
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
7. User continues browsing in the 
newly selected language
[E3: API request fails]
[E4: Network timeout]
5. Components receive the content in 
the newly selected language from 
API responses
6. System refreshes the current page 
display with:
 All interface text, labels, and 
buttons in the new language (via 
i18n translation system, 
automatically updated when 
language changes)
 All content (titles, summaries, 
etc.) in the new language (from 
API response)<br> 
 Dates and times formatted as 
"DD-MM-YYYY HH:mm" 
(consistent format for both 
languages)<br> 
 Current page context maintained 
(same page number, same 
selected item ID, same filter 
parameters if applicable)<br> 
 Element Plus UI components 
locale updated (zhcn or en)
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 30
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Alternative 
Flow
A1: User switches language multiple times in quick succession]`
A1.1 Components may use debouncing or delay mechanisms (e.g., set Timeout) 
to reduce frequent API requests when language is switched multiple times 
quickly
A1.2 System processes the most recent language switch request, and previous 
requests may complete but their results may be overwritten by newer requests
A1.3 Use case continues from Step 3
Exception 
Flow
E1: Language change event fails
E1.1 System detects that the language code is invalid (not "zh" or "en")
E1.2 System logs a warning to console (e.g., "Unsupported language: {lang}") 
but does not display an error message to the user
E1.3 System maintains the current language setting (no change occurs)
E1.4 Use case end.
E2: Storage update fails
E2.1 System attempts to update the language preference in localStorage (key: 
'userLanguage') but fails (e.g., localStorage quota exceeded, localStorage 
disabled in browser)
E2.2 System logs error to console (e.g., "Failed to save language preference to 
localStorage") but does not display an error message to the user (language 
switch still proceeds for current session)
E2.3 The 'languageChanged' event has already been triggered (before the 
localStorage write failure was detected), so components will still receive the 
notification and refresh their content
E2.4 System may still proceed with the language switch for the current session, 
but the preference may not persist across browser sessions
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 31
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
E2.5 Use case continues from Step 4 (language switch completes, but 
preference may not be saved)
[E3: API request fails]
E3.1 System sends API request with new language parameter but receives an 
error response (e.g., 500 Internal Server Error, 404 Not Found)
E3.2 System displays an error message to the user (e.g., "Failed to load content 
in the selected language. Please try again.") and may show an error state in the 
UI
E3.3 System keeps the new language setting (localStorage and UI language 
have already been updated), but content may not be displayed or may show in 
the previous language if cached
E3.4 User can retry by refreshing the page or switching language again
E3.5 Use case end.
E4: Network timeout
E4.1 Request to fetch content in the new language exceeds the configured 
timeout
E4.2 System displays a localized timeout message (e.g., "Request timeout. 
Please check your internet connection and try again.")
E4.3 User can retry the language switch operation
E4.4 Use case end.
Note The language switch should be instantaneous from the user's perspective, with 
minimal loading time. The system uses eventdriven architecture where 
components listen to 'languageChanged' events and automatically refresh.
The system maintains the user's current browsing context (page number, 
selected item ID, filter parameters) when switching languages. For example, if 
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 32
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
AD03: Switch Interface Language
The Activity Diagram for Switch Interface Language illustrates the interaction 
between the User and the System when the user changes the interface language:
the user is on page 3 of Daily Briefing with filter "Bangkok Post", switching 
language will reload page 3 with the same filter in the new language.
If the user switches language while viewing a specific news detail page, the 
system reloads the news detail in the new language while maintaining the same 
news item ID (newsId).
The language preference is stored in localStorage with key 'userLanguage' and 
persists across browser sessions. When a user logs in, if the user profile has a 
preferredLanguage field, it is loaded and synchronized with localStorage. 
However, when switching language via the sidebar buttons, only localStorage 
is updated; the user profile's preferredLanguage field is only updated when the 
user explicitly saves their profile in the My Profile page.
The system uses a centralized i18n system (frontend/src/i18n/index.js) that 
manages translations for all UI text. When language changes, all components 
using the t() translation function automatically display text in the new language.
The system supports two languages: "zh" (Chinese) and "en" (English). The 
default language is "en" if no preference is stored.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 33
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 34
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
2.1.3.4 UCD04
URS04: The User can jump to the original text link to read the full report from the 
source website when viewing news details.
 SRS22: The system shall display a "Read Original" button (or "阅读原文"(Read 
Original) in Chinese interface) on both the Daily Briefing list page and the News 
Detail page. The button shall be clearly visible and accessible to users.
 SRS23: The system shall display the "Read Original" button with an external link 
icon (e.g., "elicontopright") to indicate that clicking it will open an external 
website in a new browser tab.
 SRS24: The system shall disable the "Read Original" button if the news item 
does not have a valid originalUrl field (i.e., originalUrl is null, undefined, or 
empty string). When disabled, the button shall be visually distinct (e.g., grayed 
out) and nonclickable.
 SRS25: When the user clicks the "Read Original" button, the system shall call the 
`openOriginalUrl(url)` method with the news item's originalUrl value. Inside the 
method, the system shall check if the url parameter is valid using `if (url)`. If the 
url is valid, the system shall execute `window.open(url, '_blank')` to open the 
original URL in a new browser tab, allowing the user to read the full report from 
the source website while maintaining their current browsing context in the 
BridgeU application. If the url is null, undefined, or empty (falsy), the method 
shall return without executing `window.open()`, and no new tab shall be opened.
 SRS26: The system shall handle cases where the original URL is invalid or 
inaccessible. If the URL fails to load in the new tab, the browser's native error 
handling shall be used (e.g., browser displays "This site can't be reached" or 
similar error message). The BridgeU application shall not display additional error 
messages, as the external website loading is handled by the browser.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 35
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Use Case ID UC04
Use Case 
Name
Jump to Original Link
Created By ZhiYi Pan Last Update By
Date Created 06/01/2026 Last Revision 
Date
Actors User
Description User can click the "Read Original" button (or "阅读原文" in Chinese interface) 
on the Daily Briefing list page or News Detail page to open the original news 
article from the source website in a new browser tab. 
Trigger User clicks the "Read Original" button on a Daily Briefing card (list page) or on 
the News Detail page
Precondition
s
1. User is viewing the Daily Briefing list page (UI01) or the News Detail page 
(UI02).
2. The news item has a valid originalUrl field (not null, undefined, or empty 
string).
3. The user's browser supports opening new tabs (window.open API).
4. The user has internet connectivity to access external websites. 
Use Case Input Specification
Input type Constraint Example
Original 
URL
String Must be a valid HTTP/HTTPS URL https://www.ban
gkokpost.com/th
ailand/general/1
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 36
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
234567/newstitl
e" 
Post 
conditions
The original news article from the source website is opened in a new browser 
tab
The user's current browsing context in the BridgeU application remains 
unchanged (user stays on the same page)
The user can read the full report from the source website while maintaining 
access to the BridgeU application
Normal 
Flows
User System
1. User views a Daily Briefing item on 
the list page or News Detail page and 
identifies the "Read Original" button 
(displayed with an external link icon). 
The button is enabled and clickable (the 
news item has a valid originalUrl field)
[A1: News item does not have a valid 
originalUrl field]
2. System displays the "Read 
Original" button as enabled and 
clickable (rendered with 
`:disabled="!news.originalUrl"` 
evaluating to false, meaning 
originalUrl is valid) 
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 37
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
3. User clicks the enabled "Read 
Original" button
[A2: User clicks "Read Original" 
button multiple times in quick 
succession]
5. User views the original news article 
in the new browser tab 
4. System calls the 
`openOriginalUrl(url)` method with 
the news item's originalUrl value 
 4a. System checks if the url 
parameter is valid using `if (url)` 
as a defensive check
 4b. System executes 
`window.open(url, '_blank')` to 
open the original URL in a new 
browser tab
 4c. The new tab opens 
(background or foreground 
depending on browser settings)
 4d. The BridgeU application tab 
remains active and unchanged
Note: For edge cases (invalid URL 
parameter, browser blocks popup, 
URL fails to load), see Exception 
Flows [E1], [E2], [E3]
6. System maintains the user's 
current browsing context in the 
BridgeU application (user remains on 
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 38
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
the same page, same scroll position, 
same language setting)
Alternative 
Flow
A1: News item does not have a valid originalUrl field
A1.1 User views a Daily Briefing item on the list page or News Detail page
A1.2 System checks if the news item has a valid originalUrl field
A1.3 If originalUrl is null, undefined, or empty: System disables the button 
(rendered with `:disabled="!news.originalUrl"`)
A1.4 Button is visually distinct (grayed out) and nonclickable
A1.5 User cannot click the button (button is disabled)
A1.6 Use case end.
A2: User clicks "Read Original" button multiple times in quick succession
A2.1 System may open multiple tabs with the same original URL (one tab per 
click)
A2.2 Each click triggers a new `window.open()` call, which may result in 
multiple tabs being opened
A2.3 Use case continues from Step 5
Note: The current implementation does not prevent multiple tabs from being 
opened. Browser settings may control whether multiple tabs are opened or if the 
existing tab is reused.
Exception 
Flow
E1: URL parameter is invalid]`
E1.1 System calls the `openOriginalUrl(url)` method with the news item's 
originalUrl value
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 39
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
E1.2 Inside the method, the system checks if the url parameter is valid using 
`if (url)`
E1.3 If the url is null, undefined, or empty (falsy), the method returns without 
executing `window.open()`
E1.4 No new tab is opened
E1.5 System does not display an error message to the user (as this is a clientside 
operation)
E1.6 Use case end.
Note: The current implementation uses a simple `if (url)` check before calling 
`window.open()`. If the URL is falsy (null, undefined, or empty string), the 
method returns without opening a tab. This aligns with the button's disabled state 
when `originalUrl` is invalid. However, if the button is enabled but the url 
parameter passed to the method is somehow invalid, this exception flow handles 
that case.
E2: Browser blocks popup
E2.1 Browser's popup blocker prevents `window.open()` from opening a new 
tab (e.g., user has popup blocker enabled, or browser security settings block the 
action)
E2.2 Browser may display a notification to the user (e.g., "Popup blocked" 
message in browser UI)
E2.3 No new tab is opened
E2.4 User can manually allow popups for the BridgeU domain or disable 
popup blocker
E2.5 Use case end.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 40
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
E3: URL fails to load
E3.1 New tab opens successfully, but the original URL fails to load (e.g., 
website is down, URL is invalid, network error, CORS issue)
E3.2 Browser displays its native error message (e.g., "This site can't be 
reached", "404 Not Found", "ERR_CONNECTION_REFUSED")
E3.3 BridgeU application does not display additional error messages (external 
website loading is handled by the browser)
E3.4 User can see the browser's error message in the new tab
E3.5 User can close the error tab and return to the BridgeU application
E3.6 Use case end.
Note The "Read Original" button is available on both the Daily Briefing list page 
and the News Detail page, providing consistent functionality across different 
views.
The button text is localized: "Read Original" in English interface and "阅读原
文" in Chinese interface, with an external link icon (e.g., "elicontopright") to 
indicate it opens an external website.
The button is automatically disabled if the news item does not have a valid 
originalUrl, preventing user confusion and unnecessary clicks.
Opening the original URL in a new tab allows users to read the full report from 
the source website while maintaining their browsing context in the BridgeU 
application. Users can easily switch between tabs to compare information or 
return to the BridgeU application.
The system does not track or log when users click the "Read Original" button, 
as this is a simple navigation action to an external website.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 41
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
If the original URL is accessible, the user can read the full article, view images, 
and access additional content that may not be available in the Daily Briefing 
summary.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 42
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
AD04 Switch Interface Language
The Activity Diagram for Switch Interface Language illustrates the interaction 
between the User and the System when the user changes the interface language:
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 43
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
2.1.3.5 UCD05
URS‑05 – Filter Daily Briefings News by Date
The User can filter news based on specific criteria (start date and end date) while 
browsing.
 SRS27: The system shall provide a filter panel on the Daily Briefing list page 
(UI01) containing:
 A “Start Date” picker (optional).
 An “End Date” picker (optional).
 A "Filter" action button.
 A "Reset" action button that clears both date fields.
 SRS28: When the user clicks the "Filter" button, the system shall validate that:
If both dates are provided, Start Date ≤ End Date.
If validation fails, the system shall display an appropriate error message and shall 
not send a filter request to the backend.
 SRS29: When validation succeeds, the system shall send a filter request to the 
backend including the provided filter parameters:
`startDate` (optional)
 `endDate` (optional)
 SRS30: The backend shall query the Daily Briefing data such that:
If `startDate` and/or `endDate` is provided, only news items whose publication 
date (`publishDate`) falls within the date range (inclusive) are returned.
 If only `startDate` is provided, the backend shall set `endDate` to today.
If only `endDate` is provided, the backend shall set `startDate` to 30 days before
the provided end date.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 44
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
 Results shall be paginated and ordered from newest to oldest by publication date 
(`publishDate` descending).
 SRS31: The system shall update the Daily Briefing list page (UI01) to display 
only the filtered news items, resetting the results view to the first page while 
preserving pagination controls for navigating through multiple result pages.
 SRS32: If no news items match the filter conditions, the system shall display an 
empty list and a user-friendly message "No news data available" while keeping 
the filter panel visible so that the user can adjust conditions and retry.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 45
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Use Case ID UC-05
Use Case 
Name
Filter Daily Briefings News by Date
Created By ZhiYi Pan Last Update By 14/01/2026
Date Created 08/01/2026 Last Revision 
Date
Actors User
Description User can filter Daily Briefing items by choosing an optional start date and an 
optional end date, and then browse only the items that meet these filter 
conditions.
Trigger User is on the Daily Briefing list page (UI-01) and interacts with the filter panel 
(selects dates, then clicks the "Filter" button).
Precondition
s
1. User is logged into the BridgeU platform.
2. User has an active internet connection.
3. The Daily Briefing system has successfully crawled news from approved 
sources and stored publication dates.
4. The filter panel (date pickers) is visible on the Daily Briefing list page (UI-
01).
Use Case Input Specification
Input type Constraint Example
Start Date Date Must be a valid calendar date; must not be later 
than End Date
01-01-2026
End Date Date Must be a valid calendar date; must not be 
earlier than Start Date
03-01-2026
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 46
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Post 
conditions
The Daily Briefing list page (UI-01) displays only news items that match the 
provided date conditions (if any), ordered from newest to oldest by publication 
date, with pagination.
Normal 
Flows
User System
1. User opens the Daily Briefing list 
page (UI-01) and sees the filter panel 
with date pickers.
3. User sets filter criteria (“Start Date” 
and/or “End Date”).
5. (Optional) User clicks the "Reset" 
button.
7. User clicks the "Filter" button.
2. System displays the filter panel 
with empty (optional) fields and 
shows the current news list 
(unfiltered), with pagination controls 
when multiple pages exist.
4. System updates the filter model 
accordingly.
6. System clears Start Date and End 
Date and refreshes the list as 
unfiltered (page reset to 1).
8. System validates the filter inputs (if 
both dates are provided, Start Date ≤ 
End Date).
[E1: Invalid date range]`
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 47
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
13. User browses the filtered news list 
and can navigate between pages using 
pagination controls. 
9. If validation passes, the system 
sends a filter request to the backend 
API including any provided 
parameters (`startDate`, `endDate`) 
and the current UI language (`lang`).
[E2: Authentication token invalid or 
expired]
[E3: Network timeout or connection 
error]
10. Backend queries the database for 
Daily Briefing items matching the 
provided conditions (date range on 
`publishDate`), orders results from 
newest to oldest by `publishDate`, 
and applies pagination.
[E4: Database error or server error]
11. Backend returns the filtered news 
list (with pagination data) to the 
frontend.
12. System updates the Daily 
Briefing list on UI-01 to show only 
filtered items (page reset to 1) and 
updates pagination controls 
accordingly.
[A1: No news match filter 
conditions]`
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 48
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
15. User may adjust filter criteria and 
click "Filter" again (or reset).
14. System loads and displays the 
corresponding page of filtered results 
while preserving the current filter 
conditions.
16. System repeats the validation￾and-query flow with the new 
conditions.
Alternative 
Flow
A1: No news match filter conditions
A1.1 Backend returns an empty result set for the specified Filter (no records 
match date range conditions).
A1.2 System displays an empty list on the Daily Briefing page and shows a 
message "No news data available"
A1.3 Filter panel remains visible and retains the user's selected dates (if any) so 
that the user can easily adjust them.
A1.4 Use case ends or continues when the user modifies filter conditions and 
clicks "Filter" again.
Exception 
Flow
E1: Invalid date range
E1.1 System detects that Start Date is later than End Date during validation.
E1.2 System displays an inline validation error message (e.g., "Start date cannot 
be later than end date") near the date fields.
E1.3 System does not send a request to the backend.
E1.4 User can correct the dates and click "Filter" again (return to step 7).
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 49
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
E2: Authentication token invalid or expired
E2.1 System returns a 401 Unauthorized response (if authentication is required 
for this operation).
E2.2 Frontend detects the 401 error and clears the invalid token from 
localStorage.
E2.3 Frontend triggers an authentication error event and displays "Login 
expired, please log in again" message.
- E2.4 System redirects the user to the login page.
- E2.5 Use case ends.
E3: Network timeout or connection error
E3.1 The request to the backend times out or fails due to network issues.
E3.2 System displays an error message "Network request failed, please try again 
later"
E3.3 User may retry the operation by clicking a "Retry" button or by clicking 
"Filter" again; the system re-sends the request with the same filter parameters 
(return to step 9).
E4: Database error or server error
E4.1 Backend encounters an error while querying the database and returns a 500 
Internal Server Error.
E4.2 Frontend displays an error message "Failed to fetch news" 
E4.3 Backend logs the error details for administrator review.
E4.4 User may retry by clicking "Filter" again after adjusting conditions, or retry 
later.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 50
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Note The filter panel allows users to set optional Start Date and/or End Date. When 
only one date is provided, the backend applies default date range logic (if only 
Start Date is provided, End Date defaults to today; if only End Date is provided, 
Start Date defaults to 30 days before the End Date).
Filtered results are displayed in chronological order (newest to oldest by 
publication date) and reset to page 1 when filter conditions are applied.
The filter panel remains visible after filtering, allowing users to adjust 
conditions and re-filter without losing their filter settings.
When the user clicks "Reset", all filter fields are cleared and the list is refreshed 
to show unfiltered results, resetting pagination to page 1.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 51
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
AD-05
The Activity Diagram for Filter Daily Briefings News by Date illustrates the 
interaction between the “User“ and the “System” when the user filters Daily 
Briefing items by date range.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 52
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
2.1.3.6 UCD06
URS06 – Search for Daily Briefing News 
User can type Chinese or English keywords into a search box on the Daily Briefing 
page and view only Daily Briefing items that match the entered keywords.
 SRS-33: The system shall provide a search box on the Daily Briefing list page 
(UI-01) that allows users to enter keywords in Chinese or English. The search 
box shall have:
A text input field with placeholder text "Search by keywords 
(Chinese/English)..." 
A search button (icon: "el-icon-search") that triggers the search when clicked.
Support for triggering search by pressing the Enter key.
A clear button that appears when the search box contains text, allowing users to 
clear the search keyword and trigger a new search.
 SRS-34: When the user enters keywords and triggers the search (by clicking the 
search button or pressing Enter), the system shall:
Trim whitespace from the keyword input.
Reset the current page to page 1.
Send a search request to the backend API including the keyword parameter 
(`keyword`) and the current UI language (`lang`).
If the user has also set date filter conditions (Start Date and/or End Date), the 
system shall include those parameters in the same request, allowing combined 
search and date filtering.
 SRS-35: The backend shall search for Daily Briefing items where the keyword 
matches any of the following fields (case-insensitive partial match):
`title` (original title)
`originalContent` (original content)
`summary` (AI-generated summary)
`titleZh` (Chinese translated title)
`titleEn` (English translated title)
`summaryZh` (Chinese translated summary)
`summaryEn` (English translated summary)
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 53
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
 SRS-36: The backend shall apply the search logic as follows:
If only a keyword is provided (no date filter), the system shall search across all 
historical news in the database.
If both keyword and date range are provided, the system shall search only within 
news items whose publication date (`publishDate`) falls within the specified date 
range (inclusive).
Results shall be “paginated” and ordered from newest to oldest by “publication 
date”(`publishDate` descending).
 SRS-37: The system shall update the Daily Briefing list page (UI-01) to display 
only the news items that match the search keyword, “resetting the results view to 
the first page” while preserving pagination controls for navigating through 
multiple result pages.
 SRS-38: If no news items match the search keyword (and any date filter 
conditions), the system shall display an empty list and a user-friendly message 
"No news data available" while keeping the search box visible and retaining the 
entered keyword so that the user can modify it and retry.
 SRS-39: When the user clears the search keyword (by clicking the clear button), 
the system shall:
Clear the search keyword from the input field.
Reset the current page to page 1.
Send a new request to the backend without the keyword parameter, effectively 
showing all news (or filtered by date range if date filters are active).
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 54
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Use Case ID UC-06
Use Case 
Name
Search for Daily Briefing News
Created By ZhiYi Pan Last Update By
Date Created 08/01/2026 Last Revision 
Date
Actors User
Description User can type Chinese or English keywords into a search box on the Daily 
Briefing page and view only Daily Briefing items that match the entered 
keywords. The search can be combined with date filtering to narrow down 
results.
Trigger User is on the Daily Briefing list page (UI-01) and enters keywords into the 
search box, then clicks the search button or presses Enter.
Precondition
s
1. User is logged into the BridgeU platform.
2. User has an active internet connection.
3. The Daily Briefing system has successfully crawled news from approved 
sources and stored publication dates and content.
4. The search box is visible on the Daily Briefing list page (UI-01).
Use Case Input Specification
Input type Constraint Example
Keyword String Can be Chinese or English characters; can 
contain spaces; will be trimmed of 
leading/trailing whitespace
" 泰 国 " or 
"Thailand" or 
"travel"
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 55
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
Post 
conditions
The Daily Briefing list page (UI-01) displays only news items that match the 
entered keyword (and any date filter conditions if set), ordered from newest to 
oldest by publication date, with pagination.
Normal 
Flows
User System
1. User opens the Daily Briefing list 
page (UI-01) and sees the search box.
3. User types keywords (Chinese or 
English) into the search box.
5. User clicks the "Search" button or 
presses “Enter”.
2. System displays the search box 
with placeholder text and shows the 
current news list (unfiltered), with 
pagination controls when multiple 
pages exist.
4. System updates the search keyword 
model accordingly.
6. System trims whitespace from the 
keyword input.
[E1: Invalid keyword input]
7. System resets the current page to 
page 1.
8. System sends a search request to 
the backend API including the 
keyword parameter (`keyword`), any 
date filter parameters (if set), and the 
current UI language (`lang`).
[E2: Authentication token invalid or 
expired]
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 56
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
12. User browses the search results and 
can navigate between pages using 
pagination controls.
[E3: Network timeout or connection 
error]`
9. Backend searches the database for 
Daily Briefing items where the 
keyword matches any of the 
searchable fields (title, 
originalContent , summary, and all 
translation fields). If date filters are 
provided, the search is limited to 
items within the date range. Results 
are ordered from newest to oldest by 
`publishDate` and paginated.
[E4: Database error or server error]
10. Backend returns the search results 
(with pagination data) to the frontend.
11. System updates the Daily 
Briefing list on UI-01 to show only 
matching items (page reset to 1) and 
updates pagination controls 
accordingly.
[A1: No news match search 
keyword]
13. System loads and displays the 
corresponding page of search results 
while preserving the current search 
keyword and any date filter 
conditions.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 57
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
14. User may modify the search 
keyword and click "Search" again (or 
clear the keyword). 
16. (Optional) User clicks the “clear 
button” in the search box.
15. System repeats the search flow 
with the new keyword. 
17. System clears the search keyword, 
resets the current page to page 1, and 
sends a new request without the 
keyword parameter (showing all news 
or filtered by date range if date filters 
are active). 
Alternative 
Flow
[A1: No news match search keyword]
A1.1 Backend returns an empty result set for the specified search keyword (and 
any date filter conditions).
A1.2 System displays an empty list on the Daily Briefing page and shows a 
message "No news data available" .
A1.3 Search box remains visible and retains the user's entered keyword so that 
the user can easily modify it and retry.
A1.4 Use case ends or continues when the user modifies the keyword and clicks 
"Search" again.
Exception 
Flow
[E1: Invalid keyword input]
E1.1 System detects that the keyword input exceeds the maximum allowed 
length (e.g., more than 200 characters) or contains invalid characters after 
trimming whitespace.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 58
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
E1.2 System displays an inline validation error message near the search box 
(e.g., "Keyword is too long" or "Invalid characters in keyword").
E1.3 System does not send a request to the backend.
E1.4 User can correct the keyword and click "Search" again (return to step 5).
[E2: Authentication token invalid or expired]
E2.1 System returns a 401 Unauthorized response (if authentication is required 
for this operation).
E2.2 Frontend detects the 401 error and clears the invalid token from 
localStorage.
E2.3 Frontend triggers an authentication error event and displays "Login 
expired, please log in again" message.
E2.4 System redirects the user to the login page.
E2.5 Use case ends.
[E3: Network timeout or connection error]
E3.1 The request to the backend times out or fails due to network issues.
E3.2 System displays an error message "Network request failed, please try again 
later" .
E3.3 User may retry the operation by clicking the "Search" button again; the 
system re-sends the request with the same search parameters (return to step 8).
[E4: Database error or server error]
E4.1 Backend encounters an error while querying the database and returns a 500 
Internal Server Error.
E4.2 Frontend displays an error message "Failed to fetch news".
E4.3 Backend logs the error details for administrator review.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 59
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
E4.4 User may retry by clicking "Search" again after modifying the keyword, or 
retry later.
Note The search functionality can be combined with date filtering. When both 
keyword and date filters are provided, the system searches only within news 
items that match both the keyword and the date range.
If only a keyword is provided (no date filter), the system searches across all 
historical news in the database.
Search results are displayed in chronological order (newest to oldest by 
publication date) and reset to page 1 when a new search is performed.
The search box remains visible after searching, allowing users to modify 
keywords and re-search without losing their search context.
When the user clears the search keyword, the system removes the keyword filter 
and shows all news (or filtered by date range if date filters are active), resetting 
pagination to page 1.
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 60
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025
AD-06
The Activity Diagram for Search for Daily Briefing News illustrates the interaction 
between the User and the System when the user searches for Daily Briefing items by 
entering keywords:
Document
Name
BridgeUSRS 
V.0.8
Owner ZHIYI PAN Page 61
Document
Type
Software 
Requirement
Specification
Release Date 12/12/2025 Print date 12/12/2025