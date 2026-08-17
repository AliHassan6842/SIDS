package com.agrosense.knowledge.domain;

import java.util.List;

public interface KnowledgeEvidenceProvider {
    List<String> getSemanticEvidence(String query);
    List<String> getDocumentEvidence(String query);
}
