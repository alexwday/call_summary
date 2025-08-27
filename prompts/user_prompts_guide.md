# User Prompts Guide for Earnings Call Summary Analysis

This guide provides optimized prompts for analyzing bank earnings call summaries using the Chat+ application.

## Phase 1: Individual Bank Summary Analysis

For each bank's earnings call summary, use the following prompt after uploading the document:

### Prompt for Individual Analysis

```
Analyze this earnings call summary document and provide a comprehensive structural and content analysis. Focus on:

1. Document organization and section structure
2. Content selection criteria and prioritization patterns  
3. Financial metrics included and their presentation format
4. Qualitative elements and management commentary patterns
5. Formatting conventions and emphasis techniques
6. Information that appears to be deliberately excluded

Please identify:
- What makes this summary distinctive
- Patterns that appear consistent and reproducible
- Elements that seem bank-specific or quarter-specific
- The apparent decision logic for including/excluding information

Provide specific examples from the document to support your observations.
```

### Follow-up Questions for Deeper Analysis

After the initial analysis, you might ask:

```
Based on your analysis, what are the 3-5 most critical elements that define this bank's summarization approach?
```

```
What information from a typical earnings call appears to be intentionally excluded from this summary, and what might be the rationale?
```

```
How would you rate the reproducibility of this format on a scale of 1-10, and what elements contribute most to that score?
```

## Phase 2: Saving Individual Analyses

After analyzing each bank's summary:

1. Copy the complete analysis response
2. Save it to a document named: `[BankName]_[Quarter]_Analysis.md`
3. Repeat for all bank summaries you want to analyze

## Phase 3: Cross-Document Pattern Synthesis

Once you have analyzed all individual summaries and saved the analyses, upload all the analysis documents together and use this prompt:

### Prompt for Synthesis

```
I've uploaded multiple analyses of different bank earnings call summaries. Please synthesize these analyses to create:

1. A standardized template structure that could work across all banks
2. Core required sections that appear in all/most summaries
3. Optional sections with clear trigger conditions for inclusion
4. Best practices derived from the most effective patterns
5. A decision framework for content inclusion/exclusion
6. Specific formatting and presentation guidelines

Focus on:
- Identifying patterns that appear in 70%+ of analyses as "standard"
- Patterns in 40-69% as "common variations" 
- Patterns in <40% as "bank-specific"

Provide a practical, implementable template that balances standardization with necessary flexibility for bank-specific needs.
```

### Refinement Prompts

After receiving the synthesized template:

```
Based on this template, create a step-by-step implementation guide for preparing an earnings call summary from a raw transcript.
```

```
What are the top 5 quality metrics I should use to evaluate whether a summary prepared using this template meets professional standards?
```

```
Create a checklist of must-have elements for any earnings call summary based on the patterns you've identified.
```

## Phase 4: Template Application

When you want to apply the template to a new earnings call transcript:

### Prompt for New Summary Creation

```
I'm uploading an earnings call transcript for [Bank Name] [Quarter]. Using the standardized template we developed, please create a summary that:

1. Follows the standard structure we identified
2. Includes all mandatory sections
3. Evaluates which optional sections should be included based on the content
4. Applies the formatting and presentation conventions
5. Uses the content selection criteria we established

Please also note any challenges or ambiguities in applying the template to this specific transcript.
```

## Tips for Optimal Results

### Document Preparation
- Ensure summaries are complete and well-formatted before upload
- Remove any sensitive or confidential information
- If documents are very long, consider uploading in sections

### Model Selection
- Use **Large** model for initial analysis and synthesis (highest quality)
- Use **Medium** model for follow-up questions and clarifications
- Use **Small** model for simple formatting or extraction tasks

### Context Management
- Keep all relevant documents uploaded during analysis phase
- Remove documents that are no longer needed to reduce token usage
- Monitor token count and costs in the header display

### Iteration Strategy
1. Start with 2-3 summaries to test the analysis approach
2. Refine your prompts based on initial results
3. Scale up to full analysis once satisfied with output quality
4. Save intermediate results frequently

## Advanced Techniques

### Comparative Analysis
```
Compare the summary structures between [Bank A] and [Bank B]. What are the key philosophical differences in their approaches to summarization?
```

### Temporal Analysis
```
If you have summaries from the same bank across multiple quarters: How has [Bank Name]'s summary format evolved over time? What changes appear deliberate vs. incidental?
```

### Industry Segmentation
```
Group the analyzed banks by their summary patterns. Do these groups correlate with bank type (investment vs. retail vs. regional)?
```

## Expected Outputs

Your analysis should produce:

1. **Individual Analysis Documents**: Detailed structural analysis for each bank
2. **Synthesis Document**: Comprehensive template and guidelines
3. **Implementation Guide**: Step-by-step process for creating new summaries
4. **Quality Checklist**: Metrics and criteria for evaluation
5. **Template Document**: Ready-to-use template with clear instructions

## Troubleshooting

If the analysis seems incomplete or unclear:
- Break down complex prompts into smaller, specific questions
- Ask for specific examples to support general observations
- Request confidence levels for pattern identification
- Use follow-up prompts to drill into specific areas

Remember: The goal is to reverse-engineer the implicit methodology used in manual summarization and create an explicit, reproducible process.