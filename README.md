# FS 2.0 Prototype

This is a prototype for a genealogy research tool focused on integrating with FamilySearch and other providers. The system is designed with modular servers to handle API interactions, record routing, document processing, analysis, research management, and location services.

## Project Overview

The prototype aims to build an efficient, ethical genealogy research system using AI agents. It follows a split-server architecture for scalability and maintainability. Key features include secure API access, data standardization, privacy compliance, and incremental development.

## Suggestions for Changes and Adjustments

Before proceeding with development, incorporate the following refinements:

1. **Adopt GEDCOM X as a Standard Data Format**: Standardize outputs to GEDCOM X for interoperability.
2. **Enhance Privacy and Compliance Features**: Add consent mechanisms, anonymization, and compliance with data regs.
3. **Refine Authentication Strategy**: Use OAuth Code Flow with a centralized auth module.
4. **Incorporate AI-Specific Best Practices**: Include human-in-the-loop validation, aggressive caching, and fallbacks.
5. **Start with a Minimal Prototype Scope**: Begin with FamilySearch API Server and Records Router, 5-7 core tools.
6. **Add Non-Functional Priorities**: Security (env vars, sanitization), Testing (80%+ coverage with pytest), Deployment (Docker Compose), Monitoring (basic logging).
7. **Tool List Tweaks**: Prioritize reusability, add `merge_results` in Records Router.

These adjustments will enhance resilience and alignment with best practices.

## Product Requirements Documents (PRDs)

Detailed PRDs for each server are available in the `docs` directory:

- [Suggestions for Changes](./docs/suggestions.md)
- [PRD 1: FamilySearch API Server](./docs/prd1-familysearch-api-server.md)
- [PRD 2: Records Router Server](./docs/prd2-records-router-server.md)
- [PRD 3: Document Processing Server](./docs/prd3-document-processing-server.md)
- [PRD 4: Analysis Server](./docs/prd4-analysis-server.md)
- [PRD 5: Research Management Server](./docs/prd5-research-management-server.md)
- [PRD 6: Location Server](./docs/prd6-location-server.md)

## Next Steps

Following the minimal prototype scope, we will start by implementing the FamilySearch API Server and Records Router in Python, ensuring alignment with the PRDs and suggestions.

## Development Guidelines

- Use Python for backend servers.
- Follow best practices for async handling, security, and testing as outlined.
- For any frontend/mobile components, adhere to React Native and Expo guidelines (though backend-focused initially).
