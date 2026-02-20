# 3DJewelryCraft

**Build the jewelry business with ease through 3D design**

3DJewelryCraft
Build the jewelry business with ease through 3D design.

## THIS PROJECT PROPOSAL REPORT HAS BEEN APPROVED TO BE


## A PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE


## SOFTWARE ENGINEERING PROGRAM: COLLEGE OF ARTS, MEDIA,


## AND TECHNOLOGY

…………………………………. Advisor
Dr. Siraprapa Wattanakul
…………………………………. Member
Nichakorn Prompong
…………………………………. Member
Nonlanee Panjateerawit
20 October 2025
©Copyright by College of Arts Media and Technology

---


## ACKNOWLEDGEMENT

First of all, we would like to begin by expressing our sincere gratitude to the dedicated
team 3DJewelryCraft behind this project for bringing our jewelry platform to life. Their innovative
ideas, hard work, and passion have been essential in transforming our vision into reality.
Our deepest thanks also go to the project committee, especially to the advisor:
Dr. Siraprapa Wattanakul, whose valuable feedback, insights, and suggestions have played a
crucial role in refining and enhancing our project.
We are also grateful to our stakeholders, developers, and advisors for their ongoing support
and trust in the potential of this platform to empower jewelry entrepreneurs. Their belief in our
vision drives us to continue working towards creating a tool that will simplify and elevate the
process of building a jewelry business.
Finally, we look forward to the continued success and impact of this platform, which aims
to democratize jewelry design and business creation, enabling creative people and starter
entrepreneurs to easily transform their ideas into a thriving reality. With the collective effort of all
involved, we believe that we can help shape the future of the jewelry industry.
Nichakorn Prompong
Nonlanee Panjateerawit

---

Title 3DJewelryCraft
Build the jewelry business with ease
through 3D design.
Author Nichakorn Prompong
Nonlanee Panjateerawit
Degree Bachelor of science software engineering
program
Project Advisor Dr. Siraprapa Wattanakul

## ABSTRACT

3DJewelryCraft introduces an innovative platform that simplifies jewelry business creation by
providing a seamless, customizable, and 3D-based design experience. Aimed at aspiring jewelry
entrepreneurs, including creative people, the platform allows users to easily create and visualize
their jewelry designs in 3D, offering features such as pre-designed mockups, advanced 2D-to-3D
conversion, and customization of materials, colors, and shapes. It also provides tools for
visualizing products in various packaging options and virtual try-on. Additionally, the platform
includes a sharing feature that allows creators to share their jewelry models, including the materials
and colors used, with others or manufacturing partners, streamlining the production process and
reducing the risk of errors or production costs. By integrating these features, the platform
empowers users to effortlessly create and share their jewelry designs, facilitating the establishment
of their own brand with ease. With its user-friendly interface and innovative technology, this
project aims to revolutionize the jewelry design and industry, making it more accessible and
inclusive for individuals looking to start their own business.

---


## TABLE OF CONTENTS

ACKNOWLEDGEMENT ............................................................................................................... I
ABSTRACT .................................................................................................................................... II
CHAPTER 1: PROJECT PROPOSAL ........................................................................................... 1
CHAPTER 2: PROJECT MANAGEMENT PLAN ..................................................................... 49
CHAPTER 3: SOFTWARE REQUIREMENT SPECIFICATION ............................................. 74
CHAPTER 4: SOFTWARE DESIGN DEVELOPMENT ......................................................... 244
CHAPTER 5: TEST PLAN ........................................................................................................ 343
CHAPTER 6: TEST RECORD .................................................................................................. 442
CHAPTER 7: TRACEABILITY RECORD ............................................................................... 530
CHAPTER 8: CHANGE REQUEST.......................................................................................... 545
CHAPTER 9: EXECUTIVE SUMMARY ................................................................................. 549

---


## CHAPTER 1


## PROJECT PROPOSAL


---

Document History
Document Version History Status Date Editable Reviewer
Name
Project Proposal Project Research Information Draft 01/04/2025 NP1, SW
Proposal_V.0 • Summarize of NP2
research
3DJewelryCraft Project Insert content Draft 05/04/2025 NP1, SW
_Proposal_V.1.0 Proposal_V.1.0 • Chapter 1 NP2
• Chapter 2
3DJewelryCraft Project Update Chapter 1 Draft 05/04/2025 NP1, SW
_Proposal_V.1.1 Proposal_V.1.1 • Introduction NP2
and
Background
• Purpose and
Scope
• Target User
Update Chapter 2
• Business and
Software
Review
• Tools and
Technology
Reviews
• Infrastructure
Tool Reviews
3DJewelryCraft Project Insert Content Draft 08/04/2025 NP1, SW
_Proposal_V.1.2 Proposal_V.1.2 • Chapter 3 NP2
• Chapter 4
• Chapter 5
3DJewelryCraft Project Update Chapter 3 Draft 08/04/2025 NP1, SW
_Proposal_V.1.3 Proposal_V.1.3 • Product NP2
Perspective
• Objective
• Acronyms and
Definitions
• Type of sytem
users and the
user’s
characteristics
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 2
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

• Software
Development
Life Cycle
• Product
Features
• Limits
Update Chapter 4
• Quality
Standard
3DJewelryCraft Project Update Chapter 2 Draft 17/04/2025 NP1, SW
_Proposal_V.1.4 Proposal_V.1.4 • SWOT NP2
Analysis
• Risk Analysis
Update Chapter 3
• Quality
Planning
• Schedule and
Milestone
3DJewelryCraft Project Update Chapter 3 Draft 19/04/2025 NP1, SW
_Proposal_V.1.5 Proposal_V.1.5 • System NP2
Architecture
• Use Case
Diagram
Update Chapter 5
• Reference
3DJewelryCraft Project Insert Content Draft 20/04/2025 NP1, SW
_Proposal_V.1.6 Proposal_V.1.6 • Chapter 6 NP2
Update Chapter 6
• Prototype
3DJewelryCraft Project Update Content Draft 22/04/2025 NP1, SW
_Proposal_V.1.7 Proposal_V.1.7 • Chapter 3 NP2
• Chapter 4
• Chapter 5
• Chapter 6
3DJewelryCraft Project Final Final 22/04/2025 NP1, SW
_Proposal_V.1.8 Proposal_V.1.8 NP2
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 3
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## TABLE OF CONTENTS

Document History ......................................................................................................................... 2
TABLE OF CONTENTS ............................................................................................................. 4
LIST OF FIGURES ...................................................................................................................... 6
Chapter One | Introduction and Background .................................................................................. 7
1.1 Introduction and Background ............................................................................................... 7
1.2 Purpose and Scope ................................................................................................................ 8
1.2.1 Purpose ........................................................................................................................... 8
1.2.2 Scope .............................................................................................................................. 8
1.3 Target Users (Persona) ........................................................................................................ 10
Chapter Two | Literature Review .................................................................................................. 12
2.1 Business Review and Software Review .............................................................................. 12
2.1.1 Competitive Analysis ................................................................................................... 12
2.1.2 Feature Comparison ..................................................................................................... 16
2.2 SWOT Analysis .................................................................................................................. 17
2.3 Tools and Technologies Review ....................................................................................... 19
2.3.1 External Service ........................................................................................................... 19
2.3.2 Development tools ....................................................................................................... 20
2.3.3 Library/ Framework/ Database .................................................................................... 21
2.4 Infrastructure Tool Review .............................................................................................. 23
2.5 Risk Analysis ..................................................................................................................... 24
2.5.1 Manage Scope Table .................................................................................................... 24
2.5.2 Project Risks and Alternative Solutions ...................................................................... 25
Chapter Three | Project Plan ......................................................................................................... 25
3.1 Product Perspective .......................................................................................................... 26
3.2 Objective ............................................................................................................................ 26
3.3 Acronyms and Definitions ................................................................................................ 26
3.3.1 Acronyms ..................................................................................................................... 26
3.3.2 Definitions.................................................................................................................... 27
3.3.3 Application Usage Definitions ..................................................................................... 28
3.4 Type of System Users and User Characteristics ............................................................ 28

---

3.5 System Architecture .......................................................................................................... 29
3.6 Use Case Diagram ............................................................................................................. 31
3.7 Software Development Life Cycle ................................................................................... 35
3.8 Product Features ............................................................................................................... 36
3.8.1 Feature #1 – Registration ............................................................................................. 36
3.8.2 Feature #2 – Jewelry and Packaging Mockups ............................................................ 36
3.8.3 Feature #3 – Image to 3D............................................................................................. 36
3.8.4 Feature #4 – Customization ......................................................................................... 37
3.8.5 Feature #5 – Virtual Try-on ......................................................................................... 37
3.8.6 Feature #6 – Workspace............................................................................................... 38
3.8.7 Feature #7 – Super Export ........................................................................................... 38
3.9 Quality Planning ............................................................................................................... 39
3.9.1 Look and Feel .............................................................................................................. 39
3.9.2 Cultural ........................................................................................................................ 39
3.9.3 Political Legal .............................................................................................................. 39
3.9.4 Usability and Humanity ............................................................................................... 40
3.9.5 Operational ................................................................................................................... 40
3.9.6 Performance ................................................................................................................. 40
3.9.7 Security ........................................................................................................................ 41
3.10 Limits ............................................................................................................................... 41
3.11 Schedule Plan and Milestones ........................................................................................ 42
3.11.1 Schedule Plan ............................................................................................................. 42
3.11.2 Milestones .................................................................................................................. 43
Chapter Four | Quality Standard ................................................................................................... 46
4.1 ISO 9001 ............................................................................................................................. 46
Chapter Five | References ............................................................................................................. 47
Chapter Six | Appendix ................................................................................................................. 48
6.1 Prototype ............................................................................................................................ 48

---


## LIST OF FIGURES

Figure 1: Persona of the starter jewelry entrepreneurs ................................................................. 10
Figure 2: Persona of the creative self-expressers .......................................................................... 11
Figure 3: Jweel .............................................................................................................................. 12
Figure 4: Zakeke ........................................................................................................................... 13
Figure 5: Apviz ............................................................................................................................. 14
Figure 6: MyNove25 ..................................................................................................................... 15
Figure 7: Amazon Elastic Compute Cloud ................................................................................... 23
Figure 8: System Architecture ...................................................................................................... 29
Figure 9: Registration System ....................................................................................................... 31
Figure 10: Jewelry and Packaging Mockups System ................................................................... 31
Figure 11: Image to 3D System .................................................................................................... 32
Figure 12: Customization System ................................................................................................. 32
Figure 13: Virtual Try-On System ................................................................................................ 33
Figure 14: Workspace System ...................................................................................................... 33
Figure 15: Super Export System ................................................................................................... 34
Figure 16: Iterative Process .......................................................................................................... 35
Figure 17: Phase 1 Plan................................................................................................................. 43
Figure 18: Phase 2 Plan................................................................................................................. 44
Figure 19: Phase 3 Plan................................................................................................................. 44
Figure 20: Phase 4 Plan................................................................................................................. 45
Figure 21: Prototype ..................................................................................................................... 48

---

Chapter One | Introduction and Background
1.1 Introduction and Background
In recent years, the jewelry industry has entered an unprecedented turning point.
The traditional design process, which relies on technical skills and long production times,
has now become more open and accessible through modern technology, especially with the
advent of artificial intelligence (AI), automation, and 3D modeling, which have all-around
improved the design, manufacturing, and consumer experience.
The article “Unleashing The Power Of AI: A Paradigm Shift In The Jewelry
Industry”, published in Forbes (2023), clearly reflects this change, mentioning how jewelry
brands are beginning to apply AI to analyze individual consumer behavior and preferences,
and then use this data to further develop more personalized designs, limiting the design
process to professional designers, and also allowing consumers to participate in creating
their own pieces. [1]
In the same vein, the article from Professional Jeweller (2025) also points out the
important role of digital technology in the retail sector, especially tools such as AI-driven
Virtual Try-On and Web-based 3D Customization, which allow consumers to design and
try on jewelry in real time. Through user-friendly interfaces and no need for in-depth
software or design knowledge. [2]
This evolution has driven customization to the forefront of the modern jewelry
industry, with automation making custom-made jewelry production more accessible.
Advanced 3D visualization tools also allow customers to freely design and select elements,
from metal types to frame styles and gemstones, and see virtual renderings before the actual
production begins. This not only increases confidence in ordering, but also significantly
reduces production time and costs.
Importantly, this integration of AI and automation is more than just a technological
upgrade. It marks a fundamental shift in how the jewelry industry operates, serving
customers more efficiently while still preserving the emotional value, craftsmanship, and
personal touch that define the experience of buying and owning jewelry.
Therefore, the “3DJewelryCraft project” was born with the vision of making 3D
jewelry design accessible to everyone, without the need for complex design skills or
specialized software.
The heart of the project is an online platform that allows users to upload their own
2D sketches and convert them into customizable 3D models through automation and a user-
friendly interface. Changing the material, color, shape, and other elements of the piece can
be done in real time, along with various supporting features, such as jewelry mockups,
packaging mockups, image to 3D, customization, workspace, super export and virtual try-
on.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 7
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

In summary, this project not only allows users to design jewelry easily, but also
allows brands to offer customized jewelry according to their customer’s needs quickly and
without complicated steps, and also enhances the user experience.
1.2 Purpose and Scope
1.2.1 Purpose
In today's digital era, personalized jewelry design is becoming increasingly popular.
However, many users still face difficulties in visualizing their ideas before production
due to the lack of intuitive tools. Traditional communication with jewelry designers
often leads to misunderstandings, a lack of confidence in the final product, and limited
creative control.
3DJewelryCraft was created to solve this problem by allowing users to easily
design their own jewelry through a user-friendly interface by simply uploading a sketch
image. With support for advanced 3D rendering and AI-powered image-to-3D
conversion, users can see their custom jewelry realistically and see the simulation
image on the body before the manufacturing process. There is also a packaging
simulation to help provide a complete overview of the product, which reduces errors,
builds confidence for users, and promotes personal creativity in jewelry design.
1.2.2 Scope
The jewelry industry is evolving in the digital age, yet many of the software tools
available today still cater mainly to professionals with technical expertise. These tools
are often complex, unintuitive, and require significant training, making them
inaccessible to everyday users or starter jewelry entrepreneurs who want to bring their
ideas to life. Additionally, most existing platforms lack features such as image-to-3D
conversion, realistic packaging mockups, or virtual try-on experiences—functions that
could vastly improve user confidence and creative freedom.
This gap in accessibility and visualization tools often leads to poor communication
between entrepreneurs and manufacturers, increased production errors, and higher
costs to produce. Without a clear preview of how a jewelry piece will look or fit, many
users hesitate to move forward with their ideas.
To solve these problems, we created 3DJewelryCraft, a web application designed
to empower anyone that have an idea to design their jewelry easily—whether starting
from a sketch image or photo, for both users who have prior design experience or no
ideas at all, they can access an intuitive and inclusive environment. Users can upload
2D images that are automatically converted into 3D models, or choose from ready-
made mockups that can be customized in their own style.
Our platform offers a range of features to simplify and enrich the design process.
These include the ability to virtually try on necklaces and bracelets using uploaded
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 8
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

photos, offering a lifelike visualization before production. Users can also preview
packaging designs through packaging mockups, allowing them to see how the final
product will look in its full presentation, reducing design errors and boosting
confidence. Additionally, users can save their creations through a workspace, and the
final outputs can be exported in professional-grade formats like high-quality images
and videos. Our user-friendly interface is built for accessibility, removing technical
barriers and empowering creativity for both beginners and experts.
3DJewelryCraft is truly a platform for everyone to convert imagination to reality,
combining the power of AI and 3D technology to make jewelry design accessible,
personalized, and practical.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 9
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

1.3 Target Users (Persona)
1.3.1 Starter Jewelry Entrepreneurs: Individuals starting their own jewelry business who
lack access to professional design tools, by helping users create their jewelry brand with minimal
technical expertise without hiring a full design team.
Figure 1: Persona of the starter jewelry entrepreneurs
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 10
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

1.3.2 Creative Self-Expressers: Fashion-forward, social-media-active users who enjoy
customization and want to express their individuality through jewelry. They’re often early
adopters of tech and driven by aesthetics, shareability, and creative freedom.
Figure 2: Persona of the creative self-expressers
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 11
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter Two | Literature Review
2.1 Business Review and Software Review
2.1.1 Competitive Analysis
2.1.1.1 Jweel ( https://www.jweel.com/ )
Figure 3: Jweel
Description: An online jewelry creation platform that lets users design rings, pendants,
and other items using parametric modeling. It allows users to manipulate forms in 3D space in
real-time, adjusting sizes, and basic stylistic elements such as select text and font on jewelry or
material. Jweel aims to make jewelry design accessible to people without technical design skills.
Once the design is complete, users can order the finished piece, which is 3D printed in precious
metals and delivered to them. The platform is ideal for quick customizations but does not support
importing user-generated content like 2D images or external 3D models.
Pros Cons
Jweel simplifies the jewelry design process by using While user-friendly, Jweel offers limited design
real-time parametric modeling, allowing users to freedom compared to full 3D modeling platforms. Users
customize rings and pendants without requiring technical cannot upload custom 3D models or convert images into
skills. This design approach is highly intuitive for jewelry-compatible structures, which may constrain
beginners and hobbyists, enabling users to personalize creativity for more advanced designers.
their jewelry with inscriptions and stylistic adjustments
quickly and with minimal friction. The platform also
connects directly with 3D printing services, offering a
streamlined path from digital concepts to physical
products, including the ability to try on jewelry on
simulated body models.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 12
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.1.1.2 Zakeke ( https://www.zakeke.com/ )
Figure 4: Zakeke
Description: The B2B visual product configurator used by brands and retailers to enable
interactive 3D and AR customization on their websites. It supports real-time 3D previews of
custom products, including jewelry. Businesses can upload their 3D models and allow customers
to modify attributes such as size, color, and shape. Zakeke also integrates seamlessly with major
e-commerce platforms like Shopify, WooCommerce, and Magento. It includes AR functionality,
letting users try on items virtually using their phone camera. While powerful, Zakeke is built
primarily for brands to enhance their online store, not for end-users to create from scratch.
Pros Cons
Zakeke enables e-commerce brands to offer interactive Despite its visual strength, Zakeke is not designed for
product customization experiences through real-time 3D end-users to create their own 3D content from scratch. It
and AR visualizations. The platform supports requires businesses to upload ready-made 3D models
customizing jewelry components such as materials, and configure them manually, which could pose a
engraving, and integrates seamlessly with major technical barrier for new entrepreneurs.
platforms like Shopify and Magento. The platform’s AR
features enhance the customer experience by enabling
real-time try-ons using a smartphone, which increases
shopper confidence and reduces return rates.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 13
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.1.1.3 Apviz ( https://apviz.io/ )
Figure 5: Apviz
Description: The SaaS solution for brands to showcase configurable jewelry products in
3D. It offers highly detailed product visualizations with options to change metal types, stone sizes,
ring shapes, engraving text, and more, all rendered in real-time. It also features a web-based AR
component for mobile-based virtual try-on. Designed primarily for high-end jewelers and
eCommerce platforms, Apviz allows for flexible scene configuration and product logic but
requires extensive preparation of 3D assets by the brand.
Pros Cons
Apviz offers premium-grade real-time rendering for Requires significant technical setup, including the
luxury jewelry brands, showcasing products with high preparation of multiple 3D model variants and
realism. It supports web-based AR Try-on and advanced configurations by the brand. This setup can be resource-
customization, allowing users to modify various product intensive, making the platform less accessible for new
attributes in details. The platform’s flexibility and entrepreneurs.
scalability make it a robust tool for high-end e-commerce
websites focused on product detail and visual fidelity.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 14
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.1.1.4 MyNove25 ( https://www.nove25.net/ )
Figure 6: MyNove25
Description: The jewelry customization platform, that offers users the ability to design
personalized rings, bracelets, necklaces, and earrings in real-time 3D. The platform allows for
modifications of shapes, engravings, and decorative elements, with immediate visual feedback in
a smooth 3D environment. Once finalized, designs are produced by in-house artisans using high-
quality materials.
Pros Cons
Offers a visually rich and real-time 3D environment for Users are not able to upload their own jewelry design
customizing rings, earrings, and necklaces. The platform pictures or create their own 3D jewelry models, as the
emphasizes brand storytelling and product quality by platform provides only limited customization options,
blending digital customization with artisan-level making it more of a guided customization tool than a
craftsmanship. Its straightforward interface appeals to generative or adaptive platform.
users looking for a smooth shopping and design
experience, with options for engraving and other detailed
touches.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 15
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.1.2 Feature Comparison
Platform
Feature
Jweel Zakeke Apviz MyNove25 3DjewelryCraft
Jewelry and
Packaging
Mockups (Only jewelry) (Only jewelry) (Only jewelry) (Only jewelry) (Jewelry and
Packaging)
Image to 3D
Customization
WorkSpace
Super Export
Virtual Try-on
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 16
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.2 SWOT Analysis
Strengths
- User-Friendly Customization Platform: No need for technical or design
skills. Users can easily convert 2D sketches into 3D jewelry with a simple
interface.
- Comprehensive Feature Set: Prepares jewelry and packaging mockups to
customization, try-on, and super export. All-in-one functionality provides an
end-to-end experience.
- Innovative Virtual Try-On: Offers an interactive 3D try-on experience using
simulated body parts, enhancing user confidence before finalizing designs.
- AI-Powered Automation: Integration Meshy AI and Blender automate
complex tasks like 2D-to-3D conversion and model segmentation, saving time
and effort.
- Packaging Mockup Integration: Unlike most platforms that only focus on
jewelry design, 3DJewelryCraft includes a packaging mockup feature that
allows users to visualize jewelry inside professionally designed boxes. This
helps users present and refine their ideas with complete context—something
rarely offered in competing platforms.
Weaknesses
- Heavy Reliance on External APIs: Dependency on third-party services like
Meshy AI could impact system availability, cost control, or feature continuity
if APIs change.
- Initial User Learning Curve: While user-friendly, first-time users might still
require guidance or onboarding to fully understand 3D customization
workflows.
- Limited Mobile Optimization: If not fully optimized for mobile, users on
smartphones may have a reduced experience, especially for 3D customization.
- Adoption Barrier for Traditional Entrepreneurs: Many jewelry
entrepreneurs are accustomed to working with physical products and may be
hesitant to transition to digital design tools. Changing their mindset and habits
to adopt a software-based workflow could require education, incentives, and
clear demonstrations of value.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 17
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Opportunities
- Growing Demand for Personalized Products: Customization trends in
fashion and jewelry are rapidly increasing, and positioning the platform as a
leader in this niche can capture a strong audience.
- Community & Marketplace: Enabling sharing or selling of designs could
foster a creative community and expand engagement.
- AR/VR Integration: Adding augmented reality support in the future (e.g., real-
time camera-based try-on) can greatly enhance user experience.
Threats
- Technology Dependency Risks: If tools like Blender or Meshy AI introduce
limitations, pricing changes, or API restrictions, platform functionality may be
affected.
- Competition from Established Design Tools: Larger players with advanced
tools (e.g., Adobe Substance, Rhino) may enter the low-barrier customization
market.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 18
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.3 Tools and Technologies Review
2.3.1 External Service
Name Description Alternative The selection of
technology
Online version control • Gitlab • GitHub used for
platform that is used to • Bitbucket version control,
develop software with a collaboration and
team. code management
• Everyone in team
GitHub can use GitHub
Container software - • Simplifies
allows users to create a deployment and
virtual environment for scaling
sharing the software • Support
without any hardware microservice
issues architecture
• Container uses less
docker resources
• Reducing cloud or
hardware costs.
A developer interface - • Automated
that allows connection Workflow: No need
to the Meshy system to convert files or
via a programming use 3D programs,
language (API call), just send images,
allowing input to be and wait for the
sent to the Meshy model.
server and
• Easy Integration:
Meshy AI API automatically receive a Connect to Next.js
finished 3D model
or Backend
back.
immediately.
• Real-time
Feedback: Get
results within
minutes, suitable for
interactive use.
Open-source software - • Blender can be
for creating and editing controlled through
3D work in one place, Python using scripts
including 3D models, to easily customize
animations, and
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 19
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

rendering, is used models
Blender externally to support automatically.
important system • Open-source and
features. 100% free, no
license fees,
suitable for both
developers and
beginners.
• Can cut, separate,
edit workpieces in
detail.
2.3.2 Development tools
Name Description Alternative The selection of
technology
General development • WebStorm • Extensible and
platform • Sublime Text efficient code editor
• Atom
VS Code
Python development • PyDev • Auto-completed and
platform • Spyder auto-build with
python
Pycharm
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 20
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.3.3 Library/ Framework/ Database
Name Description Alternative The selection of
technology
Frontend Framework • ReactJS • Next.js benefits from a
• V ue3 large and active
ecosystem of libraries,
tools, and resources,
making it easier to find
solutions and
extensions for projects.
• Next.js uses automatic
Next.js
code splitting to make
page loads faster.
Extension CSS • Bootstrap 5 • Tailwind can
frontend framework customizable and
reusable styling
components
Tailwin d CSS
3D model Library, • Babylon.js • Three.js supports 3D
A library that can be graphics generation,
loaded with PBR allowing for easy
colors (glossy or creation of 3D models,
other colors) and 3D environments, and
cropped models. [3] highly detailed
animations.
• Three.js supports a
Three.js
wide range of 3D
model formats,
including .obj, .fbx.,
stl, and more, allowing
for easy import of
existing 3D models
from other tools.
The scraping • Lightweight and
services • Fast API flexible web
framework for
building python
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 21
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Flask
Relation Database • PostgreSQL • MySQL uses a
that can manage the • MariaDB standard form of the
data structure. • MongoDB well-known SQL data
language.
• MySQL stores and
represents data
SQL organized in rows and
columns.
A promise-based • Fetch API • Ease of use,
HTTP client for the request/response
browser and Node.js interceptors, and better
used to handle error handling.
requests between
Axios
frontend (Next.js)
and backend (Flask).
A complete open- • Firebase Auth • Seamless integration
source authentication with Next.js, built-in
solution for Next.js security, and high
applications. flexibility.
NextAuth.js
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 22
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.4 Infrastructure Tool Review
Figure 7: Amazon Elastic Compute Cloud
Description: a part of Amazon.com’s cloud-computing platform, Amazon Web Services (AWS),
that allows users to rent virtual computers on which to run their own computer applications. [4]
The selection of technology:
• Amazon EC2 provides over 500 instances and a choice of the latest processor, storage,
networking, and operating system.
• Amazon EC2 provides a scalable infrastructure on demand.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 23
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.5 Risk Analysis
2.5.1 Manage Scope Table
Feature Priority Effort Risk
Registration Critical Low Low
Image to 3D Critical High High
Customization Critical High High
Jewelry and Packaging Mockups Important Medium Medium
Virtual Try-on Important Medium Medium
Super export Useful Low Low
Workspace Useful Medium Low
Critical Features
- Registration: It is very important for saving the history of users selections and
securing their design, customizing the user experience, and enabling backend
services. If it is not there, it will impact many core features and prevent them from
being used to their full potential, especially customization features, which cannot
be used if the user does not register, as well as other important features like super
export and workspace.
- Image to 3D: The core of 3DjewelryCraft by converts user sketches into 3D
models, enabling the entire creative experience. Without this, the platform loses its
uniqueness and affects other features such as jewelry and packaging mockups, and
customization.
- Customization: The core of 3DJewelryCraft, it creates user ownership over their
design and is the key to engagement. Without this, user would only be able to view
static models, which removes the interactive and personalized nature of the
platform.
Important Features
- Jewelry and Packaging Mockups: Provides users with pre-designed templates to
start with, lowering the barrier for those without artistic skills. It makes the design
process easier and faster. If missing, it will impact the user may feel overwhelmed
or unable to start designing from scratch, leading to drop-offs.
- Virtual Try-On: Allows users to visualize how jewelry would look on them using
3D face/neck mockups. It improves confidence in the design and purchase decision.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 24
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

If missing, the experience becomes less immersive. Users may not feel sure about
their design's appearance on them, affecting satisfaction and conversion.
Useful Features
- Super Export: If missing, it will limit professional use cases, but regular users can
still enjoy a full design experience and visualization without this.
- Workspace: Serves as a personal space for users to view their history of jewelry
and packaging mockups they have been interested in or tried, allowing them to
easily go back and review their previous selections. Without this feature, users may
forget ideas they were interested in or not remember mockups they liked, resulting
in a lack of consistency in their user experience.
2.5.2 Project Risks and Alternative Solutions
Potential Risk Impact Alternative solution
1. Inaccurate of AI image-to-3D User may abandon platform if results - Allow manual adjustment after
conversion are poor or unusable. conversion.
- Provide fallback templates or preset
shapes.
2. High technical complexity of Development delays or bugs in live - Start with simplified UI and
Customization and Virtual preview experience. improve iteratively.
Try-On
3. API limitations or downtime Service interruptions could block core - Set up monitoring & auto-retry
features. system.
- Use queue system with status alerts.
4. Users don’t understand how to Low user engagement - Create onboarding guide and video
use platform tutorial.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 25
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter Three | Project Plan
3.1 Product Perspective
3DJewelryCraft is a user-friendly web application that was created to meet the
changing needs of the jewelry industry in an era where consumers are demanding more
customization and easier access to designs without 3D knowledge or specialized software.
3.2 Objective
The objective of the 3DJewelryCraft project is to bridge creativity and
manufacturing, making the creation of personalized jewelry faster, easier, and more
immersive for both creative self-expressers and starter entrepreneurs, as well as improving
the design workflow by providing easy-to-use tools for sizing, material and color
customization, realistic packaging mockups, and virtual try-on. Users can also manage
their creations in their personal workspace and export production-ready files in a variety
of 3D formats. By allowing detailed visualization before production, the system reduces
trial-and-error processes and minimizes design and manufacturing errors, ultimately
helping to lower unnecessary costs.
3.3 Acronyms and Definitions
3.3.1 Acronyms
AI Artificial Intelligence
AR Augmented Reality
API Application Programming Interface
HTTP Hypertext Transfer Protocol
UI User Interface
PBR Physically Based Rendering
MP4 MPEG-4 Part 14
MOV QuickTime Movie
2D Two Dimension
3D Three Dimension
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 26
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.3.2 Definitions
Name Definition
Project Proposal A project proposal is a detailed document
outlining a proposed project's objectives,
scope, approach, and expected outcomes,
used to secure funding, approval, or support
from stakeholders.
Project Plan A project plan is a detailed, formal document
outlining a project's scope, goals, tasks,
deliverables, timelines, budget, and other
crucial aspects to guide execution and control,
ensuring successful project completion.
Feature Feature transformation of input parameters to
output parameters based on a specified
algorithm. It describes the functionality of the
product in the language of the product. Used
for requirements analysis, design, coding,
testing or maintenance.
Risk Analysis A process of identifying, assessing, and
prioritizing risks to organizational operations,
assets, and individuals, and developing
strategies to mitigate or eliminate those risks.
System Architecture A conceptual model that defines the structure,
behavior, and different perspectives of a
system, outlining its components,
interactions, and how they work together to
achieve specific objectives.
Use Case Diagram Represents the interactions between a system
and its users (actors) to achieve specific goals,
illustrating the system's functionalities from
the user's perspective.
Quality Planning A process in which a company determines the
quality of its products by identifying the key
aspects and then developing methods that can
guarantee these qualities. It can determine
what your team needs to deliver value.
Quality Standard Quality standards are established benchmarks
and guidelines that organizations use to
ensure consistent quality in their products,
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 27
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

services, and processes, aiming to meet or
exceed customer expectations and industry
requirements.
3.3.3 Application Usage Definitions
Name Definition
3D Model The 3D models in this project are used to
visualize the designed jewelry and to modify
it in color, material or shape.
Virtual try-on Virtual try-on in this project it is used to help
make design decisions and visualize how the
jewelry will look in real life before deciding
to customize or manufacture it.
Bounding Box Coordinate Rectangular outlines drawn around objects or
regions of interest within an image, defining
their spatial location. These coordinates are
typically represented by two pairs of (x, y)
values, indicating the top-left and bottom-
right corners of the rectangle.
3.4 Type of System Users and User Characteristics
Type of System User User Characteristics
Unregistered user The people who are not registered to the
system. These users can only browse and
preview mockups available on the platform.
They typically include curious creatives who
are exploring the idea of designing custom
jewelry.
User The people who have already registered and
logged in to the web application. These users
range from beginner jewelry entrepreneurs
looking to launch a brand with minimal
technical skills, to self-expressive, trend-
conscious individuals who value aesthetic
freedom without needing a full design team.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 28
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.5 System Architecture
Figure 8: System Architecture
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 29
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Description:
1. The system flow begins when the user accesses the web application and
proceeds to register or log in using NextAuth.js, which manages authentication
securely and efficiently on the front-end.
2. Once authenticated, user interact with the Web Application Services,
which are built using Next.js and integrated with our features.
3. When a user selects to upload a 2D image (e.g., a sketch of jewelry
design, a request is sent via Axios (HTTP client) to the Backend Services, which
are powered by Flask.
4. The back-end then calls the Meshy AI API to convert the 2D sketch into
a 3D model, and returns a .glb file as the result. Then, the .glb file stored and awaits
cropping:
4.1 In the Customization feature, the user selects the area of the
model to be cropped using three.js library.
4.2 The Bounding Box Coordinates from the cropped area will be
sent to the Flask Backend. Then, Flask will call the Separate 3D Component
based on user-defined crop area Service that uses Blender and Python to cut
only that part of the model into separate components.
4.3 After the model is separated, the system will send the separated
.glb file back to the front-end, enabling the user to customize the jewelry in
real-time and try it on using mock body models within the Virtual Try-On
interface.
5. User then have the option to export their model using the Super Export
feature.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 30
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.6 Use Case Diagram
Feature 1: Registration
Figure 9: Registration System
Feature 2: Jewelry and Packaging Mockups
Figure 10: Jewelry and Packaging Mockups System
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 31
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Feature 3: Image to 3D
Figure 11: Image to 3D System
Feature 4: Customization
Figure 12: Customization System
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 32
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Feature 5: Virtual Try-On
Figure 13: Virtual Try-On System
Feature 6: Workspace
Figure 14: Workspace System
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 33
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Feature 7: Super Export
Figure 15: Super Export System
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 34
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.7 Software Development Life Cycle
Figure 16: Iterative Process
The iterative model is a software development life cycle (SDLC) approach in which initial
development work is carried out based on well-stated basic requirements, and successive
enhancements are added to this base piece of software through iterations until the final system is
built. We get a working piece of software very early in the lifecycle because the iterative model
begins with a simple execution of a small collection of software requirements, which iteratively
improves the evolving variants until the entire system is executed and ready to be redistributed.
Every Iterative model release is created over a certain and predetermined time period known as
iteration. Bugs and errors from the previous iteration do not propagate to the next iteration, and
this model is flexible enough to incorporate customer feedback in every iteration. [5]
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 35
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.8 Product Features
3.8.1 Feature #1 – Registration
Actor: User and Unregistered User
Description: The 3DJewelryCraft platform requires users to create an
account and sign in before accessing 3DJewelryCraft’s features. This
process is crucial as it allows the system to identify and provide a
personalized experience to each user.
Details:
1. Unregistered User can register for a new account to access the
3DJewelryCraft website.
2. User can log in to access their workspaces and customized jewelry.
3. User can log out at any time to ensure account security.
3.8.2 Feature #2 – Jewelry and Packaging Mockups
Actor: User and Unregistered User
Description:
Jewelry Mockup: A feature designed to help users get started in creating
jewelry more easily by presenting a variety of jewelry mockups, such as
necklaces, and bracelets. Users can select the model they are interested in
and continue customizing it immediately.
Packaging Mockup: Allows users to freely choose jewelry packaging by
offering a variety of packaging box mockups to choose from. Users can
choose the prototypes they are interested in.
Details:
1. Unregistered User can view the jewelry and packaging mockup that the
website provided from various mockup formats.
2. User can select the base mockup of jewelry and packaing that they are
interested in from various mockup formats and continue customizing it
immediately.
3.8.3 Feature #3 – Image to 3D
Actor: User
Description: A feature that helps transform the user's 2D jewelry drawings
or sketches into 3D models quickly and accurately, without having to draw
in a design program. Suitable for people who have ideas but are not
comfortable using 3D software.
Details:
1. User can upload 2D jewelry drawings immediately.
2. The system will convert the drawing into a 3D model.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 36
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3. User will get a 3D model that is the same as the designed drawing and
can rotate to view the model in 360 degrees.
3.8.4 Feature #4 – Customization
Actor: User
Description:
Jewelry Customization: A feature that allows users to design and customize
jewelry as desired, whether it's changing colors, choosing materials, or
adding shapes to the piece, including selecting specific points as desired, all
of which can be done on the 3D model in real time with an easy and friendly
experience.
Packaging Customization: The packaging can also be customized, such as
changing the color or adding text, and the jewelry can be placed in the
packaging that user have designed.
Details:
Jewelry Customization:
1. User can change the color of each element of the jewelry, such
as changing the color of the pendant and chain.
2. User can change the material of the jewelry as desired.
3. User can add shapes to the jewelry as desired.
4. User can crop the jewelry model to specific areas for recoloring.
Packaging Customization:
5. User can change the packaging color.
6. User can crop the packaging model to specific areas for
recoloring.
7. User can add text on the packaging.
8. User can place the jewelry model that they designed into the
box.
3.8.5 Feature #5 – Virtual Try-on
Actor: User
Description: A feature that allows users to try on jewelry on a 3D model of
a simulated body for a realistic look, allowing users to see exactly how their
jewelry will look on their body, whether it’s on their neck, or wrist.
Details:
1. User can choose their jewelry and try it on the simulated body model.
2. User can instantly see the jewelry they are trying on in a realistic way.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 37
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.8.6 Feature #6 – Workspace
Actor: User
Description: A personal space feature designed to allow users to store their
jewelry designs safely without worrying about losing them when closing
the program or logging out. Users can view the history of their tried jewelry
and packaging mockup selections.
Details:
1. User can view a gallery of all jewelry designs and packages they have
tried.
2. User can add new design.
3. User can share their designs with others.
3.8.7 Feature #7 – Super Export
Actor: User
Description: A feature that allows users to render and export their
customized 3D jewelry models in various formats and styles depending on
their desired usage, whether for manufacturing, showcasing, or sharing.
Users can choose to export their models as high-quality images, animated
videos, or shareable links.
Details:
1. User can export the model as a picture with:
• The image format (JPG or PNG).
2. User can export the model as a video with:
• The video format (MP4 or MOV).
• The animation duration (e.g.,4s, 8s).
3. User can copy a shareable link to their rendered model, enabling
easy distribution or collaboration.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 38
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.9 Quality Planning
State measurable Non-functional Requirement
3.9.1 Look and Feel
- Modern Design: The website uses a modern design approach,
emphasizing simplicity and ease of use. It also uses decorative graphic
elements to show creativity and communicate the design well, making users
feel that it is easily accessible.
- Color Scheme: The website mainly uses white, purple, and black to make
the website look modern and emphasizes the display of content or 3D design
clearly. Suitable for beginners to design for ease of use.
- Clarity and Focus: The design will prioritize clarity, with minimal
distractions, ensuring users can focus on the core functions of the website
without unnecessary visual noise.
- Responsive Layout: The website’s layout will be designed to maintain its
aesthetic and functionality across different devices and screen sizes,
ensuring a seamless user experience.
3.9.2 Cultural
- Language: Focus on using English as the primary language because it is
an internationally understood language and supports users from many
countries.
3.9.3 Political Legal
- User Consent Management: 100% of users must provide explicit consent
for data processing, consisting of reading the app's information and pressing
consent to create an account.
- Intellectual Property: Since users can create 3D jewelry designs and if
they have unique designs, clear information must be provided to users about
the copyright ownership of the work they create and 100% of users should
have consent.
- Data Security: Achieve a 100% success rate in annual security audits and
vulnerability assessments.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 39
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.9.4 Usability and Humanity
- 98% of new users can easily register for the app and complete the process
within 3 minutes for the first time.
- 98% of users can precisely customize jewelry and packages according to
their needs.
- 95% of users can use the user interface that is easy to use and comfortable
for new users, returning users, and experienced users.
- 95% of users can create and customize their own 3D designs without the
need for a design expert.
- 90% of users are satisfied with the user experience, feeling fun and
engaged in designing their jewelry.
3.9.5 Operational
- System Maintenance and Downtime: The system must provide 99.9%
uptime with scheduled maintenance not exceeding 2 hours per month.
- Backup and Recovery: The website must perform daily backups of all
data to ensure data recovery in case of system failure, with a maximum
recovery time of 1 hour and no more than 10 minutes of data loss.
- Scalability: The system must be scalable to support up to 1,000,000
simultaneous users without any decrease in performance. Automatic scaling
must be implemented to handle sudden spikes in user traffic, ensuring
smooth performance during peak usage times.
3.9.6 Performance
- Data Processing Speed: When users customize jewelry in 3D, the model
must be displayed immediately in real-time without any lag or delay.
- Big Data Management: The system should be able to handle big data,
such as storing user data, designing 3D jewelry, or storing user work history
efficiently.
- Appropriate display time: Web pages or screens should load within 3
seconds to load data or display when performing complex tasks.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 40
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.9.7 Security
- Data Privacy: 100 % of systems will protect user privacy and ensure that
applications meet legal security standards.
- Authorization: Each user should have access to the data or features
appropriate to their role. For example, a regular user cannot access another
user’s data.
- API Protection: Connections between internal and external systems
should be strictly protected, using techniques such as OAuth, API Key, or
JWT (JSON Web Token) to ensure that malicious users or systems cannot
access APIs.
- Registration: When a user registers, the system should send an OTP code
to the registered phone number within 5-10 seconds to verify the user's
identity.
3.10 Limits
- Quality of 3D models converted from 2D: Converting from 2D drawings to 3D
models has many technical limitations, especially in terms of deep details such as
multi-level surfaces, depth of cavities, or hidden areas in a 2D view.
- Precision of color cropping and recoloring: When user attempt to crop and
recolor specific sections of a jewelry model, especially on highly connected
surfaces, there is a risk of unintentionally affecting nearby parts. Fine-grained
isolation can be challenging without distinct model boundaries.
- Generation time varies by image complexity: The time it takes to generate the
3D model may increase significantly for complex or high-resolution images, as
more processing is required to analyze intricate details and textures.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 41
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.11 Schedule Plan and Milestones
3.11.1 Schedule Plan
3.11.1.1 Progress Report
- Normal Plan
Senior Project Event Deliverables
Proposal Presentation • Project proposal
Progress I Presentation • Software Requirement Specification
• Implement features 1, 2, 3
• Test features 1, 2, 3
• 1st Progress presentation
Progress II Presentation • Software Requirement Specification
• Design Documents
• Implement feature 4,5
• Test feature 4,5
• 2nd Progress presentation
Final Progress • Remaining documents
• Implement feature 6,7
• Test feature 6,7
• Final progress presentation
- Alternative Plan
Senior Project Event Deliverables
Proposal Presentation • Project Proposal
Progress I Presentation • Software Requirement Specification
• Implement features 1, 2, 3
• Test features 1, 2, 3
• 1st Progress presentation
Progress II Presentation • Software Requirement Specification
• Design Documents
• Implement feature 4, 5, 6,
• Test feature 4, 5, 6
• 2nd Progress presentation
Final Progress • Recheck Documents
• Implement feature 7
• Test feature 7
• Final progress presentaion
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 42
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.11.2 Milestones
Phase 1. Proposal: 1st April 2025 – 3rd May 2025 = 33 days
Phase 2. Progress I: 4th May 2025 – 18th July 2025 = 76 days
Phase 3. Progress II: 19th July 2025 – 30 th August 2025 = 43 days
Phase 4. Final Progress: 31st August 2025 – 17 th October 2025 = 48 day
Phase 1. Proposal: 1st April 2025 –3rd May 2025 = 33 days
Task Start Date End Date Duration0 Responsibility
Research Information 1st April 2025 4th April 2025 4 days NP1, NP2
Proposal Document 5th April 2025 22th April 2025 8 days NP1, NP2
Proposal Presentation 16th April 2025 19th April 2025 4 days NP1, NP2
Figure 17: Phase 1 Plan
Phase 2. Progress I: 4th May 2025 – 18th July 2025 = 76 days
Task Start Date End Date Duration Responsibility
Software Requitement 4th May 2025 6th May 2025 3 days NP1, NP2
Specification
Design Document 7th May 2025 10th May 2025 4 days NP1, NP2
Setup Frontend and 11st May 2025 17th May 2025 7 days NP1, NP2
Backend
Feature #1 18th May 2025 22nd May 2025 5 days NP1, NP2
Registration
Test Feature #1 23rd May 2025 24th May 2025 2 days NP1, NP2
Feature #3 25th May 2025 6th June 2025 13 days NP1, NP2
Image to 3D
Test Feature #3 7th June 2025 8th June 2025 2 days NP1, NP2
Feature #2 9th June 2025 4th July 2025 26 days NP1, NP2
Jewelry and Packaging
Mockups
Test Feature #2 5th July 2025 8th July 2025 4 days NP1, NP2
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 43
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Review and Fix all 9th July 2025 14th July 2025 6 days NP1, NP2
features
Develop Presentation II 15th July 2025 18th July 2025 4 days NP1, NP2
Figure 18: Phase 2 Plan
Phase 3. Progress II: 19th July 2025 – 30 th August 2025 = 43 days
Task Start Date End Date Duration0 Responsibility
Software Requitement 19th July 2025 21st July 2025 3 days NP1, NP2
Specification
Design Document 22nd July 2025 25th July 2025 4 days NP1, NP2
Feature #4 26th July 2025 9th Aug 2025 15 days NP1, NP2
Customization
Test Feature #4 10th Aug 2025 11th Aug 2025 2 days NP1, NP2
Feature #5 12th Aug 2025 18th Aug 2025 7 days NP1, NP2
Virtual Try-on
Test Feature #5 19th Aug 2025 20th Aug 2025 2 days NP1, NP2
Review and Fix all 21st Aug 2025 26th Aug 2025 6 days NP1, NP2
features
Develop Presentation III 27th Aug 2025 30th Aug 2025 4 days NP1, NP2
Figure 19: Phase 3 Plan
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 44
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Phase 4. Final Progress: 31st August 2025 – 17th October 2025 = 48 days
Task Start Date End Date Duration0 Responsibility
Software Requitement 31st Aug 2025 1st Sep 2025 2 days NP1, NP2
Specification
Design Document 2th Aug 2025 7th Sep 2025 6 days NP1, NP2
Feature #6 8th Aug 2025 17th Sep 2025 10 days NP1, NP2
Workspace
Test Feature #6 18th Sep 2025 19th Sep 2025 2 days NP1, NP2
Feature #7 20th Sep 2025 24th Sep 2025 5 days NP1, NP2
Super Export
Test Feature #7 25th Sep 2025 26th Sep 2025 2 days NP1, NP2
Review and Fix all 27st Sep 2025 9th Oct 2025 13 days NP1, NP2
features
Recheck Document 10st Oct 2025 12th Oct 2025 3 days NP1, NP2
Software Requirement 13st Oct 2025 17th Oct 2025 5 days NP1, NP2
Specification
Figure 20: Phase 4 Plan
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 45
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter Four | Quality Standard

## 4.1 ISO 9001

ISO 9001 the internationally recognized standard for quality management systems (QMS),
providing a framework for organizations to establish, implement, maintain, and continually
improve their QMS to consistently meet customer and regulatory requirements. [6]
ISO 9001 is a quality management standard that is suitable for businesses that want to make
the 3D modeling process easy, accurate, and efficient. It provides a good management system for
quality control, can adjust internal processes to make the tools developed simple and most
efficient, and can reduce the risk of production or design not meeting customer expectations.
3.1.1 Project Management Process
The purpose of the Project Management process is to establish and carry out in a
systematic way the tasks of the software implementation project, which allows complying
with the project’s objectives in the expected quality, time, and cost. There are four activities
as following:
Selected Activity:
1. Project Planning Process
2. Project Plan Execution Process
3. Project Assesment and Control Process
4. Project Closure Process
3.1.2 Software Implementation Process
The purpose of the Software Implementation process is the systematic performance
of the analysis, design, construction, integration, and test activities for new or modified
software products according to the specified requirements. There are six activities as
following:
Selected Activity:
1. Software Implementation Initiation
2. Software Requirements Analysis
3. Software Architectural and Detailed Design
4. Software Construction
5. Software Integration and Test
6. Software Delivery
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 46
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter Five | References
[1] A. Shahn, "Unleashing The Power Of AI: A Paradigm Shift In The Jewelry Industry,"
Forbes Business Council, 2 August 2023. [Online]. Available:
https://www.forbes.com/councils/forbesbusinesscouncil/2023/08/02/unleashing-the-power-
o f-ai-a-paradigm-shift-in-the-jewelry-industry/.
[2] R. Butler, "AI and automation: Transforming jewellery retail in 2025," 4 February 2025.
[Online]. Available: https://www.professionaljeweller.com/ai-and-automation-transforming-
j ewellery-retail-in-2025/.
[3] B . Simon, "Raycaster," [Online]. Available: https://threejs.org/docs/#api/en/core/Raycaster.
[4] "Amazon EC2," Amazon Web Services, Inc., 2024. [Online]. Available:
h ttps://aws.amazon.com/th/ec2/.
[5] S. Kumar, "SDLC - Iterative Model," InterviewBit Technologies Pvt. Ltd. , 22 May 2023.
[Online]. Available: https://www.scaler.com/topics/software-engineering/iterative-model-in-
s oftware-engineering/.
[6] " ISO 9001:2015," [Online]. Available: https://www.iso.org/standard/62085.html.
[7] A. Shah, "Unleashing The Power Of AI: A Paradigm Shift In The Jewelry Industry," 2
August 2023. [Online]. Available:
https://www.forbes.com/councils/forbesbusinesscouncil/2023/08/02/unleashing-the-power-
of-ai-a-paradigm-shift-in-the-jewelry-industry/.
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 47
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter Six | Appendix
6.1 Prototype
Prototype Link
Figure 21: Prototype
Document 3DJewelryCraft_Proposal_V.1.8 Owner NP1, NP2 Page 48
Name
Document Project Proposal Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 2
Project Management Plan

---

Document History
Document Version History Status Date Editable Reviewer
Name
3DJewelryCraft_ 3DJewelryCraft_ Add Chapter 1 Draft 09/06/2025 NP1, SW
Project_Manage Project_Manage Add Chapter 2 NP2
ment_Plan_V.0.1 ment_Plan_V.0.1 Add Chapter 3
Add Chapter 4
Add Chapter 5
Add Chapter 6
Add Chapter 7
Add Chapter 8
Add Chapter 9
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 09/06/2025 NP1, SW
Project_Manage Project_Manage Update Chapter 2 NP2
ment_Plan_V.0.2 ment_Plan_V.0.2 Update Chapter 3
Update Chapter 4
Update Chapter 5
Update Chapter 6
Update Chapter 7
Update Chapter 8
Update Chapter 9
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 30/08/2025 NP1, SW
Project_Manage Project_Manage Update Chapter 2 NP2
ment_Plan_V.0.3 ment_Plan_V.0.3 Update Chapter 3
Update Chapter 4
Update Chapter 5
Update Chapter 6
Update Chapter 7
Update Chapter 8
Update Chapter 9
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 7 Final 18/10/2025 NP1, SW
Project_Manage Project_Manage NP2
ment_Plan_V.0.3 ment_Plan_V.0.3
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 50
Name Management_Plan_V.0.3
Document Project Management Release 20/10/2025 Print 20/10/2025
Type Plan Date Date

---


## TABLE OF CONTENTS

Document History ....................................................................................................................... 50
TABLE OF CONTENTS ........................................................................................................... 51
TABLE OF FIGURES ................................................................................................................ 53
Chapter 1 | Introduction ............................................................................................................. 54
1.1) Project Overview ............................................................................................................. 54
1.2) Purpose and Scope ........................................................................................................... 55
1.2.1) Purpose ...................................................................................................................... 55
1.2.2) Scope .......................................................................................................................... 55
1.3) Project Deliverables ......................................................................................................... 55
1.4) Acronyms and Definitions............................................................................................... 56
1.4.1) Acronyms ................................................................................................................... 56
1.4.2) Definitions.................................................................................................................. 56
1.4.3) Application Usage Definitions ................................................................................. 58
Chapter 2 | Infrastructure .......................................................................................................... 59
2.1) Development Tools .......................................................................................................... 59
2.2) Design Tools ..................................................................................................................... 59
2.3) Document Tools ............................................................................................................... 59
2.4) Hardware and Materials Resources .............................................................................. 59
Chapter 3 | Management Procedures ........................................................................................ 60
3.1) Project Team Structure................................................................................................... 60
3.2) Monitoring and Controlling Mechanisms ..................................................................... 61
3.2.1) Project Meeting ......................................................................................................... 61
3.2.2) Software Development Life Cycle ........................................................................... 61
3.2.3) Features ..................................................................................................................... 62
3.2.3.1) Feature #1 – Registration ......................................................................................... 62
3.2.3.2) Feature #2 – Jewelry and Packaging Mockups ....................................................... 62
3.2.3.3) Feature #3 – Image to 3D ........................................................................................ 62
3.2.3.4) Feature #4 – Customization ..................................................................................... 63
3.2.3.5) Feature #5 – Virtual Try-on ..................................................................................... 63
3.2.3.6) Feature #6 – Workspace .......................................................................................... 64
3.2.3.7) Feature #7 – Super Export ....................................................................................... 64

---

Chapter 4 | Quality Standard..................................................................................................... 65
4.1) ISO 9001 ........................................................................................................................... 65
4.1.1) Project Management Process .................................................................................. 65
4.1.2) Software Implementation Process ........................................................................... 65
Chapter 5 | Quality Planning ..................................................................................................... 66
5.1) Reviews / Responsibilities ............................................................................................... 66
5.2) Testing............................................................................................................................... 66
Chapter 6 | Schedule and Milestones ........................................................................................ 67
6.1) Proposal ............................................................................................................................ 67
6.2) Progress I .......................................................................................................................... 67
6.3) Progress II ........................................................................................................................ 67
Chapter 7 | Software Configuration Management .................................................................. 69
7.1) Naming Convention ......................................................................................................... 69
7.2) Change Management ....................................................................................................... 69
7.3) Project Repository ........................................................................................................... 70
7.4) Software Configuration Item Table ............................................................................... 71
Chapter 8 | Risk Management ................................................................................................... 72
Chapter 9 | Reference ................................................................................................................. 73

---


## TABLE OF FIGURES

Figure 22: Iterative Model ............................................................................................................ 61
Figure 23: Proposal ....................................................................................................................... 67
Figure 24: Progress I ..................................................................................................................... 67
Figure 25: Progress II.................................................................................................................... 67
Figure 26: Final Progress .............................................................................................................. 68

---

Chapter 1 | Introduction
1.1) Project Overview
3DJewelryCraft is revolutionizing the custom jewelry design experience by
offering a platform that streamlines the traditionally complex process of creating 3D
jewelry. In a world where personalization and speed are increasingly important, especially
for aspiring entrepreneurs without access to professional design tools, turning creative
ideas into high-quality, tangible 3D models can be a significant challenge. Traditional tools
demand specialized skills, time-consuming manual work, and long production cycles.
3DJewelryCraft overcomes these obstacles with an intuitive, automated 3D model platform
designed specifically for both starter jewelry entrepreneurs and individuals seeking
creative self-expression.
3DJewelryCraft empowers users to upload a 2D sketch or image, which is then
converted into a 3D model through advanced 3D modeling AI API technologies. Moreover,
users can customize the jewelry mockup in real time, try it virtually using a Virtual Try-
On feature, and save or share their designs with others. The platform supports designing
necklaces and bracelets with accuracy and realism.
In progress I, focus on Feature#1 Registration for the user can create secure
accounts, log in to access their workspace, and log out to ensure account security. Then
implement Feature#3 Image to 3D, which allows the user to upload a 2D jewelry sketch or
image for automatic conversion into 3D models. The phase concludes with
Feature #2 Jewelry and Packaging Mockups, where the user can browse a variety of jewelry
and packaging mockups to help visualize and select a base design for further customization.
In progress II, focus on Feature#4 Customization, where users can personalize
jewelry and packaging through an intuitive real-time editor. This includes changing colors,
selecting materials, cropping specific areas, and even inserting jewelry into custom
packaging boxes. Simultaneously, Feature #5: Virtual Try-On, enabling users to preview
how their jewelry will look on a simulated 3D model of the body.
In the final progress, focus on implementing Feature#6 Workspace gives the user a
personal area to store and view all of their jewelry designs, with the option to add new
items or share them with others. Then implement Feature#7 Super Export, which provides
tools to export 3D models as high-quality images (JPG/PNG), PDF reports, or 3D files

## (STL/OBJ/GLB).

Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 54
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

1.2) Purpose and Scope
1.2.1) Purpose
The purpose of the Project Plan document is to plan, schedule activities, and
evaluate the overall progress of the 3DJewelryCraft project so that it can be completed
successfully despite all the risks. It provides detailed schedules, assigned tasks, and
identified risks of the 3DJewelryCraft project.
1.2.2) Scope
• Provide estimated timelines for each phase of development.
• Specify responsibilities for each developer.
• Identify potential risks that may arise throughout the development process.
• Specify the tools that are used for development.
• Define the key deliverables expected at the end of each development
phase.
1.3) Project Deliverables
No. Deliverable/Release Media Copies Date
1 Project Proposal Document 1 18/05/2025
2 Progress I Report
• Project Plan
• Software
Requirement
Specification
• Software Design Document 1 28/06/2025
Document
• Test Plan
• Test Record
• Traceability Record
• Executive Summary
Software Version V.0.1 Source Code
3 Progress II Report
Document 1 04/09/2025
• Project Plan
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 55
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

• Software
Requirement
Specification
• Software Design
Document
• Test Plan
• Test Record
• Traceability Record
• Executive Summary
Software Version V.0.1 Source Code
1.4) Acronyms and Definitions
1.4.1) Acronyms
UI User Interface
URS User Requirement Specification
SDD Software Design Document
SRS Software Requirements Specification
UTC Unit Test Case
STC System Test Case
1.4.2) Definitions
Name Definition
The application of knowledge, skills,
tools, and techniques to project activities
Project Management to meet or exceed stakeholder needs and
expectations from a project.
A documented series of tasks requires
meeting an objective, typically including
the associated schedule, budget, resources,
Plan organizational description, and work
breakdown structure.
A formal, approved document used to
guide both project execution and project
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 56
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

control. The primary uses of the project
plan are to document planning
Project Plan assumptions and the decision, to facilitate
communication among stakeholders, and
to document approved scope, cost, and
schedule baseline.
Feature Transformation of input
parameters to output parameters based on
Feature a specified algorithm. It describes the
functionality of the product in the
language of the product. Used for
requirements analysis, design, coding,
testing or maintenance.
Institute for Electrical and Electronics
Engineers. Biggest global interest group
for engineers of different branches and

## IEEE

computer scientists.
1) The combination of the probability of
an event and its consequence (ISO 16085).
Note 1: The term “risk” is generally used
only when there is at least the possibility
of negative consequences. Note 2: In some
Risk situations, risk arises from the possibility
of deviation from the expected outcome or
event. 2) An uncertain event or condition
that, if it occurs, has a positive or negative
effect on one or more project objectives
(PMBOK® Guide)
The systematic application of
management policies, procedures, and
Risk Management practices to the tasks of identifying,
analyzing, evaluating, treating, and
monitoring risk.
Testing conducted on a complete and
integrated system for evaluate the
System Testing system’s compliance with its specified
requirements.
1) Testing of individual routines and
modules by the developer or an
Unit Testing
independent tester.
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 57
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2) A test of individual programs or
modules to ensure that there are no
analysis or programming errors (ISO/IEC
2382-20).
3) Test of individual hardware or software
units or groups of related units (ISO
24765).
1) The degree to which a relationship can
be established between two or more
products of the development process,
especially products having a predecessor-
successor or master subordinate
relationship to one another (ISO 24765).
Example: the degree to which the
requirements and design of a given system
Traceability element match; the degree to which each
element in a bubble chart references the
requirement that it satisfies. 2) A
discernable association among two or
more logical entities such as requirements,
system elements, verifications, or tasks.
(See also “bidirectional traceability” and
“requirements traceability.”) (CMMI-

## DEV).

1.4.3) Application Usage Definitions
Name Definition
The people who are not registered to the
system. These users can only browse and
Unregistered User preview mockups available on the
platform. They typically include curious
creatives who are exploring the idea of
designing custom jewelry.
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 58
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The people who have already registered
and logged in to the web application.
Registered User These users range from beginner jewelry
entrepreneurs looking to launch a brand
with minimal technical skills, to self-
expressive, trend-conscious individuals
who value aesthetic freedom without
needing a full design team.
The people who interact with the
User 3DJewelryCraft system. This can include
both unregistered and registered user.
Chapter 2 | Infrastructure
2.1) Development Tools
• Python (3.12.7)
• Pycharm (2024.2.4)
• VScode (1.84.2)
• MySQL (8.0.41)
• Docker Desktop (4.37.2)
2.2) Design Tools
• Figma
• Draw.io
2.3) Document Tools
• Microsoft Word
• OneDrive
2.4) Hardware and Materials Resources
• Lenovo IdeaPad 3i 15IAU7
o Processor: 12th Gen Intel(R) Core(TM) i5-1235U 1.30 GHz
o RAM: 16GB
o Operating System: Windows 11 Home Single Language
• MacBook Air M1 (13.3 inch - 2020)
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 59
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

o Processor: Apple M1 chip with 8-core CPU (4 performance cores and 4
efficiency cores), 8GB unified memory
o RAM: 8GB LPDDR4
o Operating System: macOS
Chapter 3 | Management Procedures
3.1) Project Team Structure
No. Participants Roles Responsibilities
1. Nichakorn Prompong - UI Designer Document
- Project Manager • Project Proposal
- System Analysis • Project Plan
- Tester • Software Design
- Lead Programmer
• Software
2. Nonlanee Panjateerawit - UI Designer Requirement
- Project Manager Specification
- System Analysis
• Test Plan
- Tester
• Test Record
- Lead Programmer
• Traceability Record
Development
• Frontend
• Backend
Testing
• Unit Test
• System Test
3. Dr. Siraprapa Wattanakul Project Advisor Review and Approve
• Document
• Change Request
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 60
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.2) Monitoring and Controlling Mechanisms
3.2.1) Project Meeting
Participants Roles
Nichakorn Prompong Development Team Member
Nonlanee Panjateerawit Development Team Member
Dr. Siraprapa Wattanakul Project Advisor
3.2.2) Software Development Life Cycle
Figure 22: Iterative Model
The iterative model is a software development life cycle (SDLC) approach in which initial
development work is carried out based on well-stated basic requirements, and successive
enhancements are added to this base piece of software through iterations until the final system is
built. We get a working piece of software very early in the lifecycle because the iterative model
begins with a simple execution of a small collection of software requirements, which iteratively
improves the evolving variants until the entire system is executed and ready to be redistributed.
Every Iterative model release is created over a certain and predetermined time period known as
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 61
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

iteration. Bugs and errors from the previous iteration do not propagate to the next iteration, and
this model is flexible enough to incorporate customer feedback in every iteration. [1]
3.2.3) Features
3.2.3.1) Feature #1 – Registration
Actor: User (Unregistered user and Registered user)
Description: The 3DJewelryCraft platform requires user to create an
account and sign in before accessing 3DJewelryCraft’s features. This
process is crucial as it allows the system to identify and provide a
personalized experience to each user.
Details:
1. Unregistered User can register for a new account to access the
3DJewelryCraft website.
2. Registered user can log in to access their workspaces and customized
jewelry.
3. Registered user can log out at any time to ensure account security.
3.2.3.2) Feature #2 – Jewelry and Packaging Mockups
Actor: User (Unregistered user and Registered user)
Description:
• Jewelry Mockup: A feature designed to help user get started in
creating jewelry more easily by presenting a variety of jewelry
mockups, such as necklaces and bracelets. The user can select the
model they are interested in and continue customizing it
immediately.
• Packaging Mockup: Allows user to freely choose jewelry packaging
by offering a variety of packaging box mockups to choose from.
User can choose the prototypes they are interested in.
Details:
1. Unregistered user can view the jewelry and packaging mockup that the
website provided from various mockup formats.
2. Registered user can select the base mockup of jewelry and packaing that
they are interested in from various mockup formats and continue
customizing it immediately.
3.2.3.3) Feature #3 – Image to 3D
Actor: Registered user
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 62
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Description: A feature that helps transform the user's 2D jewelry drawings
or sketches into 3D models quickly and accurately, without having to draw
in a design program. Suitable for people who have ideas but are not
comfortable using 3D software.
Details:
1. Registered user can upload 2D jewelry drawings immediately.
2. The system will convert the drawing into a 3D model.
3. Registered user will get a 3D model that is the same as the designed
drawing and can rotate to view the model in 360 degrees.
3.2.3.4) Feature #4 – Customization
Actor: Registered user
Description:
Jewelry Customization: A feature that allows user to design and customize
jewelry as desired, whether it's changing colors or materials, including
selecting specific points as desired, all of which can be done on the 3D
model in real time with an easy and friendly experience.
Packaging Customization: The packaging can also be customized, such as
changing the color or adding text, and the jewelry can be placed in the
packaging that user have designed.
Details:
Jewelry Customization:
1. Registered user can change the color of the jewelry as desired.
2. Registered user can change the material of the jewelry as desired.
3. Registered user can crop the jewelry model to specific areas for
changing the color or material.
Packaging Customization:
4. Registered user can change the packaging color.
5. Registered user can add the engraving text on the packaging.
6. Registered user can place the jewelry model that they designed into the
box.
3.2.3.5) Feature #5 – Virtual Try-on
Actor: Registered user
Description: A feature that allows user to try on jewelry on a 3D model of
a simulated body for a realistic look, allowing user to see exactly how their
jewelry will look on their body, whether it’s on their neck, or wrist.
Details:
1. Registered user can choose their jewelry and try it on the simulated body
model.
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 63
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2. Registered user can instantly see the jewelry they are trying on in a
realistic way.
3.2.3.6) Feature #6 – Workspace
Actor: Registered user
Description: A personal space feature designed to allow user to store their
jewelry designs safely without worrying about losing them when closing
the program or logging out. User can view the history of their tried jewelry
and packaging mockup selections.
Details:
1. Registered user can view a gallery of all jewelry designs and packages
they have tried.
2. Registered user can add new design.
3. Registered user can share their designs with others.
3.2.3.7) Feature #7 – Super Export
Actor: Registerd user
Description: A feature that allows user to render and export their
customized 3D jewelry models in various formats and styles depending on
their desired usage, whether for manufacturing, showcasing, or sharing.
User can choose to export their models as high-quality images, a PDF
report, or export as a 3D file.
Details:
1. Registerd user can export the model as a picture with:
• The image format (JPG and PNG).
2. Registerd user can export the information of the model as PDF report
3. Registerd user can export the model as a 3D file with:
• The 3D model format (STL, OBJ, and GLB).
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 64
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 4 | Quality Standard

## 4.1) ISO 9001

ISO 9001 is the internationally recognized standard for quality management
systems (QMS), providing a framework for organizations to establish, implement,
maintain, and continually improve their QMS to consistently meet customer and regulatory
requirements. [2]
ISO 9001 is a quality management standard that is suitable for businesses that want
to make the 3D modeling process easy, accurate, and efficient. It provides a good
management system for quality control, can adjust internal processes to make the tools
developed simple and most efficient, and can reduce the risk of production or design not
meeting customer expectations.
4.1.1) Project Management Process
The purpose of the project management process is to establish and carry out in a
systematic way the tasks of the software implementation project, which allows complying
with the project’s objectives in the expected quality, time, and cost. There are four activities
as follows:
Selected Activity:
1. Project Planning Process
2. Project Plan Execution Process
3. Project Assessment and Control Process
4. Project Closure Process
4.1.2) Software Implementation Process
The purpose of the software implementation process is the systematic performance
of the analysis, design, construction, integration, and test activities for new or modified
software products according to the specified requirements. There are six activities as
follows:
Selected Activity:
1. Software Implementation Initiation
2. Software Requirements Analysis
3. Software Architectural and Detailed Design
4. Software Construction
5. Software Integration and Test
6. Software Delivery
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 65
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 5 | Quality Planning
5.1) Reviews / Responsibilities
No. Stage Review Item Responsibility
1. Business Analysis Project Proposal NP1, NP2, SW
2. Project Planning Project Plan NP1, NP2, SW
Requirement Analysis and
3. Specification Software Requirement Specification NP1, NP2, SW
Architecture and Detailed
4. Design Software Design Document NP1, NP2, SW
5. Software Implementation Source Code NP1, NP2, SW
Unit Testing and Software
6. Testing Test Plan, Test Record NP1, NP2, SW
Project Monitoring and
7. Control Traceability Record NP1, NP2, SW
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
5.2) Testing
No. Test Responsibility
1. Unit Test NP1, NP2
2. System Test NP1, NP2
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 66
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 6 | Schedule and Milestones
6.1) Proposal
Figure 23: Proposal
6.2) Progress I
Figure 24: Progress I
6.3) Progress II
Figure 25: Progress II
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 67
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

6.4) Final Progress
Figure 26: Final Progress
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 68
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 7 | Software Configuration Management
7.1) Naming Convention
• The file name format that we are using for all documents is
3DJewelryCraft_[File Name]_V.[Version].(File Type)
• File Name: The name of each process phase.
• Version: This part is the version of the file. The version number will be in this
format "(Main version).[Subversion]"
• File Type - The type of the file format for example .docx or .pdf.
7.2) Change Management
Change management manages all the changes in the project during the development
process. All the change requests will be recorded in the change record document.
The procedures for managing changes are:
1. Discuss with the advisor about the change.
2. Record the change information in the change document.
3. Send the change request to the advisor.
3.1 Request accepted: change the document and software to follow the change
information.
3.2 Request rejected: continue and find an alternative solution.
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 69
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

7.3) Project Repository
Figure 27: 3DJewelryCraft Repository Diagram
- OneDrive: For Document Management
- GitHub: For Source Code Management. This project uses GitHub as the following purpose:
• This project uses GitHub to manage the version of the software. The reason is for storing
and sharing source code for developing software projects. The GitHub repository of this
project is named 3DjewelryCraft-project. It is used for implementing the code of the entire
system for the application. The branches of the project will be as follow models:
o Main Branch: This branche is the main of the project. Once the Develop Branch
reaches a stable point and is ready to be released, all the changes should be merged
back into the Main Branch.
o Develop Branch: This branch is for developing the project, which has supporting
branches as follows:
▪ Connect-backend Branch: This branch is branched off from the Develop
Branch. It is intended to integrate the back-end with the front-end.
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 70
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

7.4) Software Configuration Item Table
File Baseline
No. Item File Name
Type Version
1. Project Proposal 3DJewelryCraft_Proposal_V.1.8 .pdf 1.8
2. Project 3DJewelryCraft_Project_Management_ .pdf 0.4
Management Plan Plan_V.0.4
3. Software 3DJewelryCraft_Software_Requirement_ .pdf 1.0
Requirement Specification_V.1.0
Specification
4. Software Design 3DJewelryCraft_Software_Design_ .pdf 1.0
Document Document_V.1.0
5. Test Plan 3DJewelryCraft_Test_Plan_V.0.9 .pdf 0.9
6. Test Record 3DJewelryCraft_Test_Record_V.0.6 .pdf 0.6
7. Traceability 3DJewelryCraft_Traceability_Record_ .pdf 0.4
Record V.0.4
8. Change Request 3DJewelryCraft_Change_Request_V.0.2 .pdf 0.2
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 71
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 8 | Risk Management
8.1) Risk Identification and Solution
No. Risk Statement Solution
The development process might not keep - The development process might not
1. up with the project schedule. keep up with the project schedule.
The requirements might change. - Make a change request and discuss with
2. the project advisor to reprioritize the
change requirement.
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 72
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 9 | Reference
[1] S. Kumar, "SDLC - Iterative Model," InterviewBit Technologies Pvt. Ltd. , 22 May 2023.
[Online]. Available: https://www.scaler.com/topics/software-engineering/iterative-model-in-
software-engineering/.
[2] " ISO 9001:2015," [Online]. Available: https://www.iso.org/standard/62085.html.
Document 3DJewelryCraft_Project_ Owner NP1, NP2 Page 73
Name Management_Plan_V.0.3
Document Project Management Plan Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 3
Software Requirement Specification

---

Document History
Document Version History Status Date Editable Reviewer
Name
3DJewelryCraft_ 3DJewelryCraft_ Add Chapter 1 Draft 05/05/2025 NP1, NP2 SW
Software_ Software_ Add Chapter 2
Requirement_ Requirement
Specification _Specification

## _V.0.1 _V.0.1

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 2 Draft 05/05/2025 NP1, NP2 SW
Software_ Software_
Requirement_ Requirement_
Specification Specification

## _V.0.2 _V.0.2

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 06/05/2025 NP1, NP2 SW
Software_ Software_ Update Chapter 2
Requirement_ Requirement_
Specification Specification

## _V.0.3 _V.0.3

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 2 Draft 20/05/2025 NP1, NP2 SW
Software_ Software_
Requirement_ Requirement_
Specification Specification

## _V.0.4 _V.0.4

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 24/05/2025 NP1, NP2 SW
Software_ Software_ Update Chapter 2
Requirement_ Requirement_
Specification Specification

## _V.0.5 _V.0.5

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 10/06/2025 NP1, NP2 SW
Software_ Software_ Update Chapter 2
Requirement_ Requirement_
Specification Specification

## _V.0.6 _V.0.6

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 2 Draft 05/08/2025 NP1, NP2 SW
Software_ Software_
Requirement_ Requirement_
Specification Specification

## _V.0.7 _V.0.7

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 28/08/2025 NP1, NP2 SW
Document 3DJewelryCraft_ Owner NP1, NP2 Page 75
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Software_ Software_ Update Chapter 2
Requirement_ Requirement_
Specification Specification

## _V.0.8 _V.0.8

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 30/08/2025 NP1, NP2 SW
Software_ Software_ Update Chapter 2
Requirement_ Requirement_
Specification Specification

## _V.0.9 _V.0.9

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Final 18/10/2025 NP1, NP2 SW
Software_ Software_ Update Chapter 2
Requirement_ Requirement_
Specification Specification

## _V.0.10 _V.1.0

*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_ Owner NP1, NP2 Page 76
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---


## TABLE OF CONTENTS

Document History ....................................................................................................................... 75
TABLE OF CONTENTS ........................................................................................................... 77
LIST OF FIGURES .................................................................................................................... 82
Chapter One | Introduction........................................................................................................ 84
1.1) Purpose ............................................................................................................................. 84
1.2) Scope ................................................................................................................................. 84
1.3) User Characteristic .......................................................................................................... 84
1.4) Acronyms and Definitions............................................................................................... 85
1.4.1) Acronyms ................................................................................................................... 85
1.4.2) Definitions.................................................................................................................. 85
Chapter Two | Specific Requirements....................................................................................... 88
2.1) Use Case Diagram ............................................................................................................ 88
2.2) Use Case Description and Activity Diagram ................................................................. 96
2.2.1) UC-01: Register......................................................................................................... 96
2.2.2) UC-02: Log in .......................................................................................................... 100
2.2.3) UC-03: Log out........................................................................................................ 103
2.2.4) UC-04: View all of the jewelry mockups .............................................................. 105
2.2.5) UC-05: View all of the packaging mockups ......................................................... 107
2.2.6) UC-06: View the jewelry mockups by category ................................................... 109
2.2.7) UC-07: View the packaging mockups by category .............................................. 111
2.2.8) UC-08: Use the predefined jewelry mockup to customize .................................. 113
2.2.9) UC-09: Use the predefined packaging mockup to customize ............................. 115
2.2.10) UC-10: Upload an image to convert to 3D ......................................................... 117
2.2.11) UC-11: Create the name of the design ................................................................ 120
2.2.12) UC-12: Delete the uploaded image ...................................................................... 123
2.2.13) UC-13: Select the jewelry model to customize ................................................... 125
2.2.14) UC-14: Use the converted image to 3d model to customize .............................. 127
2.2.15) UC-15: View the jewelry model ........................................................................... 130
2.2.16) UC-16: Customize the jewelry model ................................................................. 132
2.2.17) UC-17: Customize the name of the jewelry model ............................................ 134

---

2.2.18) UC-18: Customize the color of the jewelry model ............................................. 137
2.2.19) UC-19: Customize the material of the jewelry model ....................................... 140
2.2.20) UC-20: Customize the size of the jewelry model ............................................... 143
2.2.21) UC-21: Customize the color of specific jewelry sections ................................... 146
2.2.22) UC-22: Customize the material of specific jewelry sections ............................. 150
2.2.23) UC-23: Zoom in and zoom out the jewelry model ............................................. 154
2.2.24) UC-24: View the packaging model ...................................................................... 157
2.2.25) UC-25: Customize the packaging model ............................................................ 159
2.2.26) UC-26: Customize the color of the packaging model ........................................ 162
2.2.27) UC-27: Add engraved text to the packaging model .......................................... 165
2.2.28) UC-28: Replace with a new packaging model .................................................... 169
2.2.29) UC-29: Choose the jewelry to try on with packaging........................................ 172
2.2.30) UC-30: Zoom in and zoom out the packaging model ........................................ 176
2.2.31) UC-31: Select the type of simulated body to try on ........................................... 179
2.2.32) UC-32: View the jewelry on the simulated body ............................................... 182
2.2.33) UC-33: View all previously designed work ........................................................ 186
2.2.34) UC-34: Create a new design ................................................................................ 189
2.2.35) UC-35: Save the designed work ........................................................................... 191
2.2.36) UC-36: Save the designed work from the predefined jewelry mockup ........... 194
2.2.37) UC-37: Save the designed work from the converted image to 3d model ......... 197
2.2.38) UC-38: Save the designed work from the predefined packaging mockup ...... 199
2.2.39) UC-39: Export the model as image ..................................................................... 202
2.2.40) UC-40: Export image as PNG format ................................................................. 205
2.2.41) UC-41: Export image as JPG format .................................................................. 208
2.2.42) UC-42: Export the model as PDF report ............................................................ 211
2.2.43) UC-43: Export the model as 3D file .................................................................... 214
2.2.44) UC-44: Export 3D file as STL format ................................................................. 217
2.2.45) UC-45: Export 3D file as OBJ format ................................................................ 220
2.2.46) UC-46: Export 3D file as GLB format ................................................................ 223
2.3) User Requirement Specification ................................................................................... 226
2.3.1) Feature #1: Registration ........................................................................................ 226
2.3.2) Feature #2: Jewelry and Packaging Mockups ..................................................... 226
2.3.3) Feature #3: Image to 3D ......................................................................................... 226
2.3.4) Feature #4: Customization ..................................................................................... 226

---

2.3.5) Feature #5: Virtual Try-On ................................................................................... 227
2.3.6) Feature #6: Workspace .......................................................................................... 228
2.3.7) Feature #7: Super Export ...................................................................................... 228
2.4) System Requirement Specification............................................................................... 229
2.4.1) URS-01: The unregistered user can register to the system. ................................ 229
2.4.2) URS-02: The registered user can log in to the system. ........................................ 229
2.4.3) URS-03: The registered user can log out from the system. ................................ 230
2.4.4) URS-04: The user can view all of the jewelry mockups in the system. .............. 230
2.4.5) URS-05: The user can view all of the packaging mockups in the system. ......... 230
2.4.6) URS-06: The user can view the jewelry mockups by category. ......................... 230
2.4.7) URS-07: The user can view packaging mockups by category. ........................... 231
2.4.8) URS-08: Registered user can use the predefined jewelry mockup to customize by
clicking the ‘Custom’ button............................................................................................ 231
2.4.9) URS-09: Registered user can use the predefined packaging mockup to customize
by clicking the ‘Custom’ button. ..................................................................................... 231
2.4.10) URS-10: The user can upload an image (JPG, JPEG or PNG) by clicking,
dragging, and dropping the image into the upload area to convert the image into a 3D
model. ................................................................................................................................. 231
2.4.11) URS-11: The registered user can create the name of their design. .................. 232
2.4.12) URS-12: The registered user can delete the currently uploaded image to upload
a new one before generating the 3D model. .................................................................... 232
2.4.13) URS-13: The registered user can select the jewelry model to customize. ....... 232
2.4.14) URS-14: The registered user can use the converted image to 3d model to
customize by clicking the ‘Custom’ button in the navigation sidebar after the model is
converted successfully. ...................................................................................................... 233
2.4.15) URS-15: The registered user can view the selected jewelry model in the model
viewer. ................................................................................................................................ 233
2.4.16) URS-16: The registered user can customize the jewelry model, including color,
material, and size clicking the “Custom” button in the navigation sidebar. ............... 233
2.4.17) URS-17: The registered user can customize the name of the jewelry model to a
new desired name. ............................................................................................................. 233
2.4.18) URS-18: Registered user can customize the color of the jewelry model and can
preview the color changes in real-time. ........................................................................... 234
2.4.19) URS-19: The registered user can customize the material of the jewelry model
and can preview the material changes in real-time. ...................................................... 234
2.4.20) URS-20: The registered user can customize the size of the jewelry model and
can preview the size changes in real-time. ...................................................................... 234

---

2.4.21) URS-21: The registered user can customize the color of specific parts of a
jewelry model by cropping the part that they want....................................................... 234
2.4.22) URS-22: The registered user can customize the material of specific parts of a
jewelry model by cropping the part that they want....................................................... 235
2.4.23) URS-23: The registered user can zoom in and zoom out of the jewelry model to
closely examine design details or view the entire piece more clearly. .......................... 235
2.4.24) URS-24: The registered user can view the selected packaging model in the
model viewer. ..................................................................................................................... 236
2.4.25) URS-25: The registered user can customize the packaging model, including
changing the color and adding engraved text from the navigation sidebar. ............... 236
2.4.26) URS-26: The registered user can change the color of the packaging model by
selecting a color from a system-provided palette, entering a hex color code, or choosing
a custom color from the color picker tool. The selected color is applied in real-time to
the packaging preview. ..................................................................................................... 236
2.4.27) URS-27: The registered user can add engraved text to the selected packaging
model includes entering the text, choosing font style, font size, and dragging the text to
the desired position. .......................................................................................................... 237
2.4.28) URS-28: The registered user can select and apply a new packaging model to
replace an existing one. ..................................................................................................... 237
2.4.29) URS-29: The registered user can choose the saved jewelry from their
workspace to try on with the selected packaging model. .............................................. 237
2.4.30) URS-30: The registered user can zoom in and zoom out of the packaging model
to closely examine design details or view the entire piece more clearly. ...................... 238
2.4.31) URS-31: The registered user can select the type of selected body on which the
jewelry will be virtually tried-on. .................................................................................... 238
2.4.32) URS-32: The registered user can view the jewelry on the simulated body (neck
or wrist) in the model viewer. .......................................................................................... 238
2.4.33) URS-33: The registered user can view a list of all previously designed work in
their personal workspace. ................................................................................................ 239
2.4.34) URS-34: The registered user can create a new design to save in their
workspace. ......................................................................................................................... 239
2.4.35) URS-35: The registered user can save the designed work to their workspace
when the design is successful. ........................................................................................... 239
2.4.36) URS-36: The registered user can save the designed work from the predefined
jewelry mockup to their workspace when the jewelry design is successful. ................ 240
2.4.37) URS-37: The registered user can save the designed work from the converted
image to 3d model to their workspace when the model design is successful. .............. 240
2.4.38) URS-38: The registered user can save the designed work from the predefined
packaging mockup to their workspace when the packaging design is successful or try-
on the jewelry with the packaging. .................................................................................. 240

---

2.4.39) URS-39: The registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a PNG or a JPG. .......................... 241
2.4.40) URS-40: Registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a PNG (transparent background).
............................................................................................................................................. 241
2.4.41) URS-41: Registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a JPG (white background). ......... 241
2.4.42) URS-42: Registered users can export their customized designs, including
jewelry, packaging, or a combination of both, as detailed PDF reports. ..................... 242
2.4.43) URS-43: Registered users can export 3D models displayed in the model viewer
to various 3D file formats, including STL, OBJ, and GLB format. ............................. 242
2.4.44) URS-44: Registered users can export 3D models displayed in the model viewer
in STL format. ................................................................................................................... 243
2.4.45) URS-45: Registered users can export 3D models displayed in the model viewer
in OBJ format. ................................................................................................................... 243
2.4.46) URS-46: Registered users can export 3D models displayed in the model viewer
in GLB format. .................................................................................................................. 243

---


## LIST OF FIGURES

Figure 28: Registration System ..................................................................................................... 88
Figure 29: Jewelry and Packaging Mockups System ................................................................... 89
Figure 30: Image to 3D System .................................................................................................... 90
Figure 31: Customization System ................................................................................................. 92
Figure 32: Virtual Try-On System ................................................................................................ 93
Figure 33: Workspace ................................................................................................................... 94
Figure 34: Super Export ................................................................................................................ 95
Figure 35: AD-01: Register .......................................................................................................... 99
Figure 36: AD-02: Log in ........................................................................................................... 102
Figure 37: AD-03: Log out ......................................................................................................... 104
Figure 38: AD-04: View all of the jewelry mockups ................................................................. 106
Figure 39: AD-05: View all of the packaging mockups ............................................................. 108
Figure 40: AD-06: View the jewelry mockups by category ....................................................... 110
Figure 41: AD-07: View the packaging mockups by category ................................................... 112
Figure 15: AD-08: Use the predefined jewelry mockup to customize ....................................... 114
Figure 42: AD-09: Use the predefined packaging mockup to customize ................................... 116
Figure 43: AD-10: Upload an Image to convert to 3D ............................................................... 119
Figure 44: AD-11: Create the name of the design ...................................................................... 122
Figure 45: AD-12: Delete the uploaded image ........................................................................... 124
Figure 46: AD-13: Select the jewelry model to customize ......................................................... 126
Figure 47: AD-14: Use the converted image to 3d model to customize ..................................... 129
Figure 48: AD-15: View the jewelry model ............................................................................... 131
Figure 49: AD-16: Customize the jewelry model ....................................................................... 133
Figure 50: AD-17: Customize the name of the jewelry model ................................................... 136
Figure 51: AD-18: Customize the color of the jewelry model ................................................... 139
Figure 52: AD-19: Customize the material of the jewelry mode ................................................ 142
Figure 53: AD-20: Customize the size of the jewelry model ..................................................... 145
Figure 54: AD-21: Customize the color of specific jewelry section .......................................... 149
Figure 55: AD-22: Customize the material of specific jewelry section ...................................... 153
Figure 56: AD-23: Zoom in and zoom out the jewelry model ................................................... 156
Figure 57: AD-24: View the packaging model ........................................................................... 158
Figure 58: AD-25: Customize the packaging model .................................................................. 161
Figure 59: AD-26: Change the color of the packaging model .................................................... 164
Figure 60: AD-27: Add engraved text to the packaging model .................................................. 168
Figure 61: AD-28: Replace with a new packaging model .......................................................... 171
Figure 62: AD-29: Choose the jewelry to try on with the packaging ......................................... 175
Figure 63: AD-30: Zoom in and zoom out the packaging model ............................................... 178
Figure 64: AD-31: Select the type of simulated body to try on .................................................. 181
Figure 65: AD-32: View the jewelry on the simulated body ...................................................... 185
Figure 66: AD-33: View all previously designed work .............................................................. 188
Figure 67: AD-34: Create a new design ..................................................................................... 190
Figure 68: AD-35: Save the designed work ................................................................................ 193
Figure 69: AD-36: Save the designed work from the predefined jewelry mockup .................... 196

---

Figure 70: AD-37: Save the designed work from the converted image to 3d model ................. 198
Figure 71: AD-38: Save the designed work from the predefined packaging mockup................ 201
Figure 72: AD-39: Export the model as image ........................................................................... 204
Figure 73: AD-40: Export image as PNG format ....................................................................... 207
Figure 74: AD-41: Export image as JPG format ........................................................................ 210
Figure 75: AD-42: Export the model as PDF report ................................................................... 213
Figure 76: AD-43: Export the model as 3D file ......................................................................... 216
Figure 77: AD-44: Export 3D file as STL format....................................................................... 219
Figure 78: AD-45: Export 3D file as OBJ format....................................................................... 222
Figure 79: AD-46: Export 3D file as GLB format ...................................................................... 225

---

Chapter One | Introduction
1.1) Purpose
The purpose of the software requirement specification document is to present and
describe in detail the system of the “3DJewelryCraft” project and a set of use cases.
1.2) Scope
• Describe the requirements of this project by use case diagram and use case description.
• Define user requirement specification.
• Define the system requirement specification of the
• Feature#1: Register
o Feature#2: Jewelry and Packaging Mockups
o Feature#3: Image to 3D
o Feature#4: Customization
o Feature#5: Virtual Try-On
o Feature#6: Workspace
o Feature#7: Super Export
1.3) User Characteristic
Title Definition
The people who are not registered to the
system. These users can only browse and
preview mockups available on the platform.
Unregistered user
They typically include curious creatives
who are exploring the idea of designing
custom jewelry.
Registered user The people who have already registered and
logged in to the web application. These
users range from beginner jewelry
entrepreneurs looking to launch a brand
with minimal technical skills, to self-
expressive, trend-conscious individuals who
Document 3DJewelryCraft_ Owner NP1, NP2 Page 84
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

value aesthetic freedom without needing a
full design team.
The people who interact with the
User 3DJewelryCraft system. This can include
both unregistered and registered user.
1.4) Acronyms and Definitions
1.4.1) Acronyms
UI User Interface
UC Use Case
URS User Requirement Specification
SRS Software Requirement Specification
2D Two Dimension
3D Three Dimension
WebGL Web Graphics Library
PNG Portable Network Graphics
JPG Joint Photographic Experts Group
PDF Portable Document Format
STL Stereolithography
OBJ Wavefront Object
GLB GL Transmission Format Binary file
1.4.2) Definitions
Title Definition
The web application that transforms 2D
jewelry designs into customizable 3D
3DJewelryCraft
models, allowing users to visualize,
personalize, and export their creations.
The people who are not registered to the
system. These users can only browse and
Unregistered User
preview mockups available on the platform.
They typically include curious creatives
Document 3DJewelryCraft_ Owner NP1, NP2 Page 85
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

who are exploring the idea of designing
custom jewelry.
The people who have already registered and
logged in to the web application. These
users range from beginner jewelry
entrepreneurs looking to launch a brand
Registered User
with minimal technical skills, to self-
expressive, trend-conscious individuals who
value aesthetic freedom without needing a
full design team.
The 3DJewelryCraft web application that
provides users with tools and services to
Platform
create, customize, and interact with 3D
jewelry models.
The pre-designed or visual representation of
a jewelry or packaging item in 3D format,
Mockup
allows to preview of the appearance and
structure of a design.
The 3DJewelryCraft system encompasses
System all components, technologies, and
functionalities provided by 3DJewelryCraft.
A predefined mockup is a ready-made 3D
Predefined Mockups model that serves as a template for
showcasing jewelry or packaging designs.
A 3D object generated by processing a 2D
Converted Image to 3D Model
image through the meshy API.
A JavaScript API that allows developers to
create interactive 2D and 3D graphics
WebGL-compatible viewer within a web browser without the need for
plugins. The 3DJewelryCraft system is used
to display the 3d model.
A feature that allows users to isolate and
Crop Model crop specific parts of a 3D model in order to
focus on customizing only the selected area.
A predefined set of colors grouped by
theme or style, provided by the system for
Color Palette
users to choose from when customizing the
package.
A six-digit alphanumeric code used in web
application to represent colors. It is written
Hex Color Code
with a leading hash symbol (#) followed by
three pairs of characters.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 86
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

A graphical user interface (GUI) tool that
allows users to select and customize colors,
typically by choosing from a palette,
Color Picker
entering color codes (such as HEX, RGB, or
HSL values), or interacting with a spectrum
or slider.
The process of creating a 2D image from a
Renderer
3D scene.
The virtual environment containing all 3D
Scene
objects.
The virtual viewpoint that frames what is
Camera
seen in the final rendered image.
The component used to display and interact
Model Viewer
with 3D models within an application.
A document automatically generated to
present detailed information about jewelry
PDF Report and packaging mockups. It includes specific
data such as design details, materials, sizes,
colors, and model previews.
A digital file that stores information about a
three-dimensional object, including its
3D File
shape, geometry, and sometimes materials
or textures include STL, OBJ, and GLB.
One of the most common 3D file types used
for 3D printing. It represents the surface
STL Format geometry of a 3D object using a collection
of triangles, without any color, texture, or
material information.
A widely used 3D model format that stores
both the geometry and surface details of an
OBJ Format object. It can also include references to
materials and texture maps, which define
the model’s appearance.
A modern 3D file format optimized for web
and application use. It stores geometry,
GLB Format
materials, textures, lighting, and animations
in a single compact binary file.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 87
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Chapter Two | Specific Requirements
2.1) Use Case Diagram
Feature #1: Register
Actor: User (Unregistered user and Registered user)
Description: The 3DJewelryCraft platform requires user to create an account and sign in
before accessing 3DJewelryCraft’s features. This process is crucial as it allows the system
to identify and provide a personalized experience to each user.
Figure 28: Registration System
Document 3DJewelryCraft_ Owner NP1, NP2 Page 88
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Feature #2: Jewelry and Packaging Mockups
Actor: User (Unregistered user, Registered user)
Description:
• Jewelry Mockup: A feature designed to help user get started in creating jewelry
more easily by presenting a variety of jewelry mockups, such as necklaces and
bracelets. The user can select the model they are interested in and continue
customizing it immediately.
• Packaging Mockup: Allows user to freely choose jewelry packaging by offering a
variety of packaging box mockups to choose from. User can choose the prototypes
they are interested in.
.
Figure 29: Jewelry and Packaging Mockups System
Document 3DJewelryCraft_ Owner NP1, NP2 Page 89
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Feature #3: Image to 3D
Actor: Registered user
Description: A feature that helps transform the user's 2D jewelry drawings or sketches
into 3D models quickly and accurately, without having to draw in a design program.
Suitable for people who have ideas but are not comfortable using 3D software.
Figure 30: Image to 3D System
Document 3DJewelryCraft_ Owner NP1, NP2 Page 90
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Feature #4: Customization
Actor: Registered user
Description:
• Jewelry Customization: A feature that allows registered user to customize jewelry
by changing materials, colors, sizes, or applying different colors and materials to
specific sections using cropping. All modifications are reflected in real-time on the
3D model.
• Packaging Customization: A feature that allows registered user to personalize
packaging by choosing colors from preset palettes or a color picker, adding
engraving text with adjustable font, style, size and positioning it freely. Preview the
customized packaging, along with their designed jewelry.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 91
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Figure 31: Customization System
Document 3DJewelryCraft_ Owner NP1, NP2 Page 92
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Feature #5: Virtual Try-On
Actor: Registered user
Description: A feature that allows user to try on jewelry on a 3D model of a simulated
body for a realistic look, allowing user to see exactly how their jewelry will look on their
body, whether it’s on their neck, or wrist.
Figure 32: Virtual Try-On System
Document 3DJewelryCraft_ Owner NP1, NP2 Page 93
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Feature #6: Workspace
Actor: Registered user
Description: A personal space feature designed to allow user to store their jewelry
designs safely without worrying about losing them when closing the program or logging
out. User can view the history of their tried jewelry and packaging mockup selections.
Figure 33: Workspace
Document 3DJewelryCraft_ Owner NP1, NP2 Page 94
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Feature #7: Super Export
Actor: Registered user
Description: A feature that allows user to render and export their customized 3D jewelry
models in various formats depending on their desired usage, whether for manufacturing,
showcasing, or sharing. User can choose to export their models as high-quality images, a
PDF report, or export as a 3D file.
Figure 34: Super Export
Document 3DJewelryCraft_ Owner NP1, NP2 Page 95
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2) Use Case Description and Activity Diagram
2.2.1) UC-01: Register
Use Case ID UC-01
Use Case Name Register
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors Unregistered user
Description The unregistered user registers to the system.
Trigger Sign Up button clicked
Preconditions - The unregistered user must be on the “Register” page.
- The unregistered user must not use an email that is already registered.
Use Case Input Specification
Input Type Constraint Example
First Name String -Required field. Nonlanee
- Must consist only of
alphanumeric
characters (A-Z, a-z,
0-9)
Last Name String -Required field. Panjateerawit
- Must consist only of
alphanumeric
characters (A-Z, a-z,
0-9)
Email String - Required field tomato@gmail.com
- Must consist only of
alphanumeric
characters (A-Z, a-z,
0-9) and special
characters ( _ , - , .)
- Must consist of @
Password String - Required field Beyong_2908
- Password must be at
least 8–12 characters
long, contain a mix of
uppercase letters and
numbers.
- The system creates a new record of the user information.
- The system displays a text “Registration Successful”
Postcondition - The system redirects to the ‘Sign In’ page.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 96
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Normal Flow Unregistered user System Note
1. The system
provides the user a
“Register” page.
2. The unregistered
user inputs the input
fields which are first
name, last name,
email, and password
[2A: The unregistered
user did not input the
text fields]
3. The unregistered
user clicks the
“Sign Up” button.
4. The system
validates input field
with constraints.
[4.1A: Email already
existed]
[4.2A: Email is not in
correct format]
[4.3A: Password does
not match what was
specified]
5. The system stores
the user information
to the database.
[5E: The system
cannot connect to
database]
6. The system display
a text “Registered
Successfully”.
7. The system redirect
to the “Log In” page.
Alternative Flow [2A: The unregistered user did not input the text fields]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 97
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

1. The system displays text “required” below each input fields
when user is not input text fields.
2. Continue the second normal flow.
[4.1A: Email already existed]
1. The system displays the message “Email already exists” when
user used existed email that already signed up to the system.
2. Continue the second normal flow.
[4.2A: Email is not in correct format]
1. The system displays the message “Please include an ‘@’ in the
email address. 'Your input' is missing an ‘@’ ” when the user
inputs an email that is not formatted.
2. Continue the second normal flow.
[4.3A: Password does not match the specified conditions]
1. The system will immediately display validation messages under
the password field, showing all unmet conditions in real-time.
2. Continue the second normal flow.
Exception Flow [5E: The system cannot connect to database]
1. The system displays message “The system cannot connect to the
database. Please try again later.”
2. Use case end.
Assumption The unregistered user has an internet connection.
URS-01: The unregistered user can register to the system.
SRS-01: The system shall provide a “Register” page with input fields: first name,
last name, email, password, and a “Sign Up” button.
SRS-02: The system shall validate input fields according to defined constraints.
SRS-03: The system shall create a new user record in the database upon
successful validation.
SRS-04: The system shall display the message “Registered Successfully” after
successful registration.
SRS-05: The system shall redirect the user to the “Log In” page after successful
registration.
SRS-06: The system shall display “First name is required” if the first name field
is empty.
SRS-07: The system shall display “Last name is required” if the last name field is
empty.
SRS-08: The system shall display “Email is required” if the email field is empty.
SRS-09: The system shall display “Password is required” if the password field is
empty.
SRS-10: The system shall display “Email already exists” if the email is already
registered.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 98
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-11: The system shall display “Please include an ‘@’ in the email address.
'Your input' is missing an ‘@’” if the email is not in the correct format.
SRS-12: The system will immediately display validation messages under the
password field, showing all unmet conditions in real-time.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-01: Register
Figure 35: AD-01: Register
Document 3DJewelryCraft_ Owner NP1, NP2 Page 99
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.2) UC-02: Log in
Use Case ID UC-02
Use Case Name Login
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors Registered user
Description The registered user log in to the system.
Trigger Log In button clicked
Preconditions - The registered user must be on the “Log in” page.
- The registered user must register an account.
Use Case Input Specification
Input Type Constraint Example
Email String - Required field nonneenie@gmail.com
- Must consist only of
alphanumeric
characters (A-Z, a-z,
0-9) and special
characters ( _ , - , .)
- Must consist of @
Password String - Required field Beyong_2908
- Password must be at
least 8–12 characters
long, contain a mix of
uppercase letters and
numbers.
Postcondition The system redirects to the ‘Home Page’ page.
Normal Flow Registered user System Note
1. The system
provides the “Log in”
page.
2. The registered user
inputs the input
fields, which are
email and password
[2.1A: The registered
user did not input the
text fields]
[2.2A: Email is not in
correct format]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 100
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

3. The registered user
clicks the
“Log in” button.
4. The system
validates input field
with constraints.
[4.1A: Email or
password is invalid]
5. The system check
the information in the
database.
[5E: The system
cannot connect to
database]
6. The system
redirect to the
“Home” page.
Alternative Flow [2.1A: The registered user did not input the text fields]
1. The system displays text “required” below each input fields
when user is not input text fields.
2. Continue the second normal flow.
[2.2A: Email is not in correct format]
1. The system displays the message “Please include an ‘@’ in the
email address. 'Your input' is missing an ‘@’” when the user
inputs an email that is not formatted.
2. Continue the second normal flow.
[4A: Email or password is invalid]
1. The system displays the message “Invalid email or password”
when a user enters an incorrect email or password.
2. Continue the second normal flow.
Exception Flow [5E: The system cannot connect to database]
1. The system displays message “The system cannot connect to
the database. Please try again later.”
2. Use case end.
Assumption The registered user has an internet connection.
URS-02: The registered user can log in to the system.
SRS-14: The system shall provide a “Log In” page with input fields which has
email and password, and a “Log In” button.
SRS-02: The system shall validate input fields according to defined constraints.
SRS-15: The system shall validate email and password in the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 101
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-16: The system shall redirect the user to the “Home” page after successful
login.
SRS-08: The system shall display “Email is required” if the email field is empty.
SRS-09: The system shall display “Password is required” if the password field is
empty.
SRS-17: The system shall display “Invalid email or password” if the user enters
an email or password that is different from the one registered.
SRS-11: The system shall display “Please include an ‘@’ in the email address.
'Your input' is missing an ‘@’” if the email is not in the correct format.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-02: Log in
Figure 36: AD-02: Log in
Document 3DJewelryCraft_ Owner NP1, NP2 Page 102
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.3) UC-03: Log out
Use Case ID UC-03
Use Case Name Log out
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors Registered user
Description The egistered user log out to the system.
Trigger The registered user click the “Log out” button.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Workspace” page.
Postcondition - The system terminates the user's session.
- The system redirects to the “Home” page and display
“You are sign out” modal.
Normal Flow Registered user System Note
1. The system
displays the “Log
Out” button on the
workspace page.
2. The registered user
clicks the “Log Out”
button
3. The system
removes user
information from the
local storage.
4. The system redirect
to the “Home” page
and display “You are
sign out” modal.
Assumption The registered user has an internet connection.
URS-03: The registered user can log out from the system.
SRS-18: The system shall provide a “Log Out” button in the workspace page.
SRS-19: The system shall remove user information from the local storage.
SRS-20: The system redirects to the ‘Home’ page and displays “You are signed
out” modal.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 103
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-03: Log out
Figure 37: AD-03: Log out
Document 3DJewelryCraft_ Owner NP1, NP2 Page 104
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.4) UC-04: View all of the jewelry mockups
Use Case ID UC-04
Use Case Name View all of the jewelry mockups
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors User (Unregistered user, Registered user)
Description The user can view a list of all jewelry mockups available in the system.
Trigger The user clicks on the “Jewelry” button on the “Home” page.
Preconditions The user must be on the “All Mockups” page.
Postcondition The system displays a list of all available jewelry mockups.
Normal Flow User System Note
1. The user clicks on
the “Jewelry” button
on the home page.
2. The system
displays a list of all
available jewelry
mockups.
[2E: The system
cannot connect to
database]
3. The user can view
all jewelry mockups
available in the
system.
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption The user has an internet connection.
URS-04: The user can view all of the jewelry mockups in the system.
SRS-21: The system shall allow the users to view jewelry mockups.
SRS-22: The system shall retrieve and display all jewelry mockups from the
database.
SRS-23: The system shall show mockup name and thumbnail in grid format.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 105
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-04: View all of the jewelry mockups
Figure 38: AD-04: View all of the jewelry mockups
Document 3DJewelryCraft_ Owner NP1, NP2 Page 106
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.5) UC-05: View all of the packaging mockups
Use Case ID UC-05
Use Case Name View all of the packaging mockups
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors The user (Unregistered user, Registered user)
Description The user can view a list of all packaging mockups available in the
system.
Trigger The user clicks on the “Packaging” button on the “Home” page.
Preconditions The user must be on the “All Packages” page.
Postcondition The system displays a list of all available packaging mockups.
Normal Flow User System Note
1. The user clicks on
the “Packaging”
button on the home
page.
2. The system
displays a list of all
available packaging
mockups.
[2E: The system
cannot connect to
database]
3. The user can view
all packaging
mockups available in
the system.
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The user has an internet connection.
URS-05: The user can view all of the packaging mockups in the system.
SRS-24: The system shall allow the users to view packaging mockups.
SRS-25: The system shall retrieve and display all packaging mockups from the
database.
SRS-23: The system shall show mockup name and thumbnail in grid format.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 107
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-05: View all of the packaging mockups
Figure 39: AD-05: View all of the packaging mockups
Document 3DJewelryCraft_ Owner NP1, NP2 Page 108
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.6) UC-06: View the jewelry mockups by category
Use Case ID UC-06
Use Case Name View the packaging mockups by category
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors User (Unregistered user and Registered user)
Description The user can view jewelry mockups by category including Necklaces
and Bracelets.
Trigger The user opens the “All Mockups” page and selects a specific category
from the sidebar.
Preconditions The user can access the “All Mockups” page.
Postcondition The system displays the jewelry mockups based on the selected
category.
Normal Flow User System Note
1. The user selects a
category from the
sidebar.
2. The system filters
and displays
thumbnail, “Custom”
button, 3D icon, and
label showing the
mockup name for
each mockup
according to the
selected category.
[2E: The system
cannot connect to
database]
3. The user views all
mockups in the
selected category.
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption The user has an internet connection.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 109
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

URS-06: The user can view the jewelry mockups by category.
SRS-26: The system shall provide access to the “All Mockups” page.
SRS-27: The system shall display a sidebar with filter buttons for “All Mockups”
including “Necklaces” and “Bracelets”.
SRS-28: The system shall update the mockups in real-time based on the selected
category.
SRS-29: The system shall display mockups in grid layout for each mockup
includes a thumbnail, 3D icon, “Custom” button, and a label showing the mockup
name.
SRS-30: The system shall redirect the user to the customization page when the
"Custom" button is clicked.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-06: View the jewelry mockups by category
Figure 40: AD-06: View the jewelry mockups by category
Document 3DJewelryCraft_ Owner NP1, NP2 Page 110
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.7) UC-07: View the packaging mockups by category
Use Case ID UC-07
Use Case Name View the packaging mockups by category
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors User (Unregistered user and Registered user)
Description The user can view packaging mockups by category including Necklace
Boxes, Bracelet Boxes, Bracelet Boxes with Pillow.
Trigger The user opens the “All Packages” page and selects a specific category
from the sidebar.
Preconditions The user can access the “All Packages” page.
Postcondition The system displays the packaging mockups based on the selected
category.
Normal Flow User System Note
1. The user selects a
category from the
sidebar.
2. The system filters
and displays preview
image, “Custom”
button,3D icon, and
label showing the
mockup name for
each mockup
according to the
selected category.
[2E: The system
cannot connect to
database]
3. The user views all
mockups in the
selected category.
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The user has an internet connection.
URS-07: The user can view packaging mockups by category.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 111
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-31: The system shall provide access to the “All Packages.”
SRS-32: The system shall display a sidebar with filter buttons for “All Packages,”
“Necklace Boxes,” “Bracelet Boxes,” and “Bracelet Boxes with Pillow.”
SRS-28: The system shall update the mockups in real-time based on the selected
category.
SRS-29: The system shall display mockups in grid layout for each mockup
includes a preview image, 3D icon, “Custom” button, and a label showing the
mockup name.
SRS-30: The system shall redirect the user to the customization page when the
“Custom” button is clicked.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-07: View the packaging mockups by category
Figure 41: AD-07: View the packaging mockups by category
Document 3DJewelryCraft_ Owner NP1, NP2 Page 112
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.8) UC-08: Use the predefined jewelry mockup to customize
Use Case ID UC-08
Use Case Name Use the predefined jewelry mockup to customize
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors Registered user
Description The registered user can use the predefined jewelry mockup to
customize by clicking the ‘Custom’ button.
Trigger The registered user clicks the ‘Custom’ button.
Preconditions The system has displayed list of jewelry mockups with ‘Custom’
buttons.
Postcondition The selected jewelry mockup is loaded into the jewelry customization
page.
Normal Flow Registered User System Note
1. The system
provides the list of
jewelry mockups with
the ‘Custom’ buttons.
[1E: The system
cannot connect to
database]
2. The registered user
clicks the ‘Custom’
button.
3. The system
redirects and loads
the selected mockup
into the customization
jewelry page.
Exception Flow [1E: The system cannot connect to database]
1. The system displays ‘The system cannot connect to database.
Please try again later.’
2. Use Case end
Assumption - The registered user has an internet connection.
URS-08: Registered user can use the predefined jewelry mockup to customize by
clicking the “Custom” button.
SRS-33: The system shall provide the list of jewelry mockups with the ‘Custom’
buttons.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 113
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-34: When the registered user clicks the "Custom" button, the system shall
redirect and load the selected mockup into the customization jewelry page.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-08: Use the predefined jewelry mockup to customize
Figure 15: AD-08: Use the predefined jewelry mockup to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 114
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.9) UC-09: Use the predefined packaging mockup to customize
Use Case ID UC-09
Use Case Name Use the predefined jewelry mockup to customize
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors Registered user
Description Registered user can choose the packaging mockup to customize by
clicking the “Custom” button.
Trigger The registered user clicks the “Custom” button.
Preconditions The system has displayed list of packaging mockups with “Custom”
buttons.
Postcondition The selected packaging mockup is loaded into the customization
packaging page.
Normal Flow Registered User System Note
1. The system
provides the list of
packaging mockups
with the “Custom”
buttons.
[1E: The system
cannot connect to
database]
2. The registered user
clicks the “Custom”
buttons.
3. The system
redirects and loads
the selected mockup
into the customization
packaging page.
Exception Flow [1E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-09: Registered user can use the predefined packaging mockup to customize by
clicking the “Custom” button.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 115
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-35: The system shall provide the list of packaging mockups with the
“Custom” buttons.
SRS-36: When the user clicks the “Custom” button, the system shall redirect and
load the selected mockup into the customization packaging page.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-09: Use the predefined packaging mockup to customize
Figure 42: AD-09: Use the predefined packaging mockup to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 116
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.10) UC-10: Upload an image to convert to 3D
Use Case ID UC-10
Use Case Name Upload an Image to convert to 3D
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors Registered user
Description The registered user can upload an image (JPG, JPEG or PNG) by
clicking or dragging-and-dropping the image into the upload area to
convert the image into a 3D model.
Trigger The registered user interacts with the upload area (click or drag-drop)
an uploaded image.
Preconditions The registered user is on the Image to 3D page and has valid image
format.
Postcondition The system generates and shows a 3D model from the uploaded image.
Normal Flow Registered User System Note
1. The registered user
opens the Image to
3D page.
2. The system
provides the upload
area and “Generate”
button.
3. The registered user
upload the image by
click or drag-drop.
4. The system
displays the uploaded
image in the upload
area.
5. The registered user
click “Generate”
button.
6. The system shows
loading state.
7. The system shows
the 3D model
generation from the
uploaded image.
Assumption - The registered user has an internet connection.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 117
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

URS-10: The user can upload an image (JPG, JPEG or PNG) by clicking, dragging,
and dropping the image into the upload area to convert the image into a 3D model.
SRS-37: The system shall display an image upload area with instructions.
SRS-38: The system shall support image upload via click-to-browse file dialog,
drag-and-drop into the upload area.
SRS-39: The system shall accept image only JPG, JPEG and PNG format and
limits the upload to a single image at a time.
SRS-40: The system shall display the uploaded image in the upload area once
successfully uploaded.
SRS-41: When the “Generate” button is clicked with a valid image, the system
shall start the 3D model conversion process and displays a loading state.
SRS-42: When the process is successful, the system shows the 3D model
generation from the uploaded image.
SRS-43: The system shall display a message “Something went wrong while
generating your 3D model. Please try again later.” if the system error occurs
during conversion.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 118
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-10: Upload an Image to convert to 3D
Figure 43: AD-10: Upload an Image to convert to 3D
Document 3DJewelryCraft_ Owner NP1, NP2 Page 119
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.11) UC-11: Create the name of the design
Use Case ID UC-11
Use Case Name Create the name of the designed
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjeteerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors Registered user
Description Registered user can create the name of their design.
Trigger Registered user finishes uploading an image.
Preconditions The valid image has been uploaded.
Postcondition The system stores the design name in the database.
Use Case Input Specification
Input Type Constraint Example
Design Name String - Gift_Valentine_01
Normal Flow Registered User System Note
1. The registered user
opens the Image to
3D page and
successful upload the
image.
2. The system
provides the input
field with the default
name “New Model”
3. The registered user
types the new design
name in the input
field.
[3A: The registered
user does not enter
the design name]
4. The registered user
click “Generate”
button.
5. The system saves
the design name in
the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 120
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

[5E: The system
cannot connect to the
database]
Alternative Flow [3E: The registered user does not enter the design name]
1. The system will use the default name “New Model”
2. Continue to the fourth flow.
Exception Flow [5E: The system cannot connect to the database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-11: The registered user can create the name of their design.
SRS-44: The system shall provide the input field with the default name “New
Model.”
SRS-45: The system shall allow registered user to re-edit the new design name in
the input field.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 121
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-11: Create the name of the design
Figure 44: AD-11: Create the name of the design
Document 3DJewelryCraft_ Owner NP1, NP2 Page 122
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.12) UC-12: Delete the uploaded image
Use Case ID UC-12
Use Case Name Delete the uploaded image
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 05/05/2025 Last Updated 19/06/2025
Actors Registered user
Description The registered user can delete the currently uploaded image to upload a
new one before proceeding to generate the 3D model.
Trigger The registered user clicks on the ‘Delete’ (trash button).
Preconditions An image must already be uploaded.
Postcondition The uploaded image is removed, and the upload area is reset to allow
new image input.
Normal Flow Registered User System Note
1. The registered user
opens the Image to
3D page and has
already uploaded the
image.
2. The system
displays a delete icon
next to the thumbnail.
3. The registered user
clicks the delete icon.
4. The system deletes
the uploaded image
and clears the
preview to allow new
image input.
Assumption - The registered user has an internet connection.
URS-12: The registered user can delete the currently uploaded image to upload a
new one before generating the 3D model.
SRS-46: The system shall display a delete icon next to the uploaded image
preview.
SRS-47: After image deletion, the system shall delete the uploaded image and
clear the preview to allow new image input.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 123
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-48: The system shall allow a new image to be uploaded immediately after
the previous one is deleted.
AD-12: Delete the uploaded image
Figure 45: AD-12: Delete the uploaded image
Document 3DJewelryCraft_ Owner NP1, NP2 Page 124
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.13) UC-13: Select the jewelry model to customize
Use Case ID UC-13
Use Case Name Select the jewelry model to customize
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can select the jewelry model to customize.
Trigger - The registered user clicks the “Custom” button to select the
predefined jewelry model to customize.
- The registered user clicks the “Custom” button in the navigation
sidebar after the model has been converted to custom the completed
image to a 3D model.
Preconditions - The system has displayed list of jewelry mockups with “Custom”
buttons.
- The system displays the converted model from image to 3d with the
“Custom” button in the navigation sidebar.
Postcondition The selected jewelry or the converted model is loaded into the jewelry
customization page.
Normal Flow Registered User System Note
1. The registered user
clicks the ‘Custom’
button to customize
the predefined
jewelry model or the
converted image to 3d
model.
2. The system
redirects and loads
the model into the
jewelry customization
page.
[2E: The system
cannot connect to
database]
Exception Flow [2E: The system cannot connect to database]
1. The system displays ‘The system cannot connect to database.
Please try again later.’
2. Use Case end
Document 3DJewelryCraft_ Owner NP1, NP2 Page 125
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Assumption - The registered user has an internet connection.
URS-13: The registered user can select the jewelry model to customize.
SRS-33: The system shall provide the list of jewelry mockups with the ‘Custom’
buttons.
SRS-49: The system shall display the model from the image to 3d after the model
has been converted with the ‘Custom’ button in the navigation sidebar.
SRS-50: When the registered user clicks the "Custom" button in the navigation
sidebar, the system shall redirect and load the selected mockup or the converted
model into the customization jewelry page.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-13: Select the jewelry model to customize
Figure 46: AD-13: Select the jewelry model to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 126
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.14) UC-14: Use the converted image to 3d model to customize
Use Case ID UC-14
Use Case Name Use the converted image to 3d model to customize
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can use the converted image to 3d model to
customize by clicking the ‘Custom’ button in the navigation sidebar
after the model is converted successfully.
Trigger - The registered user clicks the “Custom” button in the navigation
sidebar after the model has been converted successfully.
Preconditions - The system displays the converted model from image to 3d with the
“Custom” button in the navigation sidebar.
Postcondition The jewelry mockup is loaded into the customization jewelry page.
Normal Flow Registered User System Note
1. The system
displays the
completed converted
model from image to
3d in the model
viewer with the
“Custom” button.
[1E: The system
cannot connect to
database]
2. The registered user
clicks the ‘Custom’
button in the
navigation sidebar.
[2E: The model has
not yet been
converted.]
3. The system
redirects and loads
the model into the
image to 3d
customization page.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 127
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Alternative Flow [2E: The model has not yet been converted.]
1. The system displays ‘The model has not been converted yet.
Please wait until the model is converted successfully.’
2. Continue to the first flow.
Exception Flow [1E: The system cannot connect to database]
1. The system displays ‘The system cannot connect to database.
Please try again later.’
2. Use Case end
Assumption - The registered user has an internet connection.
URS-14: The registered user can use the converted image to 3d model to customize
by clicking the ‘Custom’ button in the navigation sidebar after the model is
converted successfully.
SRS-49: The system shall display the model from the image to 3d
after the model has been converted with the ‘Custom’ button in the
navigation sidebar.
SRS-51: When the registered user clicks the "Custom" button, the system shall
redirect and load the model into the image to 3d customization page.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 128
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-14: Use the converted image to 3d model to customize
Figure 47: AD-14: Use the converted image to 3d model to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 129
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.15) UC-15: View the jewelry model
Use Case ID UC-15
Use Case Name View the jewelry model
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can view the selected jewelry model in the model
viewer.
Trigger The registered user selects a jewelry model to customize
Preconditions The registered user must be on the “Jewelry Customization” or “Image
to 3d Customization” page.
Postcondition The system displays the selected jewelry model in the model viewer.
Normal Flow Registered User System Note
1. The system
provides a “Jewelry
Customization” or
“Image to 3d
Customization” page.
2. The system
displays the selected
jewelry model in the
model viewer.
[2E: The system
cannot connect to
database]
3. The registered user
can view the selected
jewelry model.
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-15: The registered user can view the selected jewelry model in the model
viewer.
SRS-52: The system shall display the selected jewelry model in the model viewer
when the registered user chooses the model to customize.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 130
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-53: The system shall render the 3D model using a WebGL-compatible
viewer.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-15: View the jewelry model
Figure 48: AD-15: View the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 131
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.16) UC-16: Customize the jewelry model
Use Case ID UC-16
Use Case Name Customize the jewelry model
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can customize the jewelry model including color,
material, and size by clicking the “Custom” button in the navigation
sidebar.
Trigger - The registered user clicks the “Custom” button in the navigation
sidebar after select the jewelry model or the model converted
successfully.
Preconditions - The system displays the jewelry model in the model viewer with the
“Custom” button in the navigation sidebar.
Postcondition The jewelry mockup is loaded into the customization jewelry page with
the customization options.
Normal Flow Registered User System Note
1. The system
displays the jewelry
model in the model
viewer with the
“Custom” button
2. The registered user
clicks the ‘Custom’
button in the
navigation sidebar.
3. The system
redirects and loads
the model into the
jewelry customization
page with the
customization
options.
[3E: The system
cannot connect to
database]
Exception Flow [3E: The system cannot connect to database]
1. The system displays ‘The system cannot connect to database.
Please try again later.’
Document 3DJewelryCraft_ Owner NP1, NP2 Page 132
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2. Use Case end
Assumption - The registered user has an internet connection.
URS-16: The registered user can customize the jewelry model, including color,
material, and size clicking the “Custom” button in the navigation sidebar.
SRS-54: The system shall display the jewelry model in the model viewer with the
“Custom” button.
SRS-55: When the registered user clicks the "Custom" button in the navigation
sidebar, the system shall redirect and load the model into the jewelry
customization page with the customization options.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-16: Customize the jewelry model
Figure 49: AD-16: Customize the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 133
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.17) UC-17: Customize the name of the jewelry model
Use Case ID UC-17
Use Case Name Customize the name of the jewelry model
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can customize the name of the jewelry model to a
new desired name.
Trigger The registered user clicks to rename in the input field.
Preconditions - The registered user must be on the “Jewelry Customization” page.
- The jewelry model has been loaded and displayed in the model
viewer.
Postcondition The jewelry model’s name is updated in the input field.
Normal Flow Registered User System Note
1. The system
provides a “Jewelry
Customization” page
with the selected
jewelry model.
[1E: The system
cannot connect to
database]
2. The system
displays the current
name of the jewelry
model in the input
field.
3. The registered user
enters the new name
for the jewelry model.
4. The system updates
the displayed name in
the input field.
Exception Flow [1E: The system cannot connect to database]
1. The system displays message “The system cannot connect to
database. Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 134
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

URS-17: Registered user can customize the name of the jewelry model to a new
desired name.
SRS-56: The system shall provide a “Jewelry Customization” page that includes
an input field for editing the jewelry model’s name.
SRS-57: The system shall display the current name of the jewelry model in the
input field when the page loads.
SRS-58: The system shall update the displayed name in the input field.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 135
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-17: Customize the name of the jewelry model
Figure 50: AD-17: Customize the name of the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 136
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.18) UC-18: Customize the color of the jewelry model
Use Case ID UC-18
Use Case Name Customize the color of the jewelry model
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can customize the color of the jewelry model and
can preview the color changes in real-time.
Trigger The registered user clicks on the color dropdown from the
customization sidebar.
Preconditions - The registered user must be on the “Jewelry Customization” or
“Image to 3d Customization” page.
- The registered user must click the “Custom” button on the navigation
sidebar.
- The jewelry model has been loaded and displayed in the model
viewer.
Postcondition The color of the jewelry model changes according to the selection.
Normal Flow Registered User System Note
1. The system
provides a “Jewelry
Customization” or
“Image to 3d
Customization” page
with the selected
jewelry model.
2. The registered user
clicks on the
“Custom” button on
the navigation
sidebar.
3. The system
redirects to the
customization page
with the sidebar to
choose the color.
4. The registered user
clicks on the color
dropdown to select
the desired color.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 137
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The system updates
and displays the
jewelry model with
the selected color in
real-time.
[5E: The system
cannot connect to
database]
Exception Flow [5E: The system cannot connect to database]
1. The system displays message “The system cannot connect to
database. Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-18: Registered user can customize the color of the jewelry model and can
preview the color changes in real-time.
SRS-59: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes a color dropdown on the customization
sidebar.
SRS-60: The system shall immediately apply and render the color to the jewelry
model in real-time when the registered user selects a color.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 138
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-18: Customize the color of the jewelry model
Figure 51: AD-18: Customize the color of the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 139
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.19) UC-19: Customize the material of the jewelry model
Use Case ID UC-19
Use Case Name Customize the material of the jewelry model
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can customize the material of the jewelry model
and can preview the material changes in real-time.
Trigger The registered user clicks on the material dropdown from the
customization sidebar.
Preconditions - The registered user must be on the “Jewelry Customization” or
“Image to 3d Customization” page.
- The registered user must click the “Custom” button on the navigation
sidebar.
- The jewelry model has been loaded and displayed in the model
viewer.
Postcondition The material of the jewelry model changes according to the selection.
Normal Flow Registered User System Note
1. The system
provides a “Jewelry
Customization” or
“Image to 3d
Customization” page
with the selected
jewelry model.
2. The registered user
clicks on the
“Custom” button on
the navigation
sidebar.
3. The system
redirects to the
customization page
with the sidebar to
choose the material.
4. The registered user
clicks on the material
dropdown to select
the desired material.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 140
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The system updates
and displays the
jewelry model with
the selected material
in real-time.
[5E: The system
cannot connect to
database]
Exception Flow [5E: The system cannot connect to database]
1. The system displays message “The system cannot connect to
database. Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-19: Registered user can customize the material of the jewelry model and can
preview the material changes in real-time.
SRS-61: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes a material dropdown on the customized
sidebar.
SRS-62: The system shall immediately apply and render the material to the
jewelry model in real-time when the registered user selects a material.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 141
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-19: Customize the material of the jewelry model
Figure 52: AD-19: Customize the material of the jewelry mode
Document 3DJewelryCraft_ Owner NP1, NP2 Page 142
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.20) UC-20: Customize the size of the jewelry model
Use Case ID UC-20
Use Case Name Customize the size of the jewelry model
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can customize the size of the jewelry model and
can preview the size changes in real-time.
Trigger The registered user drags the slider from the customization sidebar.
Preconditions - The registered user must be on the “Jewelry Customization” or
“Image to 3d Customization” page.
- The registered user must click the “Custom” button on the navigation
sidebar.
- The jewelry model has been loaded and displayed in the model
viewer.
Postcondition The size of the jewelry model changes according to the drag on slider.
Normal Flow Registered User System Note
1. The system
provides a “Jewelry
Customization” or
“Image to 3d
Customization” page
with the selected
jewelry model.
2. The registered user
clicks on the
“Custom” button on
the navigation
sidebar.
3. The system
redirects to the
customization page
with the sidebar to
resize.
4. The registered user
drags the slider to
change the size of the
jewelry model as
desired.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 143
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The system updates
and displays the
jewelry model with
the selected size in
real-time.
[5E: The system
cannot connect to
database]
Exception Flow [5E: The system cannot connect to database]
1. The system displays message “The system cannot connect to
database. Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-20: Registered user can customize the size of the jewelry model and can
preview the size changes in real-time.
SRS-63: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes a slider on the customized sidebar.
SRS-64: The system shall immediately render the size to the jewelry model in
real-time when the registered user drags the slider.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 144
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-20: Customize the size of the jewelry model
Figure 53: AD-20: Customize the size of the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 145
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.21) UC-21: Customize the color of specific jewelry sections
Use Case ID UC-21
Use Case Name Customize the color of specific jewelry sections
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can customize the color of specific parts of a
jewelry model by cropping the part that they want.
Trigger The registered user clicks on the “Crop” button from the bottom bar.
Preconditions - The registered user must be on the “Jewelry Customization” or
“Image to 3d Customization” page.
- The registered user must click the “Custom” button on the navigation
sidebar.
- The jewelry model has been loaded and displayed in the model
viewer.
Postcondition The selected section of the jewelry model is updated with the new
color.
Normal Flow Registered User System Note
1. The system
provides a “Jewelry
Customization” or
“Image to 3d
Customization” page
with the selected
jewelry model.
2. The registered user
clicks on the
“Custom” button on
the navigation
sidebar.
3. The system
redirects to the
customization page
with the “Crop”
button in the bottom
bar.
4. The registered user
clicks on the “Crop”
button.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 146
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered user
drags on the 3D
model to define the
area to recolor.
[5A: The registered
user drags the
selected area outside
the jewelry model]
6. The system
displays a square crop
box following the
registered user’s drag.
7. The system
highlights the selected
area.
8. The registered user
selects a new color
from the
customization
sidebar.
9. The system applies
the new color to the
cropped section and
updates the model in
real-time.
10. The registered
user clicks on the
“Cancel Crop” button
to exit crop mode.
[10A: The registered
user clicks outside the
crop area instead of
clicking the “Cancel
Crop” button]
11. The system
preserves the applied
color and returns to
Document 3DJewelryCraft_ Owner NP1, NP2 Page 147
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

the normal
customization mode.
[11A: Starts a new
crop after applying
color]
Alternative Flow [5A: The registered user drags the selected area outside the jewelry
model]
1. The system displays message “Please drag on the model area to
apply customization”.
2. Continue to the fifth flow.
[10A: The registered user clicks outside the crop area instead of
clicking the “Cancel Crop” button]
1. The system discards any selected color.
2. Continue to the fifth flow.
[11A: The registered user starts a new crop after applying color]
1. After completing one recolor and canceling crop mode, the
registered user can customize it again.
2. Continue to the fourth flow.
Assumption - The registered user has an internet connection.
URS-21: The registered user can customize the color of specific parts of a jewelry
model by cropping the part that they want.
SRS-65: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes the “Crop” button in the bottom bar.
SRS-66: The system shall enable the registered user to define a customized area
on the 3D model by dragging to create a crop box.
SRS-67: The system shall highlight the selected cropped area during dragging.
SRS-68: The system shall allow the registered user to choose a new color and
apply it to the cropped area in real-time.
SRS-69: The system shall update and render the affected part of the model with
the selected color.
SRS-70: The system shall display message “Please drag on the model area to
apply customization” when the registered user drags the selected area outside the
jewelry model.
SRS-71: The system shall provide a “Cancel Crop” button that ends the crop
mode and preserves the recolored area.
SRS-72: The system shall discard the selected color when the registered user
clicks outside the cropped area.
SRS-73: The system shall support consecutive cropping actions after exiting a
previous crop mode.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 148
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-21: Customize the color of specific jewelry sections
Figure 54: AD-21: Customize the color of specific jewelry section
Document 3DJewelryCraft_ Owner NP1, NP2 Page 149
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.22) UC-22: Customize the material of specific jewelry sections
Use Case ID UC-22
Use Case Name Customize the material of specific jewelry sections
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can customize the material of specific parts of a
jewelry model by cropping the part that they want.
Trigger The registered user clicks on the “Crop” button from the bottom bar.
Preconditions - The registered user must be on the “Jewelry Customization” or
“Image to 3d Customization” page.
- The registered user must click the “Custom” button on the navigation
sidebar.
- The jewelry model has been loaded and displayed in the model
viewer.
Postcondition The selected section of the jewelry model is updated with the new
material.
Normal Flow Registered User System Note
1. The system
provides a “Jewelry
Customization” or
“Image to 3d
Customization” page
with the selected
jewelry model.
2. The registered user
clicks on the
“Custom” button on
the navigation
sidebar.
3. The system
redirects to the
customization page
with the “Crop”
button in the bottom
bar.
4. The registered user
clicks on the “Crop”
button.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 150
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered user
drags on the 3D
model to define the
area to change the
material.
[5A: The registered
user drags the
selected area outside
the jewelry model]
6. The system
displays a square crop
box following the
registered user’s drag.
7. The system
highlights the selected
area.
8. The registered user
selects a new material
from the
customization
sidebar.
9. The system applies
the new material to
the cropped section
and updates the
model in real-time.
10. The registered
user clicks on the
“Cancel Crop” button
to exit crop mode.
[10A: The registered
user clicks outside the
crop area instead of
clicking the “Cancel
Crop” button]
11. The system
preserves the applied
material and returns
to the normal
customization mode.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 151
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

[11A: Starts a new
crop after applying
material]
Alternative Flow [5A: The registered user drags the selected area outside the jewelry
model]
1. The system displays message “Please drag on the model area to
apply customization”.
2. Continue to the fifth flow.
[10A: The registered user clicks outside the crop area instead of
clicking the “Cancel Crop” button]
1. The system cancels the current crop operation and discards any
selected material.
2. Continue to the fifth flow.
[11A: The registered user starts a new crop after applying material]
1. After completing one material change and canceling crop mode,
the registered user can customize it again.
2. Continue to the fourth flow.
Assumption - The registered user has an internet connection.
URS-22: The registered user can customize the material of specific parts of a
jewelry model by cropping the part that they want.
SRS-65: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes the “Crop” button in the bottom bar.
SRS-66: The system shall enable the registered user to define a customized area
on the 3D model by dragging to create a crop box.
SRS-67: The system shall highlight the selected cropped area during dragging.
SRS-74: The system shall allow the registered user to choose a new material and
apply it to the cropped area in real-time.
SRS-75: The system shall update and render the affected part of the model with
the selected material.
SRS-70: The system shall display message “Please drag on the model area to
apply customization” when the registered user drags the selected area outside the
jewelry model.
SRS-76: The system shall provide a “Cancel Crop” button that ends the crop
mode and preserves the material change area.
SRS-77: The system shall cancel the crop and discard the selected material when
the registered user clicks outside the cropped area.
SRS-73: The system shall support consecutive cropping actions after exiting a
previous crop mode.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 152
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-22: Customize the material of specific jewelry sections
Figure 55: AD-22: Customize the material of specific jewelry section
Document 3DJewelryCraft_ Owner NP1, NP2 Page 153
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.23) UC-23: Zoom in and zoom out the jewelry model
Use Case ID UC-23
Use Case Name Zoom in and zoom out the jewelry model
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can zoom in and zoom out of the jewelry model to
closely examine design details or view the entire piece more clearly.
Trigger The registered user clicks on the “Zoom-in” (plus button) or “Zoom-
out” (minus button) in the bottom bar.
Preconditions - The registered user must be on the “Jewelry Customization” or
“Image to 3d Customization” page.
- The jewelry model has been loaded and displayed in the model
viewer.
Postcondition The model viewer is updated based on the zoom action
(in or out).
Normal Flow Registered User System Note
1. The registered user
opens the “Jewelry
Customization” page
and jewelry model
has been loaded and
displayed.
2. The system
displays zoom-in and
zoom-out buttons in
the bottom bar.
3. The registered user
clicks on the "Zoom
in" or "Zoom out"
button.
[3E: The system
cannot connect to
database]
4. The system detects
zoom action and
updates the model
viewer accordingly.
5. The registered user
views the updated
Document 3DJewelryCraft_ Owner NP1, NP2 Page 154
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

zoomed view of the
jewelry model.
Exception Flow [3E: The system cannot connect to the database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-23: The registered user can zoom in and zoom out of the jewelry model to
closely examine design details or view the entire piece more clearly.
SRS-78: The system shall display "Zoom In" and "Zoom Out" buttons in the
bottom action bar on the “Jewelry Customization” or “Image to 3d
Customization” pages.
SRS-79: The system shall detect the zoom action and update the model viewer
accordingly based on the user's use of the "Zoom In" and "Zoom Out" buttons.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 155
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-23: Zoom in and zoom out the jewelry model
Figure 56: AD-23: Zoom in and zoom out the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 156
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.24) UC-24: View the packaging model
Use Case ID UC-24
Use Case Name View the packaging model
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can view the selected packaging model in the
model viewer.
Trigger The registered user selects a packaging model to customize
Preconditions The registered user must be on the “Packaging Customization” page.
Postcondition The system displays the selected packaging model in the model viewer.
Normal Flow Registered User System Note
1. The system
provides a
“Packaging
Customization” page.
2. The system
displays the selected
packaging model in
the model viewer.
[2E: The system
cannot connect to
database]
3. The registered user
can view the selected
packaging model.
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-24: The registered user can view the selected packaging model in the model
viewer.
SRS-80: The system shall display the selected packaging model in the model
viewer when the registered user chooses the model to customize.
SRS-53: The system shall render the 3D model using a WebGL-compatible
viewer.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 157
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-24: View the packaging model
Figure 57: AD-24: View the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 158
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.25) UC-25: Customize the packaging model
Use Case ID UC-25
Use Case Name Customized the packaging model
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can customize the packaging model, including
changing the color and adding engraved text from the navigation
sidebar.
Trigger The registered user selects a packaging model to customize
Preconditions - The registered user must be on the “Packaging Customization” page.
- The registered user must click on the “Custom” button from the
navigation sidebar.
- The packaging model has been loaded and displayed in the model
viewer.
Postcondition The packaging model is loaded into the packaging customization page
with the customization options.
Normal Flow Registered User System Note
1. The system
provides a
“Packaging
Customization” page
2. The registered user
clicks the “Custom”
button in the
navigation sidebar.
3. The system
redirects and loads
the model into the
packaging
customization page
with the
customization
options.
[3E: The system
4. The registered user cannot connect to the
customizes the database]
packaging model.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 159
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Exception Flow [3E: The system cannot connect to the database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption The registered user has an internet connection.
URS-25: The registered user can customize the packaging model, including
changing the color and adding engraved text from the navigation sidebar.
SRS-81: The system shall display the packaging model in the model viewer with
the “Custom” button.
SRS-82: When the registered user clicks the "Custom" button in the navigation
sidebar, the system shall redirect and load the model into the packaging
customization page with the customization options.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 160
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-25: Customize the packaging model
Figure 58: AD-25: Customize the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 161
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.26) UC-26: Customize the color of the packaging model
Use Case ID UC-26
Use Case Name Change the color of the packaging model
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can change the color of the packaging model by
selecting a color from a system-provided palettes, entering a hex color
code, or choosing a custom color from color picker tool.
The selected color is applied in real-time to the packaging preview.
Trigger The registered user selects or inputs a new color from the
customization sidebar.
Preconditions - The registered user must be on the “Packaging Customization” page.
- The registered user must click the “Custom” button on the navigation
sidebar.
- The packaging model has been loaded and displayed in the model
viewer.
Postcondition The packaging model’s color is updated and displayed in the preview
area with the selected color.
Normal Flow Registered User System Note
1. The system
provides a
“Packaging
Customization” page
with the selected
packaging model.
2. The registered user
clicks the “Custom”
button in the
navigation sidebar.
3. The system
displays color
palettes, an input field
for hex color code,
and a color picker
tool.
4. The registered user
chooses a color from
the palette, or inputs a
Document 3DJewelryCraft_ Owner NP1, NP2 Page 162
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

hex code, or picks a
custom color. 5. The system
validates the input
hex color.
[5E: Invalid hex color
input]
6. The system applies
the selected color to
the packaging model
in the model viewer
area.
[6E: The system
cannot connect to
database]
7. The registered user
views the packaging
model in the model
viewer area with the
new color applied.
Exception Flow [5E: Invalid hex color input]
1. The system displays “Invalid color code. Please enter a valid hex
code or select a color from the palette.”
2. Continue to the fourth flow.
[6E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-26: The registered user can change the color of the packaging model by
selecting a color from a system-provided palette, entering a hex color code, or
choosing a custom color from the color picker tool. The selected color is applied in
real-time to the packaging preview.
SRS-83: The system shall display a color palette, an input field for hex color
code, and a color picker tool when the user clicks the “Custom” button in the
navigation sidebar.
SRS-84: The system shall allow the registered user to choose a color from the
palette, input a hex code, or select a custom color.
SRS-85: The system shall validate the input hex color to determine whether the
input is in the correct hex color format or not.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 163
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-86: The system shall apply the selected color to the packaging model in the
model viewer area.
SRS-87: The system shall display a message “Invalid color code. Please enter a
valid hex code or select a color from the palette” if registered user inputs an
invalid hex color format.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-26: Change the color of the packaging model
Figure 59: AD-26: Change the color of the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 164
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.27) UC-27: Add engraved text to the packaging model
Use Case ID UC-27
Use Case Name Add engraved text to the packaging model
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can add engraved text to the selected packaging
model includes entering the text, choosing font style, font size, and
dragging the text to the desired position.
Trigger The registered user entering the text in the “Custom Text” input field.
Preconditions - The registered user must be on the “Packaging Customization” page.
- There is at least one packaging model currently applied.
Postcondition The engraved text is displayed on the packaging model in the model
viewer area with the selected font, size, and position.
Normal Flow Registered User System Note
1. The system
provides a
“Packaging
Customization” page
with the selected
packaging model.
2. The registered user
clicks the “Custom”
button in the
navigation sidebar.
3. The system
displays the
customization panel,
including input field,
font style dropdown,
font size dropdown,
and color picker.
4. The registered user
enters custom text in
the input field, selects
a font style from the
dropdown menu,
adjusts the font size
or chooses a text
Document 3DJewelryCraft_ Owner NP1, NP2 Page 165
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

color using the color
picker.
[4A: The registered
user removes custom
text in the input
field.] 5. The system
displays the text on
the packaging model
in the model viewer
area with the selected
font, and size.
[5E: The system
cannot connect to
database]
6. The registered user
drags the text to the
desired position on
the packaging. 7. The system updates
the text position in the
3D view.
8. The registered user
views the packaging
model in the model
viewer area with the
selected font, size,
and position.
Alternative Flow [4A: The registered user removes custom text in the input field.]
1. The system removes text from preview and resets engraving state.
2. Use Case end
Exception Flow [5E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-27: The registered user can add engraved text to the selected packaging model
includes entering the text, choosing font style, font size, and dragging the text to the
desired position.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 166
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-88: The system shall display a customization panel, including an input field,
font style dropdown, font size selector, and color picker, when the registered user
clicks the “Custom” button in the sidebar of the packaging customization page.
SRS-89: The system shall allow the registered user to enter custom engraving text
into the input field, select a font style from a dropdown menu, adjust the font size
using a font size selector, and select a text color using a color picker tool.
SRS-90: The system shall render the engraved text on the packaging model in the
model viewer area with the selected font style, font size, and color.
SRS-91: The system shall allow the registered user to drag the engraved text to
the desired position on the packaging model.
SRS-92: The system shall update the text position in the model viewer in real
time as the registered user drags the text.
SRS-93: The system shall remove the engraved text from the model viewer and
reset the engraving state when the registered user clears the input field.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 167
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-27: Add engraved text to the packaging model
Figure 60: AD-27: Add engraved text to the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 168
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.28) UC-28: Replace with a new packaging model
Use Case ID UC-28
Use Case Name Replace with a new packaging model
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can select and apply a new packaging model to
replace an existing one.
Trigger The registered user selects a new packaging model in the customization
sidebar.
Preconditions - The registered user must be on the “Packaging Customization” page.
- The system has displayed list of packaging mockups.
- There is at least one packaging model currently applied.
Postcondition The selected new packaging model replaces the old one.
Normal Flow Registered User System Note
1. The registered user
must be on the
“Packaging
Customization” page
with at least one
packaging model
currently applied.
2. The system
displays a list of
packaging mockup
thumbnails in the
customization
sidebar.
3. The registered user
selects a new
packaging model
from the “All
Packaging” button in
the customization
sidebar.
4. The system
highlights selection
on the new packaging
model thumbnail.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 169
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The system
replaces the old
packaging with the
new one and updates
the model viewer.
[5E: The system
cannot connect to
database]
6. The registered user
views the new
packaging.
Exception Flow [5E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-28: The registered user can select and apply a new packaging model to replace
an existing one.
SRS-94: The system shall display a list of packaging mockup thumbnails and
displays in the sidebar of the packaging customization page.
SRS-95: The system shall highlight selection on the new packaging model
thumbnail when the registered user selects the new one.
SRS-96: The system shall replace the old packaging with the new one and update
the model viewer.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 170
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-28: Replace with a new packaging model
Figure 61: AD-28: Replace with a new packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 171
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.29) UC-29: Choose the jewelry to try on with packaging
Use Case ID UC-29
Use Case Name Choose the jewelry to try on with packaging
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can choose the saved jewelry from their workspace
to try on with the selected packaging model.
Trigger The registered user selects the saved jewelry from their workspace.
Preconditions - The registered user must be on the “Packaging Customization” page.
- There is at least one packaging model currently applied.
- The registered user must have at least one jewelry item saved in their
workspace.
Postcondition - The selected jewelry is displayed with the applied packaging in the
model viewer section.
Normal Flow Registered User System Note
1. The registered user
must be on the
“Packaging
Customization” page
with at least one
packaging model
currently applied.
2. The registered user
clicks the “My
Jewelry” button in the
customization
sidebar.
[2A: The registered
user doesn’t have any
jewelry in workspace
yet.]
3. The system
displays a list of
saved jewelry items
from the user’s
workspace.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 172
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

[3E: The system
cannot connect to
database]
4. The registered user
selects a jewelry item
from the list.
5. The system
validates whether the
packaging type
matches the selected
jewelry item.
[5E: The packaging
type and the selected
jewelry item
mismatch]
6. The system loads
the 3D jewelry model
along with the current
packaging in the
model viewer area.
7. The registered user
views the combined
display of the selected
jewelry with the
applied packaging.
Alternative Flow [2A: The registered user doesn’t have any jewelry in workspace yet.]
1. The system displays “You don’t have any jewelry in your
workspace yet.”
2. Use Case end
[5E: The packaging type and the selected jewelry item mismatch]
1. The system displays message “Oops! This jewelry doesn’t fit
with the current package. Try selecting a matching type.”
2. Use Case end
Exception Flow [3E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-29: The registered user can choose the saved jewelry from their workspace to
try on with the selected packaging model.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 173
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-97: The system shall display a list of saved jewelry thumbnails from the
registered user’s workspace when the user clicks the “My Jewelry” button in the
sidebar of the packaging customization page.
SRS-98: The system shall allow the registered user to select one jewelry item
from the list of saved jewelry.
SRS-99: The system shall render the selected jewelry model together with the
currently applied packaging in the model viewer.
SRS-100: The system shall display a message “You don’t have any jewelry in
your workspace yet.” if there are no saved jewelry items in the user’s workspace.
SRS-101: The system displays message “Oops! This jewelry doesn’t fit with the
current package. Try selecting a matching type.” if the packaging type and the
selected jewelry item mismatch.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 174
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-29: Choose the jewelry to try on with the packaging
Figure 62: AD-29: Choose the jewelry to try on with the packaging
Document 3DJewelryCraft_ Owner NP1, NP2 Page 175
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.30) UC-30: Zoom in and zoom out the packaging model
Use Case ID UC-30
Use Case Name Zoom in and zoom out the packaging model
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 02/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can zoom in and zoom out of the packaging model
to closely examine design details or view the entire piece more clearly.
Trigger The registered user clicks on the “Zoom-in” (plus button) or “Zoom-
out” (minus button) in the bottom bar.
Preconditions - The registered user must be on the “Packaging Customization” page.
- The packaging model has been loaded and displayed in the model
viewer.
Postcondition The model viewer is updated based on the zoom action
(in or out).
Normal Flow Registered User System Note
1. The registered user
opens “Packaging
Customization” page
and packaging model
has been loaded and
displayed.
2. The system
displays zoom-in and
zoom-out buttons in
the bottom action bar.
3. The registered user
clicks on the "Zoom
in" or "Zoom out"
button.
[3E: The system
cannot connect to
database]
4. The system detects
zoom action and
updates the model
viewer accordingly.
5. The registered user
observes the updated
Document 3DJewelryCraft_ Owner NP1, NP2 Page 176
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

zoomed view of the
packaging model.
Exception Flow [3E: The system cannot connect to the database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-30: The registered user can zoom in and zoom out of the packaging model to
closely examine design details or view the entire piece more clearly.
SRS-102: The system shall display "Zoom In" and "Zoom Out" buttons in the
bottom action bar on the “Packaging Customization” pages.
SRS-79: The system shall detect the zoom action and update the model viewer
accordingly based on the user's use of the "Zoom In" and "Zoom Out" buttons.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 177
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-30: Zoom in and zoom out the packaging model
Figure 63: AD-30: Zoom in and zoom out the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 178
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.31) UC-31: Select the type of simulated body to try on
Use Case ID UC-31
Use Case Name Select the type of simulated body to try on
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can select the type of selected body on which the
jewelry will be virtually tried-on.
Trigger The registered user clicks on the “Virtual Try-On” button in the bottom
bar
Preconditions - The registered user must be on the “Jewelry Customization”, “Image
to 3D” or “Image to 3D Customization” page.
- The jewelry model has been loaded and displayed in the model
viewer.
Postconditions - The selected simulated body is displayed in the model viewer
according to the type selected.
Normal Flow Registered User System Note
1. The system provide
a “Jewelry
Customization”,
“Image to 3D” or
“Image to 3D
Customization” page.
2. The registered user
clicks the “Virtual
Try-On” button in the
bottom bar.
3. The system
displays the options
“Neck Try-On” and
“Wrist Try-On” for
simulated body type.
4. The registered user
clicks the button to
select the type of
simulated body.
5. The system
displays the simulated
Document 3DJewelryCraft_ Owner NP1, NP2 Page 179
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

body in model viewer
according to the type
selected by the
registered user.
[5E: The system
cannot connect to
database]
Exception Flow [5E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-31: The registered user can select the type of selected body on which the
jewelry will be virtually tried-on.
SRS-103: The system shall display a “Virtual Try-On” button in the bottom bar.
SRS-104: The system shall display a “Neck Try-On” and “Wrist Try-On” button
after clicking on the virtual try-on button to allow the registered user to select the
type of simulated body.
SRS-105: The system shall display the neck model when the registered user
selects “Neck Try-On” button.
SRS-106: The system shall display the wrist model when the registered user
selects “Wrist Try-On” button.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 180
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-31: Select the type of simulated body to try on
Figure 64: AD-31: Select the type of simulated body to try on
Document 3DJewelryCraft_ Owner NP1, NP2 Page 181
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.32) UC-32: View the jewelry on the simulated body
Use Case ID UC-32
Use Case Name View the jewelry on the simulated body
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 03/08/2025 Last Updated 28/08/2025
Actors Registered user
Description The registered user can view the model designed on the simulated body
(neck or wrist) in the model viewer.
Trigger The registered user clicks on the “Neck Try-On” or “Wrist Try-On”
button after clicking on the “Virtual Try-On” in the bottom bar.
Preconditions - The registered user must be on the “Jewelry Customization”, “Image
to 3D” or “Image to 3D Customization” page.
- The jewelry model has been loaded and displayed in the model
viewer.
- The simulated body type (neck or wrist) must have been selected.
Postconditions The jewelry models are displayed according to the type of simulated
body model correctly selected.
Normal Flow Registered User System Note
1. The system provide
a “Jewelry
Customization”,
“Image to 3D” or
“Image to 3D
Customization” page
with the jewelry
model.
2. The registered user
clicks the “Virtual
Try-On” button in the
bottom bar.
3. The system
displays the options
“Neck Try-On” and
“Wrist Try-On” for
simulated body type.
4. The registered user
clicks the button to
select the type of
simulated body.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 182
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The system
displays the simulated
body in model viewer
according to the type
selected by the
registered user.
[5E: The system
cannot connect to
database]
6. The system
validates whether the
jewelry type and the
simulated body type
match.
[6A: Jewelry model
type and simulated
body type mismatch]
7. The jewelry models
are displayed
according to the type
of simulated body
model correctly
selected.
8. The registered user
can view the model
designed on the
simulated body in the
correct position.
Alternative Flow [6A: Jewelry model type and simulated body type mismatch]
1. The system displays message “Try-on is not supported for this
type”
2. Continue to the fourth flow
Exception Flow [5E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-32: The registered user can view the jewelry on the simulated body (neck or
wrist) in the model viewer.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 183
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-107: The system shall display a “Virtual Try-On” button in the bottom bar.
SRS-108: The system shall display a “Neck Try-On” and “Wrist Try-On” button
after clicking on the virtual try-on button to allow the registered user to select the
type of simulated body.
SRS-109: The system shall display the neck model when the registered user
selects “Neck Try-On” button.
SRS-110: The system shall display the wrist model when the registered user
selects “Wrist Try-On” button.
SRS-111: The system shall validate whether the jewelry type and the simulated
body type match.
SRS-112: The system shall display necklace jewelry to match the neck model.
SRS-113: The system shall display bracelet jewelry to match the wrist model.
SRS-114: The system shall display message “Try-on is not supported for this
type” if the jewelry model type and the simulated body type mismatch.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 184
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-32: View the jewelry on the simulated body
Figure 65: AD-32: View the jewelry on the simulated body
Document 3DJewelryCraft_ Owner NP1, NP2 Page 185
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.33) UC-33: View all previously designed work
Use Case ID UC-33
Use Case Name View all previously designed works
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 01/10/2025 Last Updated 18/10/2025
Actors Registered user
Description The registered user can view a list of all previously designed work in
their personal workspace.
Trigger The registered user clicks on the “Workspace” button on the navigation
bar or the side bar.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Workspace” page.
Postcondition The system displays all previously saved jewelry designs.
Normal Flow Registered User System Note
1. The registered user
clicks on the
“Workspace” button
on the navigation bar
or the side bar.
2. The system
validates user session
and navigates to the
“Workspace” page.
3. The system
displays all
previously saved
designs.
[3.1E: The system
doesn’t have designs
saved]
[3.2E: The system
cannot connect to
database]
4. The registered user
can view list of all
previously designed
work in their personal
workspace.
Alternative Flow [3.1E: The system doesn’t have designs saved]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 186
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

1. The system displays “No design saved yet”
2. Use Case end
Exception Flow [3.2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered user has an internet connection.
URS-33: The registered user can view a list of all previously designed work in their
personal workspace.
SRS-115: When the registered user clicks on the “Workspace” button, the system
shall validate the user session and navigate to the “Workspace” page.
SRS-116: The system shall display all previously saved designs with the
associated data, including the 3D model preview, designed name, and date and
time created.
SRS-117: The system shall display a message “No design saved yet” if the
system doesn’t have designs saved.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 187
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-33: View all previously designed work
Figure 66: AD-33: View all previously designed work
Document 3DJewelryCraft_ Owner NP1, NP2 Page 188
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.34) UC-34: Create a new design
Use Case ID UC-34
Use Case Name Create a new design
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 01/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered users can create a new design to save in their workspace.
Trigger The registered user clicks the “Create new design” button on the
“Workspace” page.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Workspace” page.
Postcondition - The system redirects to the “Image to 3D” page and save the
converted model design to the user’s workspace in the database.
Normal Flow Registered User System Note
1. The registered user
clicks the “Create
new design” button
on the “Workspace”
page.
2. The system
navigates to the
“Image to 3D” page
and save the
converted model
design to the user’s
workspace in the
database.
Assumption - The registered user has an internet connection.
URS-34: The registered user can create a new design to save in their workspace.
SRS-118: When the registered user clicks on the “Create new design” button, the
system shall navigate to the “Image to 3D” page and provide the “Upload Form”
with a “Generate” button that the registered user can create the new design and
save the converted model design to the user’s workspace in the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 189
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-34: Create a new design
Figure 67: AD-34: Create a new design
Document 3DJewelryCraft_ Owner NP1, NP2 Page 190
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.35) UC-35: Save the designed work
Use Case ID UC-35
Use Case Name Save the designed work
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 01/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered user can save the designed work to their workspace when
the design is successful.
Trigger The registered user clicks the “Save to workspace” button on the
“Mockups” or “Customization” page.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Mockups” or “Customization”
page.
Postcondition - The designed work is saved in the user’s workspace.
- The system displays a text “Your design has been saved.”
Normal Flow Registered User System Note
1. The registered user
clicks the “Save to
workspace” button on
the “Customization”
page.
2. The system saves
the design to the
user’s workspace in
the database.
[2E: The system
cannot connect to
database]
3. The system
displays a text “Your
design has been
saved.”
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered has an internet connection.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 191
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

URS-35: The registered user can save the designed work to their workspace when
the design is successful.
SRS-119: When the registered user clicks on the “Save to workspace” button, the
system shall save the design to the user’s workspace in the database.
SRS-120: The system shall display the message “Your design has been saved”
after a successful save.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 192
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-35: Save the designed work
Figure 68: AD-35: Save the designed work
Document 3DJewelryCraft_ Owner NP1, NP2 Page 193
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.36) UC-36: Save the designed work from the predefined jewelry mockup
Use Case ID UC-36
Use Case Name Save the designed work from the predefined jewelry mockup
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 01/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered user can save the designed work from the predefined
jewelry mockup to their workspace when the jewelry design is
successful.
Trigger The registered user clicks the “Save to workspace” button on the
“Jewelry Mockups” or “Jewelry Customization” page.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Jewelry Mockups” or “Jewelry
Customization” page.
Postcondition - The designed work from the predefined jewelry mockup is saved in
the user’s workspace.
- The system displays a text “Your design has been saved.”
Normal Flow Registered User System Note
1. The registered user
clicks the “Save to
workspace” button on
the “Jewelry
Mockups” or
“Jewelry
Customization” page.
2. The system saves
the designed work
from the predefined
jewelry mockup to
the user’s workspace
in the database.
[2E: The system
cannot connect to
database]
3. The system display
a text “Your design
has been saved.”
Exception Flow [2E: The system cannot connect to database]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 194
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered has an internet connection.
URS-36: The registered user can save the designed work from the predefined
jewelry mockup to their workspace when the jewelry design is successful.
SRS-121: When the registered user clicks on the “Save to workspace” button on
the “Jewelry Mockups” or “Jewelry Customization” page, the system shall save
the designed work from the predefined jewelry mockup to the user’s workspace in
the database.
SRS-120: The system shall display the message “Your design has been saved”
after a successful save.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 195
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-36: Save the designed work from the predefined jewelry mockup
Figure 69: AD-36: Save the designed work from the predefined jewelry mockup
Document 3DJewelryCraft_ Owner NP1, NP2 Page 196
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.37) UC-37: Save the designed work from the converted image to 3d model
Use Case ID UC-37
Use Case Name Save the designed work from the converted image to 3d model
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 01/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered user can save the designed work from the converted image
to 3d model to their workspace when the model design is successful.
Trigger The registered user clicks the “Save to workspace” button on the
“Image to 3d” or “Image to 3d Customization” page.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Image to 3d” or “Image to 3d
Customization” page.
Postcondition - The designed work from the converted image to 3d model is saved in
the user’s workspace.
- The system displays a text “Your design has been saved.”
Normal Flow Registered User System Note
1. The registered user
clicks the “Save to
workspace” button on
the “Image to 3d” or
“Image to 3d
Customization” page.
2. The system saves
the converted image
to 3d model to the
user’s workspace in
the database.
[2E: The system
cannot connect to
database]
3. The system display
a text “Your design
has been saved.”
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered has an internet connection.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 197
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

URS-37: The registered user can save the designed work from the converted image
to 3d model to their workspace when the model design is successful.
SRS-122: When the registered user clicks on the “Save to workspace” button on
the “Image to 3d” or “Image to 3d Customization” page, the system shall save the
converted image to 3d model to the user’s workspace in the database.
SRS-120: The system shall display the message “Your design has been saved”
after a successful save.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
AD-37: Save the designed work from the converted image to 3d model
Figure 70: AD-37: Save the designed work from the converted image to 3d model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 198
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.38) UC-38: Save the designed work from the predefined packaging mockup
Use Case ID UC-38
Use Case Name Save the designed work from the predefined packaging mockup
Created By Nichakorn Prompong Last Revision By Nonlanee
Panjateerawit
Date Created 01/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered user can save the designed work from the predefined
packaging mockup to their workspace when the packaging design is
successful or try-on the jewelry with the packaging.
Trigger The registered user clicks the “Save to workspace” button on the
“Packaging Mockups” or “Packaging Customization” page.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Packaging Mockups” or
“Packaging Customization” page.
Postcondition - The designed work from predefined packaging mockup is saved in
the user’s workspace.
- The tried-on jewelry with the packaging is saved in the user’s
workspace.
- The system displays a text “Your design has been saved.”
Normal Flow Registered User System Note
1. The registered user
clicks the “Save to
workspace” button on
the “Packaging
Mockups” or
“Packaging
Customization” page.
2. The system saves
the predefined
packaging mockup or
the tried-on jewelry
with the packaging to
the user’s workspace
in the database.
[2E: The system
cannot connect to
database]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 199
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

3. The system display
a text “Your design
has been saved.”
Exception Flow [2E: The system cannot connect to database]
1. The system displays “The system cannot connect to database.
Please try again later.”
2. Use Case end
Assumption - The registered has an internet connection.
URS-38: The registered user can save the designed work from the predefined
packaging mockup to their workspace when the packaging design is successful or
try-on the jewelry with the packaging.
SRS-123: When the registered user clicks on the “Save to workspace” button on
the “Packaging Mockups” or “Packaging Customization” page, the system shall
save the predefined packaging mockup or the tried-on jewelry with the packaging
to the user’s workspace in the database.
SRS-120: The system shall display the message “Your design has been saved”
after a successful save.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 200
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-38: Save the designed work from the predefined packaging mockup
Figure 71: AD-38: Save the designed work from the predefined packaging mockup
Document 3DJewelryCraft_ Owner NP1, NP2 Page 201
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.39) UC-39: Export the model as image
Use Case ID UC-39
Use Case Name Export the model as image
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered user can export the 3D model displayed in the model viewer
as an image, with the option to export it as a PNG or a JPG.
Trigger The registered user clicks the “Super Export” button on the “Mockups”
or “Customization” page.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Customization” page.
- The model has been loaded and displayed in the model viewer
Postcondition The image file (PNG or JPG) is downloaded to the registered user's
computer.
Normal Flow Registered User System Note
1. The registered user
clicks the “Super
Export” button on the
“Mockups” or
“Customization”
page.
2. The system
displays a modal to
select the export PNG
or JPG options.
3. The registered user
selects the desired
format.
4. The system
generates an image
file according to the
selected format and
downloads it to the
registered user's
computer.
[4E: Cannot find
renderer/scene/camera
in model viewer]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 202
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered user
receives the image in
PNG or JPG format.
Exception Flow [4E: Cannot find renderer/scene/camera in model viewer]
1. The system displays message “Renderer/Scene/Camera is not
ready”.
2. Use Case end
Assumption - The registered has an internet connection.
URS-39: The registered user can export the 3D model displayed in the model viewer
as an image, with the option to export it as a PNG or a JPG.
SRS-124: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export image in PNG or JPG format.
SRS-125: When the registered user selects the desired format, the system shall
generate the image file according to the selected format.
SRS-126: The system shall download the image file (PNG or JPG) to the
registered user’s computer.
SRS-127: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “Renderer/Scene/Camera is
not ready.”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 203
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-39: Export the model as image
Figure 72: AD-39: Export the model as image
Document 3DJewelryCraft_ Owner NP1, NP2 Page 204
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.40) UC-40: Export image as PNG format
Use Case ID UC-40
Use Case Name Export image as PNG format
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered user can export the 3D model displayed in the model viewer
as an image, with the option to export it as a PNG (transparent
background).
Trigger The registered user clicks the “Export as PNG” button on the modal.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Mockups” or “Customization”
page.
- The model has been loaded and displayed in the model viewer.
Postcondition The exported PNG file (model_snapshot.png) is downloaded to the
registered user’s device.
Normal Flow Registered User System Note
1. The registered user
clicks the “Super
Export” button on the
“Mockups” or
“Customization”
page.
2. The system
displays a modal to
select the export PNG
or JPG options.
3. The registered user
clicks on the “Export
as PNG” button.
4. The system
generates and
downloads the image
file in PNG format to
the registered user's
computer.
[4E: Cannot find
renderer/scene/camera
in model viewer]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 205
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered
users receive the
image in PNG format
named
model_snapshot.png
Exception Flow [4E: Cannot find renderer/scene/camera in model viewer]
1. The system displays message “Failed to export image. Please try
again”.
2. Use Case end
Assumption - The registered has an internet connection.
URS-40: Registered user can export the 3D model displayed in the model viewer as
an image, with the option to export it as a PNG (transparent background).
SRS-128: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export PNG format.
SRS-129: The system shall provide the “Export as PNG” button for downloading
the image.
SRS-130: The system shall generate and download an image file in PNG format
named model_snapshot.png to the registered user's computer.
SRS-127: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “Failed to export image.
Please try again”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 206
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-40: Export image as PNG format
Figure 73: AD-40: Export image as PNG format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 207
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.41) UC-41: Export image as JPG format
Use Case ID UC-41
Use Case Name Export image as JPG format
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered user can export the 3D model displayed in the model viewer
as an image, with the option to export it as a JPG (white background).
Trigger The registered user clicks the “Export as JPG” button on the modal.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Mockups” or “Customization”
page.
- The model has been loaded and displayed in the model viewer.
Postcondition The exported JPG file (model_snapshot.jpg) is downloaded to the
registered user’s device.
Normal Flow Registered User System Note
1. The registered user
clicks the “Super
Export” button on the
“Mockups” or
“Customization”
page.
2. The system
displays a modal to
select the export PNG
or JPG options.
3. The registered user
clicks on the “Export
as JPG” button.
4. The system
generates and
downloads the image
file in JPG format to
the registered user's
computer.
[4E: Cannot find
renderer/scene/camera
in model viewer]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 208
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered
users receive the
image in JPG format
named
model_snapshot.jpg
Exception Flow [4E: Cannot find renderer/scene/camera in model viewer]
1. The system displays message “Failed to export image. Please try
again”.
2. Use Case end
Assumption - The registered has an internet connection.
URS-41: Registered user can export the 3D model displayed in the model viewer as
an image, with the option to export it as a JPG (white background).
SRS-131: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export JPG format.
SRS-132: The system shall provide the “Export as JPG” button for downloading
the image.
SRS-133: The system shall generate and download the image file in JPG format
named model_snapshot.jpg to the registered user's computer.
SRS-127: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “Failed to export image.
Please try again”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 209
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-41: Export image as JPG format
Figure 74: AD-41: Export image as JPG format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 210
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.42) UC-42: Export the model as PDF report
Use Case ID UC-42
Use Case Export the model as PDF report
Name
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered users can export their customized designs, including jewelry,
packaging, or a combination of both, as detailed PDF reports.
Trigger The registered user clicks the “Generate PDF Report” button on the modal.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Mockups” or “Customization” page.
- The model has been loaded and displayed in the model viewer.
Postcondition The PDF file is downloaded with customization details to the registered
user's computer.
Normal Flow Registered User System Note
1. The registered user
clicks the “Super
Export” button on the
“Mockups” or
“Customization”
page.
2. The system displays a modal to
select the export as a PDF report.
3. The registered user
clicks on the
“Generate PDF
Report” button.
4. The system generates a PDF
report with details such as model
name, export date, jewelry details,
packaging details, and a preview
image of the model.
[4E: Cannot find
renderer/scene/camera in model
viewer]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 211
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The system downloads the PDF
report to the registered user's
computer, according to the model
type:
-
jewelryName_customization.pdf
for jewelry export
-
packageName_customization.pdf
for packaging export
- jewelryName_packageName_
6. The registered customization.pdf for combined
users receive a PDF jewelry and packaging export.
report file.
Exception [4E: Cannot find renderer/scene/camera in model viewer]
Flow 1. The system displays message “Failed to export PDF report. Please try
again”.
2. Use Case end
Assumption - The registered has an internet connection.
URS-42: Registered users can export their customized designs, including jewelry,
packaging, or a combination of both, as detailed PDF reports.
SRS-134: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the generation of a PDF report.
SRS-135: The system shall display the “Generate PDF Report” button for
downloading a PDF report.
SRS-136: The system shall generate a PDF report with details such as model
name, export date, jewelry details, packaging details, and a preview image of the
model
SRS-137: The system shall download the PDF report to the registered user's
computer, according to the model type: jewelryName_customization.pdf for
jewelry export, packageName_customization.pdf for packaging export,
jewelryName_packageName_Customization.pdf for combined jewelry and
packaging export.
SRS-138: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “Failed to export PDF report.
Please try again”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 212
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-42: Export the model as PDF report
Figure 75: AD-42: Export the model as PDF report
Document 3DJewelryCraft_ Owner NP1, NP2 Page 213
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.43) UC-43: Export the model as 3D file
Use Case ID UC-43
Use Case Name Export the model as 3D file
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered users can export 3D models displayed in the model viewer
to various 3D file formats, including STL, OBJ, and GLB format.
Trigger The registered user clicks the “Super Export” button on the “Mockups”
or “Customization” page.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Customization” page.
- The model has been loaded and displayed in the model viewer.
Postcondition The 3D file (STL, OBJ, GLB) is downloaded to the registered user's
computer.
Normal Flow Registered User System Note
1. The registered user
clicks the “Super
Export” button on the
“Mockups” or
“Customization”
page.
2. The system
displays a modal to
select the export as a
3D file.
3. The registered user
selects the desired
format.
4. The system
generates a 3d file
according to the
selected format and
downloads a 3d file to
the registered user's
computer.
[4E: Cannot find
renderer/scene/camera
in model viewer]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 214
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered
users receive the 3d
file in STL, OBJ or
GLB format.
Exception Flow [4E: Cannot find renderer/scene/camera in model viewer]
1. The system displays message “No model to export”.
2. Use Case end
Assumption - The registered has an internet connection.
URS-43: Registered users can export 3D models displayed in the model viewer to
various 3D file formats, including STL, OBJ, and GLB format.
SRS-139: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export 3d file in STL, OBJ or GLB format.
SRS-140: When the registered user selects the desired format, the system shall
generate the 3d file according to the selected format.
SRS-141: The system shall download the 3d file (STL, OBJ, GLB) to the
registered user’s computer.
SRS-142: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “No model to export”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 215
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-43: Export the model as 3D file
Figure 76: AD-43: Export the model as 3D file
Document 3DJewelryCraft_ Owner NP1, NP2 Page 216
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.44) UC-44: Export 3D file as STL format
Use Case ID UC-44
Use Case Name Export 3D file as STL format
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered users can export 3D models displayed in the model viewer
in STL format.
Trigger The registered user clicks the “Export as STL” button on the modal.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Mockups” or “Customization”
page.
- The model has been loaded and displayed in the model viewer
Postcondition The 3D file in STL format is downloaded to the registered user's
computer.
Normal Flow Registered User System Note
1. The registered user
clicks the “Super
Export” button on the
“Mockups” or
“Customization”
page.
2. The system
displays a modal to
select the export as a
STL format.
3. The registered user
clicks on the “Export
as STL” button.
4. The system
generates a 3d file in
STL format and
downloads STL files
to the registered user's
computer.
[4E: Cannot find
model in model
viewer]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 217
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered
users receive the 3d
file in STL format
named Untitled.stl
Exception Flow [4E: Cannot find model in model viewer]
1. The system displays message “No model to export as STL”
2. Use Case end
Assumption - The registered has an internet connection.
URS-44: Registered users can export 3D models displayed in the model viewer in
STL format.
SRS-143: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export 3d file in STL format.
SRS-144: The system shall display the “Export as STL” button for downloading
an STL file.
SRS-145: The system shall generate and download a 3d file in STL format to the
registered user’s computer.
SRS-146: If the model is not available in the model viewer, the system shall
display the message “No model to export as STL.”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 218
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-44: Export 3D file as STL format
Figure 77: AD-44: Export 3D file as STL format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 219
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.45) UC-45: Export 3D file as OBJ format
Use Case ID UC-44
Use Case Name Export 3D file as OBJ format
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered users can export 3D models displayed in the model viewer
in OBJ format.
Trigger The registered user clicks the “Export as OBJ” button on the modal.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Mockups” or “Customization”
pages.
- The model has been loaded and displayed in the model viewer
Postcondition The 3D file in OBJ format is downloaded to the registered user's
computer.
Normal Flow Registered User System Note
1. The registered user
clicks the “Super
Export” button on the
“Mockups” or
“Customization”
page.
2. The system
displays a modal to
select the export as a
OBJ format.
3. The registered user
clicks on the “Export
as OBJ” button.
4. The system
generates a 3d file in
OBJ format and
downloads the OBJ
file to the registered
user's computer.
[4E: Cannot find
model in model
viewer]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 220
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered
users receive the 3d
file in OBJ format
named Untitled.obj
Exception Flow [4E: Cannot find model in model viewer]
1. The system displays message “No model to export as OBJ”.
2. Use Case end
Assumption - The registered has an internet connection.
URS-45: Registered users can export 3D models displayed in the model viewer in
OBJ format.
SRS-147: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export 3d file in OBJ format.
SRS-148: The system shall display the “Export as OBJ” button for downloading
the OBJ file.
SRS-149: The system shall generate and download a 3d file in OBJ
format to the registered user’s computer.
SRS-150: If the model is not available in the model viewer, the system shall
display the message “No model to export as OBJ.”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 221
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-45: Export 3D file as OBJ format
Figure 78: AD-45: Export 3D file as OBJ format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 222
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.2.46) UC-46: Export 3D file as GLB format
Use Case ID UC-46
Use Case Name Export 3D file as GLB format
Created By Nonlanee Last Revision By Nonlanee
Panjateerawit Panjateerawit
Date Created 02/10/2025 Last Updated 18/10/2025
Actors Registered user
Description Registered users can export 3D models displayed in the model viewer
in GLB format.
Trigger The registered user clicks the “Export as GLB” button on the modal.
Preconditions - The registered user must log in to the system first.
- The registered user must be on the “Mockups” or “Customization”
pages.
- The model has been loaded and displayed in the model viewer.
Postcondition The 3D file in GLB format is downloaded to the registered user's
computer.
Normal Flow Registered User System Note
1. The registered user
clicks the “Super
Export” button on the
“Mockups” or
“Customization”
page.
2. The system
displays a modal to
select the export as a
GLB format.
3. The registered user
clicks on the “Export
as GLB” button. 4. The system
generates a 3d file in
GLB format and
downloads the GLB
file to the registered
user's computer.
[4E: Cannot find
model in model
viewer]
Document 3DJewelryCraft_ Owner NP1, NP2 Page 223
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

5. The registered
users receive the 3d
file in GLB format
named Untitled.glb
Exception Flow [4E: Cannot find model in model viewer]
1. The system displays message “No model to export as GLB”.
2. Use Case end
Assumption - The registered has an internet connection.
URS-46: Registered users can export 3D models displayed in the model viewer in
GLB format.
SRS-151: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export 3d file in GLB format.
SRS-152: The system shall display the “Export as GLB” button for downloading
the GLB file.
SRS-153: The system shall generate and download the GLB file to the registered
user’s computer.
SRS-154: If the model is not available in the model viewer, the system shall
display the message “No model to export as GLB.”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 224
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

AD-46: Export 3D file as GLB format
Figure 79: AD-46: Export 3D file as GLB format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 225
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.3) User Requirement Specification
2.3.1) Feature #1: Registration
URS-01: The unregistered user can register to the system.
URS-02: The registered user can log in to the system.
URS-03: The registered user can log out from the system.
2.3.2) Feature #2: Jewelry and Packaging Mockups
URS-04: The user can view all of the jewelry mockups in the system.
URS-05: The user can view all of the packaging mockups in the system.
URS-06: The user can view the jewelry mockups by category.
URS-07: The user can view the packaging mockups by category.
URS-08: Registered user can choose the jewelry mockup to customize by clicking
the “Custom” button.
URS-09: Registered user can choose the packaging mockup to customize by
clicking the “Custom” button.
2.3.3) Feature #3: Image to 3D
URS-10: The user can upload an image (JPG, JPEG or PNG) by clicking,
dragging, and dropping the image into the upload area to convert the image into a
3D model.
URS-11: The registered user can create the name of their design.
URS-12: The registered user can delete the currently uploaded image to upload a
new one before generating the 3D model.
2.3.4) Feature #4: Customization
URS-13: The registered user can select the jewelry model to customize.
URS-14: The registered user can use the converted image to 3d model to
customize by clicking the ‘Custom’ button in the navigation sidebar after the
model is converted successfully.
URS-15: The registered user can view the selected jewelry model in the model
viewer.
URS-16: The registered user can customize the jewelry model, including color,
material, and size clicking the “Custom” button in the navigation sidebar.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 226
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

URS-17: The registered user can customize the name of the jewelry model to a
new desired name
URS-18: The registered user can customize the color of the jewelry model and
can preview the color changes in real-time.
URS-19: The registered user can customize the material of the jewelry model and
can preview the material changes in real-time.
URS-20: The registered user can customize the size of the jewelry model and can
preview the size changes in real-time.
URS-21: The registered user can customize the color of specific parts of a jewelry
model by cropping the part that they want.
URS-22: The registered user can customize the material of specific parts of a
jewelry model by cropping the part that they want.
URS-23: The registered user can zoom in and zoom out of the jewelry model to
closely examine design details or view the entire piece more clearly.
URS-24: The registered user can view the selected packaging model in the model
viewer.
URS-25: The registered user can customize the packaging model, including
changing the color and adding engraved text from the navigation sidebar.
URS-26: The registered user can change the color of the packaging model by
selecting a color from a system-provided palette, entering a hex color code, or
choosing a custom color from the color picker tool. The selected color is applied
in real-time to the packaging preview.
URS-27: The registered user can add engraved text to the selected packaging
model includes entering the text, choosing font style, font size, and dragging the
text to the desired position.
URS-28: The registered user can select and apply a new packaging model to
replace an existing one.
URS-29: The registered user can choose the saved jewelry from their workspace
to try on with the selected packaging model.
URS-30: The registered user can zoom in and zoom out of the packaging model to
closely examine design details or view the entire piece more clearly.
2.3.5) Feature #5: Virtual Try-On
URS-31: The registered user can select the type of selected body on which the
jewelry will be virtually tried-on.
URS-32: The registered user can view the model designed on the simulated body
(neck or wrist) in the model viewer.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 227
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.3.6) Feature #6: Workspace
URS-33: The registered user can view a list of all previously designed work in
their personal workspace.
URS-34: The registered user can create a new design to save in their workspace.
URS-35: The registered user can save the designed work to their workspace when
the design is successful.
URS-36: The registered user can save the designed work from the predefined
jewelry mockup to their workspace when the jewelry design is successful.
URS-37: The registered user can save the designed work from the converted
image to 3d model to their workspace when the model design is successful.
URS-38: The registered user can save the designed work from the predefined
packaging mockup to their workspace when the packaging design is successful or
try-on the jewelry with the packaging.
2.3.7) Feature #7: Super Export
URS-39: The registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a PNG or a JPG.
URS-40: Registered user can export the 3D model displayed in the model viewer
as an image, with the option to export it as a PNG (transparent background).
URS-41: Registered user can export the 3D model displayed in the model viewer
as an image, with the option to export it as a JPG (white background).
URS-42: Registered users can export their customized designs, including jewelry,
packaging, or a combination of both, as detailed PDF reports.
URS-43: Registered users can export 3D models displayed in the model viewer to
various 3D file formats, including STL, OBJ, and GLB format.
URS-44: Registered users can export 3D models displayed in the model viewer in
STL format.
URS-45: Registered users can export 3D models displayed in the model viewer in
OBJ format.
URS-46: Registered users can export 3D models displayed in the model viewer in
GLB format.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 228
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.4) System Requirement Specification
2.4.1) URS-01: The unregistered user can register to the system.
SRS-01: The system shall provide a “Register” page with input fields: first name,
last name, email, password, and a 'Sign Up' button.
SRS-02: The system shall validate input fields according to defined constraints.
SRS-03: The system shall create a new user record in the database upon
successful validation.
SRS-04: The system shall display the message “Registered Successfully” after
successful registration.
SRS-05: The system shall redirect the user to the “Log In” page after successful
registration.
SRS-06: The system shall display “First name is required” if the first name field
is empty.
SRS-07: The system shall display “Last name is required” if the last name field is
empty.
SRS-08: The system shall display “Email is required” if the email field is empty.
SRS-09: The system shall display “Password is required” if the password field is
empty.
SRS-10: The system shall display “Email already exists” if the email is already
registered.
SRS-11: The system shall display “Please include an ‘@’ in the email address.
'Your input' is missing an ‘@’” if the email is not in the correct format.
SRS-12: The system will immediately display validation messages under the
password field, showing all unmet conditions in real-time.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.2) URS-02: The registered user can log in to the system.
SRS-14: The system shall provide a “Log In” page with input fields which has
email and password, and a “Log In” button.
SRS-02: The system shall validate input fields according to defined constraints.
SRS-15: The system shall validate email and password in the database.
SRS-16: The system shall redirect the user to the “Home” page after successful
login.
SRS-08: The system shall display “Email is required” if the email field is empty.
SRS-09: The system shall display “Password is required” if the password field is
empty.
SRS-17: The system shall display “Invalid email or password” if the user enters
an email or password that is different from the one registered.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 229
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-11: The system shall display “Please include an ‘@’ in the email address.
'Your input' is missing an ‘@’” if the email is not in the correct format.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.3) URS-03: The registered user can log out from the system.
SRS-18: The system shall provide a “Log Out” button in the workspace page.
SRS-19: The system shall remove user information from the local storage.
SRS-20: The system redirects to the ‘Home’ page and displays “You are signed
out” modal.
2.4.4) URS-04: The user can view all of the jewelry mockups in the system.
SRS-21: The system shall allow the users to view jewelry mockups.
SRS-22: The system shall retrieve and display all jewelry mockups from the
database.
SRS-23: The system shall show mockup name and thumbnail in grid format.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.5) URS-05: The user can view all of the packaging mockups in the system.
SRS-24: The system shall allow the users to view packaging mockups.
SRS-25: The system shall retrieve and display all packaging mockups from the
database.
SRS-23: The system shall show mockup name and thumbnail in grid format.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.6) URS-06: The user can view the jewelry mockups by category.
SRS-26: The system shall provide access to the “All Mockups” page.
SRS-27: The system shall display a sidebar with filter buttons for “All Mockups”
including “Necklaces” and “Bracelets”.
SRS-28: The system shall update the mockups in real-time based on the selected
category.
SRS-29: The system shall display mockups in grid layout for each mockup
includes a thumbnail, 3D icon, “Custom” button, and a label showing the mockup
name.
SRS-30: The system shall redirect the user to the customization page when the
"Custom" button is clicked.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 230
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.7) URS-07: The user can view packaging mockups by category.
SRS-31: The system shall provide access to the "All Packages."
SRS-32: The system shall display a sidebar with filter buttons for “All Packages”,
“Necklace Boxes”, “Bracelet Boxes”, and “Bracelet Boxes with Pillow.”
SRS-28: The system shall update the mockups in real-time based on the selected
category.
SRS-29: The system shall display mockups in grid layout for each mockup
includes a preview image, 3D icon, “Custom” button, and a label showing the
mockup name.
SRS-30: The system shall redirect the user to the customization page when the
“Custom" button is clicked.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.8) URS-08: Registered user can use the predefined jewelry mockup to customize
by clicking the ‘Custom’ button.
SRS-33: The system shall provide the list of jewelry mockups with the “Custom”
buttons.
SRS-34: When the registered user clicks the “Custom” button, the system shall
redirect and load the selected mockup into the customization jewelry page.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.9) URS-09: Registered user can use the predefined packaging mockup to
customize by clicking the ‘Custom’ button.
SRS-35: The system shall provide the list of packaging mockups with the
“Custom” buttons.
SRS-36: When the user clicks the “Custom” button, the system shall redirect and
load the selected mockup into the customization packaging page.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.10) URS-10: The user can upload an image (JPG, JPEG or PNG) by clicking,
dragging, and dropping the image into the upload area to convert the image into a
3D model.
SRS-37: The system shall display an image upload area with instructions.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 231
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-38: The system shall support image upload via click-to-browse file dialog,
drag-and-drop into the upload area.
SRS-39: The system shall accept image only JPG, JPEG and PNG format and
limits the upload to a single image at a time.
SRS-40: The system shall display the uploaded image in the upload area once
successfully uploaded.
SRS-41: When the “Generate” button is clicked with a valid image, the system
shall start the 3D model conversion process and display a loading state.
SRS-42: When the process is successful, the system shows the 3D model
generation from the uploaded image.
SRS-43: The system shall display a message “Something went wrong while
generating your 3D model. Please try again later.” if the system error occurs
during conversion.
2.4.11) URS-11: The registered user can create the name of their design.
SRS-44: The system shall provide the input field with the default name “New
Model.”
SRS-45: The system shall allow users to re-edit the new design name in the input
field.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.12) URS-12: The registered user can delete the currently uploaded image to
upload a new one before generating the 3D model.
SRS-46: The system shall display a delete icon next to the uploaded image
preview.
SRS-47: After image deletion, the system shall delete the uploaded image and
clear the preview to allow new image input.
SRS-48: The system shall allow a new image to be uploaded immediately after
the previous one is deleted.
2.4.13) URS-13: The registered user can select the jewelry model to customize.
SRS-33: The system shall provide the list of jewelry mockups with the “Custom”
buttons.
SRS-49: The system shall display the model from the image to 3d after the model
has been converted with the “Custom” button in the navigation sidebar.
SRS-50: When the registered user clicks the “Custom” button in the navigation
sidebar, the system shall redirect and load the selected mockup or the converted
model into the customization jewelry page.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 232
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.14) URS-14: The registered user can use the converted image to 3d model to
customize by clicking the ‘Custom’ button in the navigation sidebar after the model
is converted successfully.
SRS-49: The system shall display the model from the image to 3d after the model
has been converted with the ‘Custom’ button in the navigation sidebar.
SRS-51: When the registered user clicks the "Custom" button, the system shall
redirect and load the model into the customization jewelry page.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.15) URS-15: The registered user can view the selected jewelry model in the
model viewer.
SRS-52: The system shall display the selected jewelry model in the model viewer
when the registered user chooses the model to customize.
SRS-53: The system shall render the 3D model using a WebGL-compatible
viewer.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.16) URS-16: The registered user can customize the jewelry model, including
color, material, and size clicking the “Custom” button in the navigation sidebar.
SRS-54: The system shall display the jewelry model in the model viewer with the
“Custom” button.
SRS-55: When the registered user clicks the "Custom" button in the navigation
sidebar, the system shall redirect and load the model into the jewelry
customization page with the customization options.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.17) URS-17: The registered user can customize the name of the jewelry model to
a new desired name.
SRS-56: The system shall provide a “Jewelry Customization” page that includes
an input field for editing the jewelry model’s name.
SRS-57: The system shall display the current name of the jewelry model in the
input field when the page loads.
SRS-58: The system shall update the displayed name in the input field.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 233
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.18) URS-18: Registered user can customize the color of the jewelry model and
can preview the color changes in real-time.
SRS-59: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes a color dropdown on the customization
sidebar.
SRS-60: The system shall immediately apply and render the color to the jewelry
model in real-time when the registered user selects a color.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.19) URS-19: The registered user can customize the material of the jewelry model
and can preview the material changes in real-time.
SRS-61: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes a material dropdown on the customized
sidebar.
SRS-62: The system shall immediately apply and render the material to the
jewelry model in real-time when the registered user selects a material.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.20) URS-20: The registered user can customize the size of the jewelry model and
can preview the size changes in real-time.
SRS-63: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes a slider on the customized sidebar.
SRS-64: The system shall immediately render the size to the jewelry model in
real-time when the registered user drags the slider.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.21) URS-21: The registered user can customize the color of specific parts of a
jewelry model by cropping the part that they want.
SRS-65: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes the “Crop” button in the bottom bar.
SRS-66: The system shall enable the registered user to define a customized area
on the 3D model by dragging to create a crop box.
SRS-67: The system shall highlight the selected cropped area during dragging.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 234
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-68: The system shall allow the registered user to choose a new color and
apply it to the cropped area in real-time.
SRS-69: The system shall update and render the affected part of the model with
the selected color.
SRS-70: The system shall display message “Please drag on the model area to
apply customization” when the registered user drags the selected area outside the
jewelry model.
SRS-71: The system shall provide a “Cancel Crop” button that ends the crop
mode and preserves the recolored area.
SRS-72: The system shall discard the selected color when the registered user
clicks outside the cropped area.
SRS-73: The system shall support consecutive cropping actions after exiting a
previous crop mode.
2.4.22) URS-22: The registered user can customize the material of specific parts of a
jewelry model by cropping the part that they want.
SRS-65: The system shall provide a “Jewelry Customization” or “Image to 3d
Customization” page that includes the “Crop” button in the bottom bar.
SRS-66: The system shall enable the registered user to define a customized area
on the 3D model by dragging to create a crop box.
SRS-67: The system shall highlight the selected cropped area during dragging.
SRS-74: The system shall allow the registered user to choose a new material and
apply it to the cropped area in real-time.
SRS-75: The system shall update and render the affected part of the model with
the selected material.
SRS-70: The system shall display message “Please drag on the model area to
apply customization” when the registered user drags the selected area outside the
jewelry model.
SRS-76: The system shall provide a “Cancel Crop” button that ends the crop
mode and preserves the material change area.
SRS-77: The system shall cancel the crop and discard the selected material when
the registered user clicks outside the cropped area.
SRS-73: The system shall support consecutive cropping actions after exiting a
previous crop mode.
2.4.23) URS-23: The registered user can zoom in and zoom out of the jewelry model
to closely examine design details or view the entire piece more clearly.
SRS-78: The system shall display "Zoom In" and "Zoom Out" buttons in the
bottom action bar on the “Jewelry Customization” or “Image to 3d
Customization” pages.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 235
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-79: The system shall detect the zoom action and update the model viewer
accordingly based on the user's use of the "Zoom In" and "Zoom Out" buttons.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.24) URS-24: The registered user can view the selected packaging model in the
model viewer.
SRS-80: The system shall display the selected packaging model in the model
viewer when the registered user chooses the model to customize.
SRS-53: The system shall render the 3D model using a WebGL-compatible
viewer.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.25) URS-25: The registered user can customize the packaging model, including
changing the color and adding engraved text from the navigation sidebar.
SRS-81: The system shall display the packaging model in the model viewer with
the “Custom” button.
SRS-82: When the registered user clicks the "Custom" button in the navigation
sidebar, the system shall redirect and load the model into the packaging
customization page with the customization options.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.26) URS-26: The registered user can change the color of the packaging model by
selecting a color from a system-provided palette, entering a hex color code, or
choosing a custom color from the color picker tool. The selected color is applied in
real-time to the packaging preview.
SRS-83: The system shall display a color palette, an input field for hex color
code, and a color picker tool when the user clicks the “Custom” button in the
navigation sidebar.
SRS-84: The system shall allow the registered user to choose a color from the
palette, input a hex code, or select a custom color.
SRS-85: The system shall validate the input hex color to determine whether the
input is in the correct hex color format or not.
SRS-86: The system shall apply the selected color to the packaging model in the
model viewer area.
SRS-87: The system shall display a message “Invalid color code. Please enter a
valid hex code or select a color from the palette” if registered user inputs an
invalid hex color format.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 236
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.27) URS-27: The registered user can add engraved text to the selected packaging
model includes entering the text, choosing font style, font size, and dragging the text
to the desired position.
SRS-88: The system shall display a customization panel, including an input field,
font style dropdown, font size selector, and color picker, when the registered user
clicks the “Custom” button in the sidebar of the packaging customization page.
SRS-89: The system shall allow the registered user to enter custom engraving text
into the input field, select a font style from a dropdown menu, adjust the font size
using a font size selector, and select a text color using a color picker tool.
SRS-90: The system shall render the engraved text on the packaging model in the
model viewer area with the selected font style, font size, and color.
SRS-91: The system shall allow the registered user to drag the engraved text to
the desired position on the packaging model.
SRS-92: The system shall update the text position in the model viewer in real
time as the registered user drags the text.
SRS-93: The system shall remove the engraved text from the model viewer and
reset the engraving state when the registered user clears the input field.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.28) URS-28: The registered user can select and apply a new packaging model to
replace an existing one.
SRS-94: The system shall display a list of packaging mockup thumbnails and
displays in the sidebar of the packaging customization page.
SRS-95: The system shall highlight selection on the new packaging model
thumbnail when the registered user selects the new one.
SRS-96: The system shall replace the old packaging with the new one and update
the model viewer.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.29) URS-29: The registered user can choose the saved jewelry from their
workspace to try on with the selected packaging model.
SRS-97: The system shall display a list of saved jewelry thumbnails from the
registered user’s workspace when the user clicks the “My Jewelry” button in the
sidebar of the packaging customization page.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 237
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-98: The system shall allow the registered user to select one jewelry item
from the list of saved jewelry.
SRS-99: The system shall render the selected jewelry model together with the
currently applied packaging in the model viewer.
SRS-100: The system shall display a message “You don’t have any jewelry in
your workspace yet.” if there are no saved jewelry items in the user’s workspace.
SRS-101: The system displays message “Oops! This jewelry doesn’t fit with the
current package. Try selecting a matching type.” if the packaging type and the
selected jewelry item mismatch.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.30) URS-30: The registered user can zoom in and zoom out of the packaging
model to closely examine design details or view the entire piece more clearly.
SRS-102: The system shall display "Zoom In" and "Zoom Out" buttons in the
bottom action bar on the “Packaging Customization” pages.
SRS-79: The system shall detect the zoom action and update the model viewer
accordingly based on the user's use of the "Zoom In" and "Zoom Out" buttons.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.31) URS-31: The registered user can select the type of selected body on which
the jewelry will be virtually tried-on.
SRS-103: The system shall display a “Virtual Try-On” button in the bottom bar.
SRS-104: The system shall display a “Neck Try-On” and “Wrist Try-On” button
after clicking on the virtual try-on button to allow the registered user to select the
type of simulated body.
SRS-105: The system shall display the neck model when the registered user
selects “Neck Try-On” button.
SRS-106: The system shall display the wrist model when the registered user
selects “Wrist Try-On” button.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.32) URS-32: The registered user can view the jewelry on the simulated body
(neck or wrist) in the model viewer.
SRS-107: The system shall display a “Virtual Try-On” button in the bottom bar.
SRS-108: The system shall display a “Neck Try-On” and “Wrist Try-On” button
after clicking on the virtual try-on button to allow the registered user to select the
type of simulated body.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 238
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-109: The system shall display the neck model when the registered user
selects “Neck Try-On” button.
SRS-110: The system shall display the wrist model when the registered user
selects “Wrist Try-On” button.
SRS-111: The system shall validate whether the jewelry type and the simulated
body type match.
SRS-112: The system shall display necklace jewelry to match the neck model.
SRS-113: The system shall display bracelet jewelry to match the wrist model.
SRS-114: The system shall display message “Try-on is not supported for this
type” if the jewelry model type and the simulated body type mismatch.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.33) URS-33: The registered user can view a list of all previously designed work
in their personal workspace.
SRS-115: When the registered user clicks on the “Workspace” button,
the system shall validate the user session and navigate to the
“Workspace” page.
SRS-116: The system shall display all previously saved designs with the
associated data, including the 3D model preview, designed name, and date and
time created.
SRS-117: The system shall display a message “No design saved yet” if the
system doesn’t have designs saved.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.34) URS-34: The registered user can create a new design to save in their
workspace.
SRS-118: When the registered user clicks on the “Create new design” button, the
system shall navigate to the “Image to 3D” page and provide the “Upload Form”
with a “Generate” button that the registered user can create the new design and
save the converted model design to the user’s workspace in the database.
2.4.35) URS-35: The registered user can save the designed work to their workspace
when the design is successful.
SRS-119: When the registered user clicks on the “Save to workspace” button, the
system shall save the design to the user’s workspace in the database.
SRS-120: The system shall display the message “Your design has been saved”
after a successful save.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 239
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.36) URS-36: The registered user can save the designed work from the predefined
jewelry mockup to their workspace when the jewelry design is successful.
SRS-121: When the registered user clicks on the “Save to workspace”
button on the “Jewelry Mockups” or “Jewelry Customization” page,
the system shall save the designed work from the predefined jewelry
mockup to the user’s workspace in the database.
SRS-120: The system shall display the message “Your design has been saved”
after a successful save.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.37) URS-37: The registered user can save the designed work from the converted
image to 3d model to their workspace when the model design is successful.
SRS-122: When the registered user clicks on the “Save to workspace” button on
the “Image to 3d” or “Image to 3d Customization” page, the system shall save the
converted image to 3d model to the user’s workspace in the database.
SRS-120: The system shall display the message “Your design has been saved”
after a successful save.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
2.4.38) URS-38: The registered user can save the designed work from the predefined
packaging mockup to their workspace when the packaging design is successful or
try-on the jewelry with the packaging.
SRS-123: When the registered user clicks on the “Save to workspace” button on
the “Packaging Mockups” or “Packaging Customization” page, the system shall
save the predefined packaging mockup or the tried-on jewelry with the packaging
to the user’s workspace in the database.
SRS-120: The system shall display the message “Your design has been saved”
after a successful save.
SRS-13: The system shall display a message “The system cannot connect to the
database. Please try again later.” if the system cannot connect to the database.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 240
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.4.39) URS-39: The registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a PNG or a JPG.
SRS-124: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export image in PNG or JPG format.
SRS-125: When the registered user selects the desired format, the system shall
generate the image file according to the selected format.
SRS-126: The system shall trigger the download of the generated image file to
the registered user’s computer.
SRS-127: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “Failed to export image.
Please try again”.
2.4.40) URS-40: Registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a PNG (transparent background).
SRS-128: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export PNG format.
SRS-129: The system shall display the “Export as PNG” button for downloading
the image.
SRS-130: The system shall generate and download an image file in PNG format
named model_snapshot.png to the registered user’s computer.
SRS-127: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “Failed to export image.
Please try again”
2.4.41) URS-41: Registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a JPG (white background).
SRS-131: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export JPG format.
SRS-132: The system shall display the “Export as JPG” button for downloading
the image.
SRS-133: The system shall generate and download an image file in JPG format
named model_snapshot.jpg to the registered user’s computer.
SRS-127: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “Failed to export image.
Please try again”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 241
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.4.42) URS-42: Registered users can export their customized designs, including
jewelry, packaging, or a combination of both, as detailed PDF reports.
SRS-134: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the generation of a PDF report.
SRS-135: The system shall display the “Generate PDF Report” button for
downloading a PDF report.
SRS-136: The system shall generate a PDF report with details such as model
name, export date, jewelry details, packaging details, and a preview image of the
model
SRS-137: The system shall download the PDF report to the registered user's
computer, according to the model type: jewelryName_customization.pdf for
jewelry export, packageName_customization.pdf for packaging export,
jewelryName_packageName_Customization.pdf for combined jewelry and
packaging export.
SRS-138: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “Failed to export PDF report.
Please try again.”
2.4.43) URS-43: Registered users can export 3D models displayed in the model
viewer to various 3D file formats, including STL, OBJ, and GLB format.
SRS-139: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export 3d file in STL, OBJ or GLB format.
SRS-140: When the registered user selects the desired format, the system shall
generate the 3d file according to the selected format.
SRS-141: The system shall download the 3d file (STL, OBJ, GLB) to the
registered user’s computer.
SRS-142: If the renderer, scene, or camera is not available in the model viewer
during export, the system shall display the message “No model to export”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 242
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

2.4.44) URS-44: Registered users can export 3D models displayed in the model
viewer in STL format.
SRS-143: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export 3d file in STL format.
SRS-144: The system shall display the “Export as STL” button for downloading
an STL file.
SRS-145: The system shall generate and download a 3d file in STL format to the
registered user’s computer.
SRS-146: If the model is not available in the model viewer, the system shall
display the message “No model to export as STL.”
2.4.45) URS-45: Registered users can export 3D models displayed in the model
viewer in OBJ format.
SRS-147: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export 3d file in OBJ format.
SRS-148: The system shall display the “Export as OBJ” button for downloading
the OBJ file.
SRS-149: The system shall generate and download a 3d file in OBJ format to the
registered user’s computer.
SRS-150: If the model is not available in the model viewer, the system shall
display the message “No model to export as OBJ.”
2.4.46) URS-46: Registered users can export 3D models displayed in the model
viewer in GLB format.
SRS-151: When the registered user clicks on the “Super Export” button on the
“Mockups” or “Customization” page, the system shall display a modal to select
the export 3d file in GLB format.
SRS-152: The system shall display the “Export as GLB” button for downloading
the GLB file.
SRS-153: The system shall generate and download the GLB file to the registered
user’s computer.
SRS-154: If the model is not available in the model viewer, the system shall
display the message “No model to export as GLB.”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 243
Name Software_Requirement_
Specification_V.1.0
Document Software Requirement Release 20/10/2025 Print 20/10/2025
Type Specification Date Date

---

Chapter 4
Software Design Development

---

Document History
Document Version History Status Date Editable Reviewer
Name
3DJewelryCraft_ 3DJewelryCraft_ Add Chapter 1 Draft 20/05/2025 NP1, SW
Software_Design_ Software_Design_ Add Chapter 2 NP2
Development_ Development_ Add Chapter 3

## V.0.1 V.0.1

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 21/05/2025 NP1, SW
Software_Design_ Software_Design_ Update Chapter 2 NP2
Development_ Development_

## V.0.2 V.0.2

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 3 Draft 22/05/2025 NP1, SW
Software_Design_ Software_Design_ NP2
Development_ Development_

## V.0.3 V.0.3

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 24/05/2025 NP1, SW
Software_Design_ Software_Design_ Update Chapter 2 NP2
Development_ Development_ Update Chapter 3

## V.0.4 V.0.4

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 2 Draft 26/05/2025 NP1, SW
Software_Design_ Software_Design_ NP2
Development_ Development_

## V.0.5 V.0.5

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 29/06/2025 NP1, SW
Software_Design_ Software_Design_ Update Chapter 2 NP2
Development_ Development_ Update Chapter 3

## V.0.6 V.0.6

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 3 Draft 24/08/2025 NP1, SW
Software_Design_ Software_Design_ NP2
Development_ Development_

## V.0.7 V.0.7

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 28/08/2025 NP1, SW
Software_Design_ Software_Design_ Update Chapter 2 NP2
Document 3DJewelryCraft_ Owner NP1, NP2 Page 245
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Devvelopment Date

---

Development_ Development_ Update Chapter 3

## V.0.8 V.0.8

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 30/08/2025 NP1, SW
Software_Design_ Software_Design_ Update Chapter 2 NP2
Development_ Development_ Update Chapter 3

## V.0.9 V.0.9

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Final 18/10/2025 NP1, SW
Software_Design_ Software_Design_ Update Chapter 2 NP2
Development_ Development_ Update Chapter 3

## V.1.0 V.1.0

*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_ Owner NP1, NP2 Page 246
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Devvelopment Date

---


## TABLE OF CONTENTS

Document History ..................................................................................................................... 245
TABLE OF CONTENTS ......................................................................................................... 247
1.1) Purpose ........................................................................................................................... 254
1.2) Scope ............................................................................................................................... 254
1.3) User Characteristics ...................................................................................................... 254
1.4) Acronyms and Definitions............................................................................................. 255
1.4.1) Acronyms ................................................................................................................. 255
1.4.2) Definitions................................................................................................................ 255
Chapter Two | System Architecture ........................................................................................ 258
Chapter Three | Detail Design ................................................................................................. 260
3.1) Entity Relationship Diagram for the database ........................................................... 260
3.2) Class Diagram ................................................................................................................ 261
3.2.1) Register ..................................................................................................................... 261
3.2.2) Log in ........................................................................................................................ 261
3.2.3) View all of the jewelry mockups .............................................................................. 262
3.2.4) View all of the packaging mockups ......................................................................... 262
3.2.5) View the jewelry mockups by category ................................................................... 262
3.2.6) View the packaging mockups by category ............................................................... 263
3.2.7) Use the predefined jewelry mockups to customize .................................................. 263
3.2.8) Use the predefined packaging mockups to customize .............................................. 263
3.2.9) Upload an Image to convert to 3D............................................................................ 264
3.2.10) Select the jewelry model to customize ................................................................... 264
3.2.11) Use the converted image to 3d to customize .......................................................... 264
3.2.12) View the jewelry model .......................................................................................... 265
3.2.13) Customize the color of specific jewelry sections ................................................... 265
3.2.14) Customize the material of specific jewelry sections .............................................. 265
3.2.15) View the packaging model ..................................................................................... 266
3.2.16) Replace with a new packaging model .................................................................... 266
3.2.17) Choose the jewelry to try-on with packaging ......................................................... 266
3.2.18) View the jewelry on the simulated body ................................................................ 267
3.2.19) View all previously designed works ....................................................................... 267

---

3.2.20) Create a new design ................................................................................................ 267
3.2.21) Save the designed work .......................................................................................... 268
3.2.22) Save the designed work from the predefined jewelry mockup .............................. 268
3.2.23) Save the designed work from the converted image to 3d model ............................ 268
3.2.24) Save the designed work from the predefined packaging mockup .......................... 269
3.3) Sequence Diagram ......................................................................................................... 270
3.3.1) SD-01: Register ........................................................................................................ 270
3.3.2) SD-02: Log in ........................................................................................................... 271
3.3.3) SD:03: Log out ......................................................................................................... 272
3.3.4) SD-04: View all of the jewelry mockups ................................................................. 273
3.3.5) SD-05: View all of the packaging mockups ............................................................. 273
3.3.6) SD-06: View the jewelry mockups by category ....................................................... 274
3.3.7) SD-07: View the packaging mockups by category .................................................. 275
3.3.8) SD-08: Use the predefined jewelry mockups to customize ...................................... 276
3.3.9) SD-09: Use the predefined packaging mockups to customize ................................. 276
3.3.10) SD-10: Upload an Image to convert to 3D ............................................................. 277
3.3.11) SD-11: Create the name of the design .................................................................... 278
3.3.12) SD-12: Delete the uploaded image ......................................................................... 279
3.3.13) SD-13: Select the jewelry model to customize ....................................................... 280
3.3.14) SD-14: Use the converted image to 3d model to customize ................................... 280
3.3.15) SD-15: View the jewelry model ............................................................................. 281
3.3.16) SD-16: Customize the name of the jewelry model ................................................. 281
3.3.17) SD-17: Customize the color of the jewelry model ................................................. 282
3.3.18) SD-18: Customize the material of the jewelry model ............................................ 282
3.3.19) SD-19: Customize the size of the jewelry model ................................................... 283
3.3.20) SD-20: Customize the color of specific jewelry sections ....................................... 284
3.3.21) SD-21: Customize the material of specific jewelry sections .................................. 285
3.3.21) SD-22: View the packaging model ......................................................................... 286
3.3.23) SD-23: Customize the color of the packaging model ............................................. 286
3.3.24) SD-24: Add engraved text to the packaging model ................................................ 287
3.3.25) SD-25: Replace with a new packaging model ........................................................ 288
3.3.26) SD-26: Choose the jewelry to try-on with package ................................................ 289
3.3.27) SD-27: Select the type of simulated body to try on ................................................ 290
3.3.28) SD-28: View the jewelry on the simulated body .................................................... 291

---

3.3.29) SD-29: View all previously designed works .......................................................... 292
3.3.30) SD-30: Create a new design ................................................................................... 293
3.3.31) SD-31: Save the designed work.............................................................................. 294
3.3.32) SD-32: Save the designed work from the predefined jewelry mockup .................. 295
3.3.33) SD-33: Save the designed work from the converted image to 3d model ............... 296
3.3.34) SD-34: Save the designed work from the predefined packaging mockup ............. 297
3.3.35) SD-35: Export image as PNG format ..................................................................... 298
3.3.36) SD-36: Export image as JPG format ...................................................................... 299
3.3.37) SD-37: Export the model as PDF report ................................................................. 300
3.3.38) SD-38: Export 3D file as STL file .......................................................................... 301
3.3.39) SD-39: Export 3D file as OBJ format .................................................................... 302
3.3.40) SD-40: Export 3D file as GLB format .................................................................... 303
3.4) UI Design ........................................................................................................................ 304
3.3.1) UI-01: Register ......................................................................................................... 304
3.3.2) UI-02: Log in ............................................................................................................ 305
3.3.3) UI-03: Log out .......................................................................................................... 306
3.3.4) UI-04: View all of the jewelry mockups .................................................................. 307
3.3.5) UI-05: View all of the packaging mockups .............................................................. 308
3.3.6) UI-06: View the jewelry mockups by category ........................................................ 309
3.3.7) UI-07: View the packaging mockups by category ................................................... 310
3.3.8) UI-08: Use the predefined jewelry mockup to customize ........................................ 312
3.3.9) UI-09: Use the predefined packaging mockup to customize .................................... 313
3.3.10) UI-10: Upload an Image to convert to 3D .............................................................. 314
3.3.11) UI-11: Create the name of the design ..................................................................... 315
3.3.12) UI-12: Delete the uploaded image .......................................................................... 316
3.3.13) UI-13: Select the jewelry model to customize ........................................................ 317
3.3.14) UI-14: Use the converted image to 3d model to customize ................................... 318
3.3.15) UI-15: View the jewelry model .............................................................................. 318
3.3.16) UI-16: Customize the jewelry model ...................................................................... 319
3.3.17) UI-17: Customize the name of the jewelry model .................................................. 320
3.3.18) UI-18: Customize the color of the jewelry model .................................................. 320
3.3.19) UI-19: Customize the material of the jewelry model ............................................. 321
3.3.20) UI-20: Customize the size of the jewelry model .................................................... 321
3.3.21) UI-21: Customize the color of specific jewelry sections ........................................ 322

---

3.3.22) UI-22: Customize the material of specific jewelry sections ................................... 323
3.3.23) UI-23: Zoom in and zoom out the jewelry model .................................................. 324
3.2.24) UI-24: View the packaging model.......................................................................... 325
3.2.25) UI-25: Customize the packaging model ................................................................. 325
3.2.26) UI-26: Customize the color of the packaging model .............................................. 326
3.2.27) UI-27: Add engraved text to the packaging model ................................................. 326
3.2.28) UI-28: Replace with a new packaging model ......................................................... 327
3.2.29) UI-29: Choose the jewelry to try on with packaging.............................................. 327
3.2.30) UI-30: Zoom in and zoom out the packaging model .............................................. 328
3.2.31) UI-31: Select the type of simulated body to try on ................................................. 328
3.2.32) UI-32: View the jewelry on the simulated body..................................................... 329
3.2.33) UI-33: View all previously designed works ........................................................... 330
3.2.34) UI-34: Create a new design .................................................................................... 331
3.2.35) UI-35: Save the designed work .............................................................................. 332
3.2.36) UI-36: Save the designed work from the predefined jewelry mockup ................... 334
3.2.37) UI-37: Save the designed work from the converted image to 3d model ................ 335
3.2.38) UI-38: Save the designed work from the predefined packaging mockup .............. 336
3.2.39) UI-39: Export image as PNG format ...................................................................... 337
3.2.40) UI-40: Export image as JPG format ....................................................................... 338
3.2.41) UI-41: Export the model as PDF report.................................................................. 339
3.2.42) UI-42: Export 3D file as STL format ..................................................................... 340
3.2.43) UI-43: Export 3D file as OBJ format ..................................................................... 341
3.2.44) UI-44: Export 3D file as GLB format .................................................................... 342

---


## LIST OF FIGURES

Figure 80: System Architecture .................................................................................................. 258
Figure 81: Entity Relationship Diagram ..................................................................................... 260
Figure 82: CD - Register ............................................................................................................. 261
Figure 83: CD - Log in................................................................................................................ 261
Figure 84: CD - View all of the jewelry mockups ...................................................................... 262
Figure 85: CD - View all of the packaging mockups ................................................................. 262
Figure 86: CD - View the jewelry mockups by category ........................................................... 262
Figure 87: CD - View the packaging mockups by category ....................................................... 263
Figure 88: CD – Use the predefined jewelry mockups to customize ......................................... 263
Figure 89: CD - Use the predefined packaging mockups to customize ...................................... 263
Figure 90: CD - Upload an Image to convert to 3D ................................................................... 264
Figure 91: CD – Select the jewelry model to customize ............................................................ 264
Figure 92: CD – Use the converted image to 3d to customize ................................................... 264
Figure 93: CD - View the jewelry model.................................................................................... 265
Figure 94: CD - Customize the color of specific jewelry sections ............................................. 265
Figure 95: CD - Customize the material of specific jewelry sections ........................................ 265
Figure 96: CD - View the packaging model ............................................................................... 266
Figure 97: CD - Replace with a new packaging model .............................................................. 266
Figure 98: CD - Choose the jewelry to try-on with packaging ................................................... 266
Figure 99: CD - View the jewelry on the simulated body .......................................................... 267
Figure 100: CD - View all previously designed works ............................................................... 267
Figure 101: CD - Create a new design ........................................................................................ 267
Figure 102: CD – Save the designed work ................................................................................. 268
Figure 103: CD – Save the designed work from the predefined jewelry mockup ...................... 268
Figure 104: CD – Save the designed work from the converted image to 3d model ................... 268
Figure 105: CD – Save the designed work from the predefined packaging mockup ................. 269
Figure 106: SD - Register ........................................................................................................... 270
Figure 107: SD - Log in .............................................................................................................. 271
Figure 108: SD - Log out ............................................................................................................ 272
Figure 109: SD - View all of the jewelry mockups .................................................................... 273
Figure 110: SD - View all of the packaging mockups ................................................................ 273
Figure 111: SD - View the jewelry mockups by category .......................................................... 274
Figure 112: SD - View the packaging mockups by category ..................................................... 275
Figure 113: SD - Use the predefined jewelry mockups to customize......................................... 276
Figure 114: SD - Use the predefined packaging mockups to customize .................................... 276
Figure 115: SD - Upload an Image to convert to 3D .................................................................. 277
Figure 116: SD - Create the name of the design ......................................................................... 278
Figure 117: SD - Delete the uploaded image .............................................................................. 279
Figure 118: SD - Select the jewelry model to customize ............................................................ 280
Figure 119: SD - Use the converted image to 3d model to customize ....................................... 280
Figure 120: SD - View the jewelry model .................................................................................. 281
Figure 121: SD - Customize the name of the jewelry model ...................................................... 281

---

Figure 122: SD - Customize the color of the jewelry model ...................................................... 282
Figure 123: SD - Customize the material of the jewelry model ................................................. 282
Figure 124: SD - Customize the size of the jewelry model ........................................................ 283
Figure 126: SD - Customize the color of specific jewelry sections ............................................ 284
Figure 127: SD - Customize the material of specific jewelry sections ....................................... 285
Figure 128: SD - View the packaging model .............................................................................. 286
Figure 129: SD - Customize the color of the packaging model .................................................. 286
Figure 130: SD - Add engraved text to the packaging model..................................................... 287
Figure 131: SD - Replace with a new packaging model ............................................................. 288
Figure 132: SD - Choose the jewelry to try-on with package..................................................... 289
Figure 133: SD – Select the type of simulated body to try on .................................................... 290
Figure 134: SD – View the jewelry on the simulated body ........................................................ 291
Figure 135: SD – View all previously designed works .............................................................. 292
Figure 136: SD – Create a new design........................................................................................ 293
Figure 137: SD – Save the designed work .................................................................................. 294
Figure 138: SD – Save the designed work from the predefined jewelry mockup ...................... 295
Figure 139: SD – Save the designed work from the converted image to 3d model ................... 296
Figure 140: SD – Save the designed work from the predefined packaging mockup .................. 297
Figure 141: SD – Export image as PNG format ......................................................................... 298
Figure 142: SD – Export image as JPG format........................................................................... 299
Figure 143: SD – Export the model as PDF report ..................................................................... 300
Figure 144: SD – Export 3D file as STL file .............................................................................. 301
Figure 145: SD – Export 3D file as OBJ format ......................................................................... 302
Figure 146: SD – Export 3D file as GLB format ........................................................................ 303
Figure 147: UI - Register ............................................................................................................ 304
Figure 148: UI - Log in ............................................................................................................... 305
Figure 149: UI - Log out ............................................................................................................. 306
Figure 150: UI – View all of the jewelry mockups .................................................................... 307
Figure 151: UI – View all of the packaging mockups ................................................................ 308
Figure 152: UI – View the jewelry mockups by category .......................................................... 309
Figure 153: UI – View the packaging mockups by category ..................................................... 311
Figure 154: UI - Use the predefined jewelry mockup to customize ........................................... 312
Figure 155: UI - Use the predefined packaging mockup to customize ...................................... 313
Figure 156: UI – Upload an image to convert to 3D .................................................................. 314
Figure 157: UI – Create the name of the design ......................................................................... 315
Figure 158: UI – Delete the uploaded image .............................................................................. 316
Figure 159: UI – Select the jewelry model to customize............................................................ 317
Figure 160: UI – Use the converted image to 3d model to customize ........................................ 318
Figure 161: UI – View the jewelry model .................................................................................. 318
Figure 162: UI – Customize the jewelry model ......................................................................... 319
Figure 163: UI – Customize the name of the jewelry model ...................................................... 320
Figure 164: UI – Customize the color of the jewelry model ...................................................... 320
Figure 165: UI – Customize the material of the jewelry model ................................................. 321
Figure 166: UI – Customize the size of the jewelry model ........................................................ 321
Figure 167: UI – Customize the color of specific jewelry sections ............................................ 323
Figure 168: UI – Customize the material of specific jewelry sections ....................................... 323

---

Figure 169: UI – Zoom in and zoom out the jewelry model ...................................................... 324
Figure 170: UI – View the packaging model.............................................................................. 325
Figure 171: UI – Customize the packaging model ..................................................................... 325
Figure 172: UI – Customize the color of the packaging model .................................................. 326
Figure 173: UI – Add engraved text to the packaging model..................................................... 326
Figure 174: UI – Replace with a new packaging model ............................................................. 327
Figure 175: UI – Choose the jewelry to try on with packaging ................................................. 327
Figure 176: UI – Zoom in and zoom out the packaging model .................................................. 328
Figure 177: UI – Select the type of simulated body to try on .................................................... 328
Figure 178: UI – View the jewelry on the simulated body......................................................... 329
Figure 179: UI – View all previously designed works ............................................................... 330
Figure 180: UI – Create a new design ........................................................................................ 331
Figure 181: UI – Save the designed work .................................................................................. 333
Figure 182: UI – Save the designed work from the predefined jewelry mockup ....................... 334
Figure 183: UI – Save the designed work from the converted image to 3d model .................... 335
Figure 184: UI – Save the designed work from the predefined packaging mockup .................. 336
Figure 185: UI – Export image as PNG format .......................................................................... 337
Figure 186: UI – Export image as JPG format ........................................................................... 338
Figure 187: UI – Export the model as PDF report ..................................................................... 339
Figure 188: UI – Export 3D file as STL format ......................................................................... 340
Figure 189: UI – Export 3D file as OBJ format ......................................................................... 341
Figure 190: UI – Export 3D file as GLB format ........................................................................ 342

---

Chapter One | Introduction
1.1) Purpose
The purpose of the software design document is to present a software design of
the “3DJewelrycraft” project. This document contains the outline of the software
architecture and a detailed description of what is to be built and how it is expected to be
built. It is intended to provide several views of the system and information necessary for
the implementation.
1.2) Scope
• Describe the software architecture of this project.
• Describe the function used in this project.
• Define sequence diagram and user interface of the
o Feature#1: Register
o Feature#2: Jewelry and Packaging Mockups
o Feature#3: Image to 3D
o Feature#4: Customization
o Feature#5: Virtual Try-On
o Feature#6: Workspace
o Feature#7: Super Export
1.3) User Characteristics
Title Definition
The people who are not registered to the
system. These users can only browse and
preview mockups available on the platform.
Unregistered User
They typically include curious creatives who
are exploring the idea of designing custom
jewelry.
The people who have already registered and
logged in to the web application. These users
range from beginner jewelry entrepreneurs
Registered User looking to launch a brand with minimal
technical skills, to self-expressive, trend-
conscious individuals who value aesthetic
freedom without needing a full design team.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 254
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

The people who interact with the
User 3DJewelryCraft system. This can include both
unregistered and registered user.
1.4) Acronyms and Definitions
1.4.1) Acronyms
UI User Interface
UC Use Case
CD Class Diagram
SD Sequence Diagram
2D Two Dimension
3D Three Dimension
URL Uniform Resource Locator
HTTP Hypertext Transfer Protocol
PNG Portable Network Graphics
JPG Joint Photographic Experts Group
PDF Portable Document Format
STL Stereolithography
OBJ Wavefront Object
GLB GL Transmission Format Binary file
1.4.2) Definitions
Title Definition
The web application that transforms 2D
jewelry designs into customizable 3D models,
3DJewelryCraft
allowing users to visualize, personalize, and
export their creations.
The people who are not registered to the
system. These users can only browse and
preview mockups available on the platform.
Unregistered User
They typically include curious creatives who
are exploring the idea of designing custom
jewelry.
The people who have already registered and
logged in to the web application. These users
Registered User
range from beginner jewelry entrepreneurs
looking to launch a brand with minimal
Document 3DJewelryCraft_ Owner NP1, NP2 Page 255
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

technical skills, to self-expressive, trend-
conscious individuals who value aesthetic
freedom without needing a full design team.
The 3DJewelryCraft web application that
provides users with tools and services to
Platform
create, customize, and interact with 3D
jewelry models.
The pre-designed or visual representation of a
jewelry or packaging item in 3D format,
Mockup
allows to preview of the appearance and
structure of a design.
The 3DJewelryCraft system encompasses all
System components, technologies, and functionalities
provided by 3DJewelryCraft.
A tool or class (commonly from Three.js) that
allows developers to export 3D scenes,
GLTFExporter
meshes, or models into the glTF
(GL Transmission Format) file format.
A predefined mockup is a ready-made 3D
Predefined Mockups model that serves as a template for
showcasing jewelry or packaging designs.
A 3D object generated by processing a 2D
Converted Image to 3D Model
image through the meshy API.
A JavaScript API that allows developers to
create interactive 2D and 3D graphics within
WebGL-compatible viewer a web browser without the need for plugins.
The 3DJewelryCraft system is used to display
the 3d model.
A feature that allows users to isolate and crop
Crop Model specific parts of a 3D model in order to focus
on customizing only the selected area.
A predefined set of colors grouped by theme
Color Palette or style, provided by the system for users to
choose from when customizing the package.
A six-digit alphanumeric code used in web
application to represent colors. It is written
Hex Color Code
with a leading hash symbol (#) followed by
three pairs of characters.
A graphical user interface (GUI) tool that
allows users to select and customize colors,
Color Picker
typically by choosing from a palette, entering
color codes (such as HEX, RGB, or HSL
Document 3DJewelryCraft_ Owner NP1, NP2 Page 256
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

values), or interacting with a spectrum or
slider.
The process of creating a 2D image from a 3D
Renderer
scene.
The virtual environment containing all 3D
Scene
objects.
The virtual viewpoint that frames what is seen
Camera
in the final rendered image.
The component used to display and interact
Model Viewer
with 3D models within an application.
A document automatically generated to
present detailed information about jewelry
PDF Report and packaging mockups. It includes specific
data such as design details, materials, sizes,
colors, and model previews.
A digital file that stores information about a
three-dimensional object, including its shape,
3D File
geometry, and sometimes materials or
textures include STL, OBJ, and GLB.
One of the most common 3D file types used
for 3D printing. It represents the surface
STL Format geometry of a 3D object using a collection of
triangles, without any color, texture, or
material information.
A widely used 3D model format that stores
both the geometry and surface details of an
OBJ Format object. It can also include references to
materials and texture maps, which define the
model’s appearance.
A modern 3D file format optimized for web
and application use. It stores geometry,
GLB Format
materials, textures, lighting, and animations in
a single compact binary file.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 257
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

Chapter Two | System Architecture
Figure 80: System Architecture
Document 3DJewelryCraft_ Owner NP1, NP2 Page 258
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

Description:
1. The system flow begins when the user accesses the web application and proceeds
to register or log in using NextAuth.js, which manages authentication securely and
efficiently on the front-end.
2. Once authenticated, user interacts with the Web Application Services, which are
built using Next.js and integrated with our features.
3. When a user selects to upload a 2D image (e.g., a sketch of jewelry design, a
request is sent via Axios (HTTP client) to the Backend Services, which are powered
by Flask.
4. The back-end then calls the Meshy AI API to convert the 2D sketch into a 3D
model and returns .glb and thumbnail file in the URL as the result. Then, the
temporary .glb and thumbnail are stored in MySQL.
5. The temporary.glb and thumbnail uploads to Firebase Cloud Storage via Flask,
and returns the public URL of .glb and thumbnail back to store in the MySQL for
future access and customization.
6. If the user clicks “Save to Workspace” during customization, the system uses the
three.js GLTFExporter library on the front-end to generate a new .glb file
(reflecting crop, material, or color changes). This .glb file is then sent via Axios to
the back-end. The back-end saves the new .glb public URL along with its metadata
in MySQL, making the custom model accessible in the user’s Workspace.
7. User also have the option to export their model using the Super Export feature.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 259
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

Chapter Three | Detail Design
3.1) Entity Relationship Diagram for the database
Figure 81: Entity Relationship Diagram
Document 3DJewelryCraft_ Owner NP1, NP2 Page 260
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2) Class Diagram
3.2.1) Register
Figure 82: CD - Register
3.2.2) Log in
Figure 83: CD - Log in
Document 3DJewelryCraft_ Owner NP1, NP2 Page 261
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.3) View all of the jewelry mockups
Figure 84: CD - View all of the jewelry mockups
3.2.4) View all of the packaging mockups
Figure 85: CD - View all of the packaging mockups
3.2.5) View the jewelry mockups by category
Figure 86: CD - View the jewelry mockups by category
Document 3DJewelryCraft_ Owner NP1, NP2 Page 262
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.6) View the packaging mockups by category
Figure 87: CD - View the packaging mockups by category
3.2.7) Use the predefined jewelry mockups to customize
Figure 88: CD – Use the predefined jewelry mockups to customize
3.2.8) Use the predefined packaging mockups to customize
Figure 89: CD - Use the predefined packaging mockups to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 263
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.9) Upload an Image to convert to 3D
Figure 90: CD - Upload an Image to convert to 3D
3.2.10) Select the jewelry model to customize
Figure 91: CD – Select the jewelry model to customize
3.2.11) Use the converted image to 3d to customize
Figure 92: CD – Use the converted image to 3d to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 264
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.12) View the jewelry model
Figure 93: CD - View the jewelry model
3.2.13) Customize the color of specific jewelry sections
Figure 94: CD - Customize the color of specific jewelry sections
3.2.14) Customize the material of specific jewelry sections
Figure 95: CD - Customize the material of specific jewelry sections
Document 3DJewelryCraft_ Owner NP1, NP2 Page 265
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.15) View the packaging model
Figure 96: CD - View the packaging model
3.2.16) Replace with a new packaging model
Figure 97: CD - Replace with a new packaging model
3.2.17) Choose the jewelry to try-on with packaging
Figure 98: CD - Choose the jewelry to try-on with packaging
Document 3DJewelryCraft_ Owner NP1, NP2 Page 266
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.18) View the jewelry on the simulated body
Figure 99: CD - View the jewelry on the simulated body
3.2.19) View all previously designed works
Figure 100: CD - View all previously designed works
3.2.20) Create a new design
Figure 101: CD - Create a new design
Document 3DJewelryCraft_ Owner NP1, NP2 Page 267
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.21) Save the designed work
Figure 102: CD – Save the designed work
3.2.22) Save the designed work from the predefined jewelry mockup
Figure 103: CD – Save the designed work from the predefined jewelry mockup
3.2.23) Save the designed work from the converted image to 3d model
Figure 104: CD – Save the designed work from the converted image to 3d model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 268
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.24) Save the designed work from the predefined packaging mockup
Figure 105: CD – Save the designed work from the predefined packaging mockup
Document 3DJewelryCraft_ Owner NP1, NP2 Page 269
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3) Sequence Diagram
3.3.1) SD-01: Register
Figure 106: SD - Register
Document 3DJewelryCraft_ Owner NP1, NP2 Page 270
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.2) SD-02: Log in
Figure 107: SD - Log in
Document 3DJewelryCraft_ Owner NP1, NP2 Page 271
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.3) SD:03: Log out
Figure 108: SD - Log out
Document 3DJewelryCraft_ Owner NP1, NP2 Page 272
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.4) SD-04: View all of the jewelry mockups
Figure 109: SD - View all of the jewelry mockups
3.3.5) SD-05: View all of the packaging mockups
Figure 110: SD - View all of the packaging mockups
Document 3DJewelryCraft_ Owner NP1, NP2 Page 273
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.6) SD-06: View the jewelry mockups by category
Figure 111: SD - View the jewelry mockups by category
Document 3DJewelryCraft_ Owner NP1, NP2 Page 274
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.7) SD-07: View the packaging mockups by category
Figure 112: SD - View the packaging mockups by category
Document 3DJewelryCraft_ Owner NP1, NP2 Page 275
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.8) SD-08: Use the predefined jewelry mockups to customize
Figure 113: SD - Use the predefined jewelry mockups to customize
3.3.9) SD-09: Use the predefined packaging mockups to customize
Figure 114: SD - Use the predefined packaging mockups to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 276
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.10) SD-10: Upload an Image to convert to 3D
Figure 115: SD - Upload an Image to convert to 3D
Document 3DJewelryCraft_ Owner NP1, NP2 Page 277
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.11) SD-11: Create the name of the design
Figure 116: SD - Create the name of the design
Document 3DJewelryCraft_ Owner NP1, NP2 Page 278
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.12) SD-12: Delete the uploaded image
Figure 117: SD - Delete the uploaded image
Document 3DJewelryCraft_ Owner NP1, NP2 Page 279
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.13) SD-13: Select the jewelry model to customize
Figure 118: SD - Select the jewelry model to customize
3.3.14) SD-14: Use the converted image to 3d model to customize
Figure 119: SD - Use the converted image to 3d model to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 280
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.15) SD-15: View the jewelry model
Figure 120: SD - View the jewelry model
3.3.16) SD-16: Customize the name of the jewelry model
Figure 121: SD - Customize the name of the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 281
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.17) SD-17: Customize the color of the jewelry model
Figure 122: SD - Customize the color of the jewelry model
3.3.18) SD-18: Customize the material of the jewelry model
Figure 123: SD - Customize the material of the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 282
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.19) SD-19: Customize the size of the jewelry model
Figure 124: SD - Customize the size of the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 283
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.20) SD-20: Customize the color of specific jewelry sections
Figure 126: SD - Customize the color of specific jewelry sections
Document 3DJewelryCraft_ Owner NP1, NP2 Page 284
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.21) SD-21: Customize the material of specific jewelry sections
Figure 127: SD - Customize the material of specific jewelry sections
Document 3DJewelryCraft_ Owner NP1, NP2 Page 285
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.21) SD-22: View the packaging model
Figure 128: SD - View the packaging model
3.3.23) SD-23: Customize the color of the packaging model
Figure 129: SD - Customize the color of the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 286
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.24) SD-24: Add engraved text to the packaging model
Figure 130: SD - Add engraved text to the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 287
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.25) SD-25: Replace with a new packaging model
Figure 131: SD - Replace with a new packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 288
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.26) SD-26: Choose the jewelry to try-on with package
Figure 132: SD - Choose the jewelry to try-on with package
Document 3DJewelryCraft_ Owner NP1, NP2 Page 289
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.27) SD-27: Select the type of simulated body to try on
Figure 133: SD – Select the type of simulated body to try on
Document 3DJewelryCraft_ Owner NP1, NP2 Page 290
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.28) SD-28: View the jewelry on the simulated body
Figure 134: SD – View the jewelry on the simulated body
Document 3DJewelryCraft_ Owner NP1, NP2 Page 291
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.29) SD-29: View all previously designed works
Figure 135: SD – View all previously designed works
Document 3DJewelryCraft_ Owner NP1, NP2 Page 292
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.30) SD-30: Create a new design
Figure 136: SD – Create a new design
Document 3DJewelryCraft_ Owner NP1, NP2 Page 293
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.31) SD-31: Save the designed work
Figure 137: SD – Save the designed work
Document 3DJewelryCraft_ Owner NP1, NP2 Page 294
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.32) SD-32: Save the designed work from the predefined jewelry mockup
Figure 138: SD – Save the designed work from the predefined jewelry mockup
Document 3DJewelryCraft_ Owner NP1, NP2 Page 295
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.33) SD-33: Save the designed work from the converted image to 3d model
Figure 139: SD – Save the designed work from the converted image to 3d model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 296
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.34) SD-34: Save the designed work from the predefined packaging mockup
Figure 140: SD – Save the designed work from the predefined packaging mockup
Document 3DJewelryCraft_ Owner NP1, NP2 Page 297
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.35) SD-35: Export image as PNG format
Figure 141: SD – Export image as PNG format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 298
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.36) SD-36: Export image as JPG format
Figure 142: SD – Export image as JPG format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 299
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.37) SD-37: Export the model as PDF report
Figure 143: SD – Export the model as PDF report
Document 3DJewelryCraft_ Owner NP1, NP2 Page 300
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.38) SD-38: Export 3D file as STL file
Figure 144: SD – Export 3D file as STL file
Document 3DJewelryCraft_ Owner NP1, NP2 Page 301
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.39) SD-39: Export 3D file as OBJ format
Figure 145: SD – Export 3D file as OBJ format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 302
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.40) SD-40: Export 3D file as GLB format
Figure 146: SD – Export 3D file as GLB format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 303
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.4) UI Design
3.3.1) UI-01: Register
Figure 147: UI - Register
Document 3DJewelryCraft_ Owner NP1, NP2 Page 304
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.2) UI-02: Log in
Figure 148: UI - Log in
Document 3DJewelryCraft_ Owner NP1, NP2 Page 305
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.3) UI-03: Log out
Figure 149: UI - Log out
Document 3DJewelryCraft_ Owner NP1, NP2 Page 306
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.4) UI-04: View all of the jewelry mockups
Figure 150: UI – View all of the jewelry mockups
Document 3DJewelryCraft_ Owner NP1, NP2 Page 307
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.5) UI-05: View all of the packaging mockups
Figure 151: UI – View all of the packaging mockups
Document 3DJewelryCraft_ Owner NP1, NP2 Page 308
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.6) UI-06: View the jewelry mockups by category
Figure 152: UI – View the jewelry mockups by category
Document 3DJewelryCraft_ Owner NP1, NP2 Page 309
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.7) UI-07: View the packaging mockups by category
Document 3DJewelryCraft_ Owner NP1, NP2 Page 310
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

Figure 153: UI – View the packaging mockups by category
Document 3DJewelryCraft_ Owner NP1, NP2 Page 311
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.8) UI-08: Use the predefined jewelry mockup to customize
Figure 154: UI - Use the predefined jewelry mockup to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 312
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.9) UI-09: Use the predefined packaging mockup to customize
Figure 155: UI - Use the predefined packaging mockup to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 313
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.10) UI-10: Upload an Image to convert to 3D
Figure 156: UI – Upload an image to convert to 3D
Document 3DJewelryCraft_ Owner NP1, NP2 Page 314
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.11) UI-11: Create the name of the design
Figure 157: UI – Create the name of the design
Document 3DJewelryCraft_ Owner NP1, NP2 Page 315
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.12) UI-12: Delete the uploaded image
Figure 158: UI – Delete the uploaded image
Document 3DJewelryCraft_ Owner NP1, NP2 Page 316
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.13) UI-13: Select the jewelry model to customize
Figure 159: UI – Select the jewelry model to customize
Document 3DJewelryCraft_ Owner NP1, NP2 Page 317
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.14) UI-14: Use the converted image to 3d model to customize
Figure 160: UI – Use the converted image to 3d model to customize
3.3.15) UI-15: View the jewelry model
Figure 161: UI – View the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 318
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.16) UI-16: Customize the jewelry model
Figure 162: UI – Customize the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 319
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.17) UI-17: Customize the name of the jewelry model
Figure 163: UI – Customize the name of the jewelry model
3.3.18) UI-18: Customize the color of the jewelry model
Figure 164: UI – Customize the color of the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 320
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.19) UI-19: Customize the material of the jewelry model
Figure 165: UI – Customize the material of the jewelry model
3.3.20) UI-20: Customize the size of the jewelry model
Figure 166: UI – Customize the size of the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 321
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.21) UI-21: Customize the color of specific jewelry sections
Document 3DJewelryCraft_ Owner NP1, NP2 Page 322
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

Figure 167: UI – Customize the color of specific jewelry sections
3.3.22) UI-22: Customize the material of specific jewelry sections
Figure 168: UI – Customize the material of specific jewelry sections
Document 3DJewelryCraft_ Owner NP1, NP2 Page 323
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.3.23) UI-23: Zoom in and zoom out the jewelry model
Figure 169: UI – Zoom in and zoom out the jewelry model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 324
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.24) UI-24: View the packaging model
Figure 170: UI – View the packaging model
3.2.25) UI-25: Customize the packaging model
Figure 171: UI – Customize the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 325
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.26) UI-26: Customize the color of the packaging model
Figure 172: UI – Customize the color of the packaging model
3.2.27) UI-27: Add engraved text to the packaging model
Figure 173: UI – Add engraved text to the packaging model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 326
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.28) UI-28: Replace with a new packaging model
Figure 174: UI – Replace with a new packaging model
3.2.29) UI-29: Choose the jewelry to try on with packaging
Figure 175: UI – Choose the jewelry to try on with packaging
Document 3DJewelryCraft_ Owner NP1, NP2 Page 327
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.30) UI-30: Zoom in and zoom out the packaging model
Figure 176: UI – Zoom in and zoom out the packaging model
3.2.31) UI-31: Select the type of simulated body to try on
Figure 177: UI – Select the type of simulated body to try on
Document 3DJewelryCraft_ Owner NP1, NP2 Page 328
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.32) UI-32: View the jewelry on the simulated body
Figure 178: UI – View the jewelry on the simulated body
Document 3DJewelryCraft_ Owner NP1, NP2 Page 329
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.33) UI-33: View all previously designed works
Figure 179: UI – View all previously designed works
Document 3DJewelryCraft_ Owner NP1, NP2 Page 330
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.34) UI-34: Create a new design
Figure 180: UI – Create a new design
Document 3DJewelryCraft_ Owner NP1, NP2 Page 331
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.35) UI-35: Save the designed work
Document 3DJewelryCraft_ Owner NP1, NP2 Page 332
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

Figure 181: UI – Save the designed work
Document 3DJewelryCraft_ Owner NP1, NP2 Page 333
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.36) UI-36: Save the designed work from the predefined jewelry mockup
Figure 182: UI – Save the designed work from the predefined jewelry mockup
Document 3DJewelryCraft_ Owner NP1, NP2 Page 334
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.37) UI-37: Save the designed work from the converted image to 3d model
Figure 183: UI – Save the designed work from the converted image to 3d model
Document 3DJewelryCraft_ Owner NP1, NP2 Page 335
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.38) UI-38: Save the designed work from the predefined packaging mockup
Figure 184: UI – Save the designed work from the predefined packaging mockup
Document 3DJewelryCraft_ Owner NP1, NP2 Page 336
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.39) UI-39: Export image as PNG format
Figure 185: UI – Export image as PNG format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 337
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.40) UI-40: Export image as JPG format
Figure 186: UI – Export image as JPG format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 338
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.41) UI-41: Export the model as PDF report
Figure 187: UI – Export the model as PDF report
Document 3DJewelryCraft_ Owner NP1, NP2 Page 339
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.42) UI-42: Export 3D file as STL format
Figure 188: UI – Export 3D file as STL format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 340
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.43) UI-43: Export 3D file as OBJ format
Figure 189: UI – Export 3D file as OBJ format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 341
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

3.2.44) UI-44: Export 3D file as GLB format
Figure 190: UI – Export 3D file as GLB format
Document 3DJewelryCraft_ Owner NP1, NP2 Page 342
Name Software_Design_
Development_V.1.0
Document Software Design Release 20/10/2025 Print Date 20/10/2025
Type Developemt Date

---

Chapter 5
Test Plan

---

Document History
Document Version History Status Date Editable Reviewer
Name
3DJewelryCraft_ 3DJewelryCraft_ Add Chapter 1 Draft 22/05/2025 NP1, SW
Test_Plan_V.0.1 Test_Plan_V.0.1 Add Chapter 2 NP2
Add Chapter 3
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 22/05/2025 NP1, SW
Test_Plan_V.0.2 Test_Plan_V.0.2 Update Chapter 2 NP2
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 3 Draft 23/05/2025 NP1, SW
Test_Plan_V.0.3 Test_Plan_V.0.3 NP2
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 24/05/2025 NP1, SW
Test_Plan_V.0.4 Test_Plan_V.0.4 Update Chapter 2 NP2
Update Chapter 3
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 2 Draft 10/06/2025 NP1, SW
Test_Plan_V.0.5 Test_Plan_V.0.5 Add Chapter 4 NP2
Update Chapter 4
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 29/06/2025 NP1, SW
Test_Plan_V.0.6 Test_Plan_V.0.6 Update Chapter 2 NP2
Update Chapter 3
Update Chapter 4
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 28/08/2025 NP1, SW
Test_Plan_V.0.7 Test_Plan_V.0.7 Update Chapter 2 NP2
Update Chapter 3
Update Chapter 4
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 30/08/2025 NP1, SW
Test_Plan_V.0.8 Test_Plan_V.0.8 Update Chapter 2 NP2
Update Chapter 3
Update Chapter 4
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Final 18/10/2025 NP1, SW
Test_Plan_V.0.9 Test_Plan_V.0.9 Update Chapter 2 NP2
Update Chapter 3
Update Chapter 4
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_ Owner NP1, NP2 Page 344
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---


## TABLE OF CONTENTS

Document History ..................................................................................................................... 344
TABLE OF CONTENTS ......................................................................................................... 345
Chapter One | Introduction...................................................................................................... 348
1.1) Purpose ........................................................................................................................... 348
1.2) Scope ............................................................................................................................... 348
1.3) User Characteristics ...................................................................................................... 348
1.4) Acronyms and Definitions............................................................................................. 349
Chapter Two | Test Plan and Test Procedures ....................................................................... 351
2.1) Scope of Testing ............................................................................................................. 351
2.2) Test Duration ................................................................................................................. 351
2.3) Test Responsibility ......................................................................................................... 351
2.4) Test Strategy .................................................................................................................. 351
2.5) Test Results .................................................................................................................... 352
2.6) Test Environment .......................................................................................................... 352
Chapter Three | Unit Test ........................................................................................................ 353
3.1) UTC-01: Register ........................................................................................................... 353
3.2) UTC-02: Log in .............................................................................................................. 355
3.3) UTC-03: Log out ............................................................................................................ 356
3.4) UTC-04: View all of the jewelry mockups................................................................... 357
3.5) UTC-05: View all of the packaging mockups .............................................................. 358
3.6) UTC-06: View the jewelry mockups by category ....................................................... 359
3.7) UTC-07: View the packaging mockups by category .................................................. 360
3.8) UTC-08: Use the predefined jewelry mockup to customize ...................................... 361
3.9) UTC-09: Use the predefined packaging mockup to customize ................................. 362
3.10) UTC-10: Upload an image for 3D generation ........................................................... 363
3.11) UTC-11: Generate 3D model from the uploaded image .......................................... 364
3.12) UTC-12: Save GLB File from Meshy API................................................................. 365
3.13) UTC-13: Retrieve GLB URL from Database............................................................ 366
3.14) UTC-14: Create the name of the design .................................................................... 367
3.15) UTC-15: Customize the color of specific jewelry sections (Use the predefined
jewelry mockup) .................................................................................................................... 368

---

3.16) UTC-16: Customize the jewelry of specific jewelry sections (Use the converted
model) ..................................................................................................................................... 369
3.17) UTC-17: Customize the material of specific jewelry sections (Use the predefined
jewelry mockup) .................................................................................................................... 371
3.18) UTC-18: Customize the material of specific jewelry sections (Use the converted
model) ..................................................................................................................................... 372
3.19) UTC-19: Retrieve the previous customization of a jewelry ..................................... 374
3.20) UTC-20: Choose the jewelry to try-on with packaging ........................................... 376
3.21) UTC-21: Select the type of selected body to try on ................................................... 377
3.22) UTC-22: View all previously designed works ........................................................... 378
3.23) UTC-23: Save the designed work from the predefined jewelry mockup that has not
been customized. ................................................................................................................... 379
3.24) UTC-24: Save the designed work from the predefined jewelry mockup that has
been customized. ................................................................................................................... 380
3.25) UTC-25: Save the designed work from the converted image to 3d model that has
not been customized. ............................................................................................................. 382
3.26) UTC-26: Save the designed work from the converted image to 3d model that has
been customized. ................................................................................................................... 383
3.27) UTC-27: Save the designed work from the predefined packaging mockup that has
not been customized. ............................................................................................................. 385
3.28) UTC-28: Save the designed work from the predefined packaging mockup that has
been customized. ................................................................................................................... 386
Chapter Four | System Testing ................................................................................................ 388
4.1) STC-01: Register............................................................................................................ 388
4.2) STC-02: Log in ............................................................................................................... 392
4.3) STC-03: Log out............................................................................................................. 394
4.4) STC-04: View all of the jewelry mockups ................................................................... 395
4.5) STC-05: View all of the packaging mockups .............................................................. 396
4.6) STC-06: View the jewelry mockups by category ........................................................ 397
4.7) STC-07: View the packaging mockups by category ................................................... 398
4.8) STC-08: Use the predefined jewelry mockups ............................................................ 400
4.9) STC-09: Use the predefined packaging mockups ....................................................... 401
4.10) STC-10: Upload an Image to convert to 3D .............................................................. 402
4.11) STC-11: Create the name of the design ..................................................................... 403
4.12) STC-12: Delete the uploaded image ........................................................................... 404
4.13) STC-13: Use the converted image to 3d model to customize ................................... 405
4.14) STC-14: View the jewelry model ................................................................................ 406

---

4.15) STC-15: Customize the name of the jewelry model ................................................. 407
4.16) STC-16: Customize the color of the jewelry model .................................................. 408
4.17) STC-17: Customize the material of the jewelry model ............................................ 409
4.18) STC-18: Customize the size of the jewelry model .................................................... 410
4.19) STC-19: Customize the color of specific jewelry sections (Use the predefined
jewelry mockup) .................................................................................................................... 411
4.20) STC-20: Customize the color of specific jewelry sections (Use converted image to 3d
model) ..................................................................................................................................... 413
4.21) STC-21: Customize the material of specific jewelry sections (Use the predefined
jewelry mockup) .................................................................................................................... 415
4.22) STC-22: Customize the material of specific jewelry sections (Use converted image
to 3d model) ........................................................................................................................... 417
4.23) STC-23: Zoom in and zoom out the jewelry model .................................................. 418
4.24) STC-24: View the packaging model ........................................................................... 420
4.25) STC-25: Customize the color of the packaging model ............................................. 421
4.26) STC-26: Add engraved text to the packaging model................................................ 423
4.27) STC-27: Replace with a new packaging model ......................................................... 425
4.28) STC-28: Choose the jewelry to try-on with packaging ............................................ 426
4.29) STC-29: Zoom in and zoom out the packaging model ............................................. 427
4.30) STC-30: Select the type of simulated body to try on ................................................ 428
4.31) STC-31: View the jewelry on the simulated body .................................................... 429
4.32) STC-32: View all previously designed works ............................................................ 430
4.33) STC-33: Create a new design ..................................................................................... 431
4.34) STC-34: Save the designed work ................................................................................ 432
4.35) STC-35: Save the designed work from the predefined jewelry mockup ................ 433
4.36) STC-36: Save the designed work from the converted image to 3d model .............. 434
4.37) STC-37: Save the designed work from the predefined packaging mockup ........... 435
4.38) STC-38: Export image as PNG format ...................................................................... 436
4.39) STC-39: Export image as JPG format ....................................................................... 437
4.40) STC-40: Export the model as PDF report ................................................................. 438
4.41) STC-41: Export 3D file as STL format ...................................................................... 439
4.42) STC-42: Export 3D file as OBJ format ..................................................................... 440
4.43) STC-43: Export 3D file as GLB format ..................................................................... 441

---

Chapter One | Introduction
1.1) Purpose
The purpose of this test plan is to define the testing plan to guarantee that the
system will work properly as expected. The test result will be recorded in the test record
document.
1.2) Scope
• Measure user requirements and system requirements
• Specify unit test for the backend
• Specify system test that follows the use case of the
o Feature#1: Register
o Feature#2: Jewelry and Packaging Mockups
o Feature#3: Image to 3D
o Feature#4: Customization
o Feature#5: Virtual Try-On
o Feature#6: Workspace
o Feature#7: Super Export
1.3) User Characteristics
Title Definition
The people who are not registered to the
system. These users can only browse and
preview mockups available on the platform.
Unregistered User
They typically include curious creatives who
are exploring the idea of designing custom
jewelry.
The people who have already registered and
logged in to the web application. These users
range from beginner jewelry entrepreneurs
Registered User looking to launch a brand with minimal
technical skills, to self-expressive, trend-
conscious individuals who value aesthetic
freedom without needing a full design team.
The people who interact with the
User 3DJewelryCraft system. This can include both
unregistered and registered user.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 348
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

1.4) Acronyms and Definitions
1.4.1) Acronyms
UC Use Case
UTC Unit Test Case
STC System Test Case
TD Test case
2D Two Dimension
3D Three Dimension
PNG Portable Network Graphics
JPG Joint Photographic Experts Group
PDF Portable Document Format
STL Stereolithography
OBJ Wavefront Object
GLB GL Transmission Format Binary file
1.4.2) Definitions
Title Definition
The web application that transforms 2D
jewelry designs into customizable 3D models,
3DJewelryCraft
allowing users to visualize, personalize, and
export their creations.
The people who are not registered to the
system. These users can only browse and
preview mockups available on the platform.
Unregistered User
They typically include curious creatives who
are exploring the idea of designing custom
jewelry.
The people who have already registered and
logged in to the web application. These users
range from beginner jewelry entrepreneurs
Registered User looking to launch a brand with minimal
technical skills, to self-expressive, trend-
conscious individuals who value aesthetic
freedom without needing a full design team.
Feature Transformation of input parameters
to output parameters based on a specified
Feature
algorithm. It describes the functionality of the
product in the language of the product. Used
Document 3DJewelryCraft_ Owner NP1, NP2 Page 349
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

for requirements analysis, design, coding,
testing or maintenance.
A condition or capability that must be met or
possessed by a system or system component
Requirement
to satisfy a contract, standard, specification,
or other formally imposed documents.
A document that specifies, in a complete,
precise, verifiable manner, the requirements,
design, behavior, or other characteristics of a
Specification
system or component, and often, the
procedures for determining whether these
provisions have been satisfied.
Computer programs, procedures, and
System associated documentation and data pertain to
the operation of a computer system.
Activity in which a system or component is
executed under specified conditions, the
Test results are observed or recorded, and an
evaluation is made of some aspect of the
system or component.
1) Testing of individual routines and modules
by the developer or an independent tester.
2) A test of individual programs or modules to
Unit Testing ensure that there are no analysis or
programming errors (ISO/IEC 2382-20).
3) Test of individual hardware or software
units or groups of related units (ISO 24765).
Testing conducted on a complete and
System Testing integrated system for evaluate the system’s
compliance with its specified requirements.
A predefined mockup is a ready-made 3D
Predefined Mockups model that serves as a template for
showcasing jewelry or packaging designs.
A 3D object generated by processing a 2D
Converted Image to 3D Model
image through the meshy API.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 350
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Chapter Two | Test Plan and Test Procedures
2.1) Scope of Testing
The scope of testing covers all essential functions using unit and system testing
2.2) Test Duration
Progress I
Perform date: 5 June 2025 – 10 June 2025
Duration: 5 days
Progress II
Perform date: 23 August 2025 – 28 August 2025
Duration: 6 days
Progress II
Perform date: 30 Sep 2025 – 5 Oct 2025
Duration: 6 days
2.3) Test Responsibility
Name Responsibility
Unit Test NP1, NP2
System Test NP1, NP2
Test Record NP1, NP2
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
2.4) Test Strategy
The test will be followed by:
• Test case design
• Determine expected results
• Perform tests
• Test record
Document 3DJewelryCraft_ Owner NP1, NP2 Page 351
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

2.5) Test Results
Actual output:
Each test case performs the actual output
Pass/Fail criteria:
Pass: The actual output is the same as the expected result.
Fail: The actual output is not the same as the expected result.
2.6) Test Environment
• Lenovo IdeaPad 3i 15IAU7
o Processor: 12th Gen Intel(R) Core(TM) i5-1235U 1.30 GHz
o RAM: 16GB
o Operating System: Windows 11 Home Single Language
• MacBook Air M1 (13.3 inch - 2020)
o Processor: Apple M1 chip with 8-core CPU (4 performance cores and 4
efficiency cores), 8GB unified memory
o RAM: 8GB LPDDR4
o Operating System: macOS
Document 3DJewelryCraft_ Owner NP1, NP2 Page 352
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Chapter Three | Unit Test
3.1) UTC-01: Register
Unit Test ID: UTC-01
Function: register()
Description: This test case is created to test the register() function. This function
checks the user's first_name, last_name, email, and password.
Prepared Data: first name, last name, email, and password of the user
No. Description Input Expected Output
1. Create a user's first name, { {
last name, email, and “first_name”: “Baby”, “message”: “User
password in the correct “last_name”: “Tee”, registered
successfully”,
format. “email”:
“user”: {
“Babytee@gmail.com”,
“user_id”: 8,
“password”: “Babytee1234”
“first_name”:
}
“Baby”,
“last_name”:
“Tee”,
“email”:
“Babytee@gmail.com”
}
}
2. Create the first name, last { {
name, email, and password, “first_name”: “Baby”, “message”: “User
but the email is already “last_name”: “Tee”, with this email already
exists”
registered. “email”:
}
“Babytee@gmail.com”,
“password”: “Babytee1234”
}
3. Incomplete information { {
filling in all fields “first_name”: “”, “message”: “Missing
“last_name”: “Tee”, required fields”
}
“email”:
“Babytee@gmail.com”,
“password”: “Babytee1234”
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 353
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4. The password does not meet { {
the conditions of 8-12 “first_name”: “Baby”, “message”:
characters long and contains “last_name”: “Tee”, “Password must be 8–
12 characters long,
at least one uppercase letter “email”:
include at least one
and one number. “Babytee@gmail.com”,
uppercase letter and
“password”: “babytee1234”
number.”
}
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 354
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.2) UTC-02: Log in
Unit Test ID: UTC-02
Function: login()
Description: This test case is created to test the login() function. This function
will check the user's email and password.
Prepared Data: email and password of the user.
No. Description Input Expected Output
1. Log in successful { {
“email”: “message”: “Login
“Babytee@gmail.com”, successful",
“user”: {
“password": "Babytee1234”
“email”:
}
“babytee@gmail.com”,
“first_name”:
“Baby”,
"last_name":
“Tee”,
“user_id”: 8
}
}
2. Empty input email and { {
password “email”: “”, “message”: “Missing
“password”: “” email or password”
}
}
3. Input the wrong password { {
“email”: “message”: “Invalid
“Babytee@gmail.com”, email or password”
}
“password": "Babytee1”
}
4. Email doesn’t exist { {
“email": “user@gmail.com”, “message”: “Invalid
“password”: “Babytee1234” email or password”
}
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 355
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.3) UTC-03: Log out
Unit Test ID: UTC-03
Function: logout()
Description: This test case is created to test the logout() function. This function
will check if the user has logged out.
Prepared Data: The user has log in.
No. Description Input Expected Output
1. User click on “log out” Click on “Log out” button {
button “message”: "Logged
out successfully"
}
2. - The user session is
Session user is already null
cleared and logged
out.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 356
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.4) UTC-04: View all of the jewelry mockups
Unit Test ID: UTC-04
Function: get_mockups()
Description: This test case is created to test the get_mockups() function, which
retrieves all jewelry mockups. The function ensures that user (Registered and
Unregistered user) receive the correct mockup data for all jewelry mockups.
No. Description Input Expected Output
1. User view all of the User select “Jewelry” {
jewelry mockups button “data”: [
{
“mockup_id”: 1,
“mockup_name”: “Test
Bracelet”,
“mockup_subcategory”:
“bracelet”,
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
},
{
“mockup_id”: 2,
“mockup_name”: “Test
Bracelet2”,
“mockup_subcategory”:
“bracelet”,
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
},
…
]
“message”: “Mockups fetched
successfully”
}
2. There is no mockup in - {
the database “message”: "No mockups
found",
“data”: []
}
{
Document 3DJewelryCraft_ Owner NP1, NP2 Page 357
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3. There is an error from - “error”: "Failed to fetch
the backend or database mockups"
}
3.5) UTC-05: View all of the packaging mockups
Unit Test ID: UTC-05
Function: get_all_package_mockups()
Description: This test case is created to test the get_all_package_mockups()
function, which retrieves all packaging mockups. The function ensures that user
(Registered and Unregistered user) receive the correct mockup data for all
packaging mockups.
No. Description Input Expected Output
1. User view all of the User select “Packaging” {
packaging mockups button “data”: [
{
“mockup_id”: 6,
“mockup_name”: “Test
Package”,
“mockup_subcategory”:
“bracelet box with pillow”,
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
},
{
“mockup_id”: 7,
“mockup_name”: “Test
Package2”,
“mockup_subcategory”:
“bracelet box with pillow”,
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
}
]
“message”: “Packaging mockups
fetched successfully”
}
2. - {
Document 3DJewelryCraft_ Owner NP1, NP2 Page 358
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

There is no mockup in “message": "No packaging
the database mockups found",
“data”: []
}
3. There is an error from - {
the backend or database “error”: "Failed to fetch packaging
mockups"
}
3.6) UTC-06: View the jewelry mockups by category
Unit Test ID: UTC-06
Function: get_mockups_by_subcategory(subcategory)
Description: This test case is created to test the
get_mockups_by_subcategory(subcategory) function, which retrieves all jewelry
mockups that belong to the subcategory (necklace and bracelet). The function
ensures that user (Registered and Unregistered user) receive the correct mockup
data for each category.
No. Description Input Expected Output
1. User view all the { {
jewelry mockups in “subcategory”: “mockup_id”: 13,
the necklace “necklace” “mockup_name”: “Test Necklace”
category. }
“mockup_subcategory”: “necklace”
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
}
2. User view all the { {
jewelry mockups in “subcategory”: “mockup_id”: 1,
the bracelet “bracelet” “mockup_name”: “Test Bracelet”
“mockup_subcategory”: “bracelet”
category. }
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
}
3. Subcategory not { {
found “subcategory”: “message”: “No mockups found for the
“ring” given subcategory”
}
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 359
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.7) UTC-07: View the packaging mockups by category
Unit Test ID: UTC-07
Function: get_package_mockups_by_subcategory(subcategory)
Description: This test case is created to test the
get_package_mockups_by_subcategory(subcategory) function, which retrieves all
packaging mockups that belong to the subcategory (necklace-box, bracelet-box,
bracelet-box-with-pillow). The function ensures that user (Registered and
Unregistered user) receive the correct mockup data for each category.
No. Description Input Expected Output
1. User view all the { {
packaging mockups “subcategory”: “mockup_id”: 14,
in the necklace-box “necklace-box” “mockup_name”: “Test Necklace Box”
category. }
“mockup_subcategory”: “necklace box”
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
}
2. User view all the { {
packaging mockups “subcategory”: “mockup_id”: 15,
in the bracelet-box “bracelet-box” “mockup_name”: “Test Bracelet Box”
“mockup_subcategory”: “bracelet box”
category. }
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
}
3. User view all the { {
packaging mockups “subcategory”: “mockup_id”: 6,
in the bracelet-box- “bracelet-box-with- “mockup_name”: “Test Package”
“mockup_subcategory”: “bracelet box
with-pillow pillow”
with pillow”
category. }
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
/thumbnails”
}
4. Subcategory doesn’t { Same as for necklace-box
have a dash. “subcategory”: {
“necklacebox” “mockup_id”: 14,
“mockup_name”: “Test Necklace Box”
}
“mockup_subcategory”: “necklace box”
“mockup_thumbnail_url”:
“https://storage.googleapis.com/...
Document 3DJewelryCraft_ Owner NP1, NP2 Page 360
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

/thumbnails”
}
5. Subcategory has a { Same as for bracelet-box
space. “subcategory”: {
“bracelet box” “mockup_id”: 15,
“mockup_name”: “Test Bracelet Box”
}
“mockup_subcategory”: “bracelet box”
“mockup_thumbnail_url”:
“https://assets.meshy.ai/.../preview.png?”
}
6. Subcategory not { {
found “subcategory”: “message”: “No mockups found for the
“ringbox” given subcategory”
}
}
3.8) UTC-08: Use the predefined jewelry mockup to customize
Unit Test ID: UTC-08
Function: get_mockup_detail(jewelry_mockup_id)
Description: This test case is created to test get_mockup_detail
(jewelry_mockup_id) function. This function will retrieve detailed information of
a jewelry mockup based on the given jewelry_mockup_id and registered user can
choose the jewelry mockup to customize.
No. Description Input Expected Output
1. Registered user can { {
choose the jewelry “jewelry_mockup_id”: “jewelry_mockup_id”: 1,
mockup to 1 “mockup_name”: “Test Bracelet”,
customize. }
“mockup_category”: “jewelry”,
“urls”: {
“glbfile”:
“https://storage.googleapis.com/.../model.glb?”,
“thumbnail”:
“https://storage.googleapis.com/...
/thumbnails”
}
}
jewelry_mockup_id { {
2. is not found. “jewelry_mockup_id”: “message”: "Mockup not found"
30 }
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 361
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.9) UTC-09: Use the predefined packaging mockup to customize
Unit Test ID: UTC-09
Function: get_package_mockup_detail(packaging_mockup_id)
Description: This test case is created to test get_mockup_detail
(packaging_mockup_id) function. This function will retrieve detailed information
of a packaging mockup based on the given packaging_mockup_id and registered
user can choose the packaging mockup to customize.
No. Description Input Expected Output
1. Registered user can { {
choose the packaging “packaging_mockup_id”: “packaging_mockup_id”: 6,
mockup to customize. 6 “mockup_name”: “Test Package”,
} “packaging_category”: “bracelet box with
pillow”,
“urls”: {
“glbfile”:
“https://storage.googleapis.com/.../model.glb?”,
“thumbnail”:
“https://storage.googleapis.com/...
/thumbnails”
}
}
2. packaging_mockup_id { {
is not found. “packaging_mockup_id”: “message”: "Mockup not found"
20 }
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 362
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.10) UTC-10: Upload an image for 3D generation
Unit Test ID: UTC-10
Function: upload_image()
Description: This test case is created to test the upload_image() function. This
function handles image uploads from registered user. It saves the image file to the
database table and returns the image_upload_id with associated details.
Prepared Data: User uploaded image
No. Description Input Expected Output
1. Registered user { {
can upload the “image”: “message”: “Image uploaded”,
valid image file(). “bracelet.png” “image_upload_id": 1,
}
“image_url”:
“http://localhost:5000/uploads/6f00b03c-
2bee-43af-a9ae-18ee8fcac5b6.png”,
“generated_time”: 2025-05-16 11:50:13
}
2. Missing image { The “Generate” button cannot be
file. “image”: “” pressed.
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 363
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.11) UTC-11: Generate 3D model from the uploaded image
Unit Test ID: UTC-11
Function: generate_3d(image_upload_id)
Description: This test case is created to test the generate_3d(image_upload_id)
function. This function retrieves the uploaded image by ID, converts the image to
base64, and sends it to the Meshy API to generate a 3D model. If successful, the
returned job_id is stored in the database.
No. Description Input Expected Output
1. Valid { {
image_upload_id “image_upload_id”: 1 “message”: “3D generation started”,
} “job_id": “0196b428-33e6-71ff-b484-
1bb8628beb21”,
}
2. Invalid { {
image_upload_id “image_upload_id”: “message”: “Image not found”
999 }
}
3. API fail { {
“image_upload_id”: 1 “message”: “Meshy API failed”,
} “status_code”: 500,
“raw”: “<html>...</html>”
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 364
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.12) UTC-12: Save GLB File from Meshy API
Unit Test ID: UTC-12
Function: get_3d_model(job_id)
Description: This test case is created to test the get_3d_model(job_id) function.
This function calls the Meshy API using a given job_id to fetch the generated 3D
model. If successful, the glb_url and thumbnail_url are uploaded to the Firebase
and saved in the image_upload_glbfile table.
No. Description Input Expected Output
1. Valid job_id with { {
SUCCEEDED “job_id”: “0196b428- “message”:
response. 33e6-71ff-b484- “GLB and thumbnail file uploaded to Firebase
1bb8628beb21” and saved successfully”,
} “glb_url":
“https://storage.googleapis.com/.../model.glb?”,
“thumbnail_url":
“https://storage.googleapis.com/...
/thumbnails” ,
“progress”: 100
}
2. Valid job_id with { {
IN_PROGRESS “job_id”: “0196b428- “message”: “3D model is still processing or
response. 33e6-71ff-b484- failed.”,
1bb8628beb21” “progress”: 45,
} “raw”: {
“art_style”: “”,
“created_at”: 1749198100066,
“expires_at”: 0,
“finished_at”: 0,
“id”: “0196b428-33e6-71ff-b484-
1bb8628beb21”,
“model_url”: “”,
“model_urls”: {
“glb”: “”
},
“name”: “”,
“negative_prompt”: “”,
“object_prompt”: “”,
“progress”: 45,
“started_at”: 1749198100197,
“status”: “IN_PROGRESS”,
“style_prompt”: “’,
“task_error”: null,
Document 3DJewelryCraft_ Owner NP1, NP2 Page 365
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“texture_image_url”: “”,
“texture_prompt”: “”,
“texture_urls”: null,
“thumbnail_url”: “”
},
“status”: “IN_PROGRESS”
}
3. job_id not found. { {
“job_id”: “1234” “message”: “Image upload record not found”
} }
3.13) UTC-13: Retrieve GLB URL from Database
Unit Test ID: UTC-13
Function: get_glb_url(job_id)
Description: This test case is created to test the get_glb_url(job_id) function.
This function looks up the generated_glbfile_url in the database using the
provided job_id, to show the 3D models from image uploaded by registered user.
No. Description Input Expected Output
1. Valid job_id with { {
existing glb_url. “job_id”: “job_id”:
“0196b428-33e6-71ff- “0196b428-33e6-71ff-b484-1bb8628beb21”,
“glb_url":
b484-1bb8628beb21”
“https://storage.googleapis.com/.../model.glb?”
}
}
2. job_id not found. { {
“job_id”: “1234” “message”: “job_id not found”
} }
3. glb_url not found. { {
“job_id”: “message”: “GLB file not found”
“0196b428-33e6-71ff- }
b484-1bb8628beb21”
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 366
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.14) UTC-14: Create the name of the design
Unit Test ID: UTC-14
Function: upload_image()
Description: This test case is created to test the behavior of assigning and saving
model_name during the image upload process. It verifies whether the name is
properly stored in the database and returned in the response.
Prepared Data: User’s model name
No. Description Input Expected Output
1. Registered user { {
can create the new “model_name”: “Test “message”: “Model name saved”,
name to the Model” “model_name”: “Test Model”
design. }
}
2. Registered user { {
does not create the “model_name”: “New “message”: “Model name saved”,
new name and Model” “model_name”: “New Model”
}
uses the default }
name.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 367
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.15) UTC-15: Customize the color of specific jewelry sections (Use the predefined
jewelry mockup)
Unit Test ID: UTC-15
Function: customize_jewelry_cropmode(jewelry_mockup_id,
jewelry_custom_color)
Description: This test case is created to test the
customize_jewelry_cropmode(jewelry_mockup_id, jewelry_custom_color)
function. This function will retrieve the jewelry_mockup_id from the jewelry item
that the registered user wants to customize and apply the chosen
jewelry_custom_color, then save the customization details into the database table.
If a customization already exists, it will update the record; otherwise, it will create
a new one.
No. Description Input Expected Output
1. Registered user { {
successfully “user_id”: 11, “message”: “Customization saved
customizes the color “jewelry_mockup_id”: 28, successfully”,
“user_id”: 11,
of specify sections. “jewelry_custom_color”:
“jewelry_mockup_id”: 28,
(New “#dfbd69”
"custom_id": 334,
customization) }
“jewelry_customs”: {
“custom_glb_url”: “custom-
models/2_14.glb”,
“jewelry_custom_color”:
“#dfbd69”
}
}
2. Update existing { {
customization “user_id”: 11, “message”: “Customization saved
(Same user_id and “jewelry_mockup_id”: 28, successfully”,
“user_id”: 11,
jewelry_mockup_id) “jewelry_custom_color”:
“jewelry_mockup_id”: 28,
“#9ea3a7”
"custom_id": 334,
}
“jewelry_customs”: {
“custom_glb_url”: “custom-
models/2_14.glb”,
“jewelry_custom_ color”:
“#dfbd69”
}
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 368
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3. Missing user_id. { {
“user_id”: , “message”: “user_id and
“jewelry_mockup_id”: 128, jewelry_mockup_id are required”
}
“jewelry_custom_color”:
“#9ea3a7”
}
4. Missing { {
jewelry_mockup_id. “user_id”: 11, “message”: “user_id and
“jewelry_mockup_id”: , jewelry_mockup_id are required”
}
“jewelry_custom_material”:
“#9ea3a7”
}
3.16) UTC-16: Customize the jewelry of specific jewelry sections (Use the converted
model)
Unit Test ID: UTC-16
Function: customize_imageupload_cropmode(image_upload_id,
image_upload_custom_color)
Description: This test case is created to test the function customize_imageupload
_cropmode(image_upload_id, image_upload_custom_color). This function will
retrieve the image_upload_id from the converted item that the registered user
wants to customize and apply the chosen image_upload_custom_color, then save
the customization details into the database table. If a customization already exists,
it will update the record; otherwise, it will create a new one.
No. Description Input Expected Output
1. Registered user { {
successfully “user_id”: 11, “message”: “Imageupload
customizes the “image_upload_id”: 77, customization saved successfully”,
“user_id”: 11,
color of specify “image_upload_custom_color”:
“image_upload_id”: 77,
sections. (New “#9ea3a7”
"custom_id": 1,
customization) }
“image_upload_customs”: {
“custom_glb_url”: “custom-
models/2_17.glb”,
“image_upload_custom_ color”:
“#9ea3a7”
}
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 369
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Update existing
2. customization { {
(Same user_id and “user_id”: 11, “message”: “Imageupload
customization saved successfully”,
image_upload_id) “image_upload_id”: 77,
“user_id”: 11,
“image_upload_custom_color”:
“image_upload_id”: 77,
“#9ea3a7”
"custom_id": 1,
}
“image_upload_customs”: {
“custom_glb_url”: “custom-
models/2_17.glb”,
“image_upload_custom_ color”:
“#9ea3a7”
}
}
3. Missing user_id. { {
“user_id”: , “message”: “user_id and
“image_upload_id”: 77, image_upload_id are required”
}
“image_upload_custom_
color”: “#9ea3a7”
}
4. Missing { {
image_upload_id. “user_id”: 11, “message”: “user_id and
“image_upload_id”: , image_upload_id are required”
}
“image_upload_custom_
color”: “#9ea3a7”
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 370
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.17) UTC-17: Customize the material of specific jewelry sections (Use the
predefined jewelry mockup)
Unit Test ID: UTC-17
Function: customize_jewelry_cropmode(jewelry_mockup_id,
jewelry_custom_material)
Description: This test case is created to test the function
customize_jewelry_cropmode(jewelry_mockup_id, jewelry_custom_material).
This function will retrieve the jewelry_mockup_id from the jewelry item that the
registered user wants to customize and apply the chosen
jewelry_custom_material, then save the customization details into the database
table. If a customization already exists, it will update the record; otherwise, it will
create a new one.
No. Description Input Expected Output
1. Registered user { {
successfully “user_id”: 2, “message”: “Customization saved
customizes the “jewelry_mockup_id”: 14, successfully”,
“user_id”: 2,
material of specify “jewelry_custom_material”:
“jewelry_mockup_id”: 14,
sections. (New “#c0c0c0”
"custom_id": 334,
customization) }
“jewelry_customs”: {
“custom_glb_url”: “custom-
models/2_14.glb”,
“jewelry_custom_material”:
“#c0c0c0”
}
}
2. Update existing { {
customization “user_id”: 2, “message”: “Customization saved
(Same user_id and “jewelry_mockup_id”: 14, successfully”,
“user_id”: 2,
jewelry_mockup_id) “jewelry_custom_material”:
“jewelry_mockup_id”: 14,
“#9ea3a7”
"custom_id": 334,
}
“jewelry_customs”: {
“custom_glb_url”: “custom-
models/2_14.glb”,
“jewelry_custom_material”:
“#9ea3a7”
}
}
Missing user_id. { {
Document 3DJewelryCraft_ Owner NP1, NP2 Page 371
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“user_id”: , “message”: “user_id and
3. “jewelry_mockup_id”: 14, jewelry_mockup_id are required”
“jewelry_custom_material”: }
“#9ea3a7”
}
4. Missing { {
jewelry_mockup_id. “user_id”: 2, “message”: “user_id and
“jewelry_mockup_id”: , jewelry_mockup_id are required”
}
“jewelry_custom_material”:
“#9ea3a7”
}
3.18) UTC-18: Customize the material of specific jewelry sections (Use the converted
model)
Unit Test ID: UTC-18
Function: customize_imageupload _cropmode(image_upload_id,
image_upload_custom_material)
Description: This test case is created to test the function customize_imageupload
_cropmode(image_upload_id, image_upload_custom_material).
This function will retrieve the image_upload_id from the converted item that the
registered user wants to customize and apply the chosen
image_upload_custom_material, then save the customization details into the
database table. If a customization already exists, it will update the record;
otherwise, it will create a new one.
No. Description Input Expected Output
1. Registered user { {
successfully “user_id”: 2, “message”: “Imageupload
customizes the “image_upload_id”: 120, customization saved successfully”,
“user_id”: 2,
material of “image_upload_custom_material”:
“image_upload_id”: 120,
specify sections. “#c0c0c0”
"custom_id": 1,
(New }
“image_upload_customs”: {
customization)
“custom_glb_url”: “custom-
models/2_14.glb”,
“image_upload_custom_material”:
“#c0c0c0”
}
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 372
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

2. Update existing { {
customization “user_id”: 2, “message”: “Imageupload
(Same user_id “image_upload_id”: 120, customization saved successfully”,
“user_id”: 2,
and “image_upload_custom_material”:
“image_upload_id”: 120,
image_upload_id) “#9ea3a7”
"custom_id": 1,
}
“image_upload_customs”: {
“custom_glb_url”: “custom-
models/2_14.glb”,
“image_upload_custom_material”:
“#9ea3a7”
}
}
3. Missing user_id. { {
“message”: “user_id and
“user_id”: ,
image_upload_id are required”
“image_upload_id”: 14,
}
“image_upload_custom_material”:
“#9ea3a7”
}
4. Missing { {
image_upload_id. “user_id”: 2, “message”: “user_id and
“image_upload_id”: , image_upload_id are required”
}
“image_upload_custom_material”:
“#9ea3a7”
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 373
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.19) UTC-19: Retrieve the previous customization of a jewelry
Unit Test ID: UTC-19
Function: get_last_customization(user_id, item_type, item_id)
Description: This test case is created to test the function
get_last_customization(user_id, item_type, item_id). This function retrieves the
most recent customization jewelry model from the database. If the item type is
'mockup', it queries the 'user_jewelry_custom' table; if the type is 'image_upload',
it queries the 'user_image_upload_custom' table. The function returns the last
saved customization data to the frontend.
Prepared Data:
1. Type of the item that should be “mockup” or “image_upload”
2. item_id should be jewelry_mockup_id if the item_type is mockup.
3. item_id should be image_upload_id if the item_type is image_upload.
No. Description Input Expected Output
1. Registered user { {
can retrieve last “user_id”: 13, “user_id”: 13
customization “item_type”: “jewelry_custom_id”: 335,
“customs”: [
for a jewelry “mockup”,
{
mockup. “item_id”: 21
“jewelry_mockup_id”: 21,
}
“jewelry_created_time”: “Thu, 21 Aug

## 2025 14:42:57 GMT”,

“jewelry_custom_color”: “#fcfcfc”,
“jewelry_custom_glbfile_url”: “custom-
models/13_21.glb”,
“jewelry_custom_material”: “#c0c0c0”,
“jewelry_custom_name”: “New Granite
Necklace Design”,
“jewelry_custom_size”: “31.00”
}
],
}
2. Registered user { {
can retrieve last “user_id”: 13, “user_id”: 13
customization “item_type”: “image_upload_custom_id”: 36,
“customs”: [
for an image “image_upload”,
{
upload. “item_id”: 78
“image_upload_id”: 78,
}
“image_upload_created_time”: “Mon, 18
Aug 2025 02:43:41 GMT”,
Document 3DJewelryCraft_ Owner NP1, NP2 Page 374
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“image_upload_custom_color”: “#fcfcfc”,
“image_upload_custom_glbfile_url”:
“uploads/custom_models/13_78_1755485021.glb”,
“image_upload_custom_material”:
“c0c0c0”,
“image_upload_custom_name”: “Custom
Upload”,
“image_upload_custom_size”: “3”
}
],
}
3. No { {
customization “user_id”: 13, “message”: “No customization found”
found “item_type”: }
“mockup”,
“item_id”: 78
}
4. Invalid { {
item_type “user_id”: 13, “message”: “Invalid item_type”
“item_type”: }
“upload_image”,
“item_id”: 78
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 375
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.20) UTC-20: Choose the jewelry to try-on with packaging
Unit Test ID: UTC-20
Function: get_workspace_items_packagecustom(user_id)
Description: This test case is created to test the
get_workspace_items_packagecustom(user_id) function. This function retrieves
the workspace and the items inside the workspace by user_id. It returns the list of
jewelry items that the registered user has saved in the workspace, so the registered
user can choose jewelry to try-on with packaging.
No. Description Input Expected Output
1. Registered user { {
can retrieve the “user_id”: 11 “user_id”: 11,
items in the } “workspace_id”: 7,
“workspace_item”: [
workspace.
{
“generated_glbfile_url”:
“uploads/custom_models/11_37_1754723618.glb”,
“item_id”: 303,
“model_name”: “Italian Charm Bracelet”,
“type”: “mockup_custom”
},
{
“generated_glbfile_url”: “custom-
models/11_21.glb”,
“item_id”: 304,
“model_name”: “Amethyst Necklace”,
“type”: “mockup_custom”
}
]
}
2. Workspace { {
exists but no “user_id”: 14 “user_id”: 14,
items saved. } “workspace_id”: 11,
“workspace_item”: []
}
3. Workspace not { {
found. “user_id”: 20 “message”: “Workspace not found”
} }
Document 3DJewelryCraft_ Owner NP1, NP2 Page 376
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.21) UTC-21: Select the type of selected body to try on
Unit Test ID: UTC-21
Function: get_simulated_body(model_type)
Description: This test case is created to test the function
get_simulated_body(model_type). This function verifies that the system can
correctly retrieve and return the simulated body model (GLB file) based on the
model_type requested by the registered user.
No. Description Input Expected Output
1. Valid neck model { {
type “model_type”: “neck” "asset":
} {"generator":"Khronos glTF Blender I/O
v4.4.55","version":"2.0"},"scene":0,"scenes":
[{
"name":"Scene","nodes":[5]}],
"nodes":[{"name":"NeckBack"
, …
]}
2. Valid wrist { {
model type “model_type”: “wrist” "asset":
} {"generator":"Khronos glTF Blender I/O
v4.4.55","version":"2.0"},"scene":0,"scenes":
[{
"name":"Scene","nodes”: [1,2]}],
"nodes”:
[{"mesh":0,"name":"tripo_node_9b51b900-
ce9d-40b3-8824-26fadce13dff.001”
,...
]}
3. Invalid model { {
type “model_type”: “ear” “message”: “No model type in database”
} }
Document 3DJewelryCraft_ Owner NP1, NP2 Page 377
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.22) UTC-22: View all previously designed works
Unit Test ID: UTC-22
Function: get_workspace_items(user_id)
Description: This test case is created to test the get_workspace_items(user_id)
function. This function retrieves all mockups that are saved in the workspace
associated with the given user_id.
No. Description Input Expected Output
1. Valid user_id { {
with existing “user_id”: 16 "user_id": 16,
workspace and } "workspace_id": 13,
"workspace_item": [
workspace_item
{
"generated_glbfile_url":
"uploads/custom_models/16_30_1759564569.glb",
"generated_time": "Sat, 04 Oct 2025

## 07:56:09 GMT",

"item_id": 375,
"model_name": "Jewel Bracelet",
"type": "mockup_custom"
},
{
"generated_glbfile_url":
"uploads/custom_models/16_129_1759564821.glb",
"generated_time": "Sat, 04 Oct 2025

## 08:00:21 GMT",

"item_id": 61,
"model_name": "Character new bracelet",
"type": "image_upload_custom"
},
{
"generated_glbfile_url":
"uploads/custom_packages/16_53_1759564939.glb",
"generated_time": "Sat, 04 Oct 2025

## 08:02:19 GMT",

"item_id": 91,
"model_name": "Lid seperator Bracelet
Box",
"type": "package_custom"
}
]
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 378
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

2. Valid user_id { {
with existing “user_id”: 2 “user_id”: 2,
workspace but no } “workspace_id”: 4,
“workspace_item”: []
workspace_item
}
3. Valid user_id but { {
no associated “user_id”: 4 “message”: “Workspace not found”
workspace. } }
3.23) UTC-23: Save the designed work from the predefined jewelry mockup that has
not been customized.
Unit Test ID: UTC-23
Function: add_mockup_to_workspace()
Description: This test case is created to test add_mockup_to_workspace()
function. This function verifies that the jewelry mockup that has not been
customized from the predefined jewelry mockups can be added to a user’s
workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the item that want to add.
3. Type of the item that should be “mockup”
No. Description Input Expected Output
1. Registered user { {
can save a new “item_custom_id”: 18, “message”: “Added to workspace
jewelry mockup “item_type”: successfully”
“workspace_id”: 4
item to their “mockup”,
}
workspace. “user_id”: 2
}
2. Item_type not { {
“mockup”. “item_custom_id”: 18, “message”: “Only ‘mockup’ type is
“item_type”: allowed”
}
“image_upload”,
“user_id”: 2
}
3. user_id not found { {
in user table “item_custom_id”: 44, “message”: “User not found”
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 379
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“item_type”:
“mockup”,
“user_id”: 999
}
3.24) UTC-24: Save the designed work from the predefined jewelry mockup that has
been customized.
Unit Test ID: UTC-24
Function: customize_jewelry()
Description: This test case is created to test customize_jewelry() function.
This function verifies that the mockup that has been customized from the
predefined jewelry mockups can be added to a user’s workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the jewelry mockup that want to add.
3. ID of the workspace that want to add an item to.
4. GLB file of the jewelry that want to customize
5. New material of the jewelry in hex code
6. New color of the jewelry in hex code
7. New size of the jewelry in mm.
No. Description Input Expected Output
1. Registered user can { {
save a new “user_id”: 2, “message”: "Customization and workspace
customized jewelry “jewelry_mockup_id”: item saved successfully."
“glb_path”:
mockup item to 14,
"uploads/custom_models/2_14_1759
their workspace. “workspace_id”: 4,
569260.glb",
“file”: test_jewelry.glb,
“jewelry_custom_id”: 380,
“jewelry_custom_material”:
}
##c0c0c0,
“jewelry_custom_color”:
##e5b7c4,
“jewelry_custom_size”:
18.00,
}
2. Missing file { {
“user_id”: 2, “message”: “Missing required fields.”
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 380
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“jewelry_mockup_id”:
14,
“workspace_id”: 4,
“file”: ,
“jewelry_custom_material”:
##c0c0c0,
“jewelry_custom_color”:
##e5b7c4,
“jewelry_custom_size”:
18.00,
}
3. Missing user_id { {
“user_id”: , “message”: “Missing required fields.”
“jewelry_mockup_id”: }
14,
“workspace_id”: 4,
“file”: test_jewelry.glb,
“jewelry_custom_material”:
##c0c0c0,
“jewelry_custom_color”:
##e5b7c4,
“jewelry_custom_size”:
18.00,
}
4. Missing { {
jewelry_mockup_id “user_id”: 2, “message”: “Missing required fields.”
“jewelry_mockup_id”: , }
“workspace_id”: 4,
“file”: test_jewelry.glb,
“jewelry_custom_material”:
##c0c0c0,
“jewelry_custom_color”:
##e5b7c4,
“jewelry_custom_size”:
18.00,
}
5. workspace_id for { {
the user does not “user_id”: 2, “message”: “Workspace not found.”
exist “jewelry_mockup_id”: }
14,
“workspace_id”: 14,
“file”: test_jewelry.glb,
“jewelry_custom_material”:
##c0c0c0,
Document 3DJewelryCraft_ Owner NP1, NP2 Page 381
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“jewelry_custom_color”:
##e5b7c4,
“jewelry_custom_size”:
18.00,
}
3.25) UTC-25: Save the designed work from the converted image to 3d model that
has not been customized.
Unit Test ID: UTC-25
Function: add_imageupload_to_workspace()
Description: This test case is created to test add_imageupload_to_workspace()
function. This function verifies that the converted image to 3d model that has not
been customized can be added to a user’s workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the item that want to add.
3. Type of the item that should be “image_upload”
No. Description Input Expected Output
1. Registered user { {
can save a new “item_custom_id”: 44, “message”: “Added to workspace
image_upload item “item_type”: successfully”
“workspace_id”: 4
to their workspace. “image_upload”,
}
“user_id”: 2
}
2. Item_type not { {
“image_uplaod”. “item_custom_id”: 44, “message”: “Only ‘image_upload’ type
“item_type”: is allowed”
}
“mockup”,
“user_id”: 2
}
3. user_id not found { {
in user table “item_custom_id”: 44, “message”: “User not found”
“item_type”: }
“mockup”,
“user_id”: 999
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 382
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.26) UTC-26: Save the designed work from the converted image to 3d model that
has been customized.
Unit Test ID: UTC-26
Function: customize_imageupload_workspace()
Description: This test case is created to test
customize_imageupload_workspace()function. This function verifies that the
converted image to 3d model that has been customized can be added to a user’s
workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the uploaded image that want to add.
3. ID of the workspace that want to add an item to.
4. GLB file of the uploaded image that want to customize
5. New material in hex code
6. New color in hex code
7. New size in mm.
No. Description Input Expected Output
1. Registered user { {
can save a new “user_id”: 2, “message”: “Imageupload
customized image “image_upload_id”: 120, customization
and workspace item saved
to 3d model item “workspace_id”: 4,
successfully.”
to their “file”:
“glb_path”:
workspace. test_jewelry_imageupload.glb,
“uploads/custom_models/2_120_1759
“image_upload
569562.glb”,
_custom_material”: ##c0c0c0,
“image_upload_custom_id”: 62,
“image_upload
}
_custom_color”: ##e5b7c4,
“image_upload
_custom_size”: 18.00,
}
{ {
2. Missing file “user_id”: 2, “message”: “Missing required
“image_upload_id”: 120, fields.”
}
“workspace_id”: 4,
“file”: ,
“image_upload
_custom_material”: ##c0c0c0,
Document 3DJewelryCraft_ Owner NP1, NP2 Page 383
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“image_upload
_custom_color”: ##e5b7c4,
“image_upload
_custom_size”: 18.00,
}
3. Missing user_id { {
“user_id”: , “message”: “Missing required
“image_upload_id”: 120, fields.”
}
“workspace_id”: 4,
“file”:
test_jewelry_imageupload.glb,
“image_upload
_custom_material”: ##c0c0c0,
“image_upload
_custom_color”: ##e5b7c4,
“image_upload
_custom_size”: 18.00,
}
4. Missing { {
image_upload_id “user_id”: 2, “message”: “Missing required
“image_upload_id”: , fields.”
}
“workspace_id”: 4,
“file”:
test_jewelry_imageupload.glb,
“image_upload
_custom_material”: ##c0c0c0,
“image_upload
_custom_color”: ##e5b7c4,
“image_upload
_custom_size”: 18.00,
}
5. workspace_id for { {
the user does not “user_id”: 2, “message”: “Workspace not found.”
exist “image_upload_id”: 120, }
“workspace_id”: 14,
“file”:
test_jewelry_imageupload.glb,
“image_upload
_custom_material”: ##c0c0c0,
“image_upload
_custom_color”: ##e5b7c4,
“image_upload
_custom_size”: 18.00,
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 384
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.27) UTC-27: Save the designed work from the predefined packaging mockup that
has not been customized.
Unit Test ID: UTC-27
Function: add_mockup_to_workspace()
Description: This test case is created to test add_mockup_to_workspace()
function. This function verifies that the packaging mockup that has not been
customized from the predefined packaging mockups can be added to a user’s
workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the item that want to add.
3. Type of the item that should be “mockup”
No. Description Input Expected Output
1. Registered user { {
can save a new “item_custom_id”: 49, “message”: “Added to workspace
packaging mockup “item_type”: successfully”
“workspace_id”: 4
item to their “mockup”,
}
workspace. “user_id”: 2
}
2. Item_type not { {
“mockup”. “item_custom_id”: 49, “message”: “Only ‘mockup’ type is
“item_type”: allowed”
}
“image_upload”,
“user_id”: 2
}
3. user_id not found { {
in user table “item_custom_id”: 49, “message”: “User not found”
“item_type”: }
“mockup”,
“user_id”: 999
}
Document 3DJewelryCraft_ Owner NP1, NP2 Page 385
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3.28) UTC-28: Save the designed work from the predefined packaging mockup that
has been customized.
Unit Test ID: UTC-28
Function: customize_package()
Description: This test case is created to test customize_package() function.
This function verifies that the packaging mockup that has been customized from
the predefined packaging mockups can be added to a user’s workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the packaging mockup that want to add.
3. ID of the workspace that want to add an item to.
4. ID of the jewelry that want to try on with the packaging.
5. GLB file of the packaging that want to customize
6. New color of the packaging in hex code
7. Text that want to engrave on the packaging
8. Text font that want to engrave on the packaging
9. Text font size that want to engrave on the packaging
10. Text font color that want to engrave on the packaging
No. Description Input Expected Output
1. Registered user can { {
save a new “user_id”: 2, “message”: "Package+Jewelry saved and
customized “package_mockup_id”: 14, added to workspace",
“glb_path”:
packaging mockup “workspace_id”: 4,
"uploads/custom_packages/2_40_1759
item to their “jewelry_custom_id”: 303,
571373.glb",
workspace. “file”: test_package.glb,
"package_custom_id": 92
“package_custom_color”:
}

## #7A7766,

“package_created_text”:
3DJewlry,
“package_text_font”: Inter,
“package text_fontsize”:16,
“package_text_color”:

## #FFFFFF,

}
2. Missing file { {
“user_id”: 2, “message”: “Missing required fields.”
“package_mockup_id”: 14, }
“workspace_id”: 4,
“jewelry_custom_id”: 303,
Document 3DJewelryCraft_ Owner NP1, NP2 Page 386
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“file”: ,
“package_custom_color”:

## #7A7766,

“package_created_text”:
3DJewlry,
“package_text_font”: Inter,
“package text_fontsize”:16,
“package_text_color”:

## #FFFFFF,

}
3. Missing user_id { {
“user_id”: , “message”: “Missing required fields.”
“package_mockup_id”: 14, }
“workspace_id”: 4,
“jewelry_custom_id”: 303,
“file”: test_package.glb,
“package_custom_color”:

## #7A7766,

“package_created_text”:
3DJewlry,
“package_text_font”: Inter,
“package_text_fontsize”:16,
“package_text_color”:

## #FFFFFF,

}
4. Missing { {
package_mockup_id “user_id”: 2, “message”: “Missing required fields.”
“package_mockup_id”: 14, }
“workspace_id”: 4,
“jewelry_custom_id”: 303,
“file”: test_package.glb,
“package_custom_color”:

## #7A7766,

“package_created_text”:
3DJewlry,
“package_text_font”: Inter,
“package_text_fontsize”:16,
“package_text_color”:

## #FFFFFF,

}
5. workspace_id for { {
the user does not “user_id”: 2, “message”: “Workspace not found.”
exist “package_mockup_id”: 14, }
“workspace_id”: 14,
Document 3DJewelryCraft_ Owner NP1, NP2 Page 387
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

“jewelry_custom_id”: 303,
“file”: test_package.glb,
“package_custom_color”:

## #7A7766,

“package_created_text”:
3DJewlry,
“package_text_font”: Inter,
“package_text_fontsize”:16,
“package_text_color”:

## #FFFFFF,

}
Chapter Four | System Testing
4.1) STC-01: Register
Test ID: STC-01
Test No: UC-01
Test case name: Register
Description: Unregistered user can register to the web application.
Test Setup:
1. The unregistered user is not already registered
Test Script:
1. Click on the “Get Started” button on the navigation bar
2. Input first name
3. Input last name
4. Input email
5. Input password
6. Click on the “Sign Up” button
Prepared data: first name, last name, email, and password
Document 3DJewelryCraft_ Owner NP1, NP2 Page 388
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Test
No. Description Script Input Expected Output
No.
Register successful The web application
1 - provides the register page
with an input field.
2 Baby -
3 Tee -
1. 4 Babytee@gmail.com -
5 Babytee1234 -
The system displays a
message "Registration
6 -
successful" and redirects to
the login page.
The email is already registered The web application
1 -
provides the register page.
2 Baby -
3 Tee -
2. 4 Babytee@gmail.com -
5 Babytee1234 -
The system displays a
6 - message “Email is already
exists”.
The first name input field is The web application
empty 1 - provides the register page
with an input field.
2 - -
3 Tee -
3. 4 Babytee@gmail.com -
5 Babytee1234 -
The system displays a
message “First name is
6 -
required” under the input
field.
The last name input field is The web application
empty 1 - provides the register page
with an input field.
2 Baby -
4. 3 - -
4 Babytee@gmail.com -
5 Babytee1234 -
The system displays a
6 -
message “Last name is
Document 3DJewelryCraft_ Owner NP1, NP2 Page 389
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

required” under the input
field.
The email input field is empty The web application
1 - provides the register page
with an input field.
2 Baby -
3 Tee -
5. 4 - -
5 Babytee1234 -
The system displays a
message “Email is
6 -
required” under the input
field.
The password input field is The web application
empty 1 - provides the register page
with an input field.
2 Baby -
3 Tee -
6. 4 Babytee@gmail.com -
5 - -
The system displays a
message “Password is
6 -
required” under the input
field.
The password does not match The web application
all conditions 1 - provides the register page
with an input field.
2 Baby -
3 Tee -
4 Babytee@gmail.com -
7. 5 baby -
The system displays a
cross mark in front of
conditions that are not yet
6 - correct and displays a
message “Password does
not match all conditions”
under the input field.
The password matches some The web application
conditions 1 - provides the register page
with an input field.
8. 2 Baby -
3 Tee -
4 Babytee@gmail.com -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 390
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

5 Baby12 -
The system displays a
cross mark in front of
conditions that are not yet
correct, displays a correct
mark in front of conditions
that are correct displays a
message “Password does
6 -
not match all conditions”
under the input field.
The password matches all The web application
conditions 1 - provides the register page
with an input field.
2 Baby -
3 Tee -
4 Babytee@gmail.com -
9.
5 Babytee1234 -
The system displays a
correct mark in front of
6 - conditions that are correct
and displays a message
“Registration Successful”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 391
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.2) STC-02: Log in
Test ID: STC-02
Test No: UC-02
Test case name: Log in
Description: Registered user can log in to access the features in web application.
Test Script:
1. Click on the “Log in” button on the navigation bar
2. Input email
3. Input password
4. Click on the “Log in” button
Prepared data: email and password
Correct data:
Email: Babytee@gmail.com
Password: Babytee1234
Test
No. Description Script Input Expected Output
No.
User (registered user) login The web application
successful. 1 - provides the login page
with an input field.
2 Babytee@gmail.com -
1.
3 Babytee1234 -
The system will
4 - redirect to the home
page.
Input the wrong email. The web application
1 - provides the login page
with an input field.
2 Baby@gmail.com -
2.
3 Babytee1234 -
The system displays a
4 - message “Invalid email
or password”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 392
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Input the wrong password. The web application
1 - provides the login page
with an input field.
2 Babytee@gmail.com -
3.
3 baby -
The system displays a
4 - message “Invalid email
or password”.
The email input field is empty. The web application
1 - provides the login page
with an input field.
2 - -
4.
3 Babytee1234 -
The system displays a
4 - message “Email is
required”.
The password input field is The web application
empty. 1 - provides the login page
with an input field.
2 Babytee@gmail.com -
5.
3 - -
The system displays a
4 - message “Password is
required”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 393
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.3) STC-03: Log out
Test ID: STC-03
Test No: UC-03
Test case name: Log out
Description: Registered user can log out from the system.
Test Setup:
1. Already log in into the system
2. Registered user is on workspace page
Test Script:
1. Click on the “Workspace” button on the navigation bar
2. Click on the “Log out” button in the workspace page
Test
No. Description Script Input Expected Output
No.
Log out successfully. The web application
1. 1 - redirects to the home
page.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 394
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.4) STC-04: View all of the jewelry mockups
Test ID: STC-04
Test No: UC-04
Test case name: View all of the jewelry mockups
Description: User (unregistered and registered user) can view all available
jewelry mockups provided by the web application.
Test Setup:
1. User is on the home page.
Test Script:
1. Click on the “Jewelry” button on the home page.
2. User is on the “All Jewelry Mockups” page.
Test
No. Description Script Input Expected Output
No.
User (unregistered and The web application
registered user) view all of the displays all of the
1. 1 -
jewelry mockups. jewelry mockups from
the database.
No mockup displayed on the The system displays
web page. message “No Mockups
2. 1 - found in All Jewelry
Mockups” on all
jewelry mockups page.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 395
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.5) STC-05: View all of the packaging mockups
Test ID: STC-05
Test No: UC-05
Test case name: View all of the packaging mockups
Description: User (unregistered and registered user) can view all available
packaging mockups provided by the web application.
Test Setup:
1. User is on the home page.
Test Script:
1. Click on the “Packaging” button on the home page.
2. User is on the “All Packaging Mockups” page.
Test
No. Description Script Input Expected Output
No.
User (unregistered and The web application
registered user) view all of the displays all of the
1. 1 -
packaging mockups. packaging mockups
from the database.
No mockup displayed on the The system displays
web page. message “No Mockups
found in All Packaging
2. 1 -
Mockups” on all
packaging mockups
page.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 396
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.6) STC-06: View the jewelry mockups by category
Test ID: STC-06
Test No: UC-06
Test case name: View the jewelry mockups by category
Description: User (unregistered and registered user) can view the jewelry
mockups in the category “Necklace” and “Bracelet”.
Test Setup:
1. User is on the “All Mockups” page.
Test Script:
1. Choose the category in the “sidebar”.
Test
No. Description Script Input Expected Output
No.
View all mockups The web application will display
1. (default state, no - all available jewelry mockups
subcategory from the database.
selected.)
Choose mockups The web application display only
2. in category 1 - all available mockups in category
“Necklaces”. necklace.
Choose mockups The web application will display
3. in category 1 - only all available mockups in
“Bracelets”. category bracelet.
Empty result from The system shows message “No
4. API for all 1 - mockups found for
mockups. ‘All Mockups’”
Empty result from The system shows message “No
API for mockups mockups found for ‘Necklace’”
5. of category -
“Necklaces”.
Empty result from The system shows message “No
API for mockups mockups found for ‘Bracelet’”
1 -
6. of category
“Bracelets”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 397
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.7) STC-07: View the packaging mockups by category
Test ID: STC-07
Test No: UC-07
Test case name: View the packaging mockups by category
Description: User (unregistered and registered user) can view the packaging
mockups in the category “Necklace Boxes”, “Bracelet Boxes”, and “Bracelet
Boxes with Pillow”.
Test Setup:
1. User is on the “All Packages” page.
Test Script:
1. Choose the category in the “sidebar”.
Test
No. Description Script Input Expected Output
No.
View all mockups 1 The web application will display
1. (default state, no - all available packaging mockups
subcategory from the database.
selected.)
2. Choose mockups The web application will display
in category 1 - only mockups in category
“Necklace necklace box.
Boxes”.
3. Choose mockups - The web application will display
in category 1 only mockups in category
“Bracelets bracelet box.
Boxes”.
4. Choose mockups - The web application will display
in category 1 only mockups in category
“Bracelets Boxes bracelet box with pillow.
with Pillow”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 398
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

5. Empty result from 1 - The system shows message “No
API for all mockups found from the database.
mockups.
6. Empty result from 1 - The system shows message “No
API for mockups mockups found for
of category ‘Necklace Boxes’”
“Necklace
Boxes”.
7. Empty result from - The system shows message “No
API for mockups 1 mockups found for
of category ‘Bracelet Boxes’”
“Bracelets
Boxes”.
8. Empty result from 1 - The system shows message “No
API for mockups mockups found for
of category ‘Bracelet Boxes with Pillow’”
“Bracelets Boxes
with Pillow”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 399
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.8) STC-08: Use the predefined jewelry mockups
Test ID: STC-08
Test No: UC-08
Test case name: Choose the jewelry mockup to customize
Description: Registered user can choose the jewelry mockup to customize, then
the system redirects to the customization jewelry page and correctly displays the
3D model and mockup information.
Test Setup:
1. Already logged into the system.
2. At least one jewelry mockup exists in the system.
Test Script:
1. Registered user is on the “All Mockups” page or the mockups page
with the category.
2. Click the “Custom” button.
Test
No. Description Script Input Expected Output
No.
Registered user is - The web application will display
1. logged in and 1 the list of jewelry mockup with
clicks “Custom the “Custom” button and the
mockup name.
button”
2 - The web application redirects to
customization jewelry page and
shows correct 3D model, name,
and the default values.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 400
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.9) STC-09: Use the predefined packaging mockups
Test ID: STC-09
Test No: UC-09
Test case name: Choose the packaging mockup to customize
Description: Registered user can choose the packaging mockup to customize,
then the system redirects to the customization packaging page and correctly
displays the 3D model and mockup information.
Test Setup:
1. Already logged into the system.
2. At least one packaging mockup exists in the system.
Test Script:
1. Registered user is on the “All Packages” page or the mockups page
with the category.
2. Click the “Custom” button.
Test
No. Description Script Input Expected Output
No.
Registered user The web application will display
1. click “Custom the list of packaging mockup with
1 -
button” the “Custom” button and the
mockup name.
The web application redirects to
customization packaging page and
2 -
shows correct 3D model, name,
and the default values.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 401
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.10) STC-10: Upload an Image to convert to 3D
Test ID: STC-10
Test No: UC-10
Test case name: Upload an Image to convert to 3D
Description: Registered user can upload an image (JPG, JPEG or PNG) by
clicking, dragging-and-dropping the image into the upload area to convert the
image into a 3D model.
Test Setup:
1. Already logged into the system.
2. Already have the image in the format JPG, JPEG, or PNG to convert
Test Script:
1. Click on the “Image To 3D” button on the home page.
2. Upload the image by clicking or dragging-and-dropping.
3. View the preview image in the upload area.
4. Click on the “Generate” button.
5. View the loading state.
6. View the 3D model generation from the uploaded image.
Prepared data:
1. Valid image file format.
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application will display
upload a valid 1 - “Image To 3D” button on the
image file format. home page.
The web application will display
2 - the upload area and ‘Generate’
button.
The web application will display
3 “bracelet.png” the preview image in the upload
area.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 402
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

The web application will display
4 -
the loading state.
The web application will display
5 - the 3D model generation from the
uploaded image.
4.11) STC-11: Create the name of the design
Test ID: STC-11
Test No: UC-11
Test case name: Create the name of the design
Description: Registered user can create the name of the design according to their
needs.
Test Setup:
1. Already logged into the system
Test Script:
1. Click on the “Image To 3D” button on the home page
2. Input the model’s name in the input field on the Image to 3D page
before generating the model
Prepared Data:
- User’s model name
- Default name: New Model
Test
No. Description Script Input Expected Output
No.
Input model name. The system will create a 3D model
1. 1 Necklace
and save its name in the database.
No user input, but The system will create a 3D model
2. the default name 1 New Model and save its name in the database.
exists.
Not input model The system displays message
3. name. 1 - “Please create name before
generating your model.”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 403
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.12) STC-12: Delete the uploaded image
Test ID: STC-12
Test No: UC-12
Test case name: Delete the uploaded image
Description: Registered user can delete the uploaded image.
Test Setup:
1. Already logged into the system
Test Script:
1. Click on the “Image To 3D” button on the home page
2. Upload the image that want to convert to a model
3. Click the “Delete” button
Prepared Data:
Image: necklace.jpg
Test
No. Description Script Input Expected Output
No.
Registered user The system will display a delete
1. can upload the 1 necklace.jpg button after uploading the image.
image.
Registered user The system will delete the
can delete the uploaded image and the image
2. 1 -
image. input field will return to default
field.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 404
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.13) STC-13: Use the converted image to 3d model to customize
Test ID: STC-13
Test No: UC-13
Test case name: Use the converted image to 3d model to customize
Description: Registered users can use the converted image to 3d model to
customize, and the system will provide details of the selected model.
Test Setup:
1. Already logged into the system
Test Script:
1. Registered user is on the “Image to 3D” page
2. Click the “Custom” button in the navigation sidebar.
Test
No. Description Script Input Expected Output
No.
Registered user is The web application will display
1. logged in and 1 the 3d model with the “Custom”
-
clicks “Custom button in image to 3d page.
button” The web application redirects to
2 - image to 3d customization page
and shows correct 3D model.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 405
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.14) STC-14: View the jewelry model
Test ID: STC-14
Test No: UC-14
Test case name: View the jewelry model
Description: The registered user can view the selected jewelry model in the
model viewer.
Test Setup:
1. Already logged into the system.
2. Already selected the jewelry model.
Test Script:
1. Registered user is on the “Jewelry Customization” or “Image to 3d
Customization” page.
2. Clicks the “Custom” button in the navigation sidebar.
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application displays the
view the selected 1 - selected jewelry model in the
jewelry model. model viewer.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 406
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.15) STC-15: Customize the name of the jewelry model
Test ID: STC-15
Test No: UC-15
Test case name: Customize the name of the jewelry model
Description: The registered user can customize the name of the jewelry model to
a new desired name.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization” page.
2. Click on the input field that already has the default name in the jewelry
sidebar.
Prepared Data:
- New name: My new necklace
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application provides the
edits the name “Jewelry Customization” page
1 -
with the current name of the
jewelry model in the input field.
2 My new necklace -
The system updates the displayed
3 -
name in the input field.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 407
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.16) STC-16: Customize the color of the jewelry model
Test ID: STC-16
Test No: UC-16
Test case name: Customize the color of the jewelry model
Description: The registered user can customize the color of the jewelry model
and can preview the color changes in real-time.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization” or “Image to 3D
Customization” page.
2. Click the “Custom” button in the navigation bar.
3. Click the color dropdown.
Prepared Data:
- New selected color: Rose pink
Test
No. Description Script Input Expected Output
No.
Registered user The web application provides the
1. selects the new “Jewelry Customization” or
color of the - “Image to 3D Customization”
page with the color dropdown.
jewelry model
-
from the color
2 Rose pink
dropdown.
The system updates and displays
3 - the jewelry model with the
selected color in real-time.
2. Registered user The web application provides the
did not select a “Jewelry Customization” page or
1 -
color. “Image to 3D Customization”
page with the color dropdown.
2 - -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 408
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

The system displays the default
3 -
color as clear.
4.17) STC-17: Customize the material of the jewelry model
Test ID: STC-17
Test No: UC-17
Test case name: Customize the material of the jewelry model
Description: The registered user can customize the material of the jewelry model
and can preview the material changes in real-time.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization” or “Image to 3D
Customization” page.
2. Click the “Custom” button in the navigation bar.
3. Click the material dropdown.
Prepared Data:
- New selected material: Gold
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application provides the
selects the new “Jewelry Customization” or
1 -
material of the “Image to 3D Customization”
page with the material dropdown.
jewelry model
2 Gold -
from the material
The system updates and displays
dropdown.
3 - the jewelry model with the
selected material in real-time.
2. Registered user The web application provides the
did not select a “Jewelry Customization” page or
1 -
material. “Image to 3D Customization”
page with the material dropdown.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 409
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

2 - -
The system displays the default
3 -
color as silver.
4.18) STC-18: Customize the size of the jewelry model
Test ID: STC-18
Test No: UC-20
Test case name: Customize the size of the jewelry model
Description: The registered user can customize the size of the jewelry model and
can preview the size changes in real-time.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization” or “Image to 3D
Customization” page.
2. Click the “Custom” button in the navigation bar.
3. Drag the size slider.
Prepared Data:
- New selected size: 40mm.
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application provides the
changes the size “Jewelry Customization” or
of the jewelry 1 - “Image to 3D Customization”
page with the size slider.
model from the
size slider.
2 40mm. -
The system updates and displays
3 - the jewelry model with the
selected size in real-time.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 410
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Registered user
2. did not select the The web application provides the
size. 1 - “Jewelry Customization” page or
“Image to 3D Customization”
page with the size slider.
2 - -
The system displays the default
3 - size as 31mm.
4.19) STC-19: Customize the color of specific jewelry sections (Use the
predefined jewelry mockup)
Test ID: STC-19
Test No: UC-21
Test case name: Customize the color of specific jewelry sections (Use the
predefined jewelry mockup)
Description: The registered user can customize the color of specific parts of a
predefined jewelry mockup by cropping the part that they want.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization” page.
2. Click the “Custom” button in the navigation bar.
3. Click the “Crop” button in the bottom bar.
4. Drag on the 3D model to define the area.
5. Click the color dropdown.
Prepared Data:
- New selected color: Rose pink
Document 3DJewelryCraft_ Owner NP1, NP2 Page 411
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Test
No. Description Script Input Expected Output
No.
1. Customizes the The web application provides the
color of specific “Jewelry Customization” or
sections correctly 1 “Image to 3D Customization”
-
and confirms the
page with the color dropdown and
Crop” button in the bottom bar.
change by
The web application displays a
clicking the
2 square crop box following the
cancel crop -
registered user’s drag.
button.
The web application applies the
new color to the cropped section
3 Rose pink and updates the model in real-
time.
The web application preserves the
applied color and returns to the
- normal customization mode.
2. Customizes the The web application provides the
color of specific “Jewelry Customization” or
sections correctly “Image to 3D Customization”
and cancles the 1 - page with the color dropdown and
Crop” button in the bottom bar.
change by
The web application displays a
clicking outside
2 square crop box following the
the crop box. -
registered user’s drag.
The web application applies the
new color to the cropped section
Rose pink and updates the model in real-
time.
The web application discards the
4 selected color.
-
3. Crops outside the The system displays the message
model. “Please drag on the model area to
- apply customization.”
4. Start cropping The system allows cropping and
again after recoloring as usual.
recoloring 1 -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 412
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.20) STC-20: Customize the color of specific jewelry sections (Use converted
image to 3d model)
Test ID: STC-20
Test No: UC-21
Test case name: Customize the color of specific jewelry sections (Use the
converted image to 3d model)
Description: The registered user can customize the color of specific parts of a
converted image to 3d model by cropping the part that they want.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Image to 3d Customization” page.
2. Click the “Custom” button in the navigation bar.
3. Click the “Crop” button in the bottom bar.
4. Drag on the 3D model to define the area.
5. Click the color dropdown.
Prepared Data:
- New selected color: Rose pink
Test
No. Description Script Input Expected Output
No.
1. Customizes the The web application provides the
color of specific “Jewelry Customization” or
sections correctly 1 - “Image to 3D Customization”
and confirms the
page with the color dropdown and
Crop” button in the bottom bar.
change by
The web application displays a
clicking the
2 - square crop box following the
registered user’s drag.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 413
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

cancel crop The web application applies the
button. new color to the cropped section
3 Rose pink and updates the model in real-
time.
The web application preserves the
applied color and returns to the
4 - normal customization mode.
2. Customizes the The web application provides the
color of specific “Jewelry Customization” or
sections correctly 1 - “Image to 3D Customization”
page with the color dropdown and
and cancles the
Crop” button in the bottom bar.
change by
The web application displays a
clicking outside
2 - square crop box following the
the crop box.
registered user’s drag.
The web application applies the
new color to the cropped section
Rose pink and updates the model in real-
time.
The web application discards the
4 selected color.
-
3. Crops outside the The system displays the message
model. “Please drag on the model area to
- apply customization.”
4. Start cropping The system allows cropping and
again after recoloring as usual.
recoloring 1 -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 414
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.21) STC-21: Customize the material of specific jewelry sections (Use the
predefined jewelry mockup)
Test ID: STC-21
Test No: UC-22
Test case name: Customize the material of specific jewelry sections (Use the
predefined jewelry mockup)
Description: The registered user can customize the material of specific parts of a
predefined jewelry mockup by cropping the part that they want.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization” page.
2. Click the “Custom” button in the navigation bar.
3. Click the “Crop” button in the bottom bar.
4. Drag on the 3D model to define the area.
5. Click the material dropdown.
Prepared Data:
- New selected material: Gold
Test
No. Description Script Input Expected Output
No.
1. Customizes the The web application provides the
material of “Jewelry Customization” or
specific sections “Image to 3D Customization”
- page with the material dropdown
correctly and
and Crop” button in the bottom
confirms the
bar.
change by
The web application displays a
clicking the
2 square crop box following the
cancel crop -
registered user’s drag.
button.
The web application applies the
new material to the cropped
Document 3DJewelryCraft_ Owner NP1, NP2 Page 415
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3 Gold section and updates the model in
real-time.
The web application preserves the
applied material and returns to the
4 - normal customization mode.
Customizes the The web application provides the
2. material of “Jewelry Customization” or
1 - “Image to 3D Customization”
specific sections
page with the material dropdown
correctly and
and Crop” button in the bottom
cancles the
bar.
change by
The web application displays a
clicking outside
2 - square crop box following the
the crop box.
registered user’s drag.
The web application applies the
new material to the cropped
3 Gold section and updates the model in
real-time.
The web application discards the
4 - selected material.
3. Crops outside the The system displays the message
model. “Please drag on the model area to
1 - apply customization.”
4. Start cropping The system allows cropping and
again after change change the material as usual.
the material 1 -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 416
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.22) STC-22: Customize the material of specific jewelry sections (Use
converted image to 3d model)
Test ID: STC-22
Test No: UC-22
Test case name: Customize the material of specific jewelry sections (Use the
converted image to 3d model)
Description: The registered user can customize the material of specific parts of a
converted image to 3d model by cropping the part that they want.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Image to 3d Customization” page.
2. Click the “Custom” button in the navigation bar.
3. Click the “Crop” button in the bottom bar.
4. Drag on the 3D model to define the area.
5. Click the material dropdown.
Prepared Data:
- New selected material: Gold
Test
No. Description Script Input Expected Output
No.
1. Customizes the The web application provides the
material of “Jewelry Customization” or
specific sections “Image to 3D Customization”
1 -
page with the material dropdown
correctly and
and Crop” button in the bottom
confirms the
bar.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 417
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

change by The web application displays a
clicking the 2 - square crop box following the
cancel crop registered user’s drag.
button. The web application applies the
3 new material to the cropped
Gold
section and updates the model in
real-time.
The web application preserves the
applied material and returns to the
4 - normal customization mode.
2. Customizes the The web application provides the
material of “Jewelry Customization” or
specific sections “Image to 3D Customization”
1 -
page with the material dropdown
correctly and
and Crop” button in the bottom
cancles the
bar.
change by
The web application displays a
clicking outside
2 - square crop box following the
the crop box.
registered user’s drag.
The web application applies the
new material to the cropped
3 Gold section and updates the model in
real-time.
The web application discards the
4 - selected material.
3. Crops outside the The system displays the message
model. “Please drag on the model area to
1 - apply customization.”
4. Start cropping The system allows cropping and
again after change change the material as usual.
the material 1 -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 418
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.23) STC-23: Zoom in and zoom out the jewelry model
Test ID: STC-23
Test No: UC-23
Test case name: Zoom in and zoom out the jewelry model
Description: The registered user can zoom in and zoom out of the jewelry model
to closely examine design details or view the entire piece more clearly.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization” or “Image to 3D
Customization” page.
2. Click on the “Zoom-in” (plus button) or “Zoom-out” (minus button) in
the bottom bar.
Test
No. Description Script Input Expected Output
No.
1. Verify zoom-in The system displays a zoomed in
functionality the jewelry model (larger view,
closer details visible).
1 -
2. Verify zoom-out The system displays a zoomed out
functionality the jewelry model (smaller view,
1 - wider perspective visible).
Document 3DJewelryCraft_ Owner NP1, NP2 Page 419
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.24) STC-24: View the packaging model
Test ID: STC-24
Test No: UC-24
Test case name: View the packaging model
Description: Registered users can view the selected packaging model in the
model viewer.
Test Setup:
1. Already logged into the system
2. Already select the packaging model that want to customize.
Test Script:
1. Registered user is on the “Packaging Customization” page with the
selected packaging model.
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application will display
views the selected the selected packaging model in
packaging model 1 - the model viewer.
in the model
viewer.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 420
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.25) STC-25: Customize the color of the packaging model
Test ID: STC-25
Test No: UC-26
Test case name: Customize the color of the packaging model
Description: Registered user can change the packaging model’s color by
selecting from a color palette, inputting a valid hex code, or choosing a custom
color using a color picker, then the system applies the new color in real-time to
the packaging model in the model viewer.
Test Setup:
1. Already logged into the system
2. The packaging model has been loaded and displayed in the model
viewer.
Test Script:
1. Registered user is on the “Packaging Customization” page
2. Click on the “Custom” button in the navigation sidebar.
3. Choose a color from the palettes, or input a hex code, or pick a custom
color.
Prepared Data:
- Hex color from palettes: #EBDECD
- Valid hex color from user’s input: #C3A59A
- Invalid hex color from user’s input: #ZZZZZZ
- Hex color from color picker: #AB5C5C
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application displays the
selects a color provided palettes by the category
1 -
from the system- (e.g., Minimalist,
Elegant&Neutral).
provided palettes.
The system applies the selected
2 #EBDECD color from the palettes to the
Document 3DJewelryCraft_ Owner NP1, NP2 Page 421
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

packaging model in the model
viewer area.
2. Registered user The web application displays the
inputs a valid hex 1 input field.
-
color code.
The system applies the color from
the inputted color code to the
2 #C3A59A packaging model in the model
viewer area.
3. Registered user The web application displays the
1 -
inputs invalid input field to input the color code.
valid hex color The system displays a message
“Invalid color code. Please enter a
code. 2 #ZZZZZZ
valid hex code or select a color
from the palette.”
4. Registered user The web application displays the
1 -
chooses a custom color picker.
color using the The system displays the picked
color in the input field and applies
color picker. 2 #AB5C5C
the color to the packaging model
in the model viewer area.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 422
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.26) STC-26: Add engraved text to the packaging model
Test ID: STC-26
Test No: UC-27
Test case name: Add engraved text to the packaging model
Description: Registered user can add custom engraved text to the selected
packaging model, including entering text, selecting font style, choosing font size,
changing text color, and dragging text to the desired position, then the system
displays the updated text in real-time on the model viewer.
Test Setup:
1. Already logged into the system
2. Registered user is on the “Packaging Customization” page
3. The packaging model has been loaded and displayed in the model
viewer.
Test Script:
1. Click on the “Custom” button in the navigation sidebar.
2. Enter custom text using the input field.
3. Select a font style using the dropdown menu.
4. Select a font size using the dropdown menu.
5. Select a text color using the color picker.
6. Drag the text to the desired position on the packaging model.
7. View the packaging model with the applied text, font, size, color, and
position.
Prepared Data:
- Text: 3DJewelryCraft
- Font style: Inter
- Font size: 16
- Hex color from color picker: #AB5C5C
Document 3DJewelryCraft_ Owner NP1, NP2 Page 423
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Test
No. Description Script Input Expected Output
No.
1. Registered user The web application displays the
enters custom text 1 - input field.
in the input field.
The system displays the text on
2 3DJewelryCraft the packaging model in the model
viewer.
2. Registered user The web application displays the
selects font style 1 - font style dropdown.
using dropdown
menu. The system updates the text on the
2 Inter packaging model with the selected
font style.
3. Registered user The web application displays the
1 -
selects font size font size dropdown.
using the The system updates the text on the
dropdown menu. 2 packaging model with the selected
font size.
4. Registered user The web application displays the
1 -
selects text color color picker.
using the color The system updates the text color
2 #454A4D on the packaging model with the
picker.
selected color.
5. Registered user The web application updates the
drags the text to text position on the packaging
the desired 1 - model in real-time.
position on the
packaging model.
6. Registered user The web application removes text
removes the text 1 - from preview and resets the state.
from input field.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 424
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.27) STC-27: Replace with a new packaging model
Test ID: STC-27
Test No: UC-28
Test case name: Replace with a new packaging model
Description: Registered user can replace the currently applied packaging model
with a new one from the customization sidebar in the “Packaging Customization”
page.
Test Setup:
1. Already logged into the system
2. At least one packaging model is currently applied.
3. At least one packaging mockup exists in the system.
Test Script:
1. Registered user is on the “Packaging Customization” page with at least
one packaging model currently applied.
2. Select a new packaging model from the “All Packaging” button in the
customization sidebar.
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application displays a
selects a new list of packaging mockup
1 -
packaging model. thumbnails in the customization
sidebar.
The system highlights selection
on the new packaging model
2 -
thumbnail.
The system replaces the old
3 - packaging with the new one and
updates the model viewer.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 425
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.28) STC-28: Choose the jewelry to try-on with packaging
Test ID: STC-28
Test No: UC-29
Test case name: Choose the jewelry to try-on with packaging
Description: Registered user can select saved jewelry from their workspace to try
on with the currently applied packaging model.
Test Setup:
1. Already logged into the system
2. At least one packaging model is currently applied.
3. Registered user has at least one saved jewelry item in their workspace.
Test Script:
1. Registered user is on the “Packaging Customization” page with at least
one packaging model currently applied.
2. Click the “My Jewelry” button in the customization sidebar.
3. Select a jewelry item from the list to try-on the selected jewelry with the
applied packaging.
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application displays a
selects jewelry 1 - list of saved jewelry items from
item from the list the user’s workspace.
to try-on that The system displays the 3D
matches the jewelry model along with the
2 -
applied current packaging in the model
packaging. viewer area.
2. Registered user The web application displays a
selects jewelry 1 - list of saved jewelry items from
item from the list the user’s workspace.
to try-on that The system displays a message
mismatches the “Oops! This jewelry doesn’t fit
applied 2 - with the current package. Try
packaging. selecting a matching type.”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 426
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3. Registered user The system displays a message
doesn’t have any “You don’t have any jewelry in
1 -
saved jewelry in your workspace yet.”
the workspace.
4.29) STC-29: Zoom in and zoom out the packaging model
Test ID: STC-29
Test No: UC-30
Test case name: Zoom in and zoom out the packaging model
Description: The registered user can zoom in and zoom out of the packaging
model to closely examine design details or view the entire piece more clearly.
Test Setup:
1. Already logged into the system
2. The packaging model has been loaded and displayed in the model
viewer.
Test Script:
1. Registered user is on the “Packaging Customization” page.
2. Click on the “Zoom-in” (plus button) or “Zoom-out” (minus button) in
the bottom bar.
Test
No. Description Script Input Expected Output
No.
1. Verify zoom-in The system displays a zoomed in
functionality the jewelry model (larger view,
closer details visible).
1 -
2. Verify zoom-out The system displays a zoomed out
functionality 1 - the jewelry model (smaller view,
wider perspective visible).
Document 3DJewelryCraft_ Owner NP1, NP2 Page 427
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.30) STC-30: Select the type of simulated body to try on
Test ID: STC-30
Test No: UC-31
Test case name: Select the type of simulated body to try on
Description: Registered user can select the type of selected body on which the
jewelry will be virtually tried on.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization”, “Image to 3D”, or
“Image to 3D Customization” page.
2. Click the “Virtual Try-On” button in the bottom bar.
3. Click the “Neck Try-On” or “Wrist Try-On” button to select the type of
simulated body.
Test
No. Description Script Input Expected Output
No.
1. Registered user The web application displays the
selects the “Neck options “Neck Try-On” and
1 -
Try-On”. “Wrist Try-On” for simulated
body type.
The system displays the simulated
2 - neck in the model viewer
2. Registered user The web application displays the
selects the “Wrist options “Neck Try-On” and
1 -
Try-On”. “Wrist Try-On” for simulated
body type.
The system displays the simulated
2 - wrist in the model viewer
Document 3DJewelryCraft_ Owner NP1, NP2 Page 428
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.31) STC-31: View the jewelry on the simulated body
Test ID: STC-31
Test No: UC-32
Test case name: View the jewelry on the simulated body
Description: The registered user can view the model designed on the simulated
body (neck or wrist) in the model viewer.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
3. The simulated body type (neck or wrist) must have been selected.
Test Script:
1. Registered user is on the “Jewelry Customization”, “Image to 3D” or
“Image to 3D Customization” page.
2. Click the “Virtual Try-On” button in the bottom bar.
3. Click the “Neck Try-On” or “Wrist Try-On” button.
Test
No. Description Script Input Expected Output
No.
1. Registered user The system validates whether the
select the jewelry type and simulated body
simulated body 1 - type match.
that matches the
jewelry type.
The system correctly displays the
jewelry model on the selected
2 body model.
-
2. Registered user The system validates whether the
select the jewelry type and simulated body
1 -
simulated body type match.
that mismatches
The system displays message
the jewelry type.
2 - “Try-on is not supported for this
type”.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 429
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.32) STC-32: View all previously designed works
Test ID: STC-32
Test No: UC-33
Test case name: View all previously designed works
Description: Registered user can view all previously designed works on their
workspace.
Test Setup:
1. Already logged into the system
Test Script:
1. Clicks on the “Workspace” button on the navbar or the sidebar.
Test
No. Description Script Input Expected Output
No.
1. Registered user The system validates user
clicks on the 1 - session and navigates to the
“Workspace” “Workspace” page.
The system displays all
button and has the
previously saved jewelry
saved design. 2 -
designs.
2. Registered user The system validates user
clicks on the 1 - session and navigates to the
“Workspace” “Workspace” page.
The system displays
button and has not
2 - message “Don't have saved
the saved design.
design yet.”
Document 3DJewelryCraft_ Owner NP1, NP2 Page 430
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.33) STC-33: Create a new design
Test ID: STC-33
Test No: UC-34
Test case name: Create a new design
Description: Registered user can create a new design for their workspace.
Test Setup:
1. Already logged into the system
Test Script:
1. Clicks on the “Workspace” button on the navbar or the sidebar.
2. Click on the “Create new design” button on the “Workspace” page.
Test
No. Description Script Input Expected Output
No.
1. Registered user clicks The system navigates to the
on the “Create new 1 - “Image to 3D” page.
design” button
Document 3DJewelryCraft_ Owner NP1, NP2 Page 431
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.34) STC-34: Save the designed work
Test ID: STC-34
Test No: UC-35
Test case name: Save the designed work
Description: Registered user can save the designed work to their workspace.
Test Setup:
1. Already logged into the system
Test Script:
1. Clicks the “Save to workspace” button on the “Mockups” or
“Customization” page.
Test
No. Description Script Input Expected Output
No.
1. Registered user clicks The system saves the design to
on the “Save to 1 - the user’s workspace in the
workspace” button. database.
The system displays a message
“Your design has been saved.”
2 -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 432
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.35) STC-35: Save the designed work from the predefined jewelry mockup
Test ID: STC-34
Test No: UC-36
Test case name: Save the designed work from the predefined jewelry mockup
Description: Registered user can save the designed work from the predefined
jewelry mockup to their workspace.
Test Setup:
1. Already logged into the system
Test Script:
1. Clicks the “Save to workspace” button on the “Jewelry Mockups” or
“Jewelry Customization” page.
Test
No. Description Script Input Expected Output
No.
1. Registered user clicks The system saves the jewelry
on the “Save to 1 - design to the user’s workspace in
workspace” button. the database.
The system displays a message
“Your design has been saved.”
2 -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 433
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.36) STC-36: Save the designed work from the converted image to 3d model
Test ID: STC-36
Test No: UC-37
Test case name: Save the designed work from the converted image to 3d model
Description: Registered user can save the designed work from the converted
image to 3d model to their workspace.
Test Setup:
1. Already logged into the system
Test Script:
1. Clicks the “Save to workspace” button on the “Image to 3d” or “Image
to 3d Customization” page.
Test
No. Description Script Input Expected Output
No.
1. Registered user clicks The system saves the converted
on the “Save to 1 - image to 3d model design to the
workspace” button user’s workspace in the database.
when the converted
model is complete. The system displays a message
2 - “Your design has been saved.”
2. Registered user clicks
The system disables the “Save to
on the “Save to
workspace” button, registered
workspace” button 1 -
user cannot press and save the 3d
when the converted
model.
model is uncomplete.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 434
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.37) STC-37: Save the designed work from the predefined packaging mockup
Test ID: STC-37
Test No: UC-38
Test case name: Save the designed work from the predefined packaging mockup
Description: Registered user can save the designed work from the predefined
packaging mockup to their workspace.
Test Setup:
1. Already logged into the system
Test Script:
1. Clicks the “Save to workspace” button on the “Packaging Mockups”
or “Packaging Customization” page.
Test
No. Description Script Input Expected Output
No.
1. Registered user clicks The system saves the packaging
on the “Save to design or packaging design with
1 -
workspace” button. the jewelry to the user’s
workspace in the database.
The system displays a message
“Your design has been saved.”
2 -
Document 3DJewelryCraft_ Owner NP1, NP2 Page 435
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.38) STC-38: Export image as PNG format
Test ID: STC-38
Test No: UC-40
Test case name: Export image as PNG format
Description: Registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a PNG (transparent
background).
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as PNG” button on the modal.
Test
No. Description Script Input Expected Output
No.
1. Registered user The system generates a PNG
1 -
exported PNG image from the 3D scene.
successfully The system downloads a PNG
file named model_snapshot.png
to the registered user’s computer,
2 - and the image accurately
displays the current view of the
3D model.
2. Renderer, Scene, or The system displays the error
Camera not ready message “Failed to export image.
1 -
Please try again”, and no file is
downloaded.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 436
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.39) STC-39: Export image as JPG format
Test ID: STC-39
Test No: UC-41
Test case name: Export image as JPG format
Description: Registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a JPG (white background).
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as JPG” button on the modal.
Test
No. Description Script Input Expected Output
No.
Registered user The system generates a JPG
1.
exported JPG 1 - image from the 3D scene.
successfully
The system downloads a JPG file
named model_snapshot.jpg to
2 the registered user’s computer,
-
and the image accurately
displays the current view of the
3D model.
2. Renderer, Scene, or The system displays the error
Camera not ready message “Failed to export image.
1 -
Please try again”, and no file is
downloaded.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 437
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.40) STC-40: Export the model as PDF report
Test ID: STC-40
Test No: UC-42
Test case name: Export the model as PDF report
Description: Registered users can export their customized designs, including
jewelry, packaging, or a combination of both, as detailed PDF reports.
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Generate PDF Report” button on the modal.
Test
No. Description Script Input Expected Output
No.
1. Registered user The system generates a PDF report with details
exported the 1 - including file name, export date, material,
jewelry PDF color, size, and a preview image of the model.
successfully The system downloads the jewelry PDF report
named jewelryName_customization.pdf to the
2 - registered user’s computer.
2. Registered user The system generates a PDF report with details
exported the including file name, export date, package
packaging PDF 1 - name, package color, engraving text with
successfully color, font, font size, and a preview image of
the model.
The system downloads the jewelry PDF report
2 - named packageName_customization.pdf to the
registered user’s computer.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 438
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

3. Registered user The system generates a PDF report with details
exported the 1 - including file name, export date, jewelry
combination of details, packaging details, and a preview
jewelry and image of the model.
packaging PDF The system downloads the jewelry PDF report
successfully named
2 -
jewelryName_packageName_customization.pdf
to the registered user’s computer.
4. Renderer, Scene, The system displays the error message “Failed to
or Camera not 1 - export PDF report. Please try again”.
ready
4.41) STC-41: Export 3D file as STL format
Test ID: STC-41
Test No: UC-44
Test case name: Export 3D file as STL format
Description: Registered users can export 3D models displayed in the model
viewer in STL format.
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as STL” button on the modal.
Test
No. Description Script Input Expected Output
No.
1. Registered user The system generates a 3D file in
exported STL file 1 - STL format.
successfully.
The system downloads an STL
2 file named Untitled.stl to the
-
registered user’s computer.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 439
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

2. Cannot find model in The system displays the error
model viewer. message “No model to export
1 -
as STL” and no file is
downloaded.
4.42) STC-42: Export 3D file as OBJ format
Test ID: STC-42
Test No: UC-45
Test case name: Export 3D file as OBJ format
Description: Registered users can export 3D models displayed in the model
viewer in OBJ format.
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as OBJ” button on the modal.
Test
No. Description Script Input Expected Output
No.
1. Registered user The system generates a 3D file in
exported OBJ file 1 - OBJ format.
successfully.
The system downloads an OBJ
file named Untitled.obj to the
2 - registered user’s computer.
2. Cannot find model in The system displays the error
model viewer. message “No model to export
1 -
as OBJ” and no file is
downloaded.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 440
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

4.43) STC-43: Export 3D file as GLB format
Test ID: STC-43
Test No: UC-46
Test case name: Export 3D file as GLB format
Description: Registered users can export 3D models displayed in the model
viewer in GLB format.
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as GLB” button on the modal.
Test
No. Description Script Input Expected Output
No.
1. Registered user The system generates a 3D file in
exported GLB file 1 - GLB format.
successfully.
The system downloads a GLB
file named Untitled.glb to the
2 - registered user’s computer.
2. Cannot find model in The system displays the error
model viewer. message “No model to export
1 -
as GLB” and no file is
downloaded.
Document 3DJewelryCraft_ Owner NP1, NP2 Page 441
Name Test_Plan_V.0.9
Document Test Plan Release Date 20/10/2025 Print Date 20/10/2025
Type

---

Chapter 6
Test Record

---

Document History
Document Version History Status Date Editable Reviewer
Name
3DJewelryCraft_ 3DJewelryCraft_ Add Chapter 1 Draft 23/05/2025 NP1, SW
Test_Record_ Test_Record_ Add Chapter 2 NP2
V.0.1 V.0.1 Add Chapter 3
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 23/05/2025 NP1, SW
Test_Record_ Test_Record_ Update Chapter 2 NP2
V.0.2 V.0.2 Update Chapter 3
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 24/05/2025 NP1, SW
Test_Record_ Test_Record_ Update Chapter 2 NP2
V.0.3 V.0.3 Update Chapter 3
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 2 Draft 28/05/2025 NP1, SW
Test_Record_ Test_Record_ Update Chapter 3 NP2

## V.0.4 V.0.4

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 30/08/2025 NP1, SW
Test_Record_ Test_Record_ Update Chapter 2 NP2
V.0.5 V.0.5 Update Chapter 3
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Final 18/10/2025 NP1, SW
Test_Record_ Test_Record_ Update Chapter 2 NP2
V.0.6 V.0.6 Update Chapter 3
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 443
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## TABLE OF CONTENTS

Document History ..................................................................................................................... 443
1.1) Purpose ........................................................................................................................... 447
1.2) Scope ............................................................................................................................... 447
1.3) User Characteristics ...................................................................................................... 447
1.4) Acronyms and Definitions............................................................................................. 448
1.4.1) Acronyms ................................................................................................................. 448
1.4.2) Definitions................................................................................................................ 448
1.5) Test Responsibilities ...................................................................................................... 449
Chapter Two | Unit Test ........................................................................................................... 450
2.1) UTC-01: Register ........................................................................................................... 450
2.2) UTC-02: Log in .............................................................................................................. 451
2.3) UTC-03: Log out ............................................................................................................ 452
2.4) UTC-04: View all of the jewelry mockups................................................................... 453
2.5) UTC-05: View all of the packaging mockups .............................................................. 454
2.6) UTC-06: View the jewelry mockups by category ....................................................... 455
2.7) UTC-07: View the packaging mockups by category .................................................. 456
2.8) UTC-08: Choose the jewelry mockup to customize .................................................... 457
2.9) UTC-09: Choose the packaging mockup to customize ............................................... 458
2.10) UTC-10: Upload an image for 3D generation ........................................................... 459
2.11) UTC-11: Generate 3D model from the uploaded image. ......................................... 460
2.12) UTC-12: Save GLB File from Meshy API................................................................. 461
2.13) UTC-13: Retrieve GLB URL from Database............................................................ 462
2.14) UTC-14: Create the name of the design .................................................................... 463
2.15) UTC-15: Customize the color of specific jewelry sections (Use the predefined
jewelry mockup) .................................................................................................................... 464
2.16) UTC-16: Customize the jewelry of specific jewelry sections (Use the converted
model) ..................................................................................................................................... 465
2.17) UTC-17: Customize the material of specific jewelry sections (Use the predefined
jewelry mockup) .................................................................................................................... 466
2.18) UTC-18: Customize the material of specific jewelry sections (Use the converted
model) ..................................................................................................................................... 467
2.19) UTC-19: Retrieve the previous customization of a jewelry ..................................... 468
2.20) UTC-20: Choose the jewelry to try-on with packaging ........................................... 470

---

2.21) UTC-21: Select the type of selected body to try on ................................................... 471
2.22) UTC-22: View all previously designed works ........................................................... 472
2.23) UTC-23: Save the designed work from the predefined jewelry mockup that has not
been customized. ................................................................................................................... 473
2.24) UTC-24: Save the designed work from the predefined jewelry mockup that has
been customized. ................................................................................................................... 474
2.25) UTC-25: Save the designed work from the converted image to 3d model that has
not been customized. ............................................................................................................. 475
2.26) UTC-26: Save the designed work from the converted image to 3d model that has
been customized. ................................................................................................................... 476
Unit Test ID: UTC-26 ........................................................................................................... 476
2.27) UTC-27: Save the designed work from the predefined packaging mockup that has
not been customized. ............................................................................................................. 477
2.28) UTC-28: Save the designed work from the predefined packaging mockup that has
been customized. ................................................................................................................... 478
Chapter Three | System Test .................................................................................................... 479
3.1) STC-01: Register............................................................................................................ 479
3.2) STC-02: Log in ............................................................................................................... 481
3.3) STC-03: Log out............................................................................................................. 483
3.4) STC-04: View all of the jewelry mockups ................................................................... 484
3.5) STC-05: View all of the packaging mockups .............................................................. 485
3.6) STC-06: View the jewelry mockups by category ........................................................ 486
3.7) STC-07: View the packaging mockups by category ................................................... 487
3.8) STC-08: Use the predefined jewelry mockup to customize ....................................... 488
3.9) STC-09: Use the predefined packaging mockup to customize .................................. 489
3.10) STC-10: Upload an Image to convert to 3D .............................................................. 490
3.11) STC-11: Create the name of the design ..................................................................... 491
3.12) STC-12: Delete the uploaded image ........................................................................... 492
2.13) STC-13: Use the converted image to 3d model to customize ................................... 493
3.14) STC-14: View the jewelry model ................................................................................ 494
3.15) STC-15: Customize the name of the jewelry model ................................................. 495
3.16) STC-16: Customize the color of the jewelry model .................................................. 496
3.17) STC-17: Customize the material of the jewelry model ............................................ 497
3.18) STC-18: Customize the size of the jewelry model .................................................... 498
3.19) STC-19: Customize the color of specific jewelry sections (Use the predefined
jewelry mockup) .................................................................................................................... 499

---

3.20) STC-20: Customize the color of specific jewelry sections (Use converted image to 3d
model) ..................................................................................................................................... 501
3.21) STC-21: Customize the material of specific jewelry sections (Use the predefined
jewelry mockup) .................................................................................................................... 503
3.22) STC-22: Customize the material of specific jewelry sections (Use converted image
to 3d model) ........................................................................................................................... 505
3.23) STC-23: Zoom in and zoom out the jewelry model .................................................. 507
3.24) STC-24: View the packaging model ........................................................................... 508
3.25) STC-25: Customize the color of the packaging model ............................................. 509
3.26) STC-26: Add engraved text to the packaging model................................................ 511
3.27) STC-27: Replace with a new packaging model ......................................................... 513
3.28) STC-28: Choose the jewelry to try-on with packaging ............................................ 514
3.29) STC-29: Zoom in and zoom out the packaging model ............................................. 515
3.30) STC-30: Select the type of simulated body to try on ................................................ 516
3.31) STC-31: View the jewelry on the simulated body .................................................... 517
3.32) STC-32: View all previously designed works ............................................................ 518
3.33) STC-33: Create a new design ..................................................................................... 519
3.34) STC-34: Save the designed work ................................................................................ 520
3.35) STC-35: Save the designed work from the predefined jewelry mockup ................ 521
3.36) STC-36: Save the designed work from the converted image to 3d model .............. 522
3.37) STC-37: Save the designed work from the predefined packaging mockup ........... 523
3.38) STC-38: Export image as PNG format ...................................................................... 524
3.39) STC-39: Export image as JPG format ....................................................................... 525
3.40) STC-40: Export the model as PDF report ................................................................. 526
3.41) STC-41: Export 3D file as STL format ...................................................................... 527
3.42) STC-42: Export 3D file as OBJ format ..................................................................... 528
3.43) STC-43: Export 3D file as GLB format ..................................................................... 529

---

Chapter One | Introduction
1.1) Purpose
The purpose of this test record is to record the test result testing follow the test
plan and see if the actual result is the same as the expected result.
1.2) Scope
• Measure user requirement and system requirements
• Specify unit test for backend
• Specify system tests that follow the use case
o Feature#1: Register
o Feature#2: Jewelry and Packaging Mockups
o Feature#3: Image to 3D
o Feature#4: Customization
o Feature#5: Virtual Try-On
o Feature#6: Workspace
o Feature#7: Super Export
1.3) User Characteristics
Title Definition
The people who are not registered to the
system. These users can only browse and
preview mockups available on the platform.
Unregistered User
They typically include curious creatives who
are exploring the idea of designing custom
jewelry.
The people who have already registered and
logged in to the web application. These users
range from beginner jewelry entrepreneurs
Registered User looking to launch a brand with minimal
technical skills, to self-expressive, trend-
conscious individuals who value aesthetic
freedom without needing a full design team.
The people who interact with the
User 3DJewelryCraft system. This can include both
unregistered and registered user.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 447
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

1.4) Acronyms and Definitions
1.4.1) Acronyms
UTC Unit Test Case
STC System Test Case
TD Test case
TC Test Case
2D Two Dimension
3D Three Dimension
PNG Portable Network Graphics
JPG Joint Photographic Experts Group
PDF Portable Document Format
STL Stereolithography
OBJ Wavefront Object
GLB GL Transmission Format Binary file
1.4.2) Definitions
Title Definition
The web application that transforms 2D
jewelry designs into customizable 3D models,
3DJewelryCraft
allowing users to visualize, personalize, and
export their creations.
The people who are not registered to the
system. These users can only browse and
preview mockups available on the platform.
Unregistered User
They typically include curious creatives who
are exploring the idea of designing custom
jewelry.
The people who have already registered and
logged in to the web application. These users
range from beginner jewelry entrepreneurs
Registered User looking to launch a brand with minimal
technical skills, to self-expressive, trend-
conscious individuals who value aesthetic
freedom without needing a full design team.
Computer programs, procedures, and
System associated documentation and data pertain to
the operation of a computer system.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 448
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

An activity in which a system or component
is executed under specified conditions, the
Test results are observed or recorded, and an
evaluation is made of some aspect of the
system or component.
Testing conducted on a complete and
System Testing integrated system for evaluate the system’s
compliance with its specified requirements.
1) Testing of individual routines and modules
by the developer or an independent tester.
2) A test of individual programs or modules in
Unit Test order to ensure that there are no analysis or
programming errors (ISO/IEC 2382-20).
3) Test of individual hardware or software
units or groups of related units (ISO 24765).
Document detailing the objectives, resources,
and processes for a specific test for a software
Test Plan or hardware product. The plan typically
contains a detailed understanding of the
eventual workflow.
A predefined mockup is a ready-made 3D
Predefined Mockups model that serves as a template for
showcasing jewelry or packaging designs.
A 3D object generated by processing a 2D
Converted Image to 3D Model
image through the meshy API.
1.5) Test Responsibilities
Name Responsibilities
Unit Test NP1, NP2
System Test NP1, NP2
Test Record NP1, NP2
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 449
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter Two | Unit Test
2.1) UTC-01: Register
Unit Test ID: UTC-01
Function: register()
Description: This test case is created to test the register() function. This function
checks the user's first_name, last_name, email, and password.
Prepared Data: first name, last name, email, and password of the user
No. Expected Output Actual Output P/F
{ {
“message”: “User registered “message”: “User registered
successfully”, successfully”,
“user”: { “user”: {
“user_id”: 8, “user_id”: 8,
“first_name”: “first_name”:

## 1. P

“Baby”, “Baby”,
“last_name”: “last_name”:
“Tee”, “Tee”,
“email”: “Babytee@gmail.com” “email”: “Babytee@gmail.com”
} }
} }
{ {
“message”: “User with this email “message”: “User with this email
2. already exists” already exists” P
} }
{ {
3. “message”: “Missing required fields” “message”: “Missing required fields” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 450
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.2) UTC-02: Log in
Unit Test ID: UTC-02
Function: login()
Description: This test case is created to test the login() function. This function
will check the user's email and password.
Prepared Data: email and password of the user
No. Expected Output Actual Output P/F
{ {
“message”: “Login successful", “message”: “Login successful",
“user”: { “user”: {
“email”: “Babytee@gmail.com”, “email”: “Babytee@gmail.com”,
1. “first_name”: “Baby”, “first_name”: “Baby”, P
"last_name": “Tee”, "last_name": “Tee”,
“user_id”: 8 “user_id”: 8
} }
} }
{ {
“message”: “Missing email or “message”: “Missing email or

## 2. P

password” password”
} }
{ {
“message”: “Invalid email or “message”: “Invalid email or

## 3. P

password” password”
} }
{ {
“message”: “Invalid email or “message”: “Invalid email or

## 4. P

password” password”
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 451
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.3) UTC-03: Log out
Unit Test ID: UTC-03
Function: logout()
Description: This test case is created to test the logout() function. This function
will check if the user has logged out.
Prepared Data: The user has log in.
No. Expected Output Actual Output P/F
{ {
1. “message”: "Logged out successfully" “message”: "Logged out successfully" P
} }
The user session is cleared and logged The user session is cleared and logged

## 2. P

out. out.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 452
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.4) UTC-04: View all of the jewelry mockups
Unit Test ID: UTC-04
Function: get_mockups()
Description: This test case is created to test the get_mockups() function, which
retrieves all jewelry mockups. The function ensures that user (Registered and
Unregistered user) receive the correct mockup data for all jewelry mockups.
No. Expected Output Actual Output P/F
{ {
“data”: [ “data”: [
{ {
“mockup_id”: 1, “mockup_id”: 1,
“mockup_name”: “Test Bracelet”, “mockup_name”: “Test Bracelet”,
“mockup_subcategory”: “bracelet”, “mockup_subcategory”: “bracelet”,
“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
}, },
{ {
1. “mockup_id”: 2, “mockup_id”: 2, P
“mockup_name”: “Test Bracelet2”, “mockup_name”: “Test Bracelet2”,
“mockup_subcategory”: “bracelet”, “mockup_subcategory”: “bracelet”,
“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
}, },
… …
] ]
“message”: “Mockups fetched “message”: “Mockups fetched
successfully” successfully”
} }
{ {
“message”: "No mockups found", “message”: "No mockups found",

## 2. P

“data”: [] “data”: []
} }
{ {
3. “error”: "Failed to fetch mockups" “error”: "Failed to fetch mockups" P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 453
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.5) UTC-05: View all of the packaging mockups
Unit Test ID: UTC-05
Function: get_all_package_mockups()
Description: This test case is created to test the get_all_package_mockups()
function, which retrieves all packaging mockups. The function ensures that user
(Registered and Unregistered user) receive the correct mockup data for all
packaging mockups.
No. Expected Output Actual Output P/F
{ {
“data”: [ “data”: [
{ {
“mockup_id”: 6, “mockup_id”: 6,
“mockup_name”: “Test “mockup_name”: “Test
Package”, Package”,
“mockup_subcategory”: “bracelet “mockup_subcategory”: “bracelet
box with pillow”, box with pillow”,
“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
}, },
{ {

## 1. P

“mockup_id”: 7, “mockup_id”: 7,
“mockup_name”: “Test “mockup_name”: “Test
Package2”, Package2”,
“mockup_subcategory”: “bracelet “mockup_subcategory”: “bracelet
box with pillow”, box with pillow”,
“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
} }
] ]
“message”: “Packaging mockups fetched “message”: “Packaging mockups fetched
successfully” successfully”
} }
{ {
“message": "No packaging mockups “message": "No packaging mockups
2. found", found", P
“data”: [] “data”: []
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 454
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3. { {
“error”: "Failed to fetch packaging “error”: "Failed to fetch packaging P
mockups" mockups"
} }
2.6) UTC-06: View the jewelry mockups by category
Unit Test ID: UTC-06
Function: get_mockups_by_subcategory(subcategory)
Description: This test case is created to test the
get_mockups_by_subcategory(subcategory) function, which retrieves all jewelry
mockups that belong to the subcategory (necklace and bracelet). The function
ensures that user (Registered and Unregistered user) receive the correct mockup
data for each category.
No. Expected Output Actual Output P/F
{ {
“mockup_id”: 13, “mockup_id”: 13,
“mockup_name”: “Test Necklace” “mockup_name”: “Test Necklace”
“mockup_subcategory”: “necklace” “mockup_subcategory”: “necklace”

## 1. P

“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
} }
{ {
“mockup_id”: 1, “mockup_id”: 1,
“mockup_name”: “Test Bracelet” “mockup_name”: “Test Bracelet”
“mockup_subcategory”: “bracelet” “mockup_subcategory”: “bracelet”

## 2. P

“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
} }
{ {
“message”: “No mockups found for the “message”: “No mockups found for the

## 3. P

given subcategory” given subcategory”
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 455
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.7) UTC-07: View the packaging mockups by category
Unit Test ID: UTC-07
Function: get_package_mockups_by_subcategory(subcategory)
Description: This test case is created to test the
get_package_mockups_by_subcategory(subcategory) function, which retrieves all
packaging mockups that belong to the subcategory (necklace-box, bracelet-box,
bracelet-box-with-pillow). The function ensures that user (Registered and
Unregistered user) receive the correct mockup data for each category.
No. Expected Output Actual Output P/F
{ {
“mockup_id”: 14, “mockup_id”: 14,
“mockup_name”: “Test Necklace Box” “mockup_name”: “Test Necklace Box”
“mockup_subcategory”: “necklace box” “mockup_subcategory”: “necklace box”

## 1. P

“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
} }
{ {
“mockup_id”: 15, “mockup_id”: 15,
“mockup_name”: “Test Bracelet Box” “mockup_name”: “Test Bracelet Box”
“mockup_subcategory”: “bracelet box” “mockup_subcategory”: “bracelet box”

## 2. P

“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
} }
{ {
“mockup_id”: 6, “mockup_id”: 6,
“mockup_name”: “Test Package” “mockup_name”: “Test Package”
“mockup_subcategory”: “bracelet box “mockup_subcategory”: “bracelet box
3. with pillow” with pillow” P
“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
} }
Same as for necklace-box Same as for necklace-box
{ {
“mockup_id”: 14, “mockup_id”: 14,
4. “mockup_name”: “Test Necklace Box” “mockup_name”: “Test Necklace Box” P
“mockup_subcategory”: “necklace box” “mockup_subcategory”: “necklace box”
“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 456
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

/thumbnails” /thumbnails”
} }
Same as for bracelet-box Same as for bracelet-box
{ {
“mockup_id”: 15, “mockup_id”: 15,
“mockup_name”: “Test Bracelet Box” “mockup_name”: “Test Bracelet Box”

## 5. P

“mockup_subcategory”: “bracelet box” “mockup_subcategory”: “bracelet box”
“mockup_thumbnail_url”: “mockup_thumbnail_url”:
“https://assets.meshy.ai/.../preview.png?...” “https://assets.meshy.ai/.../preview.png?...”
} }
{ {
“message”: “No mockups found for the “message”: “No mockups found for the

## 6. P

given subcategory” given subcategory”
} }
2.8) UTC-08: Choose the jewelry mockup to customize
Unit Test ID: UTC-08
Function: get_mockup_detail(jewelry_mockup_id)
Description: This test case is created to test get_mockup_detail
(jewelry_mockup_id) function. This function will retrieve detailed information of
a jewelry mockup based on the given jewelry_mockup_id and registered user can
choose the jewelry mockup to customize.
No. Expected Output Actual Output P/F
{ {
“jewelry_mockup_id”: 1, “jewelry_mockup_id”: 1,
“mockup_name”: “Test Bracelet”, “mockup_name”: “Test Bracelet”,
“mockup_category”: “jewelry”, “mockup_category”: “jewelry”,
“urls”: { “urls”: {
“glbfile”: “glbfile”:
1. “https://storage.googleapis.com/.../ “https://storage.googleapis.com/.../ P
model.glb?”, model.glb?”,
“thumbnail”: “thumbnail”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
} }
} }
{ {
2. “message”: "Mockup not found" “message”: "Mockup not found" P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 457
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.9) UTC-09: Choose the packaging mockup to customize
Unit Test ID: UTC-09
Function: get_package_mockup_detail(packaging_mockup_id)
Description: This test case is created to test get_mockup_detail
(packaging_mockup_id) function. This function will retrieve detailed information
of a packaging mockup based on the given packaging_mockup_id and registered
user can choose the packaging mockup to customize.
No. Expected Output Actual Output P/F
{ {
“packaging_mockup_id”: 6, “packaging_mockup_id”: 6,
“mockup_name”: “Test Package”, “mockup_name”: “Test Package”,
“packaging_category”: “bracelet box with “packaging_category”: “bracelet box
pillow”, with pillow”,
“urls”: { “urls”: {
“glbfile”: “glbfile”:

## 1. P

“https://storage.googleapis.com/.../ “https://storage.googleapis.com/.../
model.glb?”, model.glb?”,
“thumbnail”: “thumbnail”:
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” /thumbnails”
} }
} }
{ {
2. “message”: "Mockup not found" “message”: "Mockup not found" P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 458
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.10) UTC-10: Upload an image for 3D generation
Unit Test ID: UTC-10
Function: upload_image()
Description: This test case is created to test the upload_image() function. This
function handles image uploads from registered user. It saves the image file to the
database table and returns the image_upload_id with associated details.
Prepared Data: User uploaded image
No. Expected Output Actual Output P/F
{ {
“message”: “Image uploaded”, “message”: “Image uploaded”,
“image_upload_id": 1, “image_upload_id": 1,
“image_url”: “image_url”:
1. “http://localhost:5000/uploads/6f00b03c- “http://localhost:5000/uploads/6f00b03c- P
2bee-43af-a9ae-18ee8fcac5b6.png”, 2bee-43af-a9ae-18ee8fcac5b6.png”,
“generated_time”: 2025-05-16 11:50:13 “generated_time”: 2025-05-16
} 11:50:13
}
The “Generate” button cannot be The “Generate” button cannot be

## 2. P

pressed. pressed.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 459
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.11) UTC-11: Generate 3D model from the uploaded image.
Unit Test ID: UTC-11
Function: generate_3d(image_upload_id)
Description: This test case is created to test the generate_3d(image_upload_id)
function. This function retrieves the uploaded image by ID, converts the image to
base64, and sends it to the Meshy API to generate a 3D model. If successful, the
returned job_id is stored in the database.
No. Expected Output Actual Output P/F
{ {
“message”: “3D generation “message”: “3D generation
started”, started”,

## 1. P

“job_id": “0196b428-33e6-71ff-b484- “job_id": “0196b428-33e6-71ff-b484-
1bb8628beb21”, 1bb8628beb21”,
} }
{ {
2. “message”: “Image not found” “message”: “Image not found” P
} }
{ {
“message”: “Meshy API failed”, “message”: “Meshy API failed”,
3. “status_code”: 500, “status_code”: 500, P
“raw”: “<html>...</html>” “raw”: “<html>...</html>”
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 460
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.12) UTC-12: Save GLB File from Meshy API
Unit Test ID: UTC-12
Function: get_3d_model(job_id)
Description: This test case is created to test the get_3d_model(job_id) function.
This function calls the Meshy API using a given job_id to fetch the generated 3D
model. If successful, the glb_url and thumbnail_url are uploaded to the Firebase
and saved in the image_upload_glbfile table.
No. Expected Output Actual Output P/F
{ {
“message”: “message”:
“GLB and thumbnail file uploaded to “GLB and thumbnail file uploaded to
Firebase and saved successfully”, Firebase and saved successfully”,
“glb_url": “glb_url":
“https://storage.googleapis.com/.../ “https://storage.googleapis.com/.../

## 1. P

model.glb?”, model.glb?”,
“thumbnail_url": “thumbnail_url":
“https://storage.googleapis.com/... “https://storage.googleapis.com/...
/thumbnails” , /thumbnails” ,
“progress”: 100 “progress”: 100
} }
{ {
“message”: “3D model is still processing “message”: “3D model is still
or failed.”, processing or failed.”,
“progress”: 45, “progress”: 45,
“raw”: { “raw”: {
“art_style”: “”, “art_style”: “”,
“created_at”: 1749198100066, “created_at”: 1749198100066,
“expires_at”: 0, “expires_at”: 0,
“finished_at”: 0, “finished_at”: 0,
“id”: “0196b428-33e6-71ff-b484- “id”: “0196b428-33e6-71ff-b484-
1bb8628beb21”, 1bb8628beb21”,
2. “model_url”: “”, “model_url”: “”, P
“model_urls”: { “model_urls”: {
“glb”: “” “glb”: “”
}, },
“name”: “”, “name”: “”,
“negative_prompt”: “”, “negative_prompt”: “”,
“object_prompt”: “”, “object_prompt”: “”,
“progress”: 45, “progress”: 45,
“started_at”: 1749198100197, “started_at”: 1749198100197,
“status”: “IN_PROGRESS”, “status”: “IN_PROGRESS”,
“style_prompt”: “’, “style_prompt”: “’,
“task_error”: null, “task_error”: null,
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 461
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

“texture_image_url”: “”, “texture_image_url”: “”,
“texture_prompt”: “”, “texture_prompt”: “”,
“texture_urls”: null, “texture_urls”: null,
“thumbnail_url”: “” “thumbnail_url”: “”
}, },
“status”: “IN_PROGRESS” “status”: “IN_PROGRESS”
} }
{ {
“message”: “Image upload record not “message”: “Image upload record not

## 3. P

found” found”
} }
2.13) UTC-13: Retrieve GLB URL from Database
Unit Test ID: UTC-13
Function: get_glb_url(job_id)
Description: This test case is created to test the get_glb_url(job_id) function.
This function looks up the generated_glbfile_url in the database using the
provided job_id, to show the 3D models from image uploaded by registered user.
No. Expected Output Actual Output P/F
{ {
“job_id”: “job_id”:
“0196b428-33e6-71ff-b484- “0196b428-33e6-71ff-b484-
1bb8628beb21”, 1bb8628beb21”,

## 1. P

“glb_url": “glb_url":
“https://storage.googleapis.com/.../model.gl“https://storage.googleapis.com/.../model
b?” .glb?”
} }
{ {
2. “message”: “job_id not found” “message”: “job_id not found” P
} }
{ {
3. “message”: “GLB file not found” “message”: “GLB file not found” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 462
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.14) UTC-14: Create the name of the design
Unit Test ID: UTC-14
Function: upload_image()
Description: This test case is created to test the behavior of assigning and saving
model_name during the image upload process. It verifies whether the name is
properly stored in the database and returned in the response.
Prepared Data: User’s model name
No. Expected Output Actual Output P/F
{ {
“message”: “Model name saved”, “message”: “Model name saved”,

## 1. P

“model_name”: “Test Model” “model_name”: “Test Model”
} }
{ {
“message”: “Model name saved”, “message”: “Model name saved”,
P
2. “model_name”: “New Model” “model_name”: “New Model”
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 463
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.15) UTC-15: Customize the color of specific jewelry sections (Use the predefined
jewelry mockup)
Unit Test ID: UTC-15
Function: customize_jewelry_cropmode(jewelry_mockup_id,
jewelry_custom_color)
Description: This test case is created to test the
customize_jewelry_cropmode(jewelry_mockup_id, jewelry_custom_color)
function. This function will retrieve the jewelry_mockup_id from the jewelry item
that the registered user wants to customize and apply the chosen
jewelry_custom_color, then save the customization details into the database table.
If a customization already exists, it will update the record; otherwise, it will create
a new one.
No. Expected Output Actual Output P/F
{ {
“message”: “Customization saved “message”: “Customization saved
successfully”, successfully”,
“user_id”: 11, “user_id”: 11,
“jewelry_mockup_id”: 28, “jewelry_mockup_id”: 28,
"custom_id": 334, "custom_id": 334,

## 1. P

“jewelry_customs”: { “jewelry_customs”: {
“custom_glb_url”: “custom- “custom_glb_url”: “custom-
models/2_14.glb”, models/2_14.glb”,
“jewelry_custom_color”: “#dfbd69” “jewelry_custom_color”: “#dfbd69”
} }
} }
{ {
“message”: “Customization saved “message”: “Customization saved
successfully”, successfully”,
“user_id”: 11, “user_id”: 11,
“jewelry_mockup_id”: 28, “jewelry_mockup_id”: 28,
"custom_id": 334, "custom_id": 334,
“jewelry_customs”: { “jewelry_customs”: {
“custom_glb_url”: “custom- “custom_glb_url”: “custom-
models/2_14.glb”, models/2_14.glb”,
2. “jewelry_custom_ color”: “#dfbd69” “jewelry_custom_ color”: P
} “#dfbd69”
} }
}
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 464
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.16) UTC-16: Customize the jewelry of specific jewelry sections (Use the converted
model)
Unit Test ID: UTC-16
Function: customize_imageupload_cropmode(image_upload_id,
image_upload_custom_color)
Description: This test case is created to test the function customize_imageupload
_cropmode(image_upload_id, image_upload_custom_color). This function will
retrieve the image_upload_id from the converted item that the registered user
wants to customize and apply the chosen image_upload_custom_color, then save
the customization details into the database table. If a customization already exists,
it will update the record; otherwise, it will create a new one.
No. Expected Output Actual Output P/F
{ {
“message”: “Imageupload customization “message”: “Imageupload
saved successfully”, customization saved successfully”,
“user_id”: 11, “user_id”: 11,
“image_upload_id”: 77, “image_upload_id”: 77,
"custom_id": 1, "custom_id": 1,
1. “image_upload_customs”: { “image_upload_customs”: { P
“custom_glb_url”: “custom- “custom_glb_url”: “custom-
models/2_17.glb”, models/2_17.glb”,
“image_upload_custom_ color”: “#9ea3a7” “image_upload_custom_ color”:
} “#9ea3a7”
} }
}
{ {
“message”: “Imageupload customization “message”: “Imageupload
saved successfully”, customization saved successfully”,
“user_id”: 11, “user_id”: 11,
“image_upload_id”: 77, “image_upload_id”: 77,
"custom_id": 1, "custom_id": 1,
“image_upload_customs”: { “image_upload_customs”: {
“custom_glb_url”: “custom- “custom_glb_url”: “custom-
models/2_17.glb”, models/2_17.glb”,
P
2. “image_upload_custom_ color”: “#9ea3a7” “image_upload_custom_ color”:
} “#9ea3a7”
} }
}
{ {
“message”: “user_id and image_upload_id “message”: “user_id and

## 3. P

are required” image_upload_id are required”
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 465
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

{ {
“message”: “user_id and image_upload_id “message”: “user_id and

## 4. P

are required” image_upload_id are required”
} }
2.17) UTC-17: Customize the material of specific jewelry sections (Use the
predefined jewelry mockup)
Unit Test ID: UTC-17
Function: customize_jewelry_cropmode(jewelry_mockup_id,
jewelry_custom_material)
Description: This test case is created to test the function
customize_jewelry_cropmode(jewelry_mockup_id, jewelry_custom_material).
This function will retrieve the jewelry_mockup_id from the jewelry item that the
registered user wants to customize and apply the chosen
jewelry_custom_material, then save the customization details into the database
table. If a customization already exists, it will update the record; otherwise, it will
create a new one.
No. Expected Output Actual Output P/F
{ {
“message”: “Customization saved “message”: “Customization saved
successfully”, successfully”,
“user_id”: 2, “user_id”: 2,
“jewelry_mockup_id”: 14, “jewelry_mockup_id”: 14,
"custom_id": 334, "custom_id": 334,
1. “jewelry_customs”: { “jewelry_customs”: { P
“custom_glb_url”: “custom- “custom_glb_url”: “custom-
models/2_14.glb”, models/2_14.glb”,
“jewelry_custom_material”: “#c0c0c0” “jewelry_custom_material”:
} “#c0c0c0”
} }
}
{ {
“message”: “Customization saved “message”: “Customization saved
successfully”, successfully”,
“user_id”: 2, “user_id”: 2,
“jewelry_mockup_id”: 14, “jewelry_mockup_id”: 14,

## 2. P

"custom_id": 334, "custom_id": 334,
“jewelry_customs”: { “jewelry_customs”: {
“custom_glb_url”: “custom- “custom_glb_url”: “custom-
models/2_14.glb”, models/2_14.glb”,
“jewelry_custom_material”: “#9ea3a7”
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 466
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

} “jewelry_custom_material”:
} “#9ea3a7”
}
}
{ {
3. “message”: “user_id and “message”: “user_id and P
jewelry_mockup_id are required” jewelry_mockup_id are required”
} }
{ {
“message”: “user_id and “message”: “user_id and

## 4. P

jewelry_mockup_id are required” jewelry_mockup_id are required”
} }
2.18) UTC-18: Customize the material of specific jewelry sections (Use the converted
model)
Unit Test ID: UTC-18
Function: customize_imageupload _cropmode(image_upload_id,
image_upload_custom_material)
Description: This test case is created to test the function customize_imageupload
_cropmode(image_upload_id, image_upload_custom_material).
This function will retrieve the image_upload_id from the converted item that the
registered user wants to customize and apply the chosen
image_upload_custom_material, then save the customization details into the
database table. If a customization already exists, it will update the record;
otherwise, it will create a new one.
No. Expected Output Actual Output P/F
{ {
“message”: “Imageupload customization “message”: “Imageupload
saved successfully”, customization saved successfully”,
“user_id”: 2, “user_id”: 2,
“image_upload_id”: 120, “image_upload_id”: 120,
"custom_id": 1, "custom_id": 1,
1. “image_upload_customs”: { “image_upload_customs”: { P
“custom_glb_url”: “custom- “custom_glb_url”: “custom-
models/2_14.glb”, models/2_14.glb”,
“image_upload_custom_material”: “image_upload_custom_material”:
“#c0c0c0” “#c0c0c0”
} }
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 467
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

{ {
“message”: “Imageupload customization “message”: “Imageupload
saved successfully”, customization saved successfully”,
“user_id”: 2, “user_id”: 2,
“image_upload_id”: 120, “image_upload_id”: 120,
"custom_id": 1, "custom_id": 1,
2. “image_upload_customs”: { “image_upload_customs”: { P
“custom_glb_url”: “custom- “custom_glb_url”: “custom-
models/2_14.glb”, models/2_14.glb”,
“image_upload_custom_material”: “image_upload_custom_material”:
“#9ea3a7” “#9ea3a7”
} }
} }
{ {
“message”: “user_id and image_upload_id “message”: “user_id and

## 3. P

are required” image_upload_id are required”
} }
{ {
“message”: “user_id and image_upload_id “message”: “user_id and

## 4. P

are required” image_upload_id are required”
} }
2.19) UTC-19: Retrieve the previous customization of a jewelry
Unit Test ID: UTC-19
Function: get_last_customization(user_id, item_type, item_id)
Description: This test case is created to test the function
get_last_customization(user_id, item_type, item_id). This function retrieves the
most recent customization jewelry model from the database. If the item type is
'mockup', it queries the 'user_jewelry_custom' table; if the type is 'image_upload',
it queries the 'user_image_upload_custom' table. The function returns the last
saved customization data to the frontend.
Prepared Data:
4. Type of the item that should be “mockup” or “image_upload”
5. item_id should be jewelry_mockup_id if the item_type is mockup.
6. item_id should be image_upload_id if the item_type is image_upload.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 468
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

No. Expected Output Actual Output P/F
{ {
“user_id”: 13 “user_id”: 13
“jewelry_custom_id”: 335, “jewelry_custom_id”: 335,
“customs”: [ “customs”: [
{ {
“jewelry_mockup_id”: 21, “jewelry_mockup_id”: 21,
“jewelry_created_time”: “Thu, 21 “jewelry_created_time”: “Thu,
Aug 2025 14:42:57 GMT”, 21 Aug 2025 14:42:57 GMT”,
“jewelry_custom_color”: “#fcfcfc”, “jewelry_custom_color”:
“jewelry_custom_glbfile_url”: “#fcfcfc”,

## 1. P

“custom-models/13_21.glb”, “jewelry_custom_glbfile_url”:
“jewelry_custom_material”: “custom-models/13_21.glb”,
“#c0c0c0”, “jewelry_custom_material”:
“jewelry_custom_name”: “New “#c0c0c0”,
Granite Necklace Design”, “jewelry_custom_name”: “New
“jewelry_custom_size”: “31.00” Granite Necklace Design”,
} “jewelry_custom_size”: “31.00”
], }
} ],
}
{ {
“user_id”: 13 “user_id”: 13
“image_upload_custom_id”: 36, “image_upload_custom_id”: 36,
“customs”: [ “customs”: [
{ {
“image_upload_id”: 78, “image_upload_id”: 78,
“image_upload_created_time”: “image_upload_created_time”:
“Mon, 18 Aug 2025 02:43:41 GMT”, “Mon, 18 Aug 2025 02:43:41 GMT”,
“image_upload_custom_color”: “image_upload_custom_color”:
“#fcfcfc”, “#fcfcfc”,
“image_upload_custom_glbfile_url”: “image_upload_custom_glbfile_url”:

## 2. P

“uploads/custom_models/13_78_ “uploads/custom_models/13_78_
1755485021.glb”, 1755485021.glb”,
“image_upload_custom_material”: “image_upload_custom_material”:
“c0c0c0”, “c0c0c0”,
“image_upload_custom_name”: “image_upload_custom_name”:
“Custom Upload”, “Custom Upload”,
“image_upload_custom_size”: “3” “image_upload_custom_size”:
} “3”
], }
} ],
}
{ {
“message”: “No customization found” “message”: “No customization
3. } found” P
}
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 469
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

{ {
4. “message”: “Invalid item_type” “message”: “Invalid item_type” P
} }
2.20) UTC-20: Choose the jewelry to try-on with packaging
Unit Test ID: UTC-20
Function: get_workspace_items_packagecustom(user_id)
Description: This test case is created to test the
get_workspace_items_packagecustom(user_id) function. This function retrieves
the workspace and the items inside the workspace by user_id. It returns the list of
jewelry items that the registered user has saved in the workspace, so the registered
user can choose jewelry to try-on with packaging.
No. Expected Output Actual Output P/F
{ {
“user_id”: 11, “user_id”: 11,
“workspace_id”: 7, “workspace_id”: 7,
“workspace_item”: [ “workspace_item”: [
{ {
“generated_glbfile_url”: “generated_glbfile_url”:
“uploads/custom_models/ “uploads/custom_models/
11_37_1754723618.glb”, 11_37_1754723618.glb”,
“item_id”: 303, “item_id”: 303,
“model_name”: “Italian Charm “model_name”: “Italian Charm
Bracelet”, Bracelet”,
1. “type”: “mockup_custom” “type”: “mockup_custom” P
}, },
{ {
“generated_glbfile_url”: “custom- “generated_glbfile_url”:
models/11_21.glb”, “custom-models/11_21.glb”,
“item_id”: 304, “item_id”: 304,
“model_name”: “Amethyst “model_name”: “Amethyst
Necklace”, Necklace”,
“type”: “mockup_custom” “type”: “mockup_custom”
} }
] ]
} }
{ {
“user_id”: 14, “user_id”: 14,
2. “workspace_id”: 11, “workspace_id”: 11, P
“workspace_item”: [] “workspace_item”: []
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 470
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

{ {
3. “message”: “Workspace not found” “message”: “Workspace not found” P
} }
2.21) UTC-21: Select the type of selected body to try on
Unit Test ID: UTC-21
Function: get_simulated_body(model_type)
Description: This test case is created to test the function
get_simulated_body(model_type). This function verifies that the system can
correctly retrieve and return the simulated body model (GLB file) based on the
model_type requested by the registered user.
No. Expected Output Actual Output P/F
{ {
"asset": "asset":
{"generator":"Khronos glTF {"generator":"Khronos glTF
Blender I/O v4.4.55","version":"2.0"}, Blender I/Ov4.4.55","version":"2.0"},
"scene":0,"scenes": "scene":0,"scenes":

## 1. [{ [{ P

"name":"Scene","nodes":[5]}], "name":"Scene","nodes":[5]}],
"nodes":[{"name":"NeckBack" "nodes":[{"name":"NeckBack"
, … , …
] ]
} }
{ {
"asset": "asset":
{"generator":"Khronos glTF {"generator":"Khronos glTF
Blender I/Ov4.4.55","version":"2.0"}, Blender I/Ov4.4.55","version":"2.0"},
"scene":0,"scenes": "scene":0,"scenes":
[{ [{
2. "name":"Scene","nodes":[1,2]}], "name":"Scene","nodes":[1,2]}], P
"nodes":[{"mesh":0,"name": "nodes":[{"mesh":0,"name":
"tripo_node_9b51b900-ce9d-40b3-8824- "tripo_node_9b51b900-ce9d-40b3-
26fadce13dff.001” 8824-26fadce13dff.001”
,... ,...
] ]
} }
{ {
“message”: “No model type in database” “message”: “No model type in

## 3. P

} database”
}
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 471
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.22) UTC-22: View all previously designed works
Unit Test ID: UTC-22
Function: get_workspace_items(user_id)
Description: This test case is created to test the get_workspace_items(user_id)
function. This function retrieves all mockups that are saved in the workspace
associated with the given user_id.
No. Expected Output Actual Output P/F
{ {
"user_id": 16, "user_id": 16,
"workspace_id": 13, "workspace_id": 13,
"workspace_item": [ "workspace_item": [
{ {
"generated_glbfile_url": "generated_glbfile_url":
"uploads/custom_models/16_30_1759564569.glb", "uploads/custom_models/16_30_1759564569.glb",
"generated_time": "Sat, 04 Oct 2025 07:56:09 "generated_time": "Sat, 04 Oct 2025 07:56:09

## GMT", GMT",

"item_id": 375, "item_id": 375,
"model_name": "Jewel Bracelet", "model_name": "Jewel Bracelet",
"type": "mockup_custom" "type": "mockup_custom"
}, },
{ {
"generated_glbfile_url": "generated_glbfile_url":
"uploads/custom_models/16_129_1759564821.glb", "uploads/custom_models/16_129_1759564821.glb",
1. "generated_time": "Sat, 04 Oct 2025 08:00:21 "generated_time": "Sat, 04 Oct 2025 08:00:21 P

## GMT", GMT",

"item_id": 61, "item_id": 61,
"model_name": "Character new bracelet", "model_name": "Character new bracelet",
"type": "image_upload_custom" "type": "image_upload_custom"
}, },
{ {
"generated_glbfile_url": "generated_glbfile_url":
"uploads/custom_packages/16_53_1759564939.glb", "uploads/custom_packages/16_53_1759564939.glb",
"generated_time": "Sat, 04 Oct 2025 08:02:19 "generated_time": "Sat, 04 Oct 2025 08:02:19

## GMT", GMT",

"item_id": 91, "item_id": 91,
"model_name": "Lid seperator Bracelet Box", "model_name": "Lid seperator Bracelet Box",
"type": "package_custom" "type": "package_custom"
} }
] ]
} }
{ {
“user_id”: 2, “user_id”: 2,
2. “workspace_id”: 4, “workspace_id”: 4, P
“workspace_item”: [] “workspace_item”: []
} }
{ {
3. “message”: “Workspace not found” “message”: “Workspace not found” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 472
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.23) UTC-23: Save the designed work from the predefined jewelry mockup that has
not been customized.
Unit Test ID: UTC-23
Function: add_mockup_to_workspace()
Description: This test case is created to test add_mockup_to_workspace()
function. This function verifies that the jewelry mockup that has not been
customized from the predefined jewelry mockups can be added to a user’s
workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the item that want to add.
3. Type of the item that should be “mockup”
No. Expected Output Actual Output P/F
{ {
“message”: “Added to workspace “message”: “Added to workspace
1. successfully” successfully” P
“workspace_id”: 4 “workspace_id”: 4
} }
{ {
“message”: “Only ‘mockup’ type is “message”: “Only ‘mockup’ type is

## 2. P

allowed” allowed”
} }
{ {
3. “message”: “User not found” “message”: “User not found” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 473
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.24) UTC-24: Save the designed work from the predefined jewelry mockup that has
been customized.
Unit Test ID: UTC-24
Function: customize_jewelry()
Description: This test case is created to test customize_jewelry() function.
This function verifies that the mockup that has been customized from the
predefined jewelry mockups can be added to a user’s workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the jewelry mockup that want to add.
3. ID of the workspace that want to add an item to.
4. GLB file of the jewelry that want to customize
5. New material of the jewelry in hex code
6. New color of the jewelry in hex code
7. New size of the jewelry in mm.
No. Expected Output Actual Output P/F
{ {
“message”: "Customization and workspace item saved “message”: "Customization and workspace item
successfully." saved successfully."
1. “glb_path”: “glb_path”: P
"uploads/custom_models/2_14_1759569260.glb", "uploads/custom_models/2_14_1759569260.glb",
“jewelry_custom_id”: 380, “jewelry_custom_id”: 380,
} }
{ {
2. “message”: “Missing required fields.” “message”: “Missing required fields.” P
} }
{ {
3. “message”: “Missing required fields.” “message”: “Missing required fields.” P
} }
{ {
4. “message”: “Missing required fields.” “message”: “Missing required fields.” P
} }
{ {
5. “message”: “Workspace not found.” “message”: “Workspace not found.” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 474
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.25) UTC-25: Save the designed work from the converted image to 3d model that
has not been customized.
Unit Test ID: UTC-25
Function: add_imageupload_to_workspace()
Description: This test case is created to test add_imageupload_to_workspace()
function. This function verifies that the converted image to 3d model that has not
been customized can be added to a user’s workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the item that want to add.
3. Type of the item that should be “image_upload”
No. Expected Output Actual Output P/F
{ {
“message”: “Added to workspace “message”: “Added to workspace
1. successfully” successfully” P
“workspace_id”: 4 “workspace_id”: 4
} }
{ {
“message”: “Only ‘image_upload’ type is “message”: “Only ‘image_upload’

## 2. P

allowed” type is allowed”
} }
{ {
3. “message”: “User not found” “message”: “User not found” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 475
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.26) UTC-26: Save the designed work from the converted image to 3d model that
has been customized.
Unit Test ID: UTC-26
Function: customize_imageupload_workspace()
Description: This test case is created to test
customize_imageupload_workspace()function. This function verifies that the
converted image to 3d model that has been customized can be added to a user’s
workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the uploaded image that want to add.
3. ID of the workspace that want to add an item to.
4. GLB file of the uploaded image that want to customize
5. New material in hex code
6. New color in hex code
7. New size in mm.
No. Expected Output Actual Output P/F
{ {
“message”: “Imageupload customization and workspace “message”: “Imageupload customization and
item saved successfully.” workspace item saved successfully.”
1. “glb_path”: “glb_path”: P
“uploads/custom_models/2_120_1759569562.glb”, “uploads/custom_models/2_120_1759569562.glb”,
“image_upload_custom_id”: 62, “image_upload_custom_id”: 62,
} }
{ {
2. “message”: “Missing required fields.” “message”: “Missing required fields.” P
} }
{ {
“message”: “Missing required fields.” “message”: “Missing required fields.”

## 3. P

} }
{ {
4. “message”: “Missing required fields.” “message”: “Missing required fields.” P
} }
{ {
5. “message”: “Workspace not found.” “message”: “Workspace not found.” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 476
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.27) UTC-27: Save the designed work from the predefined packaging mockup that
has not been customized.
Unit Test ID: UTC-27
Function: add_mockup_to_workspace()
Description: This test case is created to test add_mockup_to_workspace()
function. This function verifies that the packaging mockup that has not been
customized from the predefined packaging mockups can be added to a user’s
workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the item that want to add.
3. Type of the item that should be “mockup”
No. Expected Output Actual Output P/F
{ {
“message”: “Added to workspace “message”: “Added to workspace
1. successfully” successfully” P
“workspace_id”: 4 “workspace_id”: 4
} }
{ {
“message”: “Only ‘mockup’ type is “message”: “Only ‘mockup’ type is

## 2. P

allowed” allowed”
} }
{ {
3. “message”: “User not found” “message”: “User not found” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 477
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.28) UTC-28: Save the designed work from the predefined packaging mockup that
has been customized.
Unit Test ID: UTC-28
Function: customize_package()
Description: This test case is created to test customize_package() function.
This function verifies that the packaging mockup that has been customized from
the predefined packaging mockups can be added to a user’s workspace correctly.
Prepared Data:
1. User’s ID
2. ID of the packaging mockup that want to add.
3. ID of the workspace that want to add an item to.
4. ID of the jewelry that want to try on with the packaging.
5. GLB file of the packaging that want to customize
6. New color of the packaging in hex code
7. Text that want to engrave on the packaging
8. Text font that want to engrave on the packaging
9. Text font size that want to engrave on the packaging
10. Text font color that want to engrave on the packaging
No. Expected Output Actual Output P/F
{ {
“message”: "Package+Jewelry saved and added to “message”: "Package+Jewelry saved and added to
workspace", workspace",
1. “glb_path”: “glb_path”: P
"uploads/custom_packages/2_40_1759571373.glb", "uploads/custom_packages/2_40_1759571373.glb",
"package_custom_id": 92 "package_custom_id": 92
} }
{ {
2. “message”: “Missing required fields.” “message”: “Missing required fields.” P
} }
{ {
3. “message”: “Missing required fields.” “message”: “Missing required fields.” P
} }
{ {
4. “message”: “Missing required fields.” “message”: “Missing required fields.” P
} }
{ {
5. “message”: “Workspace not found.” “message”: “Workspace not found.” P
} }
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 478
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter Three | System Test
3.1) STC-01: Register
Test ID: STC-01
Test No: UC-01
Test case name: Register
Description: Unregistered user can register to the web application.
Test Setup:
2. The unregistered user is not already registered
Test Script:
7. Click on the “Get Started” button on the navigation bar
8. Input first name
9. Input last name
10. Input email
11. Input password
12. Click on the “Sign Up” button
Prepared data: first name, last name, email, and password
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides the The web application provides the

## 1 P

register page with an input field. register page with an input field.
1.
The system displays a message The system displays a message
6 "Registration successful" and redirects "Registration successful" and P
to the login page. redirects to the login page.
The web application provides the The web application provides the

## 1 P

r egister page. register page.
2.
The system displays a message “Email The system displays a message

## 6 P

is already exists”. “Email is already exists”.
The web application provides the The web application provides the

## 3. 1 P

register page with an input field. register page with an input field.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 479
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The system displays a message
The system displays a message “First
6 “First name is required” under the P
name is required” under the input field.
input field.
The web application provides the The web application provides the

## 1 P

register page with an input field. register page with an input field.
4.
The system displays a message
The system displays a message “Last
6 “Last name is required” under the P
name is required” under the input field.
input field.
The web application provides the The web application provides the

## 1 P

register page with an input field. register page with an input field.
5.
The system displays a message The system displays a message
6 “Email is required” under the input “Email is required” under the P
field. input field.
The web application provides the The web application provides the

## 1 P

register page with an input field. register page with an input field.
6.
The system displays a message The system displays a message
6 “Password is required” under the input “Password is required” under the P
field. input field.
The web application provides the The web application provides the

## 1 P

register page with an input field. register page with an input field.
The system displays a cross mark in The system displays a cross mark
7.
front of conditions that are not yet in front of conditions that are not
6 correct and displays a message yet correct and displays a message P
“Password does not match all “Password does not match all
conditions” under the input field. conditions” under the input field.
The web application provides the The web application provides the

## 1 P

register page with an input field. register page with an input field.
The system displays a cross mark in The system displays a cross mark
front of conditions that are not yet in front of conditions that are not
correct, displays a correct mark in front yet correct, displays a correct
of conditions that are correct displays a mark in front of conditions that
8. message “Password does not match all are correct displays a message
conditions” under the input field. “Password does not match all

## 6 P

conditions” under the input field.
The web application provides the The web application provides the

## 9. P

1 register page with an input field. register page with an input field.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 480
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The system displays a correct
The system displays a correct mark in
mark in front of conditions that
front of conditions that are correct and
6 are correct and displays a P
displays a message “Registration
message “Registration
Successful” .
Successful” .
3.2) STC-02: Log in
Test ID: STC-02
Test No: UC-02
Test case name: Log in
Description: Registered user can log in to access the features in web application.
Test Script:
5. Click on the “Log in” button on the navigation bar
6. Input email
7. Input password
8. Click on the “Log in” button
Prepared data: email and password
Correct data:
Email: babytee@gmail.com
Password: Babytee1234
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the
1 the login page with an input P
login page with an input field.
field.
1.
The system will redirect to the home
The system will redirect to the
4 page. P
home page.
The web application provides the login The web application provides the

## 2. 1 P

page with an input field login page with an input field
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 481
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The system displays a message
The system displays a message
4 “Invalid email or password”. P
“Invalid email or password”.
The web application provides the login The web application provides the

## 1 P

page with an input field. login page with an input field.
3.
The system displays a message
The system displays a message
4 “Invalid email or password”. P
“Invalid email or password”.
The web application provides the login The web application provides the

## 1 P

page with an input field. login page with an input field.
4.
The system displays a message “Email
The system displays a message
4 is required”. P
“Email is required”.
The web application provides the login The web application provides the

## 1 P

page with an input field. login page with an input field.
5.
4 The system displays a message The system displays a message
P
“Password is required”. “Password is required”.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 482
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.3) STC-03: Log out
Test ID: STC-03
Test No: UC-03
Test case name: Log out
Description: Registered user can log out from the system.
Test Setup:
3. Already log in into the system
4. Registered user is on workspace page
Test Script:
3. Click on the “Workspace” button on the navigation bar
4. Click on the “Log out” button in the workspace page
Test Script
No. Expected Output Actual Output P/F
No.
The web application redirects to the The web application redirects to

## 1. 1 P

home page. the home page.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 483
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.4) STC-04: View all of the jewelry mockups
Test ID: STC-04
Test No: UC-04
Test case name: View all of the jewelry mockups
Description: User (unregistered and registered user) can view all available
jewelry mockups provided by the web application.
Test Setup:
2. User is on the home page.
Test Script:
3. Click on the “Jewelry” button on the home page.
4. User is on the “All Jewelry Mockups” page.
Test Script
No. Expected Output Actual Output P/F
No.
The web application displays all
The web application displays all of the
1. 1 of the jewelry mockups from the P
jewelry mockups from the database.
database.
The system displays message “No The system displays message
Mockups found in All Jewelry “No Mockups found in All
P
2. 1 Mockups” on all jewelry mockups Jewelry Mockups” on all jewelry
page. mockups page.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 484
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.5) STC-05: View all of the packaging mockups
Test ID: STC-05
Test No: UC-05
Test case name: View all of the packaging mockups
Description: User (unregistered and registered user) can view all available
packaging mockups provided by the web application.
Test Setup:
2. User is on the home page.
Test Script:
3. Click on the “Packaging” button on the home page.
4. User is on the “All Packaging Mockups” page.
Test Script
No. Expected Output Actual Output P/F
No.
The web application displays all
The web application displays all of the
1. 1 of the packaging mockups from P
packaging mockups from the database.
the database.
The system displays message “No The system displays message
Mockups found in All Packaging “No Mockups found in All

## 2. 1 P

Mockups” on all packaging mockups Packaging Mockups” on all
page. packaging mockups page.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 485
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.6) STC-06: View the jewelry mockups by category
Test ID: STC-06
Test No: UC-06
Test case name: View the jewelry mockups by category
Description: User (unregistered and registered user) can view the jewelry
mockups in the category “Necklace” and “Bracelet”.
Test Setup:
1. User is on the “All Mockups” page.
Test Script:
1. Choose the category in the “sidebar”.
Test Script
No. Expected Output Actual Output P/F
No.
The web application will display all The web application will
1. 1 available jewelry mockups from the display all available jewelry P
database. mockups from the database.
The web application display
The web application display only all
2. 1 only all available mockups in P
available mockups in category necklace.
category necklace.
The web application will
The web application will display only all
3. 1 display only all available P
available mockups in category bracelet.
mockups in category bracelet.
The system shows message
The system shows message “No mockups
4. 1 “No mockups found for ‘All P
found for ‘All Mockups’”
Mockups’”
The system shows message
The system shows message “No mockups
5. 1 “No mockups found for P
found for ‘Necklace’”
‘Necklace’ ”
The system shows message
The system shows message “No mockups
6. 1 “No mockups found for P
found for ‘Bracelet’”
‘Bracelet’ ”
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 486
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.7) STC-07: View the packaging mockups by category
Test ID: STC-07
Test No: UC-07
Test case name: View the packaging mockups by category
Description: User (unregistered and registered user) can view the packaging
mockups in the category “Necklace Boxes”, “Bracelet Boxes”, and “Bracelet
Boxes with Pillow”.
Test Setup:
1. User is on the “All Packages” page.
Test Script:
1. Choose the category in the “sidebar”.
Test Script
No. Expected Output Actual Output P/F
No.
The web application will
The web application will display all
display all available
1. available packaging mockups from the P
1 packaging mockups from the
database.
database.
The web application will
The web application will display only
2. 1 display only mockups in P
mockups in category necklace box.
category necklace box.
The web application will
The web application will display only display only mockups in
3. 1 mockups in category category P
bracelet box. bracelet box.
The web application will
The web application will display only display only mockups in
4. 1 mockups in category category P
bracelet box with pillow. bracelet box with pillow.
The system shows message
The system shows message “No mockups
5. 1 “No mockups found from the P
found from the database.
database.
The system shows message “No mockups The system shows message
6. 1 found for “No mockups found for P
‘Necklace Boxes’” ‘Necklace Boxes’”
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 487
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The system shows message “No mockups The system shows message
7. 1 found for “No mockups found for P
‘Bracelet Boxes’” ‘Bracelet Boxes’”
3.8) STC-08: Use the predefined jewelry mockup to customize
Test ID: STC-08
Test No: UC-08
Test case name: Choose the jewelry mockup to customize
Description: Registered user can choose the jewelry mockup to customize, then
the system redirects to the customization jewelry page and correctly displays the
3D model and mockup information.
Test Setup:
3. Already logged into the system.
4. At least one jewelry mockup exists in the system.
Test Script:
3. Registered user is on the “All Mockups” page or the mockups page
with the category.
4. Click the “Custom” button.
Test Script
No. Expected Output Actual Output P/F
No.
The web application will
The web application will display the list of
display the list of jewelry
1. jewelry mockups with the “Custom” P
1 mockups with the “Custom”
buttons and the mockup name.
buttons and the mockup name.
The web application redirects to The web application redirects
2 customization jewelry page and shows to customization jewelry page

## 2. P

correct 3D model, name, and the default and shows correct 3D model,
values. n ame, and the default values.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 488
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.9) STC-09: Use the predefined packaging mockup to customize
Test ID: STC-09
Test No: UC-09
Test case name: Choose the packaging mockup to customize
Description: Registered user can choose the packaging mockup to customize,
then the system redirects to the customization packaging page and correctly
displays the 3D model and mockup information.
Test Setup:
3. Already logged into the system.
4. At least one packaging mockup exists in the system.
Test Script:
3. Registered user is on the “All Packages” page or the mockups page
with the category.
4. Click the “Custom” button.
Test Script
No. Expected Output Actual Output P/F
No.
The web application will
The web application will display the list of
display the list of packaging
1. packaging mockups with the “Custom” P
1 mockups with the “Custom”
buttons and the mockup name.
buttons and the mockup name.
The web application redirects
The web application redirects to
to customization packaging
customization packaging page and shows
2. 2 page and shows correct 3D P
correct 3D model, name, and the default
model, name, and the default
values.
values.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 489
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.10) STC-10: Upload an Image to convert to 3D
Test ID: STC-10
Test No: UC-10
Test case name: Upload an Image to convert to 3D
Description: Registered user can upload an image (JPG, JPEG or PNG) by
clicking, dragging-and-dropping the image into the upload area to convert the
image into a 3D model.
Test Setup:
3. Already logged into the system.
4. Already have the image in the format JPG, JPEG, or PNG to convert
Test Script:
7. Click on the “Image To 3D” button on the home page.
8. Upload the image by clicking or dragging-and-dropping.
9. View the preview image in the upload area.
10. Click on the “Generate” button.
11. View the loading state.
12. View the 3D model generation from the uploaded image.
Prepared data:
2. Valid image file format.
Test Script
No. Expected Output Actual Output P/F
No.
The web application will
The web application will display “Image
1. 1 display “Image To 3D” button P
To 3D” button on the home page.
on the home page.
The web application will
The web application will display the
2. 2 display the upload area and
upload area and ‘Generate’ button. P
‘Generate’ button.
The web application will
The web application will display the
3. 3 display the preview image in P
preview image in the upload area.
the upload area.
4. 4 The web application will display the The web application will P
loading state. display the loading state.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 490
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The web application will
The web application will display the 3D display the 3D model
5. 5 model generation from the uploaded generation from the uploaded P
image. image.
3.11) STC-11: Create the name of the design
Test ID: STC-11
Test No: UC-11
Test case name: Create the name of the design
Description: Registered user can create the name of the design according to their
needs.
Test Setup:
2. Already logged into the system
Test Script:
3. Click on the “Image To 3D” button on the home page
4. Input the model name in the input field on the Image to 3D page
before generating the model
Prepared Data:
- User’s model name
- Default name: New Model
Test Script
No. Expected Output Actual Output P/F
No.
The system will create a 3D
The system will create a 3D model and
1. 1 model and save its name in P
save its name in the database.
the database.
The system will create a 3D
The system will create a 3D model and model and save its name in
2. 1 save its name in the database. the database. P
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 491
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The system displays message “Please The system displays message
3. 1 create name before generating your “Please create name before P
model.” generating your model.”
3.12) STC-12: Delete the uploaded image
Test ID: STC-12
Test No: UC-12
Test case name: Delete the uploaded image
Description: Registered user can delete the uploaded image.
Test Setup:
2. Already logged into the system
Test Script:
4. Click on the “Image To 3D” button on the home page
5. Upload the image that want to convert to a model
6. Click the “Delete” button
Prepared Data:
Image: necklace.jpg
Test Script
No. Expected Output Actual Output P/F
No.
The system will display a
The system will display a delete button
1. 1 delete button after uploading P
after uploading the image.
the image.
The system will delete the uploaded image The system will delete the
1 and the image input field will return to uploaded image and the

## 2. P

default field. image input field will return
t o default field.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 492
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

2.13) STC-13: Use the converted image to 3d model to customize
Test ID: STC-13
Test No: UC-14
Test case name: Use the converted image to 3d model to customize
Description: Registered users can use the converted image to 3d model to
customize, and the system will provide details of the selected model.
Test Setup:
2. Already logged into the system
Test Script:
3. Registered user is on the “Image to 3D” page
4. Click the “Custom” button in the navigation sidebar.
Test Script
No. Expected Output Actual Output P/F
No.
The web application will
The web application will display the 3d
display the 3d model with the
1 model with the “Custom” button in image P
“Custom” button in image to
to 3d page.
3d page.
1.
The web application redirects
The web application redirects to image to
to image to 3d customization
2 3d customization page and shows correct P
page and shows correct 3D
3D model.
model.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 493
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.14) STC-14: View the jewelry model
Test ID: STC-14
Test No: UC-15
Test case name: View the jewelry model
Description: The registered user can view the selected jewelry model in the
model viewer.
Test Setup:
3. Already logged into the system.
4. Already selected the jewelry model.
Test Script:
3. Registered user is on the “Jewelry Customization” or “Image to 3d
Customization” page.
4. Clicks the “Custom” button in the navigation sidebar.
Test Script
No. Expected Output Actual Output P/F
No.
The web application displays
The web application displays the selected
1. 1 the selected jewelry model in P
jewelry model in the model viewer.
the model viewer.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 494
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.15) STC-15: Customize the name of the jewelry model
Test ID: STC-15
Test No: UC-17
Test case name: Customize the name of the jewelry model
Description: The registered user can customize the name of the jewelry model to
a new desired name.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
3. Registered user is on the “Jewelry Customization” page.
4. Click on the input field that already has the default name in the jewelry
sidebar.
Prepared Data:
- New name: My new necklace
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” page with the current
1 page with the current name of P
name of the jewelry model in the input
the jewelry model in the input
1. field.
field.
The system updates the
The system updates the displayed name in
3 displayed name in the input P
the input field.
field.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 495
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.16) STC-16: Customize the color of the jewelry model
Test ID: STC-16
Test No: UC-18
Test case name: Customize the color of the jewelry model
Description: The registered user can customize the color of the jewelry model
and can preview the color changes in real-time.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
4. Registered user is on the “Jewelry Customization” or “Image to 3D
Customization” page.
5. Click the “Custom” button in the navigation bar.
6. Click the color dropdown.
Prepared Data:
- New selected color: Rose pink
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
1 or “Image to 3D P
Customization” page with the color
Customization” page with the
dropdown.
1. color dropdown.
The system updates and
The system updates and displays the
displays the jewelry model
3 jewelry model with the selected color in P
with the selected color in real-
real-time.
time.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” page or “Image to 3D
1 page or “Image to 3D P
Customization” page with the color
2. Customization” page with the
dropdown.
color dropdown.
The system displays the default color as The system displays the

## 3 P

clear. default color as clear.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 496
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.17) STC-17: Customize the material of the jewelry model
Test ID: STC-17
Test No: UC-19
Test case name: Customize the material of the jewelry model
Description: The registered user can customize the material of the jewelry model
and can preview the material changes in real-time.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
4. Registered user is on the “Jewelry Customization” or “Image to 3D
Customization” page.
5. Click the “Custom” button in the navigation bar.
6. Click the material dropdown.
Prepared Data:
- New selected material: Gold
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
1 or “Image to 3D P
Customization” page with the material
Customization” page with the
dropdown.
1. material dropdown.
The system updates and
The system updates and displays the
displays the jewelry model
3 jewelry model with the selected material in P
with the selected material in
real-time.
real-time.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” page or “Image to 3D
1 page or “Image to 3D P
Customization” page with the material
2. Customization” page with the
dropdown.
material dropdown.
The system displays the default color as The system displays the

## 3 P

silver. default color as silver.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 497
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.18) STC-18: Customize the size of the jewelry model
Test ID: STC-18
Test No: UC-20
Test case name: Customize the size of the jewelry model
Description: The registered user can customize the size of the jewelry model and
can preview the size changes in real-time.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
4. Registered user is on the “Jewelry Customization” or “Image to 3D
Customization” page.
5. Click the “Custom” button in the navigation bar.
6. Drag the size slider.
Prepared Data:
- New selected size: 40mm.
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the “Jewelry the “Jewelry Customization”
1 Customization” or “Image to 3D or “Image to 3D P
Customization” page with the size slider. Customization” page with the
1. size slider.
The system updates and
The system updates and displays the
displays the jewelry model
3 jewelry model with the selected size in P
with the selected size in real-
real-time.
time.
The web application provides
The web application provides the “Jewelry the “Jewelry Customization”
1 Customization” page or “Image to 3D page or “Image to 3D P
2. Customization” page with the size slider Customization” page with the
size slider.
The system displays the default size as The system displays the

## 3 P

33mm. default size as 33mm.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 498
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.19) STC-19: Customize the color of specific jewelry sections (Use the
predefined jewelry mockup)
Test ID: STC-19
Test No: UC-21
Test case name: Customize the color of specific jewelry sections (Use the
predefined jewelry mockup)
Description: The registered user can customize the color of specific parts of a
predefined jewelry mockup by cropping the part that they want.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
6. Registered user is on the “Jewelry Customization” page.
7. Click the “Custom” button in the navigation bar.
8. Click the “Crop” button in the bottom bar.
9. Drag on the 3D model to define the area.
10. Click the color dropdown.
Prepared Data:
- New selected color: Rose pink
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
or “Image to 3D
1 Customization” page with the color P
Customization” page with the
dropdown and Crop” button in the bottom
color dropdown and Crop”
bar.
button in the bottom bar.
1. The web application displays
The web application displays a square crop
2 a square crop box following P
box following the registered user’s drag.
the registered user’s drag.
The web application applies
The web application applies the new color
the new color to the cropped
3 to the cropped section and updates the P
section and updates the model
model in real-time.
in real-time.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 499
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The web application
The web application preserves the applied
preserves the applied color
4 color and returns to the normal P
and returns to the normal
customization mode.
customization mode.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
or “Image to 3D
1 Customization” page with the color P
Customization” page with the
dropdown and Crop” button in the bottom
2. color dropdown and Crop”
bar.
button in the bottom bar.
The web application displays
The web application displays a square crop
2 a square crop box following P
box following the registered user’s drag.
the registered user’s drag.
The web application applies
The web application applies the new color
the new color to the cropped
3 to the cropped section and updates the P
section and updates the model
model in real-time.
in real-time.
The web application discards the selected The web application discards

## 4 P

color. the selected color.
The system displays the
The system displays the message “Please
message “Please drag on the
3. drag on the model area to apply P
1 model area to apply
customization.”
customization.”
The system allows cropping and recoloring The system allows cropping

## 4. 1 P

as usual. and recoloring as usual.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 500
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.20) STC-20: Customize the color of specific jewelry sections (Use converted
image to 3d model)
Test ID: STC-20
Test No: UC-21
Test case name: Customize the color of specific jewelry sections (Use the
converted image to 3d model)
Description: The registered user can customize the color of specific parts of a
converted image to 3d model by cropping the part that they want.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
6. Registered user is on the “Image to 3d Customization” page.
7. Click the “Custom” button in the navigation bar.
8. Click the “Crop” button in the bottom bar.
9. Drag on the 3D model to define the area.
10. Click the color dropdown.
Prepared Data:
- New selected color: Rose pink
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
or “Image to 3D
1 Customization” page with the color P
Customization” page with the
dropdown and Crop” button in the bottom
color dropdown and Crop”
bar.
button in the bottom bar.
1. The web application displays
The web application displays a square crop
2 a square crop box following P
box following the registered user’s drag.
the registered user’s drag.
The web application applies
The web application applies the new color
the new color to the cropped
3 to the cropped section and updates the P
section and updates the model
model in real-time.
in real-time.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 501
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The web application
The web application preserves the applied
preserves the applied color
4 color and returns to the normal P
and returns to the normal
customization mode.
customization mode.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
or “Image to 3D
1 Customization” page with the color P
Customization” page with the
dropdown and Crop” button in the bottom
2. color dropdown and Crop”
bar.
button in the bottom bar.
The web application displays
The web application displays a square crop
2 a square crop box following P
box following the registered user’s drag.
the registered user’s drag.
The web application applies
The web application applies the new color
the new color to the cropped
3 to the cropped section and updates the P
section and updates the model
model in real-time.
in real-time.
The web application discards the selected The web application discards

## 4 P

color. the selected color.
The system displays the
The system displays the message “Please
message “Please drag on the
3. drag on the model area to apply P
1 model area to apply
customization.”
customization.”
The system allows cropping and recoloring The system allows cropping

## 4. 1 P

as usual. and recoloring as usual.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 502
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.21) STC-21: Customize the material of specific jewelry sections (Use the
predefined jewelry mockup)
Test ID: STC-21
Test No: UC-22
Test case name: Customize the material of specific jewelry sections (Use the
predefined jewelry mockup)
Description: The registered user can customize the material of specific parts of a
predefined jewelry mockup by cropping the part that they want.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
6. Registered user is on the “Jewelry Customization” page.
7. Click the “Custom” button in the navigation bar.
8. Click the “Crop” button in the bottom bar.
9. Drag on the 3D model to define the area.
10. Click the material dropdown.
Prepared Data:
- New selected material: Gold
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
or “Image to 3D
1 Customization” page with the material P
Customization” page with the
dropdown and Crop” button in the bottom
material dropdown and Crop”
bar.
button in the bottom bar.
1. The web application displays
The web application displays a square crop
2 a square crop box following P
box following the registered user’s drag.
the registered user’s drag.
The web application applies
The web application applies the new
the new material to the
3 material to the cropped section and P
cropped section and updates
updates the model in real-time.
the model in real-time.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 503
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The web application
The web application preserves the applied
preserves the applied color
4 color and returns to the normal P
and returns to the normal
customization mode.
customization mode.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
or “Image to 3D
1 Customization” page with the material P
Customization” page with the
dropdown and Crop” button in the bottom
2. material dropdown and Crop”
bar.
button in the bottom bar.
The web application displays
The web application displays a square crop
2 a square crop box following P
box following the registered user’s drag.
the registered user’s drag.
The web application applies
The web application applies the new
the new material to the
3 material to the cropped section and P
cropped section and updates
updates the model in real-time.
the model in real-time.
The web application discards the selected The web application discards

## 4 P

material. the selected material.
The system displays the
The system displays the message “Please
message “Please drag on the
3. drag on the model area to apply P
1 model area to apply
customization.”
customization.”
The system allows cropping
The system allows cropping and change
4. 1 and change the material as P
the material as usual.
usual.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 504
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.22) STC-22: Customize the material of specific jewelry sections (Use
converted image to 3d model)
Test ID: STC-22
Test No: UC-22
Test case name: Customize the material of specific jewelry sections (Use the
converted image to 3d model)
Description: The registered user can customize the material of specific parts of a
converted image to 3d model by cropping the part that they want.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
6. Registered user is on the “Image to 3d Customization” page.
7. Click the “Custom” button in the navigation bar.
8. Click the “Crop” button in the bottom bar.
9. Drag on the 3D model to define the area.
10. Click the material dropdown.
Prepared Data:
- New selected material: Gold
Test Script
No. Expected Output Actual Output P/F
No.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
or “Image to 3D
1 Customization” page with the material P
Customization” page with the
dropdown and Crop” button in the bottom
material dropdown and Crop”
bar.
button in the bottom bar.
1. The web application displays
The web application displays a square crop
2 a square crop box following P
box following the registered user’s drag.
the registered user’s drag.
The web application applies
The web application applies the new
the new material to the
3 material to the cropped section and P
cropped section and updates
updates the model in real-time.
the model in real-time.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 505
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The web application
The web application preserves the applied
preserves the applied color
4 color and returns to the normal P
and returns to the normal
customization mode.
customization mode.
The web application provides
The web application provides the “Jewelry
the “Jewelry Customization”
Customization” or “Image to 3D
or “Image to 3D
1 Customization” page with the material P
Customization” page with the
dropdown and Crop” button in the bottom
2. material dropdown and Crop”
bar.
button in the bottom bar.
The web application displays
The web application displays a square crop
2 a square crop box following P
box following the registered user’s drag.
the registered user’s drag.
The web application applies
The web application applies the new
the new material to the
3 material to the cropped section and P
cropped section and updates
updates the model in real-time.
the model in real-time.
The web application discards the selected The web application discards

## 4 P

material. the selected material.
The system displays the
The system displays the message “Please
message “Please drag on the
3. drag on the model area to apply P
1 model area to apply
customization.”
customization.”
The system allows cropping
The system allows cropping and change
4. 1 and change the material as P
the material as usual.
usual.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 506
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.23) STC-23: Zoom in and zoom out the jewelry model
Test ID: STC-23
Test No: UC-23
Test case name: Zoom in and zoom out the jewelry model
Description: The registered user can zoom in and zoom out of the jewelry model
to closely examine design details or view the entire piece more clearly.
Test Setup:
3. Already logged into the system
4. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
3. Registered user is on the “Jewelry Customization” or “Image to 3D
Customization” page.
4. Click on the “Zoom-in” (plus button) or “Zoom-out” (minus button) in
the bottom bar.
Test Script
No. Expected Output Actual Output P/F
No.
The system displays a
The system displays a zoomed in the
zoomed in the jewelry model
1. 1 jewelry model (larger view, closer details P
(larger view, closer details
visible).
visible).
The system displays a
The system displays a zoomed out the
zoomed out the jewelry model
2. 1 jewelry model (smaller view, wider P
(smaller view, wider
perspective visible).
perspective visible).
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 507
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.24) STC-24: View the packaging model
Test ID: STC-24
Test No: UC-24
Test case name: View the packaging model
Description: Registered users can view the selected packaging model in the
model viewer.
Test Setup:
1. Already logged into the system
2. Already select the packaging model that want to customize.
Test Script:
1. Registered user is on the “Packaging Customization” page with the
selected packaging model.
Test Script
No. Expected Output Actual Output P/F
No.
The web application will
The web application will display the
display the selected
1. 1 selected packaging model in the model P
packaging model in the model
viewer.
viewer.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 508
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.25) STC-25: Customize the color of the packaging model
Test ID: STC-25
Test No: UC-26
Test case name: Customize the color of the packaging model
Description: Registered user can change the packaging model’s color by
selecting from a color palette, inputting a valid hex code, or choosing a custom
color using a color picker, then the system applies the new color in real-time to
the packaging model in the model viewer.
Test Setup:
1. Already logged into the system
2. The packaging model has been loaded and displayed in the model
viewer.
Test Script:
4. Registered user is on the “Packaging Customization” page
5. Click on the “Custom” button in the navigation sidebar.
6. Choose a color from the palettes, or input a hex code, or pick a custom
color.
Prepared Data:
- Hex color from palettes: #EBDECD
- Valid hex color from user’s input: #C3A59A
- Invalid hex color from user’s input: #ZZZZZZ
- Hex color from color picker: #AB5C5C
Test
No. Script Expected Output Actual Output P/F
No.
The web application displays the
The web application displays
1 provided palettes by the category (e.g., P
the input field.
Minimalist, Elegant&Neutral).
1.
The system applies the selected color The system displays the text
2 from the palettes to the packaging model on the packaging model in P
in the model viewer area. the model viewer.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 509
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The web application displays the input The web application displays

## 1 P

field. the font style dropdown.
2.
The system applies the color from the The system updates the text
inputted color code to the packaging on the packaging model with P
model in the model viewer area. the selected font style.
The web application displays the input The web application displays

## 1 P

field to input the color code. the font size dropdown.
The system displays a
The system displays a message message
3.
“Invalid color code. Please enter a valid “Invalid color code. Please

## 2 P

hex code or select a color from the enter a valid hex code or
palette.” select a color from the
palette.”
The system updates the text
The web application displays the color
1 on the packaging model with P
picker.
the selected font size.
4. The system displays the picked color in
the input field and applies the color to the The web application displays

## 2 P

packaging model in the model viewer the color picker.
area.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 510
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.26) STC-26: Add engraved text to the packaging model
Test ID: STC-26
Test No: UC-27
Test case name: Add engraved text to the packaging model
Description: Registered user can add custom engraved text to the selected
packaging model, including entering text, selecting font style, choosing font size,
changing text color, and dragging text to the desired position, then the system
displays the updated text in real-time on the model viewer.
Test Setup:
1. Already logged into the system
2. Registered user is on the “Packaging Customization” page
3. The packaging model has been loaded and displayed in the model
viewer.
Test Script:
8. Click on the “Custom” button in the navigation sidebar.
9. Enter custom text using the input field.
10. Select a font style using the dropdown menu.
11. Select a font size using the dropdown menu.
12. Select a text color using the color picker.
13. Drag the text to the desired position on the packaging model.
14. View the packaging model with the applied text, font, size, color, and
position.
Prepared Data:
- Text: 3DJewelryCraft
- Font style: Inter
- Font size: 16
- Hex color from color picker: #AB5C5C
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 511
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Test Script
No. Expected Output Actual Output P/F
No.
The web application displays the input The web application

## 1 P

field. displays the input field.
1.
The system displays the
The system displays the text on the
2 text on the packaging P
packaging model in the model viewer.
model in the model viewer.
The web application
The web application displays the font
1 displays the font style P
style dropdown.
dropdown.
2.
The system updates the text on the The system updates the text
2 packaging model with the selected font on the packaging model P
style. with the selected font style.
The web application
The web application displays the font
displays the font size P
1 size dropdown.
dropdown.
3.
The system updates the text on the The system updates the text
2 packaging model with the selected font on the packaging model P
size. with the selected font size.
The web application displays the color The web application

## 1 P

picker. displays the color picker.
The system updates the text
4.
The system updates the text color on the color on the packaging

## 2 P

packaging model with the selected color. model with the selected
color.
The web application
The web application updates the text
updates the text position on
5. 1 position on the packaging model in real- P
the packaging model in
time.
real-time.
The web application
The web application removes text from
6. 1 removes text from preview P
preview and resets the state.
and resets the state.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 512
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.27) STC-27: Replace with a new packaging model
Test ID: STC-27
Test No: UC-28
Test case name: Replace with a new packaging model
Description: Registered user can replace the currently applied packaging model
with a new one from the customization sidebar in the “Packaging Customization”
page.
Test Setup:
1. Already logged into the system
2. At least one packaging model is currently applied.
3. At least one packaging mockup exists in the system.
Test Script:
1. Registered user is on the “Packaging Customization” page with at least
one packaging model currently applied.
2. Select a new packaging model from the “All Packaging” button in the
customization sidebar.
Test Script
No. Expected Output Actual Output P/F
No.
The web application displays
The web application displays a list of
a list of packaging mockup
1 packaging mockup thumbnails in the P
thumbnails in the
customization sidebar.
customization sidebar.
1.
The system highlights
The system highlights selection on the new
selection on the new
2 packaging model thumbnail. P
packaging model thumbnail.
The system replaces the old
The system replaces the old packaging
packaging with the new one
3 with the new one and updates the model P
and updates the model
viewer.
viewer.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 513
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.28) STC-28: Choose the jewelry to try-on with packaging
Test ID: STC-28
Test No: UC-29
Test case name: Choose the jewelry to try-on with packaging
Description: Registered user can select saved jewelry from their workspace to try
on with the currently applied packaging model.
Test Setup:
1. Already logged into the system
2. At least one packaging model is currently applied.
3. Registered user has at least one saved jewelry item in their workspace.
Test Script:
1. Registered user is on the “Packaging Customization” page with at least
one packaging model currently applied.
2. Click the “My Jewelry” button in the customization sidebar.
3. Select a jewelry item from the list to try-on the selected jewelry with the
applied packaging.
Test Script
No. Expected Output Actual Output P/F
No.
The web application displays a list of The web application displays
1 saved jewelry items from the user’s a list of saved jewelry items P
workspace. from the user’s workspace.
1. The system displays the 3D
The system displays the 3D jewelry model
jewelry model along with the
2 along with the current packaging in the P
current packaging in the
model viewer area.
model viewer area.
The web application displays a list of The web application displays
1 saved jewelry items from the user’s a list of saved jewelry items P
workspace. from the user’s workspace.
The system displays a
2.
The system displays a message “Oops! message “Oops! This jewelry
2 This jewelry doesn’t fit with the current doesn’t fit with the current P
package. Try selecting a matching type.” package. Try selecting a
matching type.”
The system displays a message “You don’t The system displays a

## 3. 1 P

have any jewelry in your workspace yet.” message “You don’t have any
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 514
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

jewelry in your workspace
yet.”
3.29) STC-29: Zoom in and zoom out the packaging model
Test ID: STC-29
Test No: UC-30
Test case name: Zoom in and zoom out the packaging model
Description: The registered user can zoom in and zoom out of the packaging
model to closely examine design details or view the entire piece more clearly.
Test Setup:
1. Already logged into the system
2. The packaging model has been loaded and displayed in the model
viewer.
Test Script:
1. Registered user is on the “Packaging Customization” page.
2. Click on the “Zoom-in” (plus button) or “Zoom-out” (minus button) in
the bottom bar.
Test Script
No. Expected Output Actual Output P/F
No.
The system displays a
The system displays a zoomed in the
zoomed in the jewelry model
1. jewelry model (larger view, closer details P
1 (larger view, closer details
v isible).
v isible).
The system displays a
The system displays a zoomed out the
zoomed out the jewelry model
2. 1 jewelry model (smaller view, wider P
(smaller view, wider
perspective visible).
perspective visible).
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 515
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.30) STC-30: Select the type of simulated body to try on
Test ID: STC-30
Test No: UC-31
Test case name: Select the type of simulated body to try on
Description: Registered user can select the type of selected body on which the
jewelry will be virtually tried on.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Jewelry Customization”, “Image to 3D”, or
“Image to 3D Customization” page.
2. Click the “Virtual Try-On” button in the bottom bar.
3. Click the “Neck Try-On” or “Wrist Try-On” button to select the type of
simulated body.
Test Script
No. Expected Output Actual Output P/F
No.
The web application displays
The web application displays the options
the options “Neck Try-On”
“Neck Try-On” and “Wrist Try-On” for P
1 and “Wrist Try-On” for
simulated body type.
1. simulated body type.
The system displays the
The system displays the simulated neck in
2 simulated neck in the model P
the model viewer
viewer
The web application displays
The web application displays the options
the options “Neck Try-On”
1 “Neck Try-On” and “Wrist Try-On” for P
and “Wrist Try-On” for
simulated body type.
2. simulated body type.
The system displays the
The system displays the simulated wrist in
2 simulated wrist in the model P
the model viewer
viewer
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 516
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.31) STC-31: View the jewelry on the simulated body
Test ID: STC-31
Test No: UC-32
Test case name: View the jewelry on the simulated body
Description: The registered user can view the model designed on the simulated
body (neck or wrist) in the model viewer.
Test Setup:
1. Already logged into the system
2. The jewelry model has been loaded and displayed in the model viewer.
3. The simulated body type (neck or wrist) must have been selected.
Test Script:
1. Registered user is on the “Jewelry Customization”, “Image to 3D” or
“Image to 3D Customization” page.
2. Click the “Virtual Try-On” button in the bottom bar.
3. Click the “Neck Try-On” or “Wrist Try-On” button.
Test Script
No. Expected Output Actual Output P/F
No.
The system validates whether
The system validates whether the jewelry
1 the jewelry type and P
t ype and simulated body type match.
s imulated body type match.
1.
The system correctly displays
The system correctly displays the jewelry
2 the jewelry model on the P
model on the selected body model.
selected body model.
The system validates whether
The system validates whether the jewelry
the jewelry type and
1 type and simulated body type match. P
simulated body type match.
2.
The system displays message
The system displays message “Try-on is
2 “Try-on is not supported for P
not supported for this type”.
this type”.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 517
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.32) STC-32: View all previously designed works
Test ID: STC-32
Test No: UC-33
Test case name: View all previously designed works
Description: Registered user can view all previously designed works on their
workspace.
Test Setup:
1. Already logged into the system
Test Script:
2. Clicks on the “Workspace” button on the navbar or the sidebar.
Test Script
No. Expected Output Actual Output P/F
No.
The system validates user
The system validates user session and
1 session and navigates to the P
navigates to the “Workspace” page.
“Workspace” page.
1. The system displays all
The system displays all previously saved
previously saved jewelry
2 jewelry designs. P
designs.
The system validates user
The system validates user session and
1 session and navigates to the P
navigates to the “Workspace” page.
“Workspace” page.
2.
The system displays message
The system displays message “Don't have
2 “Don't have saved design P
saved design yet.”
yet.”
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 518
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.33) STC-33: Create a new design
Test ID: STC-33
Test No: UC-34
Test case name: Create a new design
Description: Registered user can create a new design for their workspace.
Test Setup:
1. Already logged into the system
Test Script:
3. Clicks on the “Workspace” button on the navbar or the sidebar.
4. Click on the “Create new design” button on the “Workspace” page.
Test Script
No. Expected Output Actual Output P/F
No.
The system navigates to the “Image to 3D” The system navigates to the

## 1. 1 P

page. “Image to 3D” page.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 519
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.34) STC-34: Save the designed work
Test ID: STC-34
Test No: UC-35
Test case name: Save the designed work
Description: Registered user can save the designed work to their workspace.
Test Setup:
1. Already logged into the system
Test Script:
2. Clicks the “Save to workspace” button on the “Mockups” or
“Customization” page.
Test Script
No. Expected Output Actual Output P/F
No.
The system saves the design
The system saves the design to the user’s
1 to the user’s workspace in the P
workspace in the database.
database.
1. The system displays a
The system displays a message “Your
message “Your design has
2 design has been saved.” P
been saved.”
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 520
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.35) STC-35: Save the designed work from the predefined jewelry mockup
Test ID: STC-35
Test No: UC-36
Test case name: Save the designed work from the predefined jewelry mockup
Description: Registered user can save the designed work from the predefined
jewelry mockup to their workspace.
Test Setup:
1. Already logged into the system
Test Script:
2. Clicks the “Save to workspace” button on the “Jewelry Mockups” or
“Jewelry Customization” page.
Test Script
No. Expected Output Actual Output P/F
No.
The system saves the jewelry
The system saves the jewelry design to the
design to the user’s P
1 user’s workspace in the database.
workspace in the database.
1.
The system displays a message “Your The system displays a
2 design has been saved.” message “Your design has P
been saved.”
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 521
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.36) STC-36: Save the designed work from the converted image to 3d model
Test ID: STC-36
Test No: UC-37
Test case name: Save the designed work from the converted image to 3d model
Description: Registered user can save the designed work from the converted
image to 3d model to their workspace.
Test Setup:
1. Already logged into the system
Test Script:
2. Clicks the “Save to workspace” button on the “Image to 3d” or “Image
to 3d Customization” page.
Test Script
No. Expected Output Actual Output P/F
No.
The system saves the
The system saves the converted image to
converted image to 3d model
1 3d model design to the user’s workspace in P
design to the user’s
the database.
1. workspace in the database.
The system displays a message “Your The system displays a
2 design has been saved.” message “Your design has P
been saved.”
The system disables the “Save
The system disables the “Save to
to workspace” button,
2. 1 workspace” button, users cannot press and P
registered user cannot press
save the 3d model.
and save the 3d model.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 522
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.37) STC-37: Save the designed work from the predefined packaging mockup
Test ID: STC-37
Test No: UC-38
Test case name: Save the designed work from the predefined packaging mockup
Description: Registered user can save the designed work from the predefined
packaging mockup to their workspace.
Test Setup:
1. Already logged into the system
Test Script:
2. Clicks the “Save to workspace” button on the “Packaging Mockups”
or “Packaging Customization” page.
Test Script
No. Expected Output Actual Output P/F
No.
The system saves the
The system saves the packaging design or packaging design or
1 packaging design with the jewelry to the packaging design with the P
user’s workspace in the database. jewelry to the user’s
1.
workspace in the database.
The system displays a message “Your The system displays a
2 design has been saved.” message “Your design has P
been saved.”
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 523
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.38) STC-38: Export image as PNG format
Test ID: STC-38
Test No: UC-40
Test case name: Export image as PNG format
Description: Registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a PNG (transparent
background).
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as PNG” button on the modal.
Test Script
No. Expected Output Actual Output P/F
No.
The system generates a PNG image from The system generates a PNG

## 1 P

the 3D scene. image from the 3D scene.
The system downloads a PNG
file named
The system downloads a PNG file named
1. model_snapshot.png to the
model_snapshot.png to the registered
2 registered user’s computer, P
user’s computer, and the image accurately
and the image accurately
displays the current view of the 3D model.
displays the current view of
the 3D model.
The system displays the error
The system displays the error message
message “Failed to export
2. 1 “Failed to export image. Please try again”, P
image. Please try again”, and
and no file is downloaded.
no file is downloaded.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 524
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.39) STC-39: Export image as JPG format
Test ID: STC-39
Test No: UC-41
Test case name: Export image as JPG format
Description: Registered user can export the 3D model displayed in the model
viewer as an image, with the option to export it as a JPG (white background).
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as JPG” button on the modal.
Test Script
No. Expected Output Actual Output P/F
No.
The system generates a JPG image from The system generates a JPG

## 1 P

the 3D scene. image from the 3D scene.
The system downloads a PNG
file named
The system downloads a PNG file named
1. model_snapshot.jpg to the
model_snapshot.jpg to the registered
2 registered user’s computer, P
user’s computer, and the image accurately
and the image accurately
displays the current view of the 3D model.
displays the current view of
the 3D model.
The system displays the error
The system displays the error message
message “Failed to export
2. 1 “Failed to export image. Please try again”, P
image. Please try again”, and
and no file is downloaded.
no file is downloaded.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 525
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.40) STC-40: Export the model as PDF report
Test ID: STC-40
Test No: UC-42
Test case name: Export the model as PDF report
Description: Registered users can export their customized designs, including
jewelry, packaging, or a combination of both, as detailed PDF reports.
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Generate PDF Report” button on the modal.
Test
No. Script Expected Output Actual Output P/F
No.
The system generates a PDF report
The system generates a PDF report with
with details including file name,
details including file name, export date,
1 export date, material, color, size, P
material, color, size, and a preview
and a preview image of the
image of the model.
1. model.
The system downloads the jewelry PDF The system downloads the jewelry
report named PDF report named

## 2 P

jewelryName_customization.pdf to the jewelryName_customization.pdf to
registered user’s computer. the registered user’s computer.
The system generates a PDF report
The system generates a PDF report with
with details including file name,
details including file name, export date,
export date, package name,
1 package name, package color, engraving P
package color, engraving text
text with color, font, font size, and a
with color, font, font size, and a
2. preview image of the model.
preview image of the model.
The system downloads the jewelry PDF The system downloads the jewelry
report named PDF report named

## 2 P

packageName_customization.pdf to the packageName_customization.pdf
registered user’s computer. to the registered user’s computer.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 526
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The system generates a PDF report
The system generates a PDF report with
with details including file name,
details including file name, export date,
1 export date, jewelry details, P
jewelry details, packaging details, and a
packaging details, and a preview
preview image of the model.
image of the model.
3.
The system downloads the jewelry PDF The system downloads the jewelry
report named PDF report named
2 jewelryName_packageName_ jewelryName_packageName_ P
customization.pdf to the registered user’s customization.pdf to the registered
computer. user’s computer.
The system displays the error message The system displays the error
4 1 “Failed to export PDF report. Please try message “Failed to export PDF P
again”. report. Please try again”.
3.41) STC-41: Export 3D file as STL format
Test ID: STC-41
Test No: UC-44
Test case name: Export 3D file as STL format
Description: Registered users can export 3D models displayed in the model
viewer in STL format.
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as STL” button on the modal.
Test Script
No. Expected Output Actual Output P/F
No.
The system generates a 3D file in STL The system generates a 3D

## 1 P

format. file in STL format.
1. The system downloads an
The system downloads an STL file named
STL file named Untitled.stl
2 Untitled.stl to the registered user’s P
to the registered user’s
computer.
computer.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 527
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

The system displays the error
The system displays the error message
message “No model to
2. 1 “No model to export as STL” and no P
export as STL” and no file is
file is downloaded.
downloaded.
3.42) STC-42: Export 3D file as OBJ format
Test ID: STC-42
Test No: UC-45
Test case name: Export 3D file as OBJ format
Description: Registered users can export 3D models displayed in the model
viewer in OBJ format.
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as OBJ” button on the modal.
Test Script
No. Expected Output Actual Output P/F
No.
The system generates a 3D file in OBJ The system generates a 3D

## 1 P

format. file in OBJ format.
1. The system downloads an
The system downloads an OBJ file named
OBJ file named Untitled.obj
2 Untitled.obj to the registered user’s P
to the registered user’s
computer.
computer.
The system displays the error
The system displays the error message
message “No model to
2. 1 “No model to export as OBJ” and no P
export as OBJ” and no file is
file is downloaded.
downloaded.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 528
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

3.43) STC-43: Export 3D file as GLB format
Test ID: STC-43
Test No: UC-46
Test case name: Export 3D file as GLB format
Description: Registered users can export 3D models displayed in the model
viewer in GLB format.
Test Setup:
1. Already logged into the system
2. The model has been loaded and displayed in the model viewer.
Test Script:
1. Registered user is on the “Mockups” or “Customization” page.
2. Click the “Super Export” button in the top right.
3. Click the “Export as GLB” button on the modal.
Test Script
No. Expected Output Actual Output P/F
No.
The system generates a 3D file in GLB The system generates a 3D

## 1 P

format. file in GLB format.
1.
The system downloads a GLB file named The system downloads a GLB
2 Untitled.glb to the registered user’s file named Untitled.glb to the P
computer. registered user’s computer.
The system displays the error
The system displays the error message
message “No model to
2. 1 “No model to export as GLB” and no P
export as GLB” and no file
file is downloaded.
is downloaded.
Document 3DJewelryCraft_Test_Record Owner NP1, NP2 Page 529
Name _V.0.6
Document Test Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 7
Traceability Record

---

Document History
Document Version History Status Date Editable Reviewer
Name
3DJewelryCraft_ 3DJewelryCraft_ Add Chapter Draft 24/05/2025 NP1, SW
Traceability_ Traceability_ 1 NP2
Record_V.0.1 Record_V.0.1 Add Chapter
3DJewelryCraft_ 3DJewelryCraft_ Update Draft 24/05/2025 NP1, SW
Traceability_ Traceability_ Chapter 1 NP2
Record_V.0.2 Record_V.0.2 Update
Chapter 2
3DJewelryCraft_ 3DJewelryCraft_ Update Draft 29/06/2025 NP1, SW
Traceability_ Traceability_ Chapter 1 NP2
Record_V.0.3 Record_V.0.3 Update
Chapter 2
3DJewelryCraft_ 3DJewelryCraft_ Update Draft 29/08/2025 NP1, SW
Traceability_ Traceability_ Chapter 1 NP2
Record_V.0.4 Record_V.0.4 Update
Chapter 2
3DJewelryCraft_ 3DJewelryCraft_ Update Final 18/10/2025 NP1, SW
Traceability_ Traceability_ Chapter 1 NP2
Record_V.0.5 Record_V.0.5 Update
Chapter 2
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 531
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## TABLE OF CONTENTS

Document History ..................................................................................................................... 531
Chapter One | Introduction...................................................................................................... 533
1.1) Purpose ........................................................................................................................... 533
1.2) Scope ............................................................................................................................... 533
Chapter Two | Traceability Record Table .............................................................................. 534

---

Chapter One | Introduction
1.1) Purpose
The purpose of traceability record is to describe the relation of the requirements
throughout the validation process. The purpose of the Requirements Traceability Matrix
is to ensure that all requirements defined for “3DJewelryCraft” are tested in the test
protocols.
1.2) Scope
• Describe the relationship between user requirement, system requirement, use case,
sequence diagram, user interface, class diagram, function description, unit test,
and system test.
Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 533
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter Two | Traceability Record Table
User System
Sequence Activity User
Feature Requirement Requirement Use Case Unit Test System Test
Diagram Diagram Interface
Specification Specification
Feature #1: URS-01 SRS-01 UC-01 SD-01 AD-01 UI-01 UTC-01 STC-01
Register SRS-02

## SRS-03


## SRS-04


## SRS-05


## SRS-06


## SRS-07


## SRS-08


## SRS-09


## SRS-10


## SRS-11


## SRS-12


## SRS-13


## URS-02 SRS-14 UC-02 SD-02 AD-02 UI-02 UTC-02 STC-02


## SRS-02


## SRS-15


## SRS-16


## SRS-08


## SRS-09

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 534
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## SRS-17


## SRS-11


## SRS-13


## URS-03 SRS-18 UC-03 SD-03 AD-03 UI-03 UTC-03 STC-03


## SRS-19


## SRS-20

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 535
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

User System
Feature Sequence Activity User System
Requirement Requirement Use Case Unit Test
Diagram Diagram Interface Test
Specification Specification
Feature #2: URS-04 SRS-21 UC-04 SD-04 AD-04 UI-04 UTC-04 STC-04
Jewelry and SRS-22
Packaging SRS-23
Mockups SRS-13

## URS-05 SRS-24 UC-05 SD-05 AD-05 UI-05 UTC-05 STC-05


## SRS-25


## SRS-23


## SRS-13


## URS-06 SRS-26 UC-06 SD-06 AD-06 UI-06 UTC-06 STC-06


## SRS-27


## SRS-28


## SRS-29


## SRS-30


## SRS-13


## URS-07 SRS-31 UC-07 SD-07 AD-07 UI-07 UTC-07 STC-07


## SRS-32


## SRS-28


## SRS-29


## SRS-30


## SRS-13


## URS-08 SRS-33 UC-08 SD-08 AD-08 UI-08 UTC-08 STC-08


## SRS-34


## SRS-13


## URS-09 SRS-35 UC-09 SD-09 AD-09 UI-09 UTC-09 STC-09

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 536
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## SRS-36


## SRS-13

User System
Sequence Activity User
Feature Requirement Requirement Use Case Unit Test System Test
Diagram Diagram Interface
Specification Specification
Feature #3: URS-10 SRS-37 UC-10 SD-10 AD-10 UI-10 UTC-10 STC-10
Image to 3D SRS-38 UTC-11

## SRS-39 UTC-12


## SRS-40 UTC-13


## SRS-41


## SRS-42


## SRS-43


## URS-11 SRS-44 UC-11 SD-11 AD-11 UI-11 UTC-14 STC-11


## SRS-45


## SRS-13


## URS-12 SRS-46 UC-12 SD-12 AD-12 UI-12 - STC-12


## SRS-47


## SRS-48

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 537
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

User System
Feature Sequence Activity User System
Requirement Requirement Use Case Unit Test
Diagram Diagram Interface Test
Specification Specification
Feature #4: URS-13 SRS-33 UC-13 SD-13 AD-13 UI-13 UTC-08 -
Customization SRS-49 UTC-13

## SRS-50


## SRS-13


## URS-14 SRS-49 UC-14 SD-14 AD-14 UI-14 UTC-13 STC-13


## SRS-51


## SRS-13


## URS-15 SRS-52 UC-15 SD-15 AD-15 UI-15 UTC-08 STC-14


## SRS-53


## SRS-13


## URS-16 SRS-54 UC-16 - AD-16 UI-16 - -


## SRS-55


## SRS-13


## URS-17 SRS-56 UC-17 SD-16 AD-17 UI-17 - STC-15


## SRS-57


## SRS-58


## SRS-13


## URS-18 SRS-59 UC-18 SD-17 AD-18 UI-18 - STC-16


## SRS-60


## SRS-13


## URS-19 SRS-61 UC-19 SD-18 AD-19 UI-19 - STC-17


## SRS-62


## SRS-13

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 538
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## URS-20 SRS-63 UC-20 SD-19 AD-20 UI-20 - STC-18


## SRS-64


## SRS-13


## URS-21 SRS-65 UC-21 SD-20 AD-21 UI-21 UTC-15 STC-19


## SRS-66 UTC-16 STC-20


## SRS-67 UTC-19


## SRS-68


## SRS-69


## SRS-70


## SRS-71


## SRS-72


## SRS-73


## URS-22 SRS-65 UC-22 SD-21 AD-22 UI-22 UTC-17 STC-21


## SRS-66 UTC-18 STC-22


## SRS-67 UTC-19


## SRS-74


## SRS-75


## SRS-70


## SRS-76


## SRS-77


## SRS-73


## URS-23 SRS-78 UC-23 - AD-23 UI-23 - STC-23


## SRS-79


## SRS-13


## URS-24 SRS-80 UC-24 SD-22 AD-24 UI-24 UTC-09 STC-24


## SRS-53


## SRS-13


## URS-25 SRS-81 UC-25 - AD-25 UI-25 - -


## SRS-82


## SRS-13

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 539
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## URS-26 SRS-83 UC-26 SD-23 AD-26 UI-26 - STC-25


## SRS-84


## SRS-85


## SRS-86


## SRS-87


## SRS-13


## URS-27 SRS-88 UC-27 SD-24 AD-27 UI-27 - STC-26


## SRS-89


## SRS-90


## SRS-91


## SRS-92


## SRS-93


## SRS-13


## URS-28 SRS-94 UC-28 SD-25 AD-28 UI-28 UTC-09 STC-27


## SRS-95


## SRS-96


## SRS-13


## URS-29 SRS-97 UC-29 SD-26 AD-29 UI-29 UTC-20 STC-28


## SRS-98


## SRS-99


## SRS-100


## SRS-101


## SRS-13


## URS-30 SRS-102 UC-30 - AD-30 UI-30 - STC-29


## SRS-79


## SRS-13

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 540
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

User System
Sequence Activity User
Feature Requirement Requirement Use Case Unit Test System Test
Diagram Diagram Interface
Specification Specification
Feature #5: URS-31 SRS-103 UC-31 SD-27 AD-31 UI-31 UTC-21 STC-30
Virtual SRS-104
Try-On

## SRS-105


## SRS-106


## SRS-13


## URS-32 SRS-107 UC-32 SD-28 AD-32 UI-32 - STC-31


## SRS-108


## SRS-109


## SRS-110


## SRS-111


## SRS-112


## SRS-113


## SRS-114


## SRS-13

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 541
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

User System
Sequence Activity User
Feature Requirement Requirement Use Case Unit Test System Test
Diagram Diagram Interface
Specification Specification
Feature #6: URS-33 SRS-115 UC-33 SD-29 AD-33 UI-33 UTC-22 STC-32
Workspace SRS-116

## SRS-117


## SRS-13


## URS-34 SRS-118 UC-34 SD-30 AD-34 UI-34 - STC-33


## URS-35 SRS-119 UC-35 SD-31 AD-35 UI-35 - STC-34


## SRS-120


## SRS-13


## URS-36 SRS-121 UC-36 SD-32 AD-36 UI-36 UTC-23 STC-35


## SRS-120 UTC-24


## SRS-13


## URS-37 SRS-122 UC-37 SD-33 AD-37 UI-37 UTC-25 STC-36


## SRS-120 UTC-26


## SRS-13


## URS-38 SRS-123 UC-38 SD-34 AD-38 UI-38 UTC-27 STC-37


## SRS-120 UTC-28


## SRS-13

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 542
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

User System
Sequence Activity User
Feature Requirement Requirement Use Case Unit Test System Test
Diagram Diagram Interface
Specification Specification
Feature #7: URS-39 SRS-124 UC-39 - AD-39 - - -
Super Export SRS-125

## SRS-126


## SRS-127


## URS-40 SRS-128 UC-40 SD-35 AD-40 UI-39 - STC-38


## SRS-129


## SRS-130


## SRS-127


## URS-41 SRS-131 UC-41 SD-36 AD-41 UI-40 - STC-39


## SRS-132


## SRS-133


## SRS-127


## URS-42 SRS-134 UC-42 SD-37 AD-42 UI-41 - STC-40


## SRS-135


## SRS-136


## SRS-137


## SRS-138


## URS-43 SRS-139 UC-43 SD-38 AD-43 - - -


## SRS-140


## SRS-141


## SRS-142

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 543
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## URS-44 SRS-143 UC-44 SD-39 AD-44 UI-42 STC-41


## SRS-144

-

## SRS-145


## SRS-146


## URS-45 SRS-147 UC-45 SD-40 AD-45 UI-43 - STC-42


## SRS-148


## SRS-149


## SRS-150


## URS-46 SRS-151 UC-46 SD-41 AD-46 UI-44 - STC-43


## SRS-152


## SRS-153


## SRS-154

Document 3DJewelryCraft_Traceability_ Owner NP1, NP2 Page 544
Name Record_V.0.5
Document Traceability Record Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 8
Change Request

---

Document History
Document Version History Status Date Editable Reviewer
Name
3DJewelryCraft_ 3DJewelryCraft_ Add Chapter 1 Draft 23/05/2025 NP1, SW

## NP2

Change_Request Change_Request Update Chapter 1

## V.0.1 V.0.1

3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Final 30/06/2025 NP1, SW

## NP2

Change_Request Change_Request

## V.0.2 V.0.2

*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_Change_ Owner NP1, NP2 Page 546
Name Request_V.0.2
Document Change Request Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Change Request No.1
Project 3DJewelryCraft Request 1
Number
Department N/A Date 23/05/2025
Requested
Attachment N/A Date 23/05/2025
Needed
Requester’s Nichakorn Prompong Requester’s Email nichakorn_prompong@cmu.ac
Name and .th
Title
Reviewer’s Siraprapa Wattanakul Reviewer's Siraprapa.w@cmu.ac.th
Name and Email
Title
Request Details
Change Requesting to change the data storage process for 3D model URLs .glb and
thumbnail, from storing directly in MySQL to first uploading to Firebase Storage
Description
and then saving the public URLs to MySQL.
Change Initially, the system stored .glb and thumbnail URLs from Meshy API directly into
the MySQL database. However, these URLs expire after a short period of time.
Reason
The updated architecture changes this flow by first uploading the .glb and
thumbnail to Firebase Storage (our cloud service), generating permanent public
URLs. These URLs are then saved in MySQL for long-term access and use.
Associated N/A Priority High
Incidences
Attachment N/A Change Type Major Change
Document 3DJewelryCraft_Change_ Owner NP1, NP2 Page 547
Name Request_V.0.2
Document Change Request Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Impacts
Development - Required changes in the backend Flask API to handle file uploads to
Firebase.
- Slight increase in response time due to file transfer and Firebase
upload process.
Risk
Security Requires Firebase secure upload handling to avoid misuse.
Document 3DJewelryCraft_Change_ Owner NP1, NP2 Page 548
Name Request_V.0.2
Document Change Request Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Chapter 9
Executive Summary

---

Document History
Document Version History Status Date Editable Reviewer
Name
3DJewelryCraft_ 3DJewelryCraft_ Add Chapter 1 Draft 09/06/2025 NP1, SW
Executive_ Executive_ Update Chapter 1 NP2
Summary_V.0.1 Summary_V.0.1
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 19/06/2025 NP1, SW
Executive_ Executive_ NP2
Summary_V.0.2 Summary_V.0.2
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 29/06/2025 NP1, SW
Executive_ Executive_ NP2
Summary_V.0.3 Summary_V.0.3
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Draft 30/08/2025 NP1, SW
Executive_ Executive_ NP2
Summary_V.0.4 Summary_V.0.4
3DJewelryCraft_ 3DJewelryCraft_ Update Chapter 1 Final 18/10/2025 NP1, SW
Executive_ Executive_ NP2
Summary_V.0.5 Summary_V.0.5
*NP 1 = Nichakorn Prompong
*NP 2 = Nonlanee Panjateerawit
*SW = Siraprapa Wattanakul
Document 3DJewelryCraft_Executive_ Owner NP1, NP2 Page 550
Name Summary_V.0.5
Document Executive Summary Release 20/10/2025 Print 20/10/2025
Type Date Date

---


## TABLE OF CONTENTS

Document History ..................................................................................................................... 550
Chapter 1 Executive Summary ................................................................................................ 552
Product Perspective .............................................................................................................. 552
Features in the project .......................................................................................................... 554
Project Report Overview ...................................................................................................... 554

---

Chapter 1 Executive Summary
Product Perspective
3DJewelryCraft is a user-friendly web application that was created to meet the changing
needs of the jewelry industry in an era where consumers are demanding more customization and
easier access to designs without 3D knowledge or specialized software.
Progress I
According to the project plan, we have implemented three features in this progress
which are
Feature#1 Registration allows unregistered users to register for access to the system
by inputting the following fields: First name, Last name, Email, and Password. And allows
registered users can log in to the system by inputting the following fields: Email and
Password.
Feature#2 Jewelry and Packaging Mockups allows both unregistered and registered
users to view a variety of pre-designed jewelry and packaging mockups. Registered users
can select a jewelry or packaging mockup and proceed to customize it immediately. This
feature helps users visualize design options and jumpstart their creative process.
Feature#3 Image to 3D allows registered users to upload their 2D jewelry sketch or
drawing. The system then converts the uploaded image into a 3D model, enabling users to
rotate and inspect the model in 360 degrees. This provides an easy way to bring design
ideas to life without needing advanced 3D design skills.
In Progress I, we completed 100% of the planned features.
Progress II
According to the project plan, we have implemented two features in this progress
which are
Feature#4 Customization allows registered users to design and personalize both
jewelry and packaging models in real time. For jewelry, registered users can change colors,
materials, and crop specific areas of the 3D model to apply changes with precision. For
packaging, registered users can change the color, add engraving text, and place their
customized jewelry inside the designed box. This feature provides an intuitive and user-
friendly experience that encourages creativity and personalization.
Document 3DJewelryCraft_Executive_ Owner NP1, NP2 Page 552
Name Summary_V.0.5
Document Executive Summary Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Feature#5 Virtual Try-On enables registered users to try on jewelry virtually using
a 3D simulated body model. This feature provides a realistic preview of how the jewelry
would look when worn, whether on the neck or wrist, helping users visualize their designs
more accurately and make confident decisions.
In Progress II, we completed 100% of the planned features.
Final Progress
According to the project plan, we have implemented three features in this progress
which are
Feature#6: Workspace allows registered users to securely store their jewelry
designs and revisit previous designs and mockup selections at any time, without losing
data.
Feature#7 Super Export enables registered users to render and export their
customized 3D jewelry models in multiple formats, including high-quality images, PDF
reports, and 3D files for various purposes.
In Final Progress, we completed 100% of the planned features.
Project Name: 3DJewelryCraft
Created By Date Reporting Progress
NP1, NP2 18/10/2025 Final Progress
Project Over all Status: 100%
Milestone deliverables Performance Reporting
Milestone Due Date Progress (%) Deliverable Status
M1 Proposal 18/05/2025 100% On Schedule
M2 Progress I 28/06/2025 100% On Schedule
Feature#1:
28/06/2025 100% On Schedule
Registration
Feature#2:
Jewelry and 28/06/2025 100% On Schedule
Packaging Mockups
Feature#3: 28/06/2025
100% On Schedule
Image to 3D
M3 Progress II 05/09/2025 100% On Schedule
Feature #4 05/09/2025 100% On Schedule
Document 3DJewelryCraft_Executive_ Owner NP1, NP2 Page 553
Name Summary_V.0.5
Document Executive Summary Release 20/10/2025 Print 20/10/2025
Type Date Date

---

Customization
Feature #5
05/09/2025 100% On Schedule
Virtual Try-on
M4 Show Pro 17/09/2025 100% On Schedule
M5 Final Progress 20/10/2025 100% On Schedule
Feature #6
20/10/2025 100% On Schedule
Workspace
Feature #7
20/10/2025 100% On Schedule
Super Export
Features in the project
Feature Feature Name Status
1 Registration Complete
2 Jewelry and Packaging Mockups Complete
3 Image to 3D Complete
4 Customization Complete
5 Virtual Try-on Complete
6 Workspace Complete
7 Super Export Complete
Project Report Overview
User Date Deliverable Version Complete
Project Plan 0.4 100%
Software
Requirement 1.0 100%
Specification
Software Design
1.0 100%
Development
29/08/2025 On Schedule
Test Plan 0.9 100%
Test Record 0.6 100%
Traceability
0.4 100%
Record
Change Request 0.2 100%
Source Code 0.3 100%
Document 3DJewelryCraft_Executive_ Owner NP1, NP2 Page 554
Name Summary_V.0.5
Document Executive Summary Release 20/10/2025 Print 20/10/2025
Type Date Date

---
