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
        
        // State tracking
        this.inCodeBlock = false;
        this.inTable = false;
        this.inList = false;
        this.codeBlockDelimiter = '';
        this.tableBuffer = '';
        this.listBuffer = '';
        
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
     */
    extractSafeContent(content) {
        let safeContent = '';
        let buffer = '';
        const lines = content.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const nextLine = lines[i + 1];
            
            // Check for code block
            if (line.startsWith('```')) {
                if (!this.inCodeBlock) {
                    this.inCodeBlock = true;
                    this.codeBlockDelimiter = line;
                    buffer = line + '\n';
                } else if (line === '```' || line.startsWith('```')) {
                    // End of code block
                    this.inCodeBlock = false;
                    buffer += line + '\n';
                    safeContent += buffer;
                    buffer = '';
                }
                continue;
            }
            
            // If in code block, buffer everything
            if (this.inCodeBlock) {
                buffer += line + '\n';
                continue;
            }
            
            // Check for table
            if (this.looksLikeTableRow(line)) {
                if (!this.inTable) {
                    this.inTable = true;
                    this.tableBuffer = line + '\n';
                } else {
                    this.tableBuffer += line + '\n';
                }
                
                // Check if table is complete
                if (this.isTableComplete(this.tableBuffer, nextLine)) {
                    safeContent += this.tableBuffer;
                    this.tableBuffer = '';
                    this.inTable = false;
                }
                continue;
            } else if (this.inTable) {
                // Line doesn't look like table, table must be complete
                safeContent += this.tableBuffer;
                this.tableBuffer = '';
                this.inTable = false;
                // Process current line normally
            }
            
            // Check for lists
            if (this.looksLikeListItem(line)) {
                if (!this.inList) {
                    this.inList = true;
                    this.listBuffer = line + '\n';
                } else {
                    this.listBuffer += line + '\n';
                }
                
                // Check if list is complete (next line isn't a list item or indented)
                if (!nextLine || (!this.looksLikeListItem(nextLine) && !nextLine.match(/^\s{2,}/))) {
                    safeContent += this.listBuffer;
                    this.listBuffer = '';
                    this.inList = false;
                }
                continue;
            } else if (this.inList) {
                // Check for indented continuation
                if (line.match(/^\s{2,}/)) {
                    this.listBuffer += line + '\n';
                    continue;
                } else {
                    // List is complete
                    safeContent += this.listBuffer;
                    this.listBuffer = '';
                    this.inList = false;
                }
            }
            
            // Regular line - safe to add
            if (!this.inCodeBlock && !this.inTable && !this.inList) {
                safeContent += line + '\n';
            }
        }
        
        // Don't render incomplete structures
        // They'll be rendered when complete
        
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
        this.inCodeBlock = false;
        this.inTable = false;
        this.inList = false;
        this.tableBuffer = '';
        this.listBuffer = '';
        
        // Do a complete render
        try {
            if (typeof marked !== 'undefined') {
                const rendered = marked.parse(content);
                const sanitized = DOMPurify.sanitize(rendered);
                targetElement.innerHTML = sanitized;
            } else {
                this.renderFallback(content, targetElement);
            }
        } catch (error) {
            console.error('Final render error:', error);
            this.renderFallback(content, targetElement);
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StreamingMarkdownRenderer;
}