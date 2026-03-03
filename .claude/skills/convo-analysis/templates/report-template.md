# Session Analysis
Generated: {timestamp}

## Conversation Flow

### User (Turn 1)
- **Message Type**: {direct-request | meta-request | mixed-content | clarification | feedback}
- **Content**: {sanitized message - what they requested/said}
- **Clarity**: {clear | ambiguous | unclear} - {reason}
- **Context Given**: {sufficient | partial | missing}

### AI (Turn 1)
- **Interpretation**: {what AI understood from user message}
- **Action**: {tool/command used, if any}
- **Skill**: {skill activated, if any}
- **Agent**: {subagent spawned, if any}
- **Response**: {sanitized summary of response}
- **Alignment**: {aligned | misaligned} with {rule/workflow}

{... continue for all turns ...}

## Behavior Analysis

### User Behavior
| Turn | Issue | Impact |
|------|-------|--------|
| {N} | {unclear boundaries / mixed content / missing context / ambiguous request} | {how it affected AI response} |

### AI Behavior
| Turn | Issue | Rule Violated |
|------|-------|---------------|
| {N} | {rushed implementation / skipped delegation / assumed requirements} | {specific rule from orchestrator-directives.py or _apply-all.md} |

### Contribution Summary
| Party | Contribution to Issues |
|-------|----------------------|
| User | {percentage}% - {primary issues} |
| AI | {percentage}% - {primary issues} |

## Expected Behavior

### User Should Have
- Turn {N}: {clearer request format / explicit boundaries / more context}

### AI Should Have
- Turn {N}: {asked clarifying question / used /research / waited for approval}

## Improvements

### For User Communication
- {specific improvement to request patterns}
- {how to structure mixed-content messages}

### For AI Behavior
- {specific improvement to skill/command}
- {rule clarification needed}

### For System (Skills/Commands/Rules)
- {improvements to convo-analysis skill}
- {improvements to orchestrator-directives.py or _apply-all.md}
