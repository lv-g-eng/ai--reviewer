# PlantUML Diagrams for AI-Based Code Reviewer

This directory contains all PlantUML diagrams for the AI-Based Code Reviewer platform documentation.

## 📊 Available Diagrams (25 Total)

### Architecture Diagrams (3)

1. **system-architecture.puml** ✅
   - **Type**: Component Diagram
   - **Description**: Complete system architecture showing all layers, services, and data stores
   - **Referenced in**: SDD v2.1 - Section 2.1

2. **deployment-architecture.puml** ✅
   - **Type**: Deployment Diagram
   - **Description**: AWS deployment architecture with EKS, RDS, ElastiCache, and monitoring
   - **Referenced in**: SDD v2.1 - Section 7

3. **component-interaction.puml** ✅
   - **Type**: Sequence Diagram
   - **Description**: Detailed component interaction flow for PR review process
   - **Referenced in**: SDD v2.1 - Section 2.5

### Data Diagrams (11)

#### PostgreSQL ERD Diagrams (4)

4. **erd-postgresql-user-management.puml** ✅ NEW
   - **Type**: ERD Module
   - **Description**: User, Session, AuditLog entities
   - **Referenced in**: SDD v2.1 - Section 3.1

5. **erd-postgresql-project-management.puml** ✅ NEW
   - **Type**: ERD Module
   - **Description**: Project, ProjectMember, AnalysisConfig entities
   - **Referenced in**: SDD v2.1 - Section 3.1

6. **erd-postgresql-code-analysis.puml** ✅ NEW
   - **Type**: ERD Module
   - **Description**: PullRequest, Analysis, Issue, Comment, ComplianceCheck entities
   - **Referenced in**: SDD v2.1 - Section 3.1

7. **erd-postgresql-quality-metrics.puml** ✅ NEW
   - **Type**: ERD Module
   - **Description**: QualityMetric, TaskQueue entities
   - **Referenced in**: SDD v2.1 - Section 3.1

#### Neo4j Graph Diagrams (5)

8. **erd-neo4j-code-entities.puml** ✅ NEW
   - **Type**: Graph Model
   - **Description**: Module, Class, Function nodes with CONTAINS relationships
   - **Referenced in**: SDD v2.1 - Section 3.1

9. **erd-neo4j-dependencies.puml** ✅ NEW
   - **Type**: Graph Model
   - **Description**: DEPENDS_ON relationships between code entities
   - **Referenced in**: SDD v2.1 - Section 3.1

10. **erd-neo4j-calls.puml** ✅ NEW
    - **Type**: Graph Model
    - **Description**: CALLS relationships for function/method invocations
    - **Referenced in**: SDD v2.1 - Section 3.1

11. **erd-neo4j-inheritance.puml** ✅ NEW
    - **Type**: Graph Model
    - **Description**: INHERITS, IMPLEMENTS, EXTENDS relationships
    - **Referenced in**: SDD v2.1 - Section 3.1

12. **erd-neo4j-complete-graph.puml** ✅ NEW
    - **Type**: Graph Model
    - **Description**: Complete Neo4j architecture with all nodes and relationships
    - **Referenced in**: SDD v2.1 - Section 3.1

#### Complete Database Diagrams (2)

13. **entity-relationship-diagram.puml** ✅
    - **Type**: Complete ERD
    - **Description**: All PostgreSQL entities in one comprehensive diagram
    - **Referenced in**: SDD v2.1 - Section 3.1

14. **data-flow-diagram.puml** ✅
    - **Type**: Data Flow Diagram
    - **Description**: Data flow between system components and external services
    - **Referenced in**: SDD v2.1 - Section 2.4

### Design Diagrams (9)

#### Modular Class Diagrams (7)

15. **class-user-management.puml** ✅ NEW
    - **Type**: Class Diagram Module
    - **Description**: User Management domain - User, Session, AuthService, JWTManager, PasswordHasher, PermissionChecker
    - **Referenced in**: SDD v2.1 - Section 4.1

16. **class-project-management.puml** ✅ NEW
    - **Type**: Class Diagram Module
    - **Description**: Project Management domain - Project, ProjectMember, ProjectService, WebhookService, AnalysisConfig
    - **Referenced in**: SDD v2.1 - Section 4.1

17. **class-code-analysis.puml** ✅ NEW
    - **Type**: Class Diagram Module
    - **Description**: Code Analysis domain - PullRequest, Analysis, Issue, CodeReviewEngine, ParserService, IssueDetector
    - **Referenced in**: SDD v2.1 - Section 4.1

18. **class-architecture-analysis.puml** ✅ NEW
    - **Type**: Class Diagram Module
    - **Description**: Architecture Analysis domain - CodeEntity, Dependency, ArchitectureAnalyzer, ASTParser, GraphBuilder
    - **Referenced in**: SDD v2.1 - Section 4.1

19. **class-ai-integration.puml** ✅ NEW
    - **Type**: Class Diagram Module
    - **Description**: AI Integration domain - AgenticAI, LLMClient, ContextBuilder, PromptManager, EmbeddingService
    - **Referenced in**: SDD v2.1 - Section 4.1

20. **class-quality-metrics.puml** ✅ NEW
    - **Type**: Class Diagram Module
    - **Description**: Quality Metrics domain - QualityMetric, ComplianceCheck, MetricsService, TrendAnalyzer
    - **Referenced in**: SDD v2.1 - Section 4.1

21. **class-infrastructure.puml** ✅ NEW
    - **Type**: Class Diagram Module
    - **Description**: Infrastructure domain - GitHubClient, Neo4jClient, RedisClient, PostgreSQLClient, TaskQueue
    - **Referenced in**: SDD v2.1 - Section 4.1

#### Complete Design Diagrams (2)

22. **class-diagram.puml** ✅
    - **Type**: Complete Class Diagram
    - **Description**: All domains in one comprehensive object-oriented design diagram
    - **Referenced in**: SDD v2.1 - Section 4.1

23. **use-case-diagram.puml** ✅
    - **Type**: Use Case Diagram
    - **Description**: All use cases with actors and relationships
    - **Referenced in**: SRS v2.1 - Section 6.1

### Security & Operations Diagrams (2)

24. **security-architecture.puml** ✅
    - **Type**: Component Diagram
    - **Description**: Defense-in-depth security architecture with 6 layers
    - **Referenced in**: SDD-Security-Deployment.md - Section 5

25. **cicd-pipeline.puml** ✅
    - **Type**: Activity Diagram
    - **Description**: Complete CI/CD pipeline from commit to production
    - **Referenced in**: SDD v2.1 - Section 7

## 🎨 How to View Diagrams

### Online Viewer
1. Visit http://www.plantuml.com/plantuml/uml/
2. Copy the content of any `.puml` file
3. Paste and view the generated diagram

### VS Code
1. Install the "PlantUML" extension: `ext install jebbs.plantuml`
2. Install Graphviz:
   - Windows: `choco install graphviz`
   - Mac: `brew install graphviz`
   - Linux: `sudo apt-get install graphviz`
3. Open any `.puml` file
4. Press `Alt+D` to preview

### Command Line
```bash
# Install PlantUML
npm install -g node-plantuml

# Generate PNG
puml generate *.puml --png

# Generate SVG
puml generate *.puml --svg

# Or using Java
java -jar plantuml.jar *.puml
```

### Docker
```bash
# Generate all diagrams as PNG
docker run -v $(pwd):/data plantuml/plantuml -tpng /data/*.puml

# Generate all diagrams as SVG
docker run -v $(pwd):/data plantuml/plantuml -tsvg /data/*.puml
```

## 📝 Diagram Conventions

### Color Coding
- **Light Blue**: Client/Frontend components
- **Light Green**: API/Backend services
- **Orange**: Worker/Background processes
- **Light Steel Blue**: Relational databases
- **Light Pink**: Graph databases
- **Light Cyan**: Cache/Queue systems
- **Light Coral**: Monitoring/Logging
- **Light Yellow**: Gateway/Ingress
- **Light Salmon**: Incident response

### Naming Conventions
- Component names use PascalCase
- Service names include technology (e.g., "FastAPI", "Celery")
- Database names include type (e.g., "PostgreSQL", "Neo4j")

## 🔄 Updating Diagrams

When updating diagrams:

1. **Edit the `.puml` file** with your changes
2. **Test locally** using VS Code or online viewer
3. **Update references** in documentation if diagram name changes
4. **Commit changes** with descriptive message
5. **Regenerate images** if needed for presentations

## 📋 Diagram Checklist

When creating new diagrams:

- [ ] Use consistent color scheme
- [ ] Add title with `title` keyword
- [ ] Include legend or notes for clarity
- [ ] Reference in appropriate documentation
- [ ] Test rendering in multiple viewers
- [ ] Add to this README

## 🔗 Related Documentation

- **SRS v2.1**: `docs/ProjectName-SRS_v2.1.md`
- **SDD v2.1**: `docs/ProjectName-SDD_v2.1.md`
- **Security & Deployment**: `docs/SDD-Security-Deployment.md`
- **Use Cases**: `docs/SRS-UseCases-Detailed.md`
- **Document Navigation**: `docs/README-文档导航.md`

## 📊 Diagram Statistics

| Diagram Type | Count | Total Elements |
|--------------|-------|----------------|
| Architecture | 3 | ~50 components |
| Data - PostgreSQL ERD | 4 | ~15 entities |
| Data - Neo4j Graph | 5 | ~10 node types |
| Data - Complete | 2 | ~30 entities |
| Design - Modular Classes | 7 | ~120 classes |
| Design - Complete | 2 | ~70 classes |
| Security/Ops | 2 | ~40 components |
| **Total** | **25** | **~335 elements** |

### Diagram Organization

```
docs/diagram/
├── Architecture (3)
│   ├── system-architecture.puml
│   ├── deployment-architecture.puml
│   └── component-interaction.puml
├── Data - PostgreSQL (4)
│   ├── erd-postgresql-user-management.puml
│   ├── erd-postgresql-project-management.puml
│   ├── erd-postgresql-code-analysis.puml
│   └── erd-postgresql-quality-metrics.puml
├── Data - Neo4j (5)
│   ├── erd-neo4j-code-entities.puml
│   ├── erd-neo4j-dependencies.puml
│   ├── erd-neo4j-calls.puml
│   ├── erd-neo4j-inheritance.puml
│   └── erd-neo4j-complete-graph.puml
├── Data - Complete (2)
│   ├── entity-relationship-diagram.puml
│   └── data-flow-diagram.puml
├── Design - Modular Classes (7)
│   ├── class-user-management.puml
│   ├── class-project-management.puml
│   ├── class-code-analysis.puml
│   ├── class-architecture-analysis.puml
│   ├── class-ai-integration.puml
│   ├── class-quality-metrics.puml
│   └── class-infrastructure.puml
├── Design - Complete (2)
│   ├── class-diagram.puml
│   └── use-case-diagram.puml
└── Security/Ops (2)
    ├── security-architecture.puml
    └── cicd-pipeline.puml
```

## 📤 Export Formats

PlantUML supports multiple export formats:

```bash
plantuml -tpng diagram.puml    # PNG (default)
plantuml -tsvg diagram.puml    # SVG (vector)
plantuml -tpdf diagram.puml    # PDF
plantuml -teps diagram.puml    # EPS
plantuml -tlatex diagram.puml  # LaTeX
```

## 🎨 Customization

### Change Theme
```plantuml
!theme cerulean
!theme plain
!theme sketchy-outline
```

### Modify Colors
```plantuml
skinparam backgroundColor #FFFFFF
skinparam classBackgroundColor #LightBlue
skinparam classBorderColor #Blue
```

### Add Notes
```plantuml
note right of ClassName
  This is a note
end note
```

## 📚 PlantUML Resources

- [Official Documentation](https://plantuml.com/)
- [Class Diagram Syntax](https://plantuml.com/class-diagram)
- [Sequence Diagram Syntax](https://plantuml.com/sequence-diagram)
- [Use Case Diagram Syntax](https://plantuml.com/use-case-diagram)
- [Activity Diagram Syntax](https://plantuml.com/activity-diagram-beta)
- [Deployment Diagram Syntax](https://plantuml.com/deployment-diagram)

## 🤝 Contributing

To add new diagrams or improve existing ones:

1. Create or modify `.puml` file
2. Ensure diagram is clear and readable
3. Update this README
4. Submit Pull Request

## 📞 Support

For questions or suggestions:
- Check [PlantUML Official Documentation](https://plantuml.com/)
- Create an Issue in the project
- Contact project maintainers

---

**Last Updated**: 2026-02-18  
**Maintained By**: Project Team  
**Total Diagrams**: 25 (16 new modular diagrams in v2.1)
