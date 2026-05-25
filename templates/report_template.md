# Design Review Report Template

# Design Review Report: {COMPONENT_NAME}

**Ticket**: {TICKET_ID}  
**Date**: {REVIEW_DATE}  
**Component**: {COMPONENT_NAME}  
**Review Status**: {STATUS}  
**Overall Assessment**: {OVERALL_ASSESSMENT}

---

## Executive Summary

{SUMMARY_TEXT}

### Key Findings

| Severity | Count | Status |
|----------|-------|--------|
| Critical | {CRITICAL_COUNT} | {CRITICAL_STATUS} |
| High | {HIGH_COUNT} | {HIGH_STATUS} |
| Medium | {MEDIUM_COUNT} | {MEDIUM_STATUS} |
| Low | {LOW_COUNT} | {LOW_STATUS} |

### Recommendation

**Status**: {APPROVE|APPROVE_WITH_CONDITIONS|REJECT}  
**Timeline**: {IMPLEMENTATION_TIMELINE}

---

## 1. Requirements Analysis

### Overview
- **Total Requirements**: {TOTAL_REQS}
- **Clear Requirements**: {CLEAR_REQS}
- **Ambiguous Requirements**: {AMBIGUOUS_REQS}
- **Missing Requirements**: {MISSING_REQS}
- **Completeness Score**: {COMPLETENESS_SCORE}%

### Findings

#### Ambiguous Requirements
{AMBIGUOUS_FINDINGS}

#### Missing Requirements
{MISSING_FINDINGS}

#### Recommendations
{REQ_RECOMMENDATIONS}

---

## 2. Architecture Review

### Component Assessment
{COMPONENT_FINDINGS}

### Design Patterns
{PATTERN_FINDINGS}

### Technical Debt
- **Current Level**: {DEBT_LEVEL}
- **Estimated Remediation Effort**: {REMEDIATION_EFFORT}
- **Key Areas**:
  {DEBT_AREAS}

### Architecture Recommendations
{ARCH_RECOMMENDATIONS}

---

## 3. Security & Compliance Review

### Vulnerability Assessment

#### Critical Issues
{CRITICAL_VULNS}

#### High-Severity Issues
{HIGH_VULNS}

### Compliance Status

#### GDPR
- **Status**: {GDPR_STATUS}
- **Gaps**: {GDPR_GAPS}

#### SOC 2
- **Status**: {SOC2_STATUS}
- **Gaps**: {SOC2_GAPS}

### Security Recommendations
{SEC_RECOMMENDATIONS}

---

## 4. Scalability & Performance Assessment

### Performance Metrics
- **Response Time**: {RESPONSE_TIME_ASSESSMENT}
- **Throughput**: {THROUGHPUT_ASSESSMENT}
- **Concurrent Users**: {CONCURRENT_USERS_ASSESSMENT}

### Identified Bottlenecks
{BOTTLENECK_FINDINGS}

### Growth Projections
- **1 Year**: {GROWTH_YEAR1}
- **2 Years**: {GROWTH_YEAR2}
- **3 Years**: {GROWTH_YEAR3}

### Scalability Recommendations
{SCALABILITY_RECOMMENDATIONS}

---

## 5. Risk Matrix

```
        | Low Impact | Medium Impact | High Impact
--------|-----------|---------------|----------
High    | MEDIUM    | HIGH          | CRITICAL
Prob    | MEDIUM    | MEDIUM        | HIGH
Low     | LOW       | MEDIUM        | LOW
```

### Risk Distribution

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Security | {SEC_C} | {SEC_H} | {SEC_M} | {SEC_L} |
| Architecture | {ARCH_C} | {ARCH_H} | {ARCH_M} | {ARCH_L} |
| Performance | {PERF_C} | {PERF_H} | {PERF_M} | {PERF_L} |
| Compliance | {COMP_C} | {COMP_H} | {COMP_M} | {COMP_L} |

---

## 6. Recommendations Summary

### Critical Priority (Immediate)
{CRITICAL_RECS}

### High Priority (Short-term: 1-2 sprints)
{HIGH_RECS}

### Medium Priority (Medium-term: 1-2 months)
{MEDIUM_RECS}

### Low Priority (Long-term)
{LOW_RECS}

---

## 7. Approval Sign-Off

### Review Completion
- ✓ Requirements Analysis: Complete
- ✓ Architecture Review: Complete
- ✓ Security Review: Complete
- ✓ Scalability Review: Complete

### Approval Status
- **Architecture Review**: {ARCH_APPROVAL}
- **Security Review**: {SEC_APPROVAL}
- **Performance Review**: {PERF_APPROVAL}
- **Overall Status**: {OVERALL_APPROVAL}

### Approval Signatures
- **Reviewed By**: AI Design Review Agent v1.0
- **Date**: {REVIEW_DATE}
- **Recommendation**: {FINAL_RECOMMENDATION}

**Pending Human Review and Final Sign-off**

---

## 8. Audit Trail

### Review Metadata
- **Review ID**: {REVIEW_ID}
- **Ticket**: {TICKET_ID}
- **Component**: {COMPONENT_NAME}
- **Version**: {DESIGN_VERSION}
- **Review Date**: {REVIEW_DATE}
- **Reviewed By**: AI Design Review Agent v1.0

### Artifacts Analyzed
{ARTIFACTS_LIST}

### Standards Applied
{STANDARDS_LIST}

### Review Execution Details
- **Total Review Time**: {REVIEW_TIME}
- **Agents Executed**: {AGENTS_COUNT}
- **Findings Generated**: {FINDINGS_COUNT}
- **Recommendations**: {RECOMMENDATIONS_COUNT}

### Change History
{CHANGE_HISTORY}

---

## 9. Next Steps

1. Address critical findings immediately
2. Plan remediation for high-severity items
3. Include medium/low items in backlog
4. Schedule follow-up review after fixes
5. Document design decisions and rationale

---

**Report Generated**: {GENERATED_DATE}  
**Report Version**: 1.0  
**Status**: Ready for Review
