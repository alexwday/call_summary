/**
 * StreamingMarkdownRenderer - A robust markdown renderer for streaming content
 * Handles partial content intelligently without freezing
 */
class StreamingMarkdownRenderer {
    constructor() {
        this.buffer = '';
        this.renderQueue = [];
        this.isRendering = false;
        this.lastRenderTime = 0;
        this.minRenderInterval = 50; // Minimum ms between renders
        
        // Configure marked with safe defaults
        this.configureMarked();
    }
    
    configureMarked() {
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                tables: true,
                sanitize: false, // We'll use DOMPurify
                pedantic: false,
                smartLists: true,
                smartypants: false,
                headerIds: false,
                mangle: false
            });
        }
    }
    
    /**
     * Main entry point for streaming content
     */
    processStreamingContent(content, targetElement) {
        this.buffer = content;
        
        // Quick safety check for obviously incomplete structures
        const safeContent = this.extractSafeContent(content);
        
        // Throttle rendering
        const now = Date.now();
        if (now - this.lastRenderTime < this.minRenderInterval) {
            // Queue for later
            if (!this.renderTimeout) {
                this.renderTimeout = setTimeout(() => {
                    this.renderTimeout = null;
                    this.renderToElement(safeContent, targetElement);
                }, this.minRenderInterval);
            }
        } else {
            this.renderToElement(safeContent, targetElement);
            this.lastRenderTime = now;
        }
    }
    
    /**
     * Extract content that's safe to render (complete structures only)
     * IMPORTANT: Preserve order - don't extract tables/lists out of sequence
     */
    extractSafeContent(content) {
        // For streaming, we should be more conservative
        // Only render complete paragraphs and let marked handle the rest
        // This prevents reordering issues
        
        let safeContent = '';
        const lines = content.split('\n');
        let inCodeBlock = false;
        let codeBlockBuffer = '';
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // Track code blocks to avoid rendering incomplete ones
            if (line.startsWith('```')) {
                if (!inCodeBlock) {
                    inCodeBlock = true;
                    codeBlockBuffer = line + '\n';
                } else {
                    // End of code block
                    codeBlockBuffer += line + '\n';
                    safeContent += codeBlockBuffer;
                    codeBlockBuffer = '';
                    inCodeBlock = false;
                }
                continue;
            }
            
            if (inCodeBlock) {
                codeBlockBuffer += line + '\n';
                continue;
            }
            
            // For everything else, just add it directly
            // Let marked.js handle table detection and rendering
            // This preserves the original order
            safeContent += line + '\n';
        }
        
        // If we're still in a code block, don't render it yet
        // It will be rendered when complete
        
        return safeContent;
    }
    
    /**
     * Check if text looks like a table row
     */
    looksLikeTableRow(line) {
        // Must have at least 2 pipes and some content
        const pipeCount = (line.match(/\|/g) || []).length;
        if (pipeCount < 2) return false;
        
        // Check for separator row (contains dashes and pipes)
        if (/^\s*\|[\s\-:|]+\|\s*$/.test(line)) return true;
        
        // Check for data row (has pipes with content between them)
        if (/\|.*\|/.test(line)) return true;
        
        return false;
    }
    
    /**
     * Check if a table is complete enough to render
     */
    isTableComplete(tableContent, nextLine) {
        const lines = tableContent.trim().split('\n');
        
        // Need at least header and separator
        if (lines.length < 2) return false;
        
        // Check if we have a separator row
        const hasSeparator = lines.some(line => /^\s*\|[\s\-:|]+\|\s*$/.test(line));
        
        // If no separator yet, not complete
        if (!hasSeparator) return false;
        
        // If next line looks like table row, not complete
        if (nextLine && this.looksLikeTableRow(nextLine)) return false;
        
        // Check if last line has balanced pipes
        const lastLine = lines[lines.length - 1];
        const firstPipe = lastLine.indexOf('|');
        const lastPipe = lastLine.lastIndexOf('|');
        
        // Must have at least opening and closing pipe
        if (firstPipe === -1 || lastPipe === -1 || firstPipe === lastPipe) return false;
        
        return true;
    }
    
    /**
     * Check if text looks like a list item
     */
    looksLikeListItem(line) {
        return /^(\s*)([-*+]|\d+\.)\s+/.test(line);
    }
    
    /**
     * Render content to element with fallback
     */
    renderToElement(content, targetElement) {
        if (!content.trim()) {
            targetElement.innerHTML = '';
            return;
        }
        
        try {
            // Try marked.js rendering with timeout protection
            const rendered = this.renderWithTimeout(content, 100);
            
            if (rendered) {
                // Sanitize and apply
                const sanitized = DOMPurify.sanitize(rendered);
                targetElement.innerHTML = sanitized;
            } else {
                // Timeout or error - use fallback
                this.renderFallback(content, targetElement);
            }
        } catch (error) {
            console.warn('Markdown render error:', error);
            this.renderFallback(content, targetElement);
        }
    }
    
    /**
     * Render with timeout protection
     */
    renderWithTimeout(content, timeoutMs) {
        if (typeof marked === 'undefined') {
            return null;
        }
        
        let result = null;
        let completed = false;
        
        // Try to render
        try {
            // Use a promise race between rendering and timeout
            const renderPromise = new Promise((resolve) => {
                result = marked.parse(content);
                completed = true;
                resolve(result);
            });
            
            // For synchronous marked, we need a different approach
            // Just do a direct call with try-catch
            const startTime = performance.now();
            result = marked.parse(content);
            const elapsed = performance.now() - startTime;
            
            if (elapsed > timeoutMs) {
                console.warn(`Markdown rendering took ${elapsed}ms, using fallback`);
                return null;
            }
            
            return result;
        } catch (error) {
            console.warn('Markdown parsing error:', error);
            return null;
        }
    }
    
    /**
     * Fallback renderer - simple HTML escaping and basic formatting
     */
    renderFallback(content, targetElement) {
        // Create a pre-formatted display with basic enhancements
        const lines = content.split('\n');
        let html = '<div class="markdown-fallback">';
        
        for (const line of lines) {
            if (!line.trim()) {
                html += '<br>';
                continue;
            }
            
            let processedLine = this.escapeHtml(line);
            
            // Basic formatting
            // Headers
            if (line.startsWith('# ')) {
                processedLine = `<h1>${this.escapeHtml(line.slice(2))}</h1>`;
            } else if (line.startsWith('## ')) {
                processedLine = `<h2>${this.escapeHtml(line.slice(3))}</h2>`;
            } else if (line.startsWith('### ')) {
                processedLine = `<h3>${this.escapeHtml(line.slice(4))}</h3>`;
            }
            // Bold
            else if (line.includes('**')) {
                processedLine = processedLine.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            }
            // Italic
            else if (line.includes('*')) {
                processedLine = processedLine.replace(/\*(.*?)\*/g, '<em>$1</em>');
            }
            // Code
            else if (line.includes('`')) {
                processedLine = processedLine.replace(/`(.*?)`/g, '<code>$1</code>');
            }
            // List items
            else if (/^[-*+]\s/.test(line)) {
                processedLine = `• ${this.escapeHtml(line.slice(2))}`;
            }
            // Numbered lists
            else if (/^\d+\.\s/.test(line)) {
                processedLine = line;
            }
            // Tables - just show as monospace
            else if (line.includes('|')) {
                processedLine = `<pre style="margin:0;display:inline;">${this.escapeHtml(line)}</pre>`;
            } else {
                processedLine = `<span>${processedLine}</span>`;
            }
            
            html += processedLine + '<br>';
        }
        
        html += '</div>';
        targetElement.innerHTML = html;
    }
    
    /**
     * HTML escape utility
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Final render when streaming is complete
     */
    finalRender(content, targetElement) {
        // Clear any pending timeouts
        if (this.renderTimeout) {
            clearTimeout(this.renderTimeout);
            this.renderTimeout = null;
        }
        
        // Reset state
        this.buffer = '';
        
        // Log for debugging
        console.log('Final render - content length:', content.length);
        
        // Do a complete render
        try {
            if (typeof marked !== 'undefined') {
                const rendered = marked.parse(content);
                const sanitized = DOMPurify.sanitize(rendered);
                targetElement.innerHTML = sanitized;
                
                // Check if we rendered any tables
                const tables = targetElement.querySelectorAll('table');
                if (tables.length > 0) {
                    console.log('Rendered', tables.length, 'table(s) in final render');
                }
            } else {
                this.renderFallback(content, targetElement);
            }
        } catch (error) {
            console.error('Final render error:', error);
            console.error('Content that failed:', content.substring(0, 500));
            this.renderFallback(content, targetElement);
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StreamingMarkdownRenderer;
}