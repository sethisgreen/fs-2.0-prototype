### Suggestions for Changes or Adjustments Before Prototyping

Based on the current project architecture and recent best practices in genealogy tools and API development, the overall plan remains robust—modular servers, Python focus, async handling, and incremental building align well with recommendations for scalable, ethical genealogy systems. However, here are targeted suggestions to refine it before diving into code. These draw from trends like responsible AI integration in family history (e.g., emphasizing validation and ethics), API interoperability, and streamlined workflows.

1. **Adopt GEDCOM X as a Standard Data Format**: Genealogy tools thrive on interoperability. Standardize all tool outputs (e.g., search results, parsed documents) to GEDCOM X format where possible, as it's the basis for FamilySearch responses and widely supported. This enables seamless data exchange between servers (e.g., piping census results directly to the Analysis Server for relationship calculations) and future exports to tools like Ancestry or personal trees. Add a utility layer for conversion if needed.

2. **Enhance Privacy and Compliance Features**: Family history data is sensitive. Introduce explicit user consent mechanisms (e.g., a `consent_to_process` tool) and anonymization options for shared workflows. Ensure compliance with data protection regs (e.g., GDPR/CCPA equivalents in 2025) by logging only minimal personal data and offering data deletion tools. For APIs like FamilySearch, confirm ToS allow AI-agent usage—avoid bulk automation that could trigger bans; perhaps limit queries per session.

3. **Refine Authentication Strategy**: While Password Grant is fine for dev, mandate OAuth Code Flow for all production servers to avoid handling raw credentials. Add a centralized auth server or module to manage tokens across providers (FamilySearch, Ancestry, etc.), with auto-refresh and multi-user support. This reduces security risks and scales for collaborative research.

4. **Incorporate AI-Specific Best Practices**: From ongoing discussions on AI in genealogy (e.g., the 2025 AI Genealogy Do-Over initiatives), add human-in-the-loop validation for AI-suggested outputs like "next steps" or conflict detection to prevent propagation of errors (e.g., hallucinated relationships). Also, integrate caching more aggressively to respect API rate limits, and include fallback mechanisms (e.g., manual query overrides) for when AI agents misinterpret user intent.

5. **Start with a Minimal Prototype Scope**: To accelerate learning, prototype only the FamilySearch API Server and a basic Records Router first, with 5-7 core tools total. Defer advanced features like OCR in Document Processing until after end-to-end testing. This mirrors advice for genealogy workflows: build incrementally, test with real data (use anonymized samples), and iterate based on agent performance.

6. **Add Non-Functional Priorities**:

   - **Security**: Use env vars or secrets managers (e.g., Docker secrets) for all creds; implement input sanitization to prevent injection attacks.
   - **Testing**: Mandate 80%+ coverage with pytest from day one, including API mocks.
   - **Deployment**: Containerize everything with Docker Compose for easy local/prod parity.
   - **Monitoring**: Add basic logging (e.g., to stdout or ELK) for tool usage and errors.

7. **Tool List Tweaks**: For the MVP, prioritize cross-server reusability—e.g., make `normalize_place` a shared utility. Consider adding a `merge_results` tool in the Records Router to deduplicate across providers.

These adjustments should take 1-2 days to incorporate into planning and will make the prototype more resilient. No major overhauls needed; the split-server approach already future-proofs for adding providers like Ancestry.
