AI-Based Reviewer on Project Code and Architecture
Project Proposal

BaiXuan Zhang 652115546

Bachelor of Science
Software Engineering Program

Department College of Arts, Media, and Technology Chiang Mai University November 2025



Project Advisor
Siraprapa Wattanakul. ph.D.

Table of content
                                                                       page
Chapter 1 | Introduction	3
Chapter 2 | Target User/Persona	5
2.1 Overview	5
2.2 Primary User Personas	6
2.2.1 pull request reviewer	6
2.2.2 programmer	7
2.2.3 Managers	7
Chapter 3 | User Journey/Scenarios	8
3.1 Overview	8
3.2 Primary Workflow: AI-Augmented Pull Request Review	8
3.3 Secondary Workflow: Architectural Drift Detection	10
3.4 Journey Stages	11
Chapter 4 | Business Reviews	12
4.1 Overview	12
4.2 Market Demand Analysis	12
4.3 Competitive Landscape	13
4.4 Risk Assessment	14
4.5 Strategic & Standards Alignment	14
Chapter 5 | Software Reviews	15
5.1 Overview	15
5.2Technology Review	15
5.2.1 External Services	15
5.2.2 Development Tools	16
5.2.3 Libraries / Frameworks / Databases	16
5.2.4 Infrastructure Tools Review	17
5.3 Evaluation Criteria	18
5.4 Findings	18
5.5 Evaluation Methodology	19
Chapter 6 | Objective	19
6.1 Primary Objectives	19
6.2 Secondary Objectives	19
Chapter 7 | System Architecture	19
7.1 Overview	19
7.2 Components	20
7.3 Architectural Principles	20
7.4 Architecture Diagram	20
Chapter 8 | Features	21
8.1 Core Feature	21
8.1.1 Code Review	22
8.1.2 Graph-based Architecture Analysis	22
8.1.4 Agentic AI Reasoning	23
8.2 Auxiliary Features	24
8.2.1 Authenticated System	24
8.2.2 Project Management:	24
Chapter 9 | Limitation	24
9.1 Technical Limitations	24
9.2 Operational Limitations	24
Chapter 10 | Mile Stone	25
10.1 Milestone Schedule	25







Chapter 1 | Introduction 
1.1 Problem Background
In today’s software development environment, the continuous growth of team size and the increasing complexity of systems have exposed significant limitations in traditional code review practices. First, pull request reviews(PR review) scale poorly: as repositories expand, manual reviews are inefficient and susceptible to systematic oversight, reducing overall review quality. Second, architectural drift accumulates silently: system structures gradually deviate from their intended design, often remaining undetected until large-scale refactoring becomes unavoidable, resulting in high maintenance costs and risks. These challenges hinder team efficiency and pose direct threats to long-term maintainability and security.

1.2 Our Solution
To solve these issues, We propose the AI-Based Reviewer on Project Code and Architecture, which is a platform on web is used to review code and architecture. In my project the AI is used by the integration of abstract syntax trees (AST) and dependency graphs into large language model reasoning. After user inputs GitHub Repository URL or Specific Branch, the platform will output Review Report: Detailed list of code defects and architectural drifts, and Visual Graphs: Project dependency graph and architecture evolution graph (based on Neo4j). This approach incorporates visual charts into the review results, thereby achieving a more comprehensive and detailed code review that combines macro and micro perspectives.
Key feature of our platform: 
		1.Push Request Code Review
		2.Graph-based Architecture Analysis
1.3 Conclusion
In summary, the proposed platform leverages graph-base analysis and contextual AI reasoning to redefine modern code review practices. It directly addresses the pain points of Excessive workload and architectural drift, while simultaneously strengthening transparency, compliance, and developer experience. By combining efficiency with architectural intelligence, this solution enables engineering teams to achieve faster, more reliable, and more sustainable code review workflows.
Chapter 2 | Target User/Persona
2.1 Overview
When the platform is deployed in the SDLC, it defines what quality assurance and architectural governance ecosystem it provides, why it addresses manual labor intensity, architectural erosion, and lack of transparency, who the key stakeholders are, when and where it supports their workflows, which processes it improves, whom it serves across roles, and how it ensures comprehensive governance and efficiency.

2.2 Primary User Personas
2.2.1 pull request reviewer 
The Pain: In traditional workflows, pull request reviewers face an overwhelming volume of manual reviews. The large scale of project specifications makes it nearly impossible to promptly detect subtle architectural deviations, leading to high consumption of time and cognitive resources.
The Value: The platform automates mechanical checks and provides graph-based visualizations, allowing testers to prioritize high-risk changes and ensure the integrity of the architecture during each project update.
Table 1: Pros/Cons for pull request reviewer
Pros	Cons	Value Delivered
Streamlined review process with automated checks	Initial learning curve for new workflows	Context-rich suggestions and visualizations for better decision-making
Reduced manual effort and improved consistency	Dependence on integration with CI/CD pipelines	
2.2.2 programmer
The Pain: Developers often struggle to identify security vulnerabilities or logical inconsistencies during the active coding phase. Without immediate feedback, these errors are often merged into the main branch, significantly increasing the cost of later remediation.
The Value: By providing real-time AI-augmented feedback during the Push Request stage, the platform enables developers to fix bugs and align with architectural standards before code leaves their local environment.
Table 2: Pros/Cons for programmer
Pros	Cons	Value Delivered
Early detection of architectural risks	Requires adoption of graph-based analysis mindset	Faster, more accurate reviews with reduced manual effort
Improved enforcement of design standards	Potential overhead in large monorepos	
2.2.3 Managers
The Pain: Managers often suffer from a "black box" problem where they cannot accurately assess the real-time status of project health or compare the quality of different development branches. This lack of data makes ROI insights and resource allocation difficult.
The Value: Through intuitive dashboards and progress graphs, the platform provides a clear "Health Index" for branches. Managers can visualize project evolution and make informed decisions based on quantifiable code quality metrics.
Table 3: Pros/Cons for Managers
Pros	Cons	Value Delivered
Clear visibility into team performance	Requires cultural adoption of metrics-driven management	Actionable metrics for quality, velocity, and compliance
Actionable insights for ROI measurement	Possible resistance from teams wary of monitoring	
Chapter 3 | User Journey/Scenarios
3.1 Overview
This chapter defines the primary user journeys and scenarios within the Graph-Augmented AI Code Review Platform. These workflows illustrate how the platform integrates into existing development practices, enhances efficiency, and ensures architectural integrity. Each scenario is structured to highlight the sequence of activities, expected outcomes, and value delivered to stakeholders.
3.2 Primary Workflow: AI-Augmented Pull Request Review
When developers initiate an AIaugmented pull request review, the platform defines what code changes are submitted, why architectural awareness and compliance readiness are essential, who participates in the review process, when and where the analysis occurs within the CI/CD pipeline, which modules or branches are impacted, whom the results are delivered to, and how the system separates functions by performing static analysis for syntax validation, AST parsing for structural integrity, graph updates for dependency tracking, and contextual reasoning for compliance and architectural governance.
Selected Activities:
Automatic Trigger (0–5 seconds)

When a developer opens a pull request, the platform automatically triggers parallel code analysis - static checks, security scanning, AST parsing, and CI test integration to ensure code quality.
Intelligent Analysis (10–30 seconds)
Code parsing builds abstract syntax trees, graph databases update dependencies, context retrieval fetches historical data, and LLMs generate actionable suggestions ranked by impact.
Unified Review Interface (Real-time)
Reviewer dashboard displays AI-powered risk analytics with interactive visualization. Each suggestion includes acceptance controls, supporting evidence links, and confidence scores for informed decision-making.
Quality Gate Evaluation (5–10 seconds)
Automated quality gates validate metrics against configured thresholds. Results post to PR with pass/warn/block statuses, blocking violations include technical rationale, and all checks are audit-trailed.
Continuous Learning (Ongoing)
Reviewer decisions refine the system: monitoring false positives/negatives, adaptive baseline optimization, and knowledge graph enrichment with validated patterns.
3.3 Secondary Workflow: Architectural Drift Detection

This workflow ensures the sustained integrity of the software ecosystem by autonomously monitoring structural evolution and flagging deviations from the intended design.
1.Continuous Structural Auditing (Scheduled Analysis) The platform executes automated, scheduled repository scans (e.g., weekly cycles). By parsing the Abstract Syntax Tree (AST), the system generates a current-state dependency graph and performs a comparative analysis against established versioned architectural baselines.
2.Drift Analytics & Pattern Recognition (Identification) The analysis engine identifies structural erosion by detecting:
2.1Coupling Anomalies: Unauthorized inter-module dependencies.
2.2Layer Violations: Breaches in strict architectural tiering (e.g., bypasses in a 3-tier architecture).
2.3Cyclic Dependencies: Emerging circular references that compromise modularity and testability.
3.Intelligent Remediation & Proactive Alerting Discovered deviations trigger automated notifications to Technical Leads and Architects. Beyond mere reporting, the system utilizes AI reasoning to provide refactoring prescriptions, accompanied by estimated LOE (Level of Effort) metrics to facilitate data-driven decision-making.
4.Architectural Governance & Longitudinal Tracking All drift reports are systematically archived within the Governance Console. The platform tracks key stability metrics over time, providing leadership with a quantitative "Architectural Health Index" to ensure long-term system maintainability and compliance with organizational standards.
3.4 Journey Stages
Stage	Duration	Actions	Thoughts / Quotes	Emotions
Trigger	0–5s	Developer opens a pull request; webhook captures event; code diff extracted; analysis pipeline initiated (static analysis, security scanning, AST parsing, CI test aggregation).	“The platform responded to the pull request event within 5 seconds, confirming real-time responsiveness.”	Excited
Analysis	10–30s	ASTs generated; graph database updated; context retrieved (call paths, history, docs); AI reasoning produces suggestions ranked by severity, confidence, and architectural impact.	“The analysis highlights architectural impact and historical evolution, confirming contextual reasoning.”	Curious
Review	Real-time	Reviewer dashboard displays risk overview; interactive visualizations (dependency graphs, dataflow diagrams, architecture violations); inline suggestions with Accept/Modify/Dismiss controls.	“Visualization of dependency graphs and confidence scores facilitates reviewer decision-making.”	Empowered
Quality Gate	5–10s	Automated checks compare metrics against baselines (complexity, coverage, security); status posted to PR (✓ Passed / ⚠ Warning / ✗ Blocked); violations flagged with rationale; audit log updated.	“Automated quality gate evaluation provides explicit pass/fail status and rationale for merge blocking.”	Confident
Feedback Loop	Ongoing	Reviewer actions captured; false positives/negatives tracked; baseline recommendations auto-tuned; knowledge graph enriched with validated patterns.	“Reviewer feedback is incorporated into model retraining, enhancing collaborative refinement of recommendations.”	Engaged

Chapter 4 | Business Reviews
4.1 Overview
This chapter provides a structured evaluation of the business implications, strategic positioning, and operational feasibility of the Graph-Augmented AI Code Review Platform. The review encompasses market demand, competitive landscape, cost-benefit analysis, and risk assessment. The objective is to demonstrate the platform’s value proposition, sustainability, and alignment with organizational goals.
4.2 Market Demand Analysis
Industry Trends:
Growing reliance on distributed microservices and complex architectures, increasing demand for automated QA in regulated industries, and rising adoption of AI tools to reduce manual effort and accelerate delivery.
Target Segments:
Enterprise Software Companies: Require scalable review processes across large codebases.
Startups and SMEs: Seek cost-effective solutions to improve code quality without expanding headcount.
Value Proposition:
Reduced review cycle time, improved architectural governance, enhanced compliance readiness.

4.3 Competitive Landscape
Dimensions	GitHub	SonarQube	AI-Based Quality Check On Project Code And Architecture	Code Tester
Core feature	Pull Request workflow, inline code comments, CI/CD integration	Static code analysis, bug/vulnerability detection, quality gate enforcement	AI-augmented PR review, AST + dependency graph analysis, architecture visualization, explainable AI reasoning	Manual review support, unit test coverage checks
Core Tech	LLM	Static Analysis Only	AST + Dependency Graphs + LLM Reasoning	Manual Review
Scope	Architectural Impact	Code Syntax Errors	Code Error
Architectural Impact
Historical Evolution	Unit Test
Coverage
Key
Advantage	Fast Speed	Fast Speed	Explainable Suggestions + ComplianceAudit Logs + graph + AST	Low Cost
Target
Audience	Small and medium-sized teams	Small and medium-sized teams	Large Teams / Architects/ Compliance Officers	Small Team

Differentiation and Advantages
The platform’s core strength lies in its architectural reasoning and explainability. Each AI-generated suggestion is accompanied by dataflow visualizations, and references to similar historical fixes, enabling reviewers to understand not only what should be changed but also why and how it affects the broader system. This transparent reasoning process builds trust, reduces false positives, and enhances reviewer confidence. In addition, the platform incorporates continuous baseline governance, automatically tracking deviations from defined quality metrics and generating immutable audit logs to meet compliance requirements. These features collectively contribute to improved transparency, compliance, and reviewer confidence
4.4 Risk Assessment
Technical Risks:
AI model accuracy and explainability.
Graph database scalability in very large monorepos.
Mitigation Strategies:
Continuous model retraining with reviewer feedback.
Modular integration architecture to reduce disruption.
4.5 Strategic & Standards Alignment
Organizational Goals:
- Enhance software quality and reliability.
- Reduce compliance burden in regulated industries.
- Improve engineering productivity and velocity.
Platform Contribution:
- Provides measurable ROI (Return on Investment) through reduced review times and defect rates.
- Strengthens governance and compliance posture.
- Enables proactive architectural monitoring and drift detection.
Alignment with International Standards:
- ISO/IEC 25010: Ensures adherence to software quality attributes including functionality, reliability, and maintainability.
- IEEE 1471: Supports architecture description standards for system governance and traceability.
- GDPR / HIPAA: Provides compliance with international data protection and healthcare regulations through immutable audit logs and automated reporting.
By integrating strategic organizational goals with internationally recognized standards, the platform demonstrates both technical effectiveness and global compliance readiness. This dual alignment ensures sustainability, scalability, and trustworthiness across diverse industries..
Chapter 5 | Software Reviews
5.1 Overview
This chapter evaluates the software components, frameworks, and tools integrated into the Graph-Augmented AI Code Review Platform. The review ensures that each element aligns with performance, scalability, and compliance requirements.
5.2Technology Review
5.2.1 External Services
Name	Description	Alternatives	Selection Rationale

GitHub	Online version control platform for collaborative software development.	GitLab, Bitbucket	Widely adopted, supports webhook integration, ideal for PR-driven analysis.

Docker	Containerization software providing lightweight virtual environments for microservices.	Kubernetes	Simplifies deployment, reduces resource usage, ensures environment consistency.
5.2.2 Development Tools
Name	Description	Alternatives	Selection Rationale

VS Code	General-purpose development environment with multi-language support.	WebStorm, Sublime Text	Rich plugin ecosystem, suitable for both frontend and backend.

PyCharm	Python IDE with auto-completion and debugging.	PyDev	Strong compatibility with FastAPI, Celery, and Python frameworks.
5.2.3 Libraries / Frameworks / Databases
Name	Description	Alternatives	Selection Rationale
 Next.js	Frontend framework supporting server-side rendering and code splitting.	Angular, Vue.js	Enhances performance and SEO, suitable for enterprise-grade applications.

Tailwind CSS	Utility-first CSS framework for reusable components.	Bootstrap	Provides modern, customizable UI design.

FastAPI	Lightweight, high-performance Python backend framework.	Django, Flask	Native async support, auto-generates OpenAPI docs.

Neo4j	Graph database for AST, CFG, and dependency storage.	JanusGraph	Powerful graph queries and algorithms, ideal for architecture analysis.

PostgreSQL	Relational database for transactional data and audit logs.	MySQL, MariaDB	Advanced queries, time-series extensions.

Redis	In-memory database for caching and queues.	Memcached	High performance, strong community support.
5.2.4 Infrastructure Tools Review
Amazon Elastic Compute Cloud (Amazon EC2)

Description: Part of AWS cloud computing, enabling users to rent virtual servers for applications. Selection Rationale:
Offers over 500 instance types with latest processors and storage.
Provides on-demand scalability and multi-AZ high availability.

5.3 Evaluation Criteria
Functionality: Ability to meet core requirements.
Scalability: Capacity to handle large repositories and distributed teams.
Maintainability: Ease of updates and long-term support.
Compliance: Adherence to industry standards and regulations.
5.4 Findings
Frontend Frameworks: React and Next.js provide modularity and performance.
Backend Frameworks: FastAPI ensures lightweight, asynchronous processing.
Databases: Neo4j (graph database) and PostgreSQL (relational database) complement each other for structural and transactional data.
5.5 Evaluation Methodology
The platform evaluation follows a structured methodology:
- Data Sources: Open-source and enterprise repositories were selected to represent diverse architectures.
- Metrics: Accuracy of AI suggestions, efficiency gains (review time, MTTR), architectural integrity, and compliance readiness.
- Procedure: Baseline manual reviews were compared against AI-assisted reviews, with outcomes logged and analyzed.
Chapter 6 | Objective
6.1 Primary Objectives
Deliver an AI-augmented code review platform that reduces manual effort and improves quality.
Provide architectural governance through graph-based analysis.
6.2 Secondary Objectives
Enhance developer experience with intuitive dashboards and visualizations.
Continuously learn from reviewer feedback to refine AI recommendations.
Support scalability across enterprises, startups, and regulated industries.

Chapter 7 | System Architecture
7.1 Overview
The system architecture is designed for modularity, scalability, and resilience. It integrates AI reasoning, graph databases, and monitoring tools into a cohesive workflow.
7.2 Components
Frontend Layer: React/Next.js for interactive dashboards.
Backend Layer: FastAPI for API orchestration and business logic.
Data Layer:
		Neo4j for graph relationships (AST, CFG, dependencies).
		PostgreSQL for transactional data and audit logs.
		Redis for caching and queues.
AI Layer: Large Language Model (LLM) .
CI/CD Integration: Webhooks and pipelines for automated triggers.
7.3 Architectural Principles
Scalability: Horizontal scaling with containerization.
Resilience: Multi-AZ deployment for high availability.
Security: Role-based access control and encrypted audit logs.
Performance Engineering:
		Incremental update: Only update the modified subgraphs
		Asynchronous Queue: Decoupling Real-time Analysis with Redis
		Graph partitioning: Divide the graph structure by service/module 
		Performance benchmark: Small database 8–12 s, medium-sized database 18–25 s, large database 35–50 s
7.4 Architecture Diagram

Chapter 8 | Features
8.1 Core Feature
8.1.1 Feature1: Code Review
This feature is designed to implement automated quality control before code merging. The system captures the Push Request or code differences submitted by programmers through GitHub Webhook, and uses a LLM to conduct a deep scan of the code logic. Its core objective is to identify potential logical flaws, security risks, and violations of coding standards like ISO/IEC 25010、ISO/IEC 23396, and directly outputs actionable review suggestions below the PR. This not only reduces the mechanical burden of manual review but also ensures that every line of code that enters the main branch complies with the project quality standards.
8.1.2 Feature2: Graph-based Architecture Analysis	
This feature is what distinguishes this platform from traditional static analysis tools. The system parses the source code to generate an abstract syntax tree (AST), extracts the dependencies between components, classes, and functions, and stores them in the Neo4j graph database. Through graph algorithms, the system can automatically draw dynamic architecture diagrams and monitor "architectural drift" in real time. When new code introduces unexpected couplings or circular dependencies, the system will promptly issue warnings to help architects maintain the overall integrity and health of the system.

8.1.3 Feature3: Agentic AI Reasoning
As the "brain" of the entire system, this module adopts the Agentic AI model as the underlying reasoning driver. The system supports flexible switching among multiple models (such as GPT-4, Claude 3.5, etc.). It is not merely a simple text processing tool; instead, it can conduct complex reasoning based on the project context provided by the graph database. The Agent can simulate architecture decision scenarios and provide deep suggestions with "explainability" for complex reconfiguration tasks, serving as the cornerstone for achieving intelligent analysis of the system.
The specific functions of AI:
	1.Pattern Recognition: Identifying code patterns that violate the principles of Clean Code.
	2.Contextual Reasoning: Considering the dependencies in the graph database to determine whether the current modification has disrupted the overall architectural logic.
	3.Natural Language Generation: Converting the dull static analysis results into review opinions that are understandable for developers. Knowledge base/data set: * Standard Patterns: Refer to well-established open-source standards in the industry (such as OWASP Top 10, Google Style Guides).
8.2 Auxiliary Features
8.2.1 Feature4: Authenticated System
To meet the enterprise-level security requirements, the system is equipped with a comprehensive identity verification and access control system. This module adopts the Role-Based Access Control (RBAC) mechanism, strictly differentiating the permissions of different roles such as administrators, programmers, and visitors. It ensures that sensitive architecture configuration data and project analysis reports are only accessible to authorized personnel, thereby safeguarding the security and audit compliance of code assets.
8.2.2 Feature5: Project Management 
This module is responsible for managing the entire lifecycle of code analysis tasks. It provides a project management dashboard for tracking the analysis queue, managing code repository links, and monitoring the task flow status. By precisely controlling the flow of personnel and code, this feature offers an orderly workspace for engineering managers, ensuring that all review tasks and architecture reports can be promptly processed and recorded.
Chapter 9 | Limitation
9.1 Technical Limitations
whether the trained model accurate enough.
Graph database performance may degrade with extremely large monorepos.
Integration complexity with legacy CI/CD pipelines.
9.2 Operational Limitations
Resistance to adoption in teams with established manual review practices.
Customization required for industry-specific compliance standards.