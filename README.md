# TTB AI-Powered Alcohol Label Verification Prototype

## Approach & Stakeholder Alignment
This prototype was designed specifically keeping Sarah Chen, Dave Morrison, and Jenny Park's feedback in mind:
- **Speed (<5s requirement):** Utilizes `gemini-3.8-flash` for sub-second multimodal analysis, solving the latency bottleneck of previous vendor pilots.
- **Human-in-the-Loop Judgment:** Solves Dave's concern about overly strict rigid matching by allowing semantic equivalence (e.g., handling minor punctuation differences in brand names like "STONE'S THROW").
- **Statutory Warning Auditor:** Automatically validates Jenny's requirement that the government warning is present and formatted correctly with all-caps prefix.
- **Batch Processing:** Addresses Janet's request from the Seattle office for multi-file importer uploads during peak season.
- **Accessibility:** Clean, high-contrast, zero-clutter interface designed for agents across all tech-comfort levels.

## Local Setup & Run Instructions
1. Clone the repository:
   ```bash
   git clone [https://github.com/OP-PubGit/ttb-label-verifier.git](https://github.com/OP-PubGit/ttb-label-verifier.git)
   cd ttb-label-verifier
